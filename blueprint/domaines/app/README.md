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
| `modeles-config/` | `eslint.config.js` qui impose les imports `@/` | à copier dans le projet |
| `docs/` | workflow et stratégie de test | non installé (documentation) |

## Prérequis et limites connues

- Le workflow suppose : **pnpm**, une branche d'intégration **`dev`**, un board **Notion**
  (accès par son MCP) et la commande **`gh`** pour les pull requests. Sur une autre stack,
  adapter les skills avant de les installer. `gh` n'est pas installé sur ce poste.
- `merge-pr` et `start-ticket` contiennent `<TON_DATA_SOURCE_ID>` : à remplacer par l'identifiant de
  la base Notion du projet.
- `merge-pr` s'appuie sur la règle `blueprint/commun/rules/git.md` (pas de merge sans accord, PR par PR) :
  installer le commun avant ce domaine.
- `workflow-ticket-backend.md` cite un hook Stop qui lance le lint ; ce hook n'est pas fourni.

## À trancher

- Rendre pnpm, `dev` et Notion paramétrables, pour que le workflow serve hors de sa stack d'origine.
