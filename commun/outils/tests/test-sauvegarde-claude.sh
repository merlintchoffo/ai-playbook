#!/usr/bin/env bash
# Tests de outils/sauvegarde-claude.sh, sur un ~/.claude factice dans un dossier temporaire.
# Usage : bash outils/tests/test-sauvegarde-claude.sh   (code 0 si tout passe)
set -uo pipefail

SCRIPT="$(cd "$(dirname "$0")/.." && pwd)/sauvegarde-claude.sh"
RACINE="$(mktemp -d)"
trap 'rm -rf "$RACINE"' EXIT
REUSSIS=0
ECHECS=0

ok() { REUSSIS=$((REUSSIS + 1)); echo "  ✓ $1"; }
ko() { ECHECS=$((ECHECS + 1)); echo "  ✗ $1"; }
verifier() { if eval "$2"; then ok "$1"; else ko "$1"; fi; }

nouveau_claude() {
	export CLAUDE_DIR="$RACINE/claude-$RANDOM$RANDOM"
	export SAUVEGARDE_DIR="$CLAUDE_DIR/backups"
	mkdir -p "$CLAUDE_DIR"/{rules,hooks,skills/a,skills/synced/s,projects/p}
	echo '{"v":1}' >"$CLAUDE_DIR/settings.json"
	echo '{"local":1}' >"$CLAUDE_DIR/settings.local.json"
	echo 'regle v1' >"$CLAUDE_DIR/rules/methode.md"
	echo 'hook v1' >"$CLAUDE_DIR/hooks/h.py"
	echo 'skill v1' >"$CLAUDE_DIR/skills/a/SKILL.md"
	echo 'synced claude.ai' >"$CLAUDE_DIR/skills/synced/s/SKILL.md"
	echo '{"token":"SECRET"}' >"$CLAUDE_DIR/.credentials.json"
	echo 'historique' >"$CLAUDE_DIR/projects/p/x.jsonl"
}

lancer() { bash "$SCRIPT" "$@"; }
derniere() { find "$SAUVEGARDE_DIR" -name 'config-*.tar.gz' -printf '%f\n' | sort | tail -1; }

echo "Utilisation"
nouveau_claude
lancer >/dev/null 2>&1; verifier "sans argument : code 2" '[[ $? -eq 2 ]]'
lancer inconnu >/dev/null 2>&1; verifier "commande inconnue : code 2" '[[ $? -eq 2 ]]'
lancer restaurer >/dev/null 2>&1; verifier "restaurer sans archive : code 2" '[[ $? -eq 2 ]]'
verifier "l'aide cite les trois commandes" '[[ "$(lancer 2>&1)" == *sauvegarder*lister*restaurer* ]]'

echo "Sauvegarder"
nouveau_claude
sortie="$(lancer sauvegarder "Avant Essai !!")"; code=$?
verifier "code 0" '[[ $code -eq 0 ]]'
a="$(derniere)"
verifier "nom daté, libellé nettoyé" '[[ "$a" =~ ^config-[0-9]{8}-[0-9]{6}-avant-essai\.tar\.gz$ ]]'
contenu="$(tar -tzf "$SAUVEGARDE_DIR/$a")"
verifier "réglages, règles, hooks, skills inclus" '[[ "$contenu" == *settings.json* && "$contenu" == *rules/methode.md* && "$contenu" == *hooks/h.py* && "$contenu" == *skills/a/SKILL.md* ]]'
verifier "jeton (.credentials.json) jamais inclus" '[[ "$contenu" != *credentials* ]]'
verifier "skills/synced jamais inclus" '[[ "$contenu" != *synced* ]]'
verifier "projets et historique jamais inclus" '[[ "$contenu" != *projects* ]]'
verifier "archive lisible par son seul propriétaire (600)" '[[ "$(stat -c %a "$SAUVEGARDE_DIR/$a")" == 600 ]]'
verifier "la sortie donne le chemin de l'archive" '[[ "$sortie" == *"$SAUVEGARDE_DIR/$a"* ]]'
sleep 1
lancer sauvegarder >/dev/null
verifier "sans libellé : config-AAAAMMJJ-HHMMSS.tar.gz" '[[ "$(derniere)" =~ ^config-[0-9]{8}-[0-9]{6}\.tar\.gz$ ]]'

vide="$RACINE/vide"; mkdir -p "$vide"
CLAUDE_DIR="$vide" SAUVEGARDE_DIR="$vide/b" bash "$SCRIPT" sauvegarder >/dev/null 2>&1
verifier "rien à sauvegarder : code 1" '[[ $? -eq 1 ]]'

echo "Lister"
nouveau_claude
verifier "aucune sauvegarde : message, code 0" '[[ "$(lancer lister)" == *"Aucune sauvegarde"* ]]'
lancer sauvegarder un >/dev/null; sleep 1; lancer sauvegarder deux >/dev/null
echo autre >"$SAUVEGARDE_DIR/settings.json.copie-manuelle"
liste="$(lancer lister)"
verifier "deux archives listées" '[[ "$(grep -c "^config-" <<<"$liste")" -eq 2 ]]'
verifier "la plus récente d'abord" '[[ "$(head -1 <<<"$liste")" == *-deux.tar.gz* ]]'
verifier "les autres fichiers du dossier sont ignorés" '[[ "$liste" != *copie-manuelle* ]]'
verifier "le contenu de chaque archive est résumé" '[[ "$(head -1 <<<"$liste")" == *rules*settings.json* ]]'

echo "Restaurer"
nouveau_claude
lancer sauvegarder reference >/dev/null; ref="$(derniere)"
echo '{"v":2}' >"$CLAUDE_DIR/settings.json"
echo 'regle v2' >"$CLAUDE_DIR/rules/methode.md"
echo 'nouvelle' >"$CLAUDE_DIR/rules/ajoutee.md"
rm "$CLAUDE_DIR/hooks/h.py"
echo 'synced v2' >"$CLAUDE_DIR/skills/synced/s/SKILL.md"
sleep 1
sortie="$(lancer restaurer "$ref")"; code=$?
verifier "code 0" '[[ $code -eq 0 ]]'
verifier "fichier modifié : remis à l'identique" '[[ "$(cat "$CLAUDE_DIR/settings.json")" == "{\"v\":1}" ]]'
verifier "dossier : fichier modifié remis, fichier ajouté retiré" '[[ "$(cat "$CLAUDE_DIR/rules/methode.md")" == "regle v1" && ! -e "$CLAUDE_DIR/rules/ajoutee.md" ]]'
verifier "fichier supprimé : recréé" '[[ "$(cat "$CLAUDE_DIR/hooks/h.py")" == "hook v1" ]]'
verifier "skills/synced conservé tel quel (claude.ai)" '[[ "$(cat "$CLAUDE_DIR/skills/synced/s/SKILL.md")" == "synced v2" ]]'
verifier "jeton et projets non touchés" '[[ -f "$CLAUDE_DIR/.credentials.json" && -f "$CLAUDE_DIR/projects/p/x.jsonl" ]]'
avant="$(find "$SAUVEGARDE_DIR" -name '*avant-restauration*' | head -1)"
verifier "sauvegarde automatique de l'état précédent créée" '[[ -n "$avant" ]]'
verifier "elle contient bien l'état précédent (v2)" '[[ "$(tar -xzOf "$avant" settings.json)" == "{\"v\":2}" ]]'
lancer restaurer "$(basename "$avant")" >/dev/null
verifier "retour arrière possible avec cette sauvegarde automatique" '[[ "$(cat "$CLAUDE_DIR/settings.json")" == "{\"v\":2}" ]]'
verifier "(prérequis du test suivant) état courant différent de la référence" '[[ "$(cat "$CLAUDE_DIR/settings.json")" != "{\"v\":1}" ]]'
lancer restaurer "$SAUVEGARDE_DIR/$ref" >/dev/null; code=$?
verifier "accepte aussi un chemin complet" '[[ $code -eq 0 && "$(cat "$CLAUDE_DIR/settings.json")" == "{\"v\":1}" ]]'
nb="$(find "$SAUVEGARDE_DIR" -name '*avant-restauration*' | wc -l)"
verifier "trois restaurations rapprochées : trois sauvegardes automatiques distinctes" '[[ $nb -eq 3 ]]'

echo "Restaurer : archives refusées (rien n'est modifié)"
nouveau_claude
echo '{"v":"actuel"}' >"$CLAUDE_DIR/settings.json"
piege="$RACINE/piege"; mkdir -p "$piege/sub"
echo x >"$piege/evil"
tar -czf "$RACINE/absolu.tar.gz" -P "$piege/evil" 2>/dev/null
tar -czf "$RACINE/remonte.tar.gz" -C "$piege/sub" ../evil 2>/dev/null
tar -czf "$RACINE/inattendu.tar.gz" -C "$piege" evil
ln -s /etc/passwd "$piege/settings.json"; tar -czf "$RACINE/lien.tar.gz" -C "$piege" settings.json
echo "pas une archive" >"$RACINE/illisible.tar.gz"
for cas in absolu remonte inattendu lien illisible; do
	lancer restaurer "$RACINE/$cas.tar.gz" >/dev/null 2>&1; code=$?
	verifier "$cas : code 1, configuration intacte" '[[ $code -eq 1 && "$(cat "$CLAUDE_DIR/settings.json")" == "{\"v\":\"actuel\"}" ]]'
done
verifier "aucune sauvegarde automatique créée pour une archive refusée" '[[ -z "$(find "$SAUVEGARDE_DIR" -name "*avant-restauration*" 2>/dev/null)" ]]'
lancer restaurer config-inexistante.tar.gz >/dev/null 2>&1
verifier "archive introuvable : code 1" '[[ $? -eq 1 ]]'

echo
echo "$REUSSIS réussis, $ECHECS échoués"
(( ECHECS == 0 ))
