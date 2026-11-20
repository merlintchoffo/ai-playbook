# blueprint/commun/outils

## sauvegarde-claude.sh

Sauvegarde, liste et restaure la configuration de Claude Code (`~/.claude`) avant une modification
risquée : changement de règles, de hooks ou de permissions, installation de skills.

```bash
bash blueprint/commun/outils/sauvegarde-claude.sh sauvegarder [libellé]   # archive datée dans ~/.claude/backups/
bash blueprint/commun/outils/sauvegarde-claude.sh lister                  # archives, la plus récente d'abord
bash blueprint/commun/outils/sauvegarde-claude.sh restaurer <archive>     # nom affiché par « lister », ou chemin complet
```

Exemple :

```
$ bash blueprint/commun/outils/sauvegarde-claude.sh sauvegarder avant-hook
Sauvegarde créée : /home/moi/.claude/backups/config-20261120-153000-avant-hook.tar.gz
Contenu : settings.json settings.local.json statusline-command.sh rules hooks skills
```

**Ce qui est sauvegardé** : `settings.json`, `settings.local.json`, `keybindings.json`,
`CLAUDE.md`, `statusline-command.sh` et les dossiers `rules/`, `hooks/`, `skills/`, `agents/`,
`commands/`, quand ils existent.

**Jamais sauvegardé** : `.credentials.json` (votre jeton), `skills/synced/` (géré par claude.ai),
l'historique, les projets, les caches. L'archive n'est lisible que par vous (droits 600).

**Restaurer** :

1. vérifie l'archive et refuse, sans rien modifier, une archive illisible, contenant un chemin
   absolu, un `..`, un lien ou un élément hors de la liste ci-dessus ;
2. sauvegarde l'état actuel (`…-avant-restauration.tar.gz`) : on peut toujours revenir en arrière ;
3. remplace chaque élément présent dans l'archive : un fichier ajouté depuis dans `rules/` est
   donc retiré. Les éléments absents de l'archive, le jeton et `skills/synced/` ne sont pas touchés.

Redémarrer Claude Code après une restauration.

Codes de sortie : 0 succès, 1 erreur, 2 mauvaise utilisation. Variables : `CLAUDE_DIR` (défaut
`~/.claude`), `SAUVEGARDE_DIR` (défaut `$CLAUDE_DIR/backups`).

**Tests** : `bash blueprint/commun/outils/tests/test-sauvegarde-claude.sh` (38 tests sur un `~/.claude` factice,
dans un dossier temporaire supprimé à la fin).
