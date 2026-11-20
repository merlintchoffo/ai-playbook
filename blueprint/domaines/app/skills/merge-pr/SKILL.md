---
name: merge-pr
description: Merge la PR de la branche courante, puis passe le ticket de l'état en cours à l'état à tester. Fait ces deux choses, et rien d'autre. Utiliser quand l'utilisateur dit "merge la PR", "merge-pr", "merge cette PR", "on merge", après que la PR a été ouverte et relue.
disable-model-invocation: true
---

## Entrée

- La **PR de la branche courante** (celle ouverte par `open-pr` vers `{branche_integration}`), que l'utilisateur veut merger maintenant.
- Le **ticket associé**, déduit du nom de branche (`{motif_identifiant}`), à passer en `{statut_a_tester}`.

## Sortie

- La **confirmation du merge**, sous forme de l'**URL de la PR** — qui mène vers l'écran de confirmation du merge.
- La **confirmation que le ticket est passé en `{statut_a_tester}`** (sauf `outil` = `aucun`).

---

## Paramètres du projet

Lire `.claude/workflow-ticket.md` à la racine du projet (modèle : `modeles-config/workflow-ticket.md` du
domaine `app`). Clés utilisées ici : `branche_integration`, `forge`, `outil`, `data_source_id`, `propriete_identifiant`, `motif_identifiant`, `propriete_statut`, `statut_a_tester`. Fichier ou clé absent : valeur par défaut du
modèle, signalée une fois. Dans la suite, `{clé}` désigne la valeur lue.

## Base de tickets

- `outil` = `notion` : base `{data_source_id}`, propriété identifiant `{propriete_identifiant}` (texte, ex. `ID-1931`), propriété statut `{propriete_statut}` → option cible `{statut_a_tester}`.
- `outil` = `aucun` : l'étape 2 est sautée et signalée.

## ⛔️ Garde-fou merge (NON négociable)

La rule `rules/git.md` interdit tout merge sans accord explicite **pour cette PR précise**.

- **L'invocation de ce skill PAR L'UTILISATEUR vaut accord ponctuel pour CE merge-là, et lui seul.**
- Ne jamais déclencher ce skill de toi-même, ni l'enchaîner sur plusieurs PR. Un seul `merge-pr` = une seule PR mergée.
- Au moindre doute sur le fait que l'utilisateur veut merger maintenant → demander avant, ne pas merger.

## Étapes

1. **Merger la PR courante.** Avec `forge` = `aucune` : demander à l'utilisateur de merger dans le navigateur, attendre sa confirmation, puis vérifier avec `git fetch` que la branche est bien dans `origin/{branche_integration}` ; sinon stop. Avec `forge` = `gh` : `gh pr view --json number,url,state` pour la récupérer. Si aucune PR n'est ouverte pour la branche → stop, le dire. Sinon `gh pr merge --merge --delete-branch`. Si la PR n'est pas mergeable (conflits, checks rouges) → **stop**, expliquer pourquoi, ne pas forcer.
2. **Passer le ticket en `{statut_a_tester}`.**
   - Identifier le ticket depuis le nom de branche : extraire le token `{motif_identifiant}` (ex. `ID-1931-poc-backend` → `ID-1931`), chercher dans le Backlog Général le ticket dont `{propriete_identifiant}` (texte) vaut ce token exact. Charger l'outil Notion via ToolSearch si besoin (`notion-update-page`).
   - Mettre à jour `{propriete_statut}` → option `{statut_a_tester}`.
   - Si le ticket est introuvable ou ambigu → le dire, **sans bloquer** (le merge a réussi) ; ne jamais deviner au hasard.

## Restitution

Une ligne, dans l'ordre des étapes réussies. Ex :
```
✅ PR #42 mergée (branche supprimée) → ticket ID-1931 en TO TEST
```
Si une étape est sautée (ticket introuvable…), le dire explicitement sur la même ligne.

## Anti-patterns

- ❌ Merger sans que l'utilisateur ait invoqué le skill pour CETTE PR.
- ❌ Enchaîner sur une 2e PR dans la foulée.
- ❌ Forcer un merge sur une PR avec conflits ou checks rouges.
- ❌ Passer le ticket en `DONE` : rien n'est validé, il va en `{statut_a_tester}`.
- ❌ Bloquer toute la commande si le ticket est introuvable — le merge prime, signaler et finir.
