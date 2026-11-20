#!/usr/bin/env python3
"""Tests de restore_sessions.py sur une corbeille factice au format freedesktop (gio trash passe par un
portail dans un flatpak et refuse /tmp ; l'essai réel est fait à part). Lancer : python3 -I -B tests/test_restore_sessions.py"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "restore_sessions.py"


class Cas(unittest.TestCase):
    def setUp(self):
        self.maison = tempfile.mkdtemp()
        self.corbeille = os.path.join(self.maison, "data/Trash")
        self.env = {"HOME": self.maison, "PATH": os.environ["PATH"], "CORBEILLE_SESSIONS": self.corbeille}
        self.dossier = os.path.join(self.maison, ".claude/projects/-p")
        os.makedirs(self.dossier)

    def tearDown(self):
        shutil.rmtree(self.maison)

    def session(self, nom, texte, dossier=None):
        f = os.path.join(dossier or self.dossier, nom)
        Path(f).write_text(json.dumps({"type": "user", "message": {"role": "user", "content": texte}}) + "\n")
        return f

    def jeter(self, f):
        """Comme gio trash : fichier dans files/, chemin d'origine encodé dans info/<nom>.trashinfo."""
        from urllib.parse import quote
        for d in ("files", "info"):
            os.makedirs(os.path.join(self.corbeille, d), exist_ok=True)
        nom = os.path.basename(f)
        shutil.move(f, os.path.join(self.corbeille, "files", nom))
        Path(self.corbeille, "info", nom + ".trashinfo").write_text(
            f"[Trash Info]\nPath={quote(f)}\nDeletionDate=2026-11-20T05:00:00\n")

    def lancer(self, *args):
        return subprocess.run([sys.executable, "-I", str(SCRIPT), *args], env=self.env, capture_output=True, text=True)

    def test_cycle_complet(self):
        f = self.session("a b.jsonl", "bonjour")
        self.jeter(f)
        shutil.rmtree(self.dossier)  # dossier du projet disparu : doit être recréé
        lignes = self.lancer("lister").stdout.strip().split("\n")
        self.assertEqual(len(lignes), 1)
        cols = lignes[0].split("\t")
        self.assertEqual((cols[2], cols[3], cols[4], cols[5]), ("1", "a b.jsonl", f, "bonjour"))
        r = self.lancer("restaurer", "a b.jsonl")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.isfile(f))
        self.assertEqual(self.lancer("lister").stdout, "")
        self.assertFalse(os.path.exists(os.path.join(self.corbeille, "info/a b.jsonl.trashinfo")))

    def test_ignore_ce_qui_nest_pas_une_session(self):
        autre = os.path.join(self.maison, "doc.jsonl")
        Path(autre).write_text("{}\n")
        self.jeter(autre)
        txt = os.path.join(self.dossier, "x.txt")
        Path(txt).write_text("x")
        self.jeter(txt)
        self.assertEqual(self.lancer("lister").stdout, "")
        self.assertEqual(self.lancer("restaurer", "doc.jsonl").returncode, 1)

    def test_n_ecrase_jamais(self):
        f = self.session("a.jsonl", "ancien")
        self.jeter(f)
        self.session("a.jsonl", "nouveau")
        r = self.lancer("restaurer", "a.jsonl")
        self.assertEqual(r.returncode, 1)
        self.assertIn("nouveau", Path(f).read_text())
        self.assertEqual(len(self.lancer("lister").stdout.strip().split("\n")), 1)

    def test_usage(self):
        self.assertEqual(self.lancer().returncode, 2)
        self.assertEqual(self.lancer("restaurer").returncode, 2)
        self.assertEqual(self.lancer("--help").returncode, 0)
        self.assertEqual(self.lancer("lister").returncode, 0)


if __name__ == "__main__":
    unittest.main()
