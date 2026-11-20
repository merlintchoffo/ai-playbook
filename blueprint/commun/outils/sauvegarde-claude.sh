#!/usr/bin/env bash
# Sauvegarde, liste et restauration de la configuration de Claude Code (~/.claude).
#
# Usage :
#   sauvegarde-claude.sh sauvegarder [libellé]   crée une archive datée
#   sauvegarde-claude.sh lister                  liste les archives, la plus récente d'abord
#   sauvegarde-claude.sh restaurer <archive>     restaure (après une sauvegarde automatique)
#
# Sauvegardé : réglages, règles, hooks, skills, agents, commandes, statusline, CLAUDE.md.
# Jamais sauvegardé : .credentials.json (jeton), skills/synced (géré par claude.ai),
# historique, projets, caches.
#
# Variables : CLAUDE_DIR (défaut ~/.claude), SAUVEGARDE_DIR (défaut $CLAUDE_DIR/backups).
# Codes de sortie : 0 succès, 1 erreur, 2 mauvaise utilisation.
set -euo pipefail

CLAUDE_DIR="${CLAUDE_DIR:-$HOME/.claude}"
SAUVEGARDE_DIR="${SAUVEGARDE_DIR:-$CLAUDE_DIR/backups}"
ELEMENTS=(settings.json settings.local.json keybindings.json CLAUDE.md statusline-command.sh
	rules hooks skills agents commands)

erreur() { echo "Erreur : $*" >&2; exit 1; }

usage() {
	sed -n '4,7p' "$0" | sed 's/^# \{0,1\}//' >&2
	exit 2
}

sauvegarder() {
	local libelle="${1:-}" presents=() nom archive
	if [[ -n "$libelle" ]]; then
		libelle="$(printf '%s' "$libelle" | tr 'A-Z' 'a-z' | tr -c 'a-z0-9-' '-' | sed 's/-\{2,\}/-/g; s/^-//; s/-$//')"
	fi
	for e in "${ELEMENTS[@]}"; do [[ -e "$CLAUDE_DIR/$e" ]] && presents+=("$e"); done
	(( ${#presents[@]} )) || erreur "rien à sauvegarder dans $CLAUDE_DIR"

	mkdir -p "$SAUVEGARDE_DIR"
	nom="config-$(date +%Y%m%d-%H%M%S)${libelle:+-$libelle}"
	archive="$SAUVEGARDE_DIR/$nom.tar.gz"
	# Deux sauvegardes dans la même seconde : suffixe -2, -3… (jamais d'écrasement).
	local n=2
	while [[ -e "$archive" ]]; do archive="$SAUVEGARDE_DIR/$nom-$n.tar.gz"; n=$((n + 1)); done

	# umask : l'archive n'est lisible que par son propriétaire (elle contient des réglages).
	(umask 077 && tar -czf "$archive" -C "$CLAUDE_DIR" --exclude='skills/synced' "${presents[@]}")
	echo "Sauvegarde créée : $archive"
	echo "Contenu : ${presents[*]}"
}

lister() {
	local trouve=0
	[[ -d "$SAUVEGARDE_DIR" ]] || { echo "Aucune sauvegarde (dossier $SAUVEGARDE_DIR absent)."; return 0; }
	while IFS= read -r f; do
		trouve=1
		printf '%s  %6s  %s\n' "$(basename "$f")" "$(du -h "$f" | cut -f1)" \
			"$(tar -tzf "$f" | awk -F/ '{print $1}' | sort -u | tr '\n' ' ')"
	done < <(find "$SAUVEGARDE_DIR" -maxdepth 1 -name 'config-*.tar.gz' -printf '%f\n' | sort -r | sed "s#^#$SAUVEGARDE_DIR/#")
	(( trouve )) || echo "Aucune sauvegarde dans $SAUVEGARDE_DIR."
}

restaurer() {
	local cible="${1:-}" archive contenu racines
	[[ -n "$cible" ]] || usage
	if [[ -f "$cible" ]]; then archive="$cible"; else archive="$SAUVEGARDE_DIR/$cible"; fi
	[[ -f "$archive" ]] || erreur "archive introuvable : $cible"
	contenu="$(tar -tzf "$archive" 2>/dev/null)" || erreur "archive illisible : $archive"

	# Refuser toute archive qui écrirait hors de CLAUDE_DIR ou hors des éléments prévus.
	if grep -qE '(^/|(^|/)\.\.(/|$))' <<<"$contenu"; then erreur "archive refusée : chemin absolu ou « .. »"; fi
	racines="$(awk -F/ '{print $1}' <<<"$contenu" | sort -u)"
	while IFS= read -r r; do
		[[ " ${ELEMENTS[*]} " == *" $r "* ]] || erreur "archive refusée : élément inattendu « $r »"
	done <<<"$racines"
	if tar -tvzf "$archive" | grep -q '^[lh]'; then erreur "archive refusée : contient des liens"; fi

	echo "Sauvegarde de l'état actuel avant restauration :"
	sauvegarder "avant-restauration"

	while IFS= read -r r; do
		if [[ "$r" == skills ]]; then
			# skills/synced appartient à claude.ai : conservé tel quel.
			find "$CLAUDE_DIR/skills" -mindepth 1 -maxdepth 1 ! -name synced -exec rm -rf {} + 2>/dev/null || true
		else
			rm -rf "${CLAUDE_DIR:?}/$r"
		fi
	done <<<"$racines"
	tar -xzf "$archive" -C "$CLAUDE_DIR" --no-same-owner
	echo "Restauré depuis $(basename "$archive") : $(tr '\n' ' ' <<<"$racines")"
	echo "Les éléments absents de l'archive n'ont pas été touchés. Redémarrer Claude Code."
}

case "${1:-}" in
	sauvegarder) shift; sauvegarder "${1:-}" ;;
	lister) lister ;;
	restaurer) shift; restaurer "${1:-}" ;;
	*) usage ;;
esac
