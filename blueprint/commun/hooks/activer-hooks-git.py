#!/usr/bin/env python3
"""Hook PreToolUse (Bash) : avant un `git commit`, active les hooks git versionnés du dépôt (.githooks/).

Applique la règle « Identité de l'auteur » de git.md, sans dépendre du modèle :
Sécurité : activer .githooks/ fait exécuter, à chaque commit, du code écrit par l'auteur du dépôt. Le hook
ne règle rien et ne rend rien exécutable sans demander, sauf si .githooks/ contient seulement commit-msg et
que ce fichier est identique (SHA-256) au commit-msg de référence d'ai-playbook.
- pas de dossier .githooks/ dans le dépôt : rien ;
- core.hooksPath vaut .githooks : rend .githooks/commit-msg exécutable s'il ne l'est pas ;
- core.hooksPath absent (tous niveaux) : le règle à .githooks dans le dépôt, sauf si .git/hooks/ contient
  un hook actif (fichier exécutable sans suffixe .sample) : alors bloque et demande ;
- core.hooksPath à une autre valeur (dépôt ou global) : bloque et demande, sans rien écraser.
Le dépôt est celui du `cd <chemin>` ou du `git -C <chemin>` de la commande, sinon le dossier courant.
Code de sortie : 0 = commande laissée passer (réglage fait signalé sur stdout) ; 2 = bloquée (raison sur stderr).
"""
import hashlib
import json
import os
import re
import shlex
import stat
import subprocess
import sys


# SHA-256 de blueprint/commun/git-hooks/commit-msg (contrôlé par les tests : à mettre à jour avec lui).
EMPREINTE_REFERENCE = "018e1ce4dfd6ad08d0a306a449f188c5e945284d58184d53f8e2a0296c4d5b67"


def githooks_de_confiance(racine):
    """None si .githooks/ ne contient que notre commit-msg intact ; sinon la raison."""
    dossier = os.path.join(racine, ".githooks")
    autres = sorted(n for n in os.listdir(dossier) if n != "commit-msg")
    if autres:
        return f"fichiers inconnus dans .githooks/ : {', '.join(autres)}"
    try:
        with open(os.path.join(dossier, "commit-msg"), "rb") as f:
            empreinte = hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return ".githooks/commit-msg absent ou illisible"
    if empreinte != EMPREINTE_REFERENCE:
        return ".githooks/commit-msg diffère du fichier de référence d'ai-playbook"
    return None


def git(depot, *args):
    return subprocess.run(["git", "-C", depot, *args], capture_output=True, text=True)


def commits(commande, cwd):
    """Dossiers depuis lesquels la commande lance un `git commit`."""
    dossier, resultat = cwd, []
    for brut in re.split(r"\|\||&&|[;|\n]", commande):
        try:
            mots = shlex.split(brut)
        except ValueError:
            continue
        if len(mots) >= 2 and mots[0] == "cd":
            dossier = os.path.join(dossier, os.path.expanduser(mots[1]))
            continue
        if not mots or os.path.basename(mots[0]) != "git":
            continue
        ici, i = dossier, 1
        while i < len(mots) and mots[i].startswith("-"):
            if mots[i] == "-C" and i + 1 < len(mots):
                ici = os.path.join(ici, os.path.expanduser(mots[i + 1]))
                i += 2
            elif mots[i] in ("-c", "--git-dir", "--work-tree") and i + 1 < len(mots):
                i += 2
            else:
                i += 1
        if i < len(mots) and mots[i] == "commit":
            resultat.append(ici)
    return resultat


def hooks_actifs(depot):
    dossier = git(depot, "rev-parse", "--git-path", "hooks").stdout.strip()
    dossier = os.path.join(depot, dossier) if dossier and not os.path.isabs(dossier) else dossier
    try:
        noms = sorted(os.listdir(dossier))
    except OSError:
        return []
    return [n for n in noms if not n.endswith(".sample") and os.path.isfile(os.path.join(dossier, n))
            and os.access(os.path.join(dossier, n), os.X_OK)]


def verifier(depot):
    """Renvoie (message de réglage ou None, raison de blocage ou None)."""
    racine = git(depot, "rev-parse", "--show-toplevel").stdout.strip()
    if not racine or not os.path.isdir(os.path.join(racine, ".githooks")):
        return None, None
    valeur = git(racine, "config", "--show-origin", "--get", "core.hooksPath").stdout.strip()
    origine, _, chemin = valeur.partition("\t")
    confiance = githooks_de_confiance(racine)
    if chemin == ".githooks":
        hook = os.path.join(racine, ".githooks", "commit-msg")
        if confiance is None and not os.access(hook, os.X_OK):
            os.chmod(hook, os.stat(hook).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            return f"{hook} rendu exécutable.", None
        return None, None
    if chemin:
        return None, (f"core.hooksPath vaut déjà « {chemin} » ({origine}) ; le dépôt {racine} a des hooks dans "
                      ".githooks/. Ne pas l'écraser : demander à l'utilisateur.")
    if confiance:
        return None, (f"{confiance} (dépôt {racine}). L'activer ferait exécuter ce code à chaque commit : "
                      "demander à l'utilisateur.")
    actifs = hooks_actifs(racine)
    if actifs:
        return None, (f"le dépôt {racine} a des hooks actifs dans .git/hooks/ ({', '.join(actifs)}) que régler "
                      "core.hooksPath .githooks désactiverait. Demander à l'utilisateur.")
    git(racine, "config", "--local", "core.hooksPath", ".githooks")
    return f"core.hooksPath réglé à .githooks dans {racine} (dépôt seulement).", None


def principal():
    try:
        entree = json.load(sys.stdin)
    except ValueError:
        return 0
    if entree.get("tool_name") != "Bash":
        return 0
    commande = (entree.get("tool_input") or {}).get("command") or ""
    messages = []
    for depot in commits(commande, entree.get("cwd") or os.getcwd()):
        message, blocage = verifier(depot)
        if blocage:
            print(f"Commit bloqué par le hook activer-hooks-git : {blocage}", file=sys.stderr)
            return 2
        if message:
            messages.append(message)
    if messages:
        print(json.dumps({"systemMessage": "activer-hooks-git : " + " ".join(messages)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(principal())
