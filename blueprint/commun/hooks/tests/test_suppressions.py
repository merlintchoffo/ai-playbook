#!/usr/bin/env python3
"""Tests des suppressions récursives forcées (rm -rf) dans bloquer-commandes-interdites.
Lancer : python3 -I -B blueprint/commun/hooks/tests/test_suppressions.py

Règle testée : sans demander seulement si toutes les cibles sont dans le dépôt git du dossier de travail
(ni sa racine, ni .git) et récupérables par git (suivies, sans modification), ou dans le scratchpad de la
session ; sinon la fenêtre d'autorisation de Claude Code est demandée (permissionDecision « ask »)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "bloquer-commandes-interdites.py"
SESSION = "11111111-2222-3333-4444-555555555555"


class Cas(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.maison = self.base / "maison"
        (self.maison / ".claude").mkdir(parents=True)
        (self.maison / ".claude/settings.json").write_text(json.dumps({"permissions": {"deny": ["Bash(sshpass *)"]}}))
        self.env = {"PATH": os.environ["PATH"], "HOME": str(self.maison), "GIT_CONFIG_NOSYSTEM": "1",
                    "GIT_CONFIG_GLOBAL": str(self.base / "gitconfig")}
        (self.base / "gitconfig").write_text("[user]\n\tname = t\n\temail = t@example.org\n")
        self.depot = self.base / "depot"
        (self.depot / "src/sous").mkdir(parents=True)
        (self.depot / "src/a.txt").write_text("a")
        (self.depot / "src/sous/b.txt").write_text("b")
        (self.depot / ".gitignore").write_text("node_modules/\n")
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "init")
        self._tmp_scratch = tempfile.TemporaryDirectory(dir=f"/tmp/claude-{os.getuid()}")
        # Comme le vrai : /tmp/claude-<uid>/<projet>/<session>/scratchpad
        self.scratch = Path(self._tmp_scratch.name) / SESSION / "scratchpad"
        (self.scratch / "essai").mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()
        self._tmp_scratch.cleanup()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.depot, env=self.env, capture_output=True, text=True)

    def lancer(self, commande, cwd=None, session=SESSION):
        entree = json.dumps({"tool_name": "Bash", "tool_input": {"command": commande},
                             "cwd": str(cwd or self.depot), "session_id": session})
        r = subprocess.run([sys.executable, "-I", "-B", str(HOOK)], input=entree, env=self.env,
                           capture_output=True, text=True)
        decision = "passe"
        if r.returncode == 2:
            decision = "bloque"
        elif r.stdout.strip():
            decision = json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"]
        return decision, r

    def verifier(self, attendu, commande, **kw):
        decision, r = self.lancer(commande, **kw)
        self.assertEqual(decision, attendu, f"{commande!r} : {r.stdout} {r.stderr}")

    # Passe sans demander
    def test_dossier_suivi_propre(self):
        self.verifier("passe", "rm -rf src/sous")

    def test_variantes_d_options(self):
        for c in ["rm -fr src/sous", "rm -r -f src/sous", "rm -Rf src/a.txt", "rm --recursive --force src"]:
            self.verifier("passe", c)

    def test_cd_puis_suppression(self):
        self.verifier("passe", f"cd {self.depot} && rm -rf src/sous", cwd=self.base)

    def test_chemin_absolu_et_motif(self):
        self.verifier("passe", f"rm -rf {self.depot}/src/sous")
        self.verifier("passe", "rm -rf src/sous/*")

    def test_cible_inexistante_dans_le_depot(self):
        self.verifier("passe", "rm -rf build")

    def test_scratchpad_de_la_session(self):
        self.verifier("passe", f"rm -rf {self.scratch}/essai")

    def test_sans_force_non_concerne(self):
        self.verifier("passe", f"rm -r {self.maison}/x")

    # Demande
    def test_fichier_non_suivi(self):
        (self.depot / "src/sous/nouveau.txt").write_text("n")
        self.verifier("ask", "rm -rf src/sous")

    def test_fichier_modifie(self):
        (self.depot / "src/a.txt").write_text("modifié")
        self.verifier("ask", "rm -rf src")

    def test_dossier_ignore(self):
        (self.depot / "node_modules/x").mkdir(parents=True)
        (self.depot / "node_modules/x/index.js").write_text("x")  # un dossier vide n'est pas listé par git
        self.verifier("ask", "rm -rf node_modules")

    def test_racine_et_git(self):
        for c in ["rm -rf .", f"rm -rf {self.depot}", "rm -rf .git", "rm -rf src/../.."]:
            self.verifier("ask", c)

    def test_hors_du_depot(self):
        for c in [f"rm -rf {self.maison}/.claude", "rm -rf ~/.claude/skills", "rm -rf /tmp/x"]:
            self.verifier("ask", c)

    def test_scratchpad_d_une_autre_session(self):
        self.verifier("ask", f"rm -rf {self.scratch}/essai", session="autre-session")

    def test_cible_non_calculable(self):
        for c in ['rm -rf "$X"', "rm -rf $(cat liste)", "rm -rf src/{a,b}"]:
            self.verifier("ask", c)

    def test_dans_du_code(self):
        for c in ["python3 -c \"import os; os.system('rm -rf src')\"", "find . -name x -exec rm -rf {} +"]:
            self.verifier("ask", c)

    def test_une_cible_hors_suffit(self):
        self.verifier("ask", f"rm -rf src/sous {self.maison}/.claude")

    # Le reste du hook est inchangé
    def test_regle_deny_toujours_bloquante(self):
        self.verifier("bloque", "sshpass -p x ssh h")

    def test_commande_ordinaire(self):
        self.verifier("passe", "ls -la && git status")


if __name__ == "__main__":
    unittest.main()
