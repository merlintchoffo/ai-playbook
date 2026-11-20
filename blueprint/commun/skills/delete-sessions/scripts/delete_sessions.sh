#!/usr/bin/env bash
# Supprime des sessions Claude Code (.jsonl) sans passer par Claude Code.
# Les fichiers vont dans la corbeille (gio trash) : récupérables avec le skill recover-sessions.
# Usage :
#   delete_sessions.sh            -> sessions du projet courant (dossier courant)
#   delete_sessions.sh <dossier>  -> sessions d'un projet précis (chemin absolu du projet, pas le dossier ~/.claude/projects/...)
# Code de sortie : 0 ; 1 si une mise à la corbeille a échoué ; 2 si usage incorrect.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
case "${1:-}" in
  -h|--help) sed -n '2,8p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
  -*) echo "Option inconnue : $1 (voir --help)" >&2; exit 2 ;;
esac
command -v gio >/dev/null || { echo "gio est requis pour mettre à la corbeille." >&2; exit 2; }

DIRS=("$(python3 "$SCRIPT_DIR/list_sessions.py" --dossier-projet "${1:-$PWD}")")
[ -d "${DIRS[0]}" ] || { echo "Aucune session trouvée."; exit 0; }

MAPFILE_OUT=$(python3 "$SCRIPT_DIR/list_sessions.py" "${DIRS[@]}")

if [ -z "$MAPFILE_OUT" ]; then
  echo "Aucune session trouvée."
  exit 0
fi

declare -a REL_TIMES
declare -a SIZES
declare -a COUNTS
declare -a PATHS
declare -a PREVIEWS
declare -a ACTIVES

i=0
while IFS=$'\t' read -r rel size count path preview active; do
  REL_TIMES[$i]="$rel"
  SIZES[$i]="$size"
  COUNTS[$i]="$count"
  PATHS[$i]="$path"
  PREVIEWS[$i]="$preview"
  ACTIVES[$i]="$active"
  i=$((i+1))
done <<< "$MAPFILE_OUT"

echo "Sessions trouvées :"
echo
for idx in "${!PATHS[@]}"; do
  n=$((idx+1))
  marker=""
  [ "${ACTIVES[$idx]}" = "RECENTE" ] && marker=" 🟢 modifiée il y a moins de 2 min"
  fname=$(basename "${PATHS[$idx]}")
  printf "%2d) %-14s %-8s %-4s msg  %s%s\n" "$n" "${REL_TIMES[$idx]}" "${SIZES[$idx]}" "${COUNTS[$idx]}" "${PREVIEWS[$idx]:-(sans apercu)}" "$marker"
  printf "     %s\n" "$fname"
done

echo
read -rp "Numéros à supprimer (ex: 1 3 5), vide pour annuler : " -a CHOICES || CHOICES=()

if [ "${#CHOICES[@]}" -eq 0 ]; then
  echo "Annulé."
  exit 0
fi

TO_DELETE=()
for c in "${CHOICES[@]}"; do
  if ! [[ "$c" =~ ^[0-9]+$ ]] || [ "$c" -lt 1 ] || [ "$c" -gt "${#PATHS[@]}" ]; then
    echo "Numéro invalide ignoré : $c"
    continue
  fi
  idx=$((c-1))
  if [ "${ACTIVES[$idx]}" = "RECENTE" ]; then
    read -rp "⚠️  ${PATHS[$idx]} a été modifiée il y a moins de 2 min (session peut-être ouverte). Confirmer ? (o/N) " confirm || confirm=""
    [[ "$confirm" =~ ^[oOyY]$ ]] || { echo "Ignoré : ${PATHS[$idx]}"; continue; }
  fi
  TO_DELETE+=("${PATHS[$idx]}")
done

if [ "${#TO_DELETE[@]}" -eq 0 ]; then
  echo "Rien à supprimer."
  exit 0
fi

ECHECS=0
for f in "${TO_DELETE[@]}"; do
  if gio trash "$f"; then echo "Mis à la corbeille : $(basename "$f")"; else ECHECS=1; fi
done
exit "$ECHECS"
