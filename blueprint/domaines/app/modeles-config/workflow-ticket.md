# Paramètres du workflow ticket

À copier dans `<projet>/.claude/workflow-ticket.md` et à adapter. Les skills et agents du domaine `app`
le lisent avant d'agir ; une clé absente prend la valeur par défaut indiquée, et l'agent le signale une
fois. Les valeurs par défaut sont celles de la stack d'origine (pnpm, `dev`, Notion, `gh`).

## Branches

- branche_integration : `dev` — base des branches de ticket et cible des PR. Si elle n'existe pas
  (ni locale ni `origin/`), `main`.

## Commandes

- lint : `pnpm lint`
- typecheck : `pnpm typecheck`
- test : `pnpm test`
- test_unitaire : `pnpm vitest run`
- serveur : `pnpm dev`

Une commande absente du projet (pas de script) : l'étape est sautée et signalée, jamais inventée.

## Forge

- forge : `gh` — ou `aucune` : l'agent pousse la branche et donne le lien de création de PR à ouvrir
  dans le navigateur ; le merge est fait par l'utilisateur, puis `merge-pr` ne fait que la mise à jour
  du ticket.

## Tickets

- outil : `notion` — ou `aucun` : les étapes qui lisent ou changent un ticket sont sautées et
  signalées.
- data_source_id : `<TON_DATA_SOURCE_ID>`
- propriete_identifiant : `Ticket ID`
- motif_identifiant : `ID-\d+` (extrait du nom de branche par `merge-pr`)
- propriete_statut : `Agile Statut`
- statut_en_cours : `DOING`
- statut_a_tester : `TO TEST`
