#!/usr/bin/env python3
"""Contrôles arithmétiques sur les données d'audit, avant toute génération.

    python3 scripts/check_coherence.py audit.json

Sort 0 si tout est cohérent, 1 sinon. Aucune dépendance externe.

Ce script a rattrapé deux erreurs réelles en production : un compteur resté à
l'ancienne valeur après mise à jour, et une répartition incohérente avec le
nombre d'écarts. Il s'exécute AVANT la génération, pas après.
"""

import json
import sys
from pathlib import Path

TOL = 0.06  # tolérance sur les taux, en points de pourcentage


def taux(conformes, points_sensibles, applicables):
    if not applicables:
        return 0.0
    return (conformes + 0.5 * points_sensibles) / applicables * 100


def controler(data):
    err, warn, info = [], [], []

    cats = data.get("categories", [])
    if not cats:
        err.append("Aucune catégorie dans le fichier.")
        return err, warn, info

    # --- Totaux reconstruits depuis les catégories -----------------------
    somme = {k: sum(c.get(k, 0) for c in cats)
             for k in ("total", "conformes", "non_conformes",
                       "points_sensibles", "non_applicables", "a_verifier")}

    for c in cats:
        detail = (c.get("conformes", 0) + c.get("non_conformes", 0)
                  + c.get("points_sensibles", 0) + c.get("non_applicables", 0)
                  + c.get("a_verifier", 0))
        if detail != c.get("total", 0):
            err.append(
                f"Catégorie « {c['nom']} » : {detail} règles réparties "
                f"pour un total déclaré de {c.get('total', 0)}."
            )

    # --- Totaux déclarés, s'ils existent ---------------------------------
    declare = data.get("totaux")
    if declare:
        for k, v in somme.items():
            if k in declare and declare[k] != v:
                err.append(
                    f"Total « {k} » déclaré à {declare[k]}, "
                    f"mais la somme des catégories donne {v}."
                )

    applicables = somme["total"] - somme["non_applicables"]
    t_global = taux(somme["conformes"], somme["points_sensibles"], applicables)
    info.append(
        f"Taux global calculé : {t_global:.1f} % "
        f"({somme['conformes']} conformes, {somme['points_sensibles']} points "
        f"sensibles, sur {applicables} règles applicables / {somme['total']} évaluées)"
    )

    if declare and "taux" in declare:
        if abs(declare["taux"] - t_global) > TOL:
            err.append(
                f"Taux global déclaré à {declare['taux']:.1f} % "
                f"mais recalculé à {t_global:.1f} %."
            )

    # --- Taux par catégorie ----------------------------------------------
    for c in cats:
        app = c.get("total", 0) - c.get("non_applicables", 0)
        t = taux(c.get("conformes", 0), c.get("points_sensibles", 0), app)
        if "taux" in c and abs(c["taux"] - t) > TOL:
            err.append(
                f"Catégorie « {c['nom']} » : taux déclaré {c['taux']:.1f} % "
                f"mais recalculé à {t:.1f} %."
            )
        if app == 0:
            warn.append(
                f"Catégorie « {c['nom']} » : aucune règle applicable, "
                "le taux n'a pas de sens."
            )

    # --- Répartitions par qualification ----------------------------------
    ecarts = somme["non_conformes"] + somme["points_sensibles"]
    info.append(f"Écarts à qualifier : {ecarts} "
                f"({somme['non_conformes']} NC + {somme['points_sensibles']} PS)")

    for nom, bloc in (data.get("qualification") or {}).items():
        total_bloc = sum(bloc.values())
        if total_bloc != ecarts:
            err.append(
                f"Répartition « {nom} » : somme {total_bloc}, "
                f"attendu {ecarts} (NC + PS)."
            )

    # --- Constats détaillés face aux compteurs ---------------------------
    for cle, attendu, libelle in (
        ("non_conformites", somme["non_conformes"], "non-conformités"),
        ("points_sensibles_detail", somme["points_sensibles"], "points sensibles"),
    ):
        detail = data.get(cle)
        if detail is not None and len(detail) != attendu:
            warn.append(
                f"{len(detail)} {libelle} détaillées pour {attendu} comptabilisées "
                "— la slide de constats sera décalée du tableau."
            )

    if somme["a_verifier"]:
        warn.append(
            f"{somme['a_verifier']} règle(s) encore « à vérifier » : "
            "elles comptent dans le total mais dans aucun statut."
        )

    return err, warn, info


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2

    chemin = Path(sys.argv[1])
    if not chemin.exists():
        print(f"Fichier introuvable : {chemin}")
        return 2

    data = json.loads(chemin.read_text(encoding="utf-8"))
    err, warn, info = controler(data)

    for ligne in info:
        print(f"  {ligne}")
    for ligne in warn:
        print(f"  ATTENTION  {ligne}")
    for ligne in err:
        print(f"  ERREUR     {ligne}")

    print()
    if err:
        print(f"{len(err)} incohérence(s) — à lever avec l'auditeur avant de générer.")
        return 1
    print("Cohérence vérifiée." + (f" {len(warn)} point(s) de vigilance." if warn else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
