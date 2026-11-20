#!/usr/bin/env python3
"""Liste les sessions Claude Code (.jsonl) d'un ou plusieurs dossiers, de la plus récente à la plus ancienne.

Usage : list_sessions.py [--limit N] <dossier> [<dossier> ...]
        list_sessions.py --dossier-projet <chemin absolu du projet>   (affiche le dossier de sessions)

Sortie, une ligne par fichier, colonnes séparées par des tabulations :
  <temps relatif>\t<taille>\t<nb messages utilisateur>\t<chemin du fichier>\t<aperçu>\t<RECENTE ou vide>
RECENTE : fichier modifié il y a moins de 2 minutes, donc peut-être une session ouverte ailleurs.
Code de sortie : 0 ; 2 si option inconnue ou dossier illisible. --help : cette aide.
"""
import calendar
import json
import os
import re
import sys
import time

RECENTE_S = 120


def dossier_projet(chemin):
    """Dossier de sessions de Claude Code : chemin absolu, tout caractère non alphanumérique remplacé par « - »."""
    return os.path.join(os.path.expanduser("~/.claude/projects"), re.sub(r"[^A-Za-z0-9]", "-", chemin))


def temps_relatif(epoch, maintenant):
    delta = maintenant - epoch
    if delta < 60:
        return "à l'instant"
    if delta < 3600:
        return f"il y a {int(delta // 60)} min"
    if delta < 86400:
        return f"il y a {int(delta // 3600)} h"
    return f"il y a {int(delta // 86400)} j"


def taille(octets):
    if octets < 1024:
        return f"{octets} o"
    if octets < 1024 * 1024:
        return f"{octets / 1024:.0f} Ko"
    return f"{octets / 1024 / 1024:.1f} Mo"


def texte_utilisateur(obj):
    if obj.get("type") != "user" or (obj.get("message") or {}).get("role") != "user":
        return ""
    contenu = obj["message"].get("content")
    if isinstance(contenu, str):
        return contenu.strip()
    if isinstance(contenu, list):
        return " ".join(c.get("text", "") for c in contenu if isinstance(c, dict) and c.get("type") == "text").strip()
    return ""


def epoch_iso(horodatage):
    try:
        return calendar.timegm(time.strptime(horodatage.split(".")[0].rstrip("Z"), "%Y-%m-%dT%H:%M:%S"))
    except (ValueError, AttributeError):
        return None


def lire_session(chemin):
    apercu, epoch, nombre = None, None, 0
    with open(chemin, encoding="utf-8", errors="ignore") as f:
        for ligne in f:
            try:
                obj = json.loads(ligne)
            except ValueError:
                continue
            texte = texte_utilisateur(obj) if isinstance(obj, dict) else ""
            if texte:
                nombre += 1
                if apercu is None:
                    apercu = re.sub(r"\s+", " ", texte)[:80]
                    epoch = epoch_iso(obj.get("timestamp"))
    return apercu, epoch, nombre


def principal(argv):
    if "--help" in argv or "-h" in argv:
        print(__doc__.strip())
        return 0
    limite, dossiers = None, []
    i = 0
    while i < len(argv):
        if argv[i] == "--limit":
            limite = int(argv[i + 1])
            i += 2
        elif argv[i] == "--dossier-projet":
            print(dossier_projet(argv[i + 1]))
            return 0
        elif argv[i].startswith("-"):
            print(f"Option inconnue : {argv[i]} (voir --help)", file=sys.stderr)
            return 2
        else:
            dossiers.append(argv[i])
            i += 1
    maintenant = time.time()
    resultats = []
    for dossier in dossiers or ["."]:
        try:
            noms = os.listdir(dossier)
        except OSError as e:
            print(f"Erreur : dossier illisible : {dossier} ({e.strerror})", file=sys.stderr)
            return 2
        for nom in noms:
            if not nom.endswith(".jsonl"):
                continue
            chemin = os.path.join(dossier, nom)
            apercu, epoch, nombre = lire_session(chemin)
            stat = os.stat(chemin)
            resultats.append((epoch or stat.st_mtime, chemin, apercu, stat.st_size, nombre,
                              maintenant - stat.st_mtime < RECENTE_S))
    resultats.sort(key=lambda r: r[0], reverse=True)
    for epoch, chemin, apercu, octets, nombre, recente in resultats[:limite]:
        print("\t".join([temps_relatif(epoch, maintenant), taille(octets), str(nombre), chemin,
                         apercu or "(sans aperçu)", "RECENTE" if recente else ""]))
    return 0


if __name__ == "__main__":
    sys.exit(principal(sys.argv[1:]))
