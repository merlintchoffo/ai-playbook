#!/usr/bin/env bash
# Tests du hook git commit-msg. Lancer : bash blueprint/commun/git-hooks/tests/test-commit-msg.sh
# Code de sortie : 0 si tous les tests passent, 1 sinon.
set -u
HOOK="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/commit-msg"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
reussis=0; echoues=0

verifier() { # <attendu 0|1> <libellé> <message>
  printf '%s\n' "$3" > "$TMP/msg"
  bash "$HOOK" "$TMP/msg" >/dev/null 2>&1
  local obtenu=$?; [ "$obtenu" -ne 0 ] && obtenu=1
  if [ "$obtenu" = "$1" ]; then reussis=$((reussis+1)); else echoues=$((echoues+1)); echo "ÉCHEC : $2 (attendu $1, obtenu $obtenu)"; fi
}

verifier 0 "message ordinaire" "feat: ajoute X"
verifier 0 "co-auteur humain" $'feat: X\n\nCo-authored-by: Alice <alice@example.org>'
verifier 0 "le mot Claude dans le sujet" "docs: explique la config de Claude Code"
verifier 0 "ligne commentée par git" $'feat: X\n# Co-Authored-By: Claude <noreply@anthropic.com>'
verifier 1 "co-auteur Claude" $'feat: X\n\nCo-Authored-By: Claude <noreply@anthropic.com>'
verifier 1 "co-auteur Claude, casse et modèle" $'feat: X\n\nco-authored-by: Claude Opus 5.5 <noreply@anthropic.com>'
verifier 1 "adresse anthropic seule" $'feat: X\n\nCo-authored-by: Bot <noreply@anthropic.com>'
verifier 1 "mention Generated with" $'feat: X\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)'

# Installé dans un vrai dépôt : git refuse le commit.
# Comme l'installation documentée : <projet>/.githooks/commit-msg et core.hooksPath .githooks.
git init -q "$TMP/depot" && mkdir "$TMP/depot/.githooks" && cp "$HOOK" "$TMP/depot/.githooks/commit-msg" && chmod +x "$TMP/depot/.githooks/commit-msg"
git -C "$TMP/depot" config core.hooksPath .githooks && git -C "$TMP/depot" config user.name T && git -C "$TMP/depot" config user.email t@example.org
if git -C "$TMP/depot" commit -q --allow-empty -m $'feat: X\n\nCo-Authored-By: Claude <noreply@anthropic.com>' 2>/dev/null; then
  echoues=$((echoues+1)); echo "ÉCHEC : git a accepté le commit"; else reussis=$((reussis+1)); fi
if git -C "$TMP/depot" commit -q --allow-empty -m "feat: ok" 2>/dev/null; then reussis=$((reussis+1)); else
  echoues=$((echoues+1)); echo "ÉCHEC : git a refusé un commit ordinaire"; fi

echo "$reussis réussis, $echoues échoués"
[ "$echoues" -eq 0 ]
