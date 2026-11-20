# Domaine app

Développement d'une application web (backend et frontend en TypeScript), ticket par ticket,
en test-first. À installer dans le `.claude/` d'un projet de ce type, jamais dans `~/.claude`.

## Le workflow d'un ticket

Détail et schéma : [docs/workflow-ticket-backend.md](docs/workflow-ticket-backend.md). Ce que l'on
teste et comment : [docs/testing-strategy.md](docs/testing-strategy.md).

| Étape | Point d'entrée | Produit |
|---|---|---|
| 0. Démarrer | skill `start-ticket` | ticket en DOING, branche dédiée, livrable rappelé |
| 1. Planifier les tests | agent `test-planner` | `testing/inventaire-<ID>.md` (règles classées 🟢 unitaire / 🟠 mixte / 🔴 manuel) |
| 2. Écrire les tests | skill `write-tests` → agents `unit-test-writer`, `smoke-test-writer` | tests unitaires rouges + `testing/smokes-<ID>.md` |
| 3. Écrire le code | skill `write-code` | code jusqu'au vert |
| 4. Relire | skill `review-code` → agent `code-reviewer` | revue classée ⛔ / ⚠️ / 💡, sans modification |
| 5. Livrer | skills `open-pr`, puis `merge-pr` après accord | PR vers `dev`, puis ticket en TO TEST |

Autres skills du domaine : `concevoir-interface` (UI), `audit-test` (élaguer les tests sans valeur),
`apex` (pour un changement **hors ticket**, ou dans un projet sans ce workflow ; pour un ticket, le workflow ci-dessus prime).

## Contenu

| Dossier | Contenu | Installation |
|---|---|---|
| `skills/` | les skills ci-dessus | `<projet>/.claude/skills/` |
| `agents/` | `test-planner`, `unit-test-writer`, `smoke-test-writer`, `code-reviewer` | `<projet>/.claude/agents/` |
| `modeles-rules/` | conventions d'un projet Express + React/shadcn : architecture, fichiers, imports, pnpm, tests AAA, périmètre d'écriture, commentaires, nommage, UI | `<projet>/.claude/rules/`, **après adaptation à la stack** du projet |
| `modeles-config/` | `workflow-ticket.md` (paramètres du workflow : branche, commandes, forge, tickets) ; `eslint.config.js` qui impose les imports `@/` | à copier dans `<projet>/.claude/` pour le premier, dans le projet pour le second |
| `docs/` | workflow et stratégie de test | non installé (documentation) |

## Prérequis et limites connues

- Les skills et `code-reviewer` lisent `<projet>/.claude/workflow-ticket.md` (modèle dans
  `modeles-config/`) : branche d'intégration, commandes lint / typecheck / test / serveur, forge
  (`gh` ou `aucune`), outil de tickets (`notion` ou `aucun`) et ses propriétés. Sans ce fichier,
  valeurs de la stack d'origine : pnpm, `dev`, Notion, `gh`. `gh` n'est pas installé sur ce poste :
  y mettre `forge : aucune`.
- Avec `outil : notion`, renseigner `data_source_id` (l'identifiant de la base Notion du projet).
- Les agents `test-planner`, `unit-test-writer`, `smoke-test-writer` lisent le ticket par le MCP
  Notion ; avec un autre outil, leur donner le texte du ticket dans le prompt.
- `merge-pr` s'appuie sur la règle `blueprint/commun/rules/git.md` (pas de merge sans accord, PR par PR) :
  installer le commun avant ce domaine.
- `workflow-ticket-backend.md` cite un hook Stop qui lance le lint ; ce hook n'est pas fourni.
