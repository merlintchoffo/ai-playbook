#!/usr/bin/env python3
"""Liste et restaure les sessions Claude Code mises à la corbeille (corbeille freedesktop, `gio trash`).

Usage : restore_sessions.py lister
        restore_sessions.py restaurer <nom dans la corbeille> [...]

La corbeille est ~/.local/share/Trash, celle de l'utilisateur même quand l'agent tourne dans un flatpak
(dont $XDG_DATA_HOME pointe ailleurs) ; $CORBEILLE_SESSIONS la remplace (tests). Seuls les .jsonl dont le chemin
d'origine est sous ~/.claude/projects/ sont pris en compte.

lister : une ligne par session, colonnes séparées par des tabulations :
  <supprimé il y a>\t<taille>\t<nb messages utilisateur>\t<nom dans la corbeille>\t<chemin d'origine>\t<aperçu>
restaurer : remet chaque fichier à son chemin d'origine (dossier recréé si besoin), sans jamais écraser
  un fichier existant.
Code de sortie : 0 ; 1 si une restauration a échoué ; 2 si usage incorrect. --help : cette aide.
"""
import calendar
import configparser
import json
import os
import re
import shutil
import sys
import time
from urllib.parse import unquote


def corbeille():
    return os.environ.get("CORBEILLE_SESSIONS") or os.path.expanduser("~/.local/share/Trash")


def racine_sessions():
    return os.path.join(os.path.expanduser("~/.claude/projects"), "")


def lire_info(fichier):
    p = configparser.ConfigParser(interpolation=None)
    try:
        p.read(fichier, encoding="utf-8")
        section = p["Trash Info"]
        return unquote(section.get("Path", "")), section.get("DeletionDate", "")
    except (configparser.Error, KeyError, UnicodeDecodeError):
        return "", ""


def entrees():
    dossier_info = os.path.join(corbeille(), "info")
    try:
        noms = sorted(os.listdir(dossier_info))
    except OSError:
        return []
    resultat = []
    for nom_info in noms:
        if not nom_info.endswith(".trashinfo"):
            continue
        nom = nom_info[: -len(".trashinfo")]
        origine, date = lire_info(os.path.join(dossier_info, nom_info))
        fichier = os.path.join(corbeille(), "files", nom)
        if origine.endswith(".jsonl") and origine.startswith(racine_sessions()) and os.path.isfile(fichier):
            resultat.append((nom, origine, date, fichier))
    return resultat


def resume(fichier):
    apercu, nombre = None, 0
    with open(fichier, encoding="utf-8", errors="ignore") as f:
        for ligne in f:
            try:
                obj = json.loads(ligne)
            except ValueError:
                continue
            if not isinstance(obj, dict) or obj.get("type") != "user":
                continue
            contenu = (obj.get("message") or {}).get("content")
            if isinstance(contenu, list):
                contenu = " ".join(c.get("text", "") for c in contenu if isinstance(c, dict) and c.get("type") == "text")
            if isinstance(contenu, str) and contenu.strip():
                nombre += 1
                apercu = apercu or re.sub(r"\s+", " ", contenu.strip())[:80]
    return apercu or "(sans aperçu)", nombre


def depuis(date):
    try:
        epoch = time.mktime(time.strptime(date, "%Y-%m-%dT%H:%M:%S"))
    except ValueError:
        return "date inconnue"
    delta = time.time() - epoch
    for seuil, unite, div in ((60, None, 1), (3600, "min", 60), (86400, "h", 3600)):
        if delta < seuil:
            return "à l'instant" if unite is None else f"il y a {int(delta // div)} {unite}"
    return f"il y a {int(delta // 86400)} j"


def taille(octets):
    if octets < 1024:
        return f"{octets} o"
    return f"{octets / 1024:.0f} Ko" if octets < 1024 * 1024 else f"{octets / 1024 / 1024:.1f} Mo"


def lister():
    lignes = sorted(entrees(), key=lambda e: e[2], reverse=True)
    for nom, origine, date, fichier in lignes:
        apercu, nombre = resume(fichier)
        print("\t".join([depuis(date), taille(os.path.getsize(fichier)), str(nombre), nom, origine, apercu]))
    return 0


def restaurer(noms):
    connues = {e[0]: e for e in entrees()}
    echecs = 0
    for nom in noms:
        if nom not in connues:
            print(f"Introuvable dans la corbeille (ou pas une session) : {nom}", file=sys.stderr)
            echecs += 1
            continue
        _, origine, _, fichier = connues[nom]
        if os.path.exists(origine):
            print(f"Non restauré, un fichier existe déjà : {origine}", file=sys.stderr)
            echecs += 1
            continue
        os.makedirs(os.path.dirname(origine), exist_ok=True)
        shutil.move(fichier, origine)
        os.remove(os.path.join(corbeille(), "info", nom + ".trashinfo"))
        print(f"Restauré : {origine}")
    return 1 if echecs else 0


def principal(argv):
    if not argv or argv[0] in ("--help", "-h"):
        print(__doc__.strip())
        return 0 if argv else 2
    if argv[0] == "lister" and len(argv) == 1:
        return lister()
    if argv[0] == "restaurer" and len(argv) > 1:
        return restaurer(argv[1:])
    print("Usage incorrect (voir --help)", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(principal(sys.argv[1:]))
