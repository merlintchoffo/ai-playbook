# ai-playbook

Ne jamais modifier `~/.claude` à la main : modifier ce dépôt, commiter, puis installer avec
`/synchroniser-skills` (comparaison, puis accord). Une copie installée qui diffère du dépôt est un écart à signaler.

Modifier `blueprint/commun/git-hooks/commit-msg` oblige à mettre à jour `EMPREINTE_REFERENCE` dans
`blueprint/commun/hooks/activer-hooks-git.py`.

## Tests (depuis la racine du dépôt)

- `python3 -I -B blueprint/commun/hooks/tests/test_bloquer_commandes_interdites.py`
- `python3 -I -B blueprint/commun/hooks/tests/test_activer_hooks_git.py`
- `python3 -I -B blueprint/commun/hooks/tests/test_suppressions.py`
- `bash blueprint/commun/git-hooks/tests/test-commit-msg.sh`
- `bash blueprint/commun/outils/tests/test-sauvegarde-claude.sh`
- `python3 -I -B blueprint/commun/skills/delete-sessions/tests/test_list_sessions.py`
- `python3 -I -B blueprint/commun/skills/recover-sessions/tests/test_restore_sessions.py`
- `python3 -I -B blueprint/domaines/app/skills/apex/scripts/test_apex_state.py`
- `blueprint/domaines/audit/skills/produire-synthese-audit` : `npm ci`, puis `npm run build`, `npm run check`, `npm run validate`.
