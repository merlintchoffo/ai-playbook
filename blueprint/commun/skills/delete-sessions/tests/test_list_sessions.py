#!/usr/bin/env python3
"""Tests de list_sessions.py et delete_sessions.sh. Lancer : python3 -I -B tests/test_list_sessions.py"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent / "scripts"
LISTE = ICI / "list_sessions.py"
SUPPR = ICI / "delete_sessions.sh"


def session(chemin, messages, horodatage="2026-01-01T10:00:00.000Z"):
    with open(chemin, "w", encoding="utf-8") as f:
        f.write("ligne non json\n")
        f.write(json.dumps({"type": "assistant", "message": {"role": "assistant", "content": "ignoré"}}) + "\n")
        for m in messages:
            f.write(json.dumps({"type": "user", "timestamp": horodatage, "message": {"role": "user", "content": m}}) + "\n")


class Cas(unittest.TestCase):
    def setUp(self):
        self.maison = tempfile.mkdtemp()
        self.env = {"HOME": self.maison, "PATH": os.environ["PATH"], "XDG_DATA_HOME": os.path.join(self.maison, "data")}
        self.projet = "/home/x/mon.projet_1"
        self.dossier = os.path.join(self.maison, ".claude/projects/-home-x-mon-projet-1")
        os.makedirs(self.dossier)
        # gio factice (le vrai passe par un portail flatpak qui refuse /tmp) : note ses arguments, déplace le fichier.
        self.bin = os.path.join(self.maison, "bin")
        os.makedirs(self.bin)
        Path(self.bin, "gio").write_text('#!/bin/sh\n[ "$1" = trash ] || exit 3\nmkdir -p "$HOME/corbeille"\nmv "$2" "$HOME/corbeille/"\n')
        os.chmod(os.path.join(self.bin, "gio"), 0o755)
        self.env["PATH"] = self.bin + os.pathsep + self.env["PATH"]

    def tearDown(self):
        shutil.rmtree(self.maison)

    def lancer(self, *args, entree=None, prog=None):
        cmd = ["bash", str(SUPPR)] if prog == "sh" else [sys.executable, "-I", str(LISTE)]
        return subprocess.run(cmd + list(args), env=self.env, capture_output=True, text=True, input=entree)

    def test_dossier_projet(self):
        r = self.lancer("--dossier-projet", self.projet)
        self.assertEqual(r.stdout.strip(), self.dossier)

    def test_liste_tri_apercu_compte(self):
        session(os.path.join(self.dossier, "a.jsonl"), ["ancien\tavec tab", "deux"], "2026-01-01T10:00:00Z")
        session(os.path.join(self.dossier, "b.jsonl"), [[{"type": "text", "text": "récent"}]], "2026-02-01T10:00:00Z")
        Path(self.dossier, "notes.txt").write_text("x")
        lignes = self.lancer(self.dossier).stdout.strip().split("\n")
        self.assertEqual(len(lignes), 2)
        cols = [l.split("\t") for l in lignes]
        self.assertTrue(all(len(c) == 6 for c in cols))
        self.assertTrue(cols[0][3].endswith("b.jsonl"))
        self.assertEqual(cols[1][2], "2")
        self.assertEqual(cols[1][4], "ancien avec tab")
        self.assertEqual(cols[0][5], "RECENTE")

    def test_ancienne_non_recente(self):
        f = os.path.join(self.dossier, "a.jsonl")
        session(f, ["x"])
        os.utime(f, (time.time() - 3600, time.time() - 3600))
        self.assertEqual(self.lancer(self.dossier).stdout.rstrip("\n").split("\t")[5], "")

    def test_erreurs(self):
        self.assertEqual(self.lancer("--truc").returncode, 2)
        self.assertEqual(self.lancer("/inexistant").returncode, 2)
        self.assertEqual(self.lancer("--help").returncode, 0)

    def test_script_interactif_met_a_la_corbeille(self):
        f = os.path.join(self.dossier, "a.jsonl")
        session(f, ["à jeter"])
        os.utime(f, (time.time() - 3600, time.time() - 3600))
        r = self.lancer(self.projet, entree="1\n", prog="sh")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(os.path.exists(f))
        self.assertTrue(os.path.exists(os.path.join(self.maison, "corbeille/a.jsonl")))

    def test_script_recente_demande_confirmation(self):
        f = os.path.join(self.dossier, "a.jsonl")
        session(f, ["récente"])
        r = self.lancer(self.projet, entree="1\n", prog="sh")  # pas de « o » : refus
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.exists(f))
        r = self.lancer(self.projet, entree="1\no\n", prog="sh")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(os.path.exists(f))

    def test_script_echec_gio(self):
        Path(self.bin, "gio").write_text("#!/bin/sh\nexit 1\n")
        f = os.path.join(self.dossier, "a.jsonl")
        session(f, ["x"])
        os.utime(f, (time.time() - 3600, time.time() - 3600))
        self.assertEqual(self.lancer(self.projet, entree="1\n", prog="sh").returncode, 1)

    def test_script_interactif_annule(self):
        f = os.path.join(self.dossier, "a.jsonl")
        session(f, ["garder"])
        r = self.lancer(self.projet, entree="\n", prog="sh")
        self.assertEqual(r.returncode, 0)
        self.assertTrue(os.path.exists(f))

    def test_script_option_inconnue(self):
        self.assertEqual(self.lancer("--truc", prog="sh").returncode, 2)


if __name__ == "__main__":
    unittest.main()
