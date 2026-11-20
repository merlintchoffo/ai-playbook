#!/usr/bin/env bash
#
# Rend un .pptx en images JPEG, pour inspection visuelle avant livraison.
#
#   scripts/render_preview.sh sortie/score_global.pptx [dossier_sortie]
#
# Remplace le convertisseur de l'environnement claude.ai, absent ailleurs.
# Prérequis : LibreOffice (soffice) et poppler-utils (pdftoppm).
#
#   Debian/Ubuntu  sudo apt-get install libreoffice-impress poppler-utils
#   macOS          brew install --cask libreoffice && brew install poppler
#
# L'inspection visuelle n'est pas optionnelle : la validation XML ne voit pas
# un texte qui déborde de sa carte ni un chiffre resté à l'ancienne valeur.

set -euo pipefail

if [[ $# -lt 1 ]]; then
  sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'
  exit 2
fi

PPTX="$1"
OUT="${2:-$(dirname "$PPTX")/preview}"

[[ -f "$PPTX" ]] || { echo "Fichier introuvable : $PPTX" >&2; exit 2; }

SOFFICE="$(command -v soffice || command -v libreoffice || true)"
if [[ -z "$SOFFICE" ]]; then
  echo "LibreOffice introuvable (soffice). Installation :" >&2
  echo "  Debian/Ubuntu : sudo apt-get install libreoffice-impress poppler-utils" >&2
  echo "  macOS         : brew install --cask libreoffice && brew install poppler" >&2
  exit 3
fi
command -v pdftoppm >/dev/null || {
  echo "pdftoppm introuvable (paquet poppler-utils)." >&2; exit 3; }

mkdir -p "$OUT"
BASE="$(basename "${PPTX%.*}")"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# LibreOffice refuse de tourner si un profil est déjà ouvert : on lui en donne
# un jetable, ce qui le rend utilisable en parallèle et dans un CI.
"$SOFFICE" --headless --norestore \
  -env:UserInstallation="file://$TMP/profile" \
  --convert-to pdf --outdir "$TMP" "$PPTX" >/dev/null 2>&1

PDF="$TMP/$BASE.pdf"
[[ -f "$PDF" ]] || { echo "Conversion PDF échouée pour $PPTX" >&2; exit 4; }

rm -f "$OUT/$BASE"-*.jpg
pdftoppm -jpeg -r "${DPI:-150}" "$PDF" "$OUT/$BASE"
cp "$PDF" "$OUT/$BASE.pdf"

echo "Aperçus écrits dans $OUT :"
ls -1 "$OUT/$BASE"-*.jpg
echo
echo "Ouvrir chaque image et vérifier : débordement de texte hors des cartes,"
echo "chevauchement pictogramme / texte, colonne droite tronquée, puce manquante,"
echo "valeur restée à l'ancienne version."
