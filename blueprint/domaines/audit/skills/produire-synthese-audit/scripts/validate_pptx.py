#!/usr/bin/env python3
"""Validation autonome d'un .pptx généré.

    python3 scripts/validate_pptx.py sortie/score_global.pptx [...]

Remplace le validateur de l'environnement claude.ai, absent ailleurs.
Dépendance : python-pptx  (pip install python-pptx)

Contrôle ce qui casse réellement un fichier ou une slide :
  - l'archive OOXML s'ouvre et contient les parties attendues
  - python-pptx relit la présentation sans erreur
  - aucune forme ne déborde du cadre de la slide
  - aucun texte vide ou laissé en placeholder
  - les couleurs sont bien des hexadécimaux à 6 chiffres sans dièse
"""

import re
import sys
import zipfile
from pathlib import Path

try:
    from pptx import Presentation
    from pptx.util import Emu
except ImportError:
    print("python-pptx manquant : pip install python-pptx")
    sys.exit(2)

PLACEHOLDERS = re.compile(
    r"(lorem ipsum|\bTODO\b|\bTBD\b|\[insérer|\[à compléter|\bxxx+\b|\bx%)",
    re.IGNORECASE,
)
HEX_OK = re.compile(r"^[0-9A-Fa-f]{6}$")


def valider(chemin):
    err, warn = [], []
    p = Path(chemin)

    if not p.exists():
        return [f"{p} : fichier introuvable."], []

    # --- L'archive OOXML --------------------------------------------------
    try:
        with zipfile.ZipFile(p) as z:
            mauvais = z.testzip()
            if mauvais:
                err.append(f"Archive corrompue à l'entrée {mauvais}.")
            noms = set(z.namelist())
            for requis in ("[Content_Types].xml", "ppt/presentation.xml"):
                if requis not in noms:
                    err.append(f"Partie OOXML manquante : {requis}")
    except zipfile.BadZipFile:
        return [f"{p} : ce n'est pas une archive OOXML valide."], []

    # --- La présentation --------------------------------------------------
    try:
        prs = Presentation(str(p))
    except Exception as exc:  # noqa: BLE001
        return [f"{p} : python-pptx ne peut pas relire le fichier ({exc})."], []

    largeur, hauteur = prs.slide_width, prs.slide_height
    if largeur is None or hauteur is None:
        err.append("Dimensions de slide absentes.")
        return err, warn

    marge = Emu(int(0.02 * 914400))  # 0,02 pouce de tolérance

    for i, slide in enumerate(prs.slides, start=1):
        formes = 0
        for forme in slide.shapes:
            formes += 1
            try:
                gauche, haut = forme.left, forme.top
                larg, haut_f = forme.width, forme.height
            except AttributeError:
                continue
            if None in (gauche, haut, larg, haut_f):
                continue

            if gauche < -marge or haut < -marge:
                err.append(
                    f"Slide {i} : forme « {forme.shape_type} » hors cadre "
                    f"(x={gauche / 914400:.2f}\", y={haut / 914400:.2f}\")."
                )
            if gauche + larg > largeur + marge:
                err.append(
                    f"Slide {i} : forme débordant à droite "
                    f"(bord à {(gauche + larg) / 914400:.2f}\" pour une slide "
                    f"de {largeur / 914400:.2f}\")."
                )
            if haut + haut_f > hauteur + marge:
                err.append(
                    f"Slide {i} : forme débordant en bas "
                    f"(bord à {(haut + haut_f) / 914400:.2f}\" pour une slide "
                    f"de {hauteur / 914400:.2f}\")."
                )

            if forme.has_text_frame:
                for para in forme.text_frame.paragraphs:
                    for run in para.runs:
                        trouve = PLACEHOLDERS.search(run.text or "")
                        if trouve:
                            warn.append(
                                f"Slide {i} : texte de remplissage probable "
                                f"« {trouve.group(0)} » dans « {run.text[:60]} »."
                            )
                        couleur = getattr(run.font.color, "rgb", None)
                        if couleur is not None and not HEX_OK.match(str(couleur)):
                            err.append(
                                f"Slide {i} : couleur mal formée « {couleur} » "
                                "(six chiffres hexadécimaux, sans dièse)."
                            )

        if formes == 0:
            warn.append(f"Slide {i} : aucune forme, slide vide.")

    if len(prs.slides) == 0:
        err.append("La présentation ne contient aucune slide.")

    return err, warn


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2

    total_err = 0
    for chemin in sys.argv[1:]:
        err, warn = valider(chemin)
        nom = Path(chemin).name
        for ligne in warn:
            print(f"  ATTENTION  [{nom}] {ligne}")
        for ligne in err:
            print(f"  ERREUR     [{nom}] {ligne}")
        if not err:
            print(f"  OK         [{nom}]")
        total_err += len(err)

    print()
    if total_err:
        print(f"{total_err} erreur(s) de validation.")
        return 1
    print("Validation réussie.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
