---
name: synchroniser-skills
description: Installe le commun d'ai-playbook dans ~/.claude, et un domaine dans un projet, depuis la version commitée, après comparaison et accord. Utiliser quand l'utilisateur demande de synchroniser, installer ou mettre à jour ses skills, règles ou hooks.
disable-model-invocation: true
argument-hint: "[comparer | installer] [commun | <domaine> <projet>] [nom-du-skill…]"
---

## Entrée

- Le mode : `comparer` (par défaut) ou `installer`.
- La cible : le commun, ou un domaine et le chemin du projet.
- Optionnel : les noms des éléments à traiter.

## Sortie

- Un tableau `élément | état | détail` (identique, à installer, modifié dans la cible, bloqué).
- En mode `installer`, après accord : les éléments installés, identiques à la version commitée, et l'emplacement des sauvegardes.

---

# Synchroniser les skills

Le dépôt est la seule source. Le sens est toujours **dépôt → `~/.claude/skills`**, jamais l'inverse : une
modification faite directement dans `~/.claude/skills` est un écart à signaler, pas une source.

Variables : `DEPOT=$(git -C <dossier courant> rev-parse --show-toplevel)`,
`TMP=<répertoire temporaire de la session>`. Chaque commande commence par `cd "$DEPOT" &&`.

**Sources et destinations.** Le dépôt sépare ce qui vaut pour tout projet (`blueprint/commun/`) de ce qui
décrit un type de projet (`blueprint/domaines/<domaine>/`) :

| Source dans le dépôt | Destination | Quand |
|---|---|---|
| `blueprint/commun/skills/<nom>/` | `~/.claude/skills/<nom>/` | par défaut |
| `blueprint/commun/rules/*.md` | `~/.claude/rules/` | par défaut |
| `blueprint/commun/hooks/*` | `~/.claude/hooks/` | par défaut ; la clé `hooks` de `~/.claude/settings.json` demande un accord séparé |
| `blueprint/commun/settings/*.json` | clés fusionnées dans `~/.claude/settings.json` | accord séparé ; sauvegarde du fichier, seules les clés du fragment changent, le reste est vérifié inchangé |
| `blueprint/commun/git-hooks/commit-msg` | `<projet>/.githooks/commit-msg`, puis `git config core.hooksPath .githooks` | seulement si l'utilisateur nomme le projet ; le fichier se commite dans le projet, la config git se refait dans chaque clone |
| `blueprint/domaines/<domaine>/skills/<nom>/` | `<projet>/.claude/skills/<nom>/` | seulement si l'utilisateur nomme le domaine **et** le projet |
| `blueprint/domaines/<domaine>/agents/*.md` | `<projet>/.claude/agents/` | idem |
| `blueprint/domaines/<domaine>/modeles-rules/*.md` | `<projet>/.claude/rules/` | idem, fichier par fichier, après relecture : ce sont des modèles à adapter à la stack du projet |

Jamais installés : `blueprint/commun/historique/`, `blueprint/commun/outils/` (lancés depuis le dépôt), les `docs/`
d'un domaine. Dans la suite, `<source>` est le dossier source et `CIBLE` le dossier destination du
tableau ; un fichier de règle ou d'agent suit la même procédure qu'un dossier de skill.

## 1. Comparer (toujours, même pour `installer`)

1. `git status --short <source>` : tout élément qui a des modifications non commitées est **bloqué**. On
   n'installe que ce qui est commité. Le dire et proposer un commit, sans le faire.
2. Extraire la version commitée : `git archive HEAD <source>/<nom> | tar -x -C "$TMP"`. Les fichiers
   ignorés par git (`node_modules/`, `retours-prives.md`, sorties) ne peuvent pas en sortir.
3. **Contrôle avant diffusion**, sur `$TMP` : chercher les identifiants réels et les secrets
   (`grep -rnE "(password|secret|token|api[_-]?key)[\"']?\s*[:=]\s*[\"'][^\"']{8,}|BEGIN [A-Z ]*PRIVATE KEY|AKIA[0-9A-Z]{16}"`
   pour les valeurs, plus `grep -rni` des noms de client, de produit interne ou de machine connus de
   la mémoire du projet). Afficher le fichier et la ligne,
   jamais la valeur. Si un contrôle trouve quelque chose, le skill est bloqué.
4. `diff -rq "$TMP/<source>/<nom>" "$CIBLE/<nom>"` et classer chaque skill : `identique`, `à installer`
   (absent ou différent), `modifié dans la cible` (la cible a des fichiers que le dépôt n'a pas, ou est
   plus récente que le dernier commit), `bloqué`.
5. Signaler aussi, **sans y toucher** :
   - les skills de `$CIBLE` absents du dépôt, en particulier ceux qui portent un **ancien nom**
     (ex. `conception-interface`, renommé `concevoir-interface`) : proposer de les retirer, sans le faire ;
   - les liens symboliques ;
   - `$CIBLE/synced/`, géré par claude.ai. Si un skill du dépôt y existe aussi, montrer l'écart avec
     `diff -q`. Cette copie se corrige en renvoyant le skill sur claude.ai, pas en local.

Rendre le tableau `skill | état | détail`. Avec `comparer`, s'arrêter là.

## 2. Installer (seulement après accord explicite sur la liste)

Pour chaque skill accepté, de type `à installer`. Un skill `modifié dans la cible` demande un accord
séparé, car ses changements locaux seront perdus : proposer d'abord de les reporter dans le dépôt.

1. Sauvegarder la cible : `cp -a "$CIBLE/<nom>" ~/.claude/backups/skills-<nom>-<AAAA-MM-JJ-HHMM>`.
2. Copier dans un dossier voisin, puis remplacer : `cp -a "$TMP/<source>/<nom>" "$CIBLE/.<nom>.neuf"`,
   puis `mv "$CIBLE/<nom>" "$CIBLE/.<nom>.ancien"`, `mv "$CIBLE/.<nom>.neuf" "$CIBLE/<nom>"` et
   `rm -r "$CIBLE/.<nom>.ancien"`. Il n'y a jamais d'état à moitié copié.
3. Dépendances : si le skill a un `package.json`, ne pas lancer `npm install` sans accord, et
   signaler que ses scripts ne tournent pas tant que ce n'est pas fait.

## 3. Vérifier, puis rendre compte

- Refaire l'étape 1.4 : chaque skill installé doit être `identique`. Sinon, c'est un échec, pas un
  succès partiel.
- Vérifier que l'en-tête de chaque `SKILL.md` installé a un `name` égal au nom du dossier et une
  `description`. Signaler tout nom qui masque un skill intégré, comme `update-config`.
- Supprimer `$TMP/blueprint` et vérifier qu'il n'en reste rien.
- Rendre compte en un tableau : installés, identiques, bloqués (avec la raison), non touchés, et
  l'emplacement des sauvegardes. Proposer de supprimer les sauvegardes, sans le faire.

Ne jamais : écrire dans le dépôt, commiter, pousser, modifier `$CIBLE/synced/`, supprimer un skill de
`$CIBLE` absent du dépôt.
