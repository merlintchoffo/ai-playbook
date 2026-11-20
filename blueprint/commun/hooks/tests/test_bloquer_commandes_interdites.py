#!/usr/bin/env python3
"""Tests du hook bloquer-commandes-interdites. Lancer : python3 -I blueprint/commun/hooks/tests/test_bloquer_commandes_interdites.py"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "bloquer-commandes-interdites.py"
spec = importlib.util.spec_from_file_location("hook", HOOK)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)

MOTIFS = ["sshpass *", "rm -rf *"]


def bloque(commande):
    return hook.raison_blocage(commande, MOTIFS) is not None


class Bloque(unittest.TestCase):
    """Ce qui exécute un programme interdit reste bloqué."""

    def test_direct(self):
        self.assertTrue(bloque("sshpass -p x ssh h"))

    def test_enveloppes(self):
        for c in ["sudo sshpass -p x", "env A=1 sshpass x", "/usr/bin/sshpass x", "ls && sshpass x",
                  'bash -c "sshpass x"', "echo $(sshpass x)", "timeout 5 sshpass x"]:
            self.assertTrue(bloque(c), c)

    def test_interpretes(self):
        for c in ["python3 -c \"import os; os.system('sshpass x')\"", "node -e \"exec('sshpass x')\"",
                  "perl -e 'system(\"sshpass x\")'"]:
            self.assertTrue(bloque(c), c)

    def test_heredoc_vers_interpreteur(self):
        self.assertTrue(bloque("python3 - <<'EOF'\nimport os\nos.system('sshpass x')\nEOF"))
        self.assertTrue(bloque("bash <<EOF\nsshpass x\nEOF"))

    def test_heredoc_vers_script(self):
        self.assertTrue(bloque("cat > a.sh <<'EOF'\nsshpass x\nEOF\nbash a.sh"))

    def test_heredoc_vers_pipe_shell(self):
        self.assertTrue(bloque("cat <<EOF | bash\nsshpass x\nEOF"))

    def test_lanceurs(self):
        for c in ["find . -exec sshpass {} \\;", "ssh h 'sshpass x'", "awk 'BEGIN{system(\"sshpass\")}'"]:
            self.assertTrue(bloque(c), c)

    def test_rm_rf(self):
        self.assertTrue(bloque("rm -rf /tmp/x"))


class Laisse(unittest.TestCase):
    """Le mot interdit présent seulement comme donnée ne bloque plus (F6)."""

    def test_heredoc_donnees(self):
        self.assertFalse(bloque("cat > notes.md <<'EOF'\nla règle sshpass bloque\nEOF"))
        self.assertFalse(bloque("printf '%s' x | tee r.md <<EOF\nsshpass *\nEOF"))

    def test_arguments_donnees(self):
        for c in ['echo "sshpass est interdit"', "grep -n sshpass settings.json",
                  "git commit -m 'hook: faux positif sshpass'"]:
            self.assertFalse(bloque(c), c)

    def test_donnees_diverses(self):
        self.assertFalse(bloque("sed -i 's/sshpass/x/' f.md"))
        self.assertFalse(bloque("cat > n.txt <<EOF\nsshpass\nEOF"))

    def test_regle_entiere_dans_le_code(self):
        """Dans du code exécuté, c'est la règle entière qui compte, pas seulement le nom du programme."""
        self.assertFalse(bloque("find . -name '*.tmp' -exec rm {} \\;"))
        self.assertFalse(bloque("python3 -c \"import subprocess; subprocess.run(['rm', 'a.txt'])\""))
        self.assertTrue(bloque("find . -name x -exec rm -rf {} +"))
        self.assertTrue(bloque("python3 -c \"import os; os.system('rm -rf /tmp/x')\""))
        self.assertTrue(bloque("ssh h 'rm  -rf /srv'"))

    def test_commande_ordinaire(self):
        self.assertFalse(bloque("ls -la && git status"))


class Bout_en_bout(unittest.TestCase):
    """Le script lit les règles deny et renvoie 2 ou 0."""

    def lancer(self, commande):
        with tempfile.TemporaryDirectory() as maison, tempfile.TemporaryDirectory() as projet:
            os.makedirs(os.path.join(maison, ".claude"))
            with open(os.path.join(maison, ".claude", "settings.json"), "w") as f:
                json.dump({"permissions": {"deny": ["Bash(sshpass *)"]}}, f)
            entree = json.dumps({"tool_name": "Bash", "tool_input": {"command": commande}, "cwd": projet})
            return subprocess.run([sys.executable, "-I", str(HOOK)], input=entree, text=True,
                                  capture_output=True, env={"HOME": maison, "PATH": os.environ["PATH"]}).returncode

    def test_bloque(self):
        self.assertEqual(self.lancer("sshpass -p x ssh h"), 2)

    def test_laisse(self):
        self.assertEqual(self.lancer("cat > n.md <<'EOF'\nsshpass\nEOF"), 0)


if __name__ == "__main__":
    unittest.main()
