---
name: start-ticket
description: Start work on a ticket, set it in progress, branch off the integration branch, and surface the ticket's deliverable. Use when the user says "start ticket", "démarre le ticket", "je commence ID-XXXX", "on attaque le ticket", or wants to begin a piece of work tracked in the board.
disable-model-invocation: true
---

## Entrée

- L'**identifiant du ticket**, tel qu'il est écrit sur le board (ex. `ID-1931`, `PRJ-02`), ou son **lien Notion**.

## Sortie

- Le ticket passé en **`{statut_en_cours}`** sur le board (sauf `outil` = `aucun`).
- Une **branche dédiée** créée depuis la base à jour, et checkout dessus.
- Le **livrable du ticket** rappelé à l'écran.

---

## Paramètres du projet

Lire `.claude/workflow-ticket.md` à la racine du projet (modèle : `modeles-config/workflow-ticket.md` du
domaine `app`). Clés utilisées ici : `branche_integration`, `outil`, `data_source_id`, `propriete_identifiant`, `propriete_statut`, `statut_en_cours`. Fichier ou clé absent : valeur par défaut du
modèle, signalée une fois. Dans la suite, `{clé}` désigne la valeur lue.

## Le board

- `outil` = `aucun` : pas de board ; le skill crée seulement la branche, à partir de l'identifiant donné, et le signale.
- **Propriété identifiant** : `{propriete_identifiant}`
- **Propriété statut** : `{propriete_statut}`, option cible `{statut_en_cours}`
- **Base** : data source `{data_source_id}`. Utile seulement quand l'utilisateur donne un identifiant nu ; un lien Notion suffit à lui seul à ouvrir la page.

Si le board sur lequel on travaille n'a pas ces noms exacts, **prendre la propriété qui joue le même rôle** (celle qui porte l'avancement, et l'option qui signifie « en cours ») plutôt que d'échouer. Le signaler une fois, sans bloquer.

## Quand l'utiliser

- "start ticket ID-1931", "démarre le ticket 1931", "je commence ID-1931", "on attaque le ticket X"
- L'utilisateur veut commencer un travail suivi dans le board.

## Pré-vol

- **Accès au board** : le skill lit et écrit sur le board via le MCP Notion. S'il ne répond pas, **stop** : le dire en une phrase et indiquer qu'il faut installer le MCP Notion, puis relancer le skill. Ne pas tenter de l'installer, ni de contourner en travaillant sans le board.
- **Tree propre** : `git status --porcelain`. S'il reste des changements non commités → prévenir l'utilisateur (la branche emporterait ces changements) et demander avant de continuer.

## Identifier le ticket

1. Prendre l'identifiant fourni par l'utilisateur, **tel quel**. Ne pas supposer de format : c'est la propriété identifiant du board qui fait foi, quelle que soit sa forme.
2. Si l'utilisateur donne un lien Notion → l'ouvrir directement, sans passer par une recherche.
3. Si l'utilisateur donne une forme abrégée (un nombre nu, un identifiant sans son préfixe) → chercher le ticket dont l'identifiant **contient** cette forme, et confirmer le ticket trouvé avant d'agir.
4. Si rien n'est fourni → scanner la conversation pour un ticket récemment mentionné ou créé.
5. Si toujours rien, ou si plusieurs tickets correspondent → demander lequel. **Ne jamais deviner au hasard.**
6. Si aucun ticket ne correspond → **stop**, le dire clairement. Rien ne doit être créé sur un identifiant fantôme.

## Workflow

### 1. Statut → `{statut_en_cours}`
- Lire la propriété de statut du ticket.
- Si elle vaut déjà `{statut_en_cours}` → ne rien faire, juste le signaler.
- Sinon → la passer à `{statut_en_cours}`.

### 2. Créer la branche
- **Détecter la branche de base** :
  - si `{branche_integration}` existe (locale ou `origin/{branche_integration}`) → base = `{branche_integration}` ;
  - sinon → base = `main`.
  - L'utilisateur peut forcer explicitement (« depuis main », « depuis dev ») — sa consigne prime.
- Partir d'une base à jour :
  ```
  git checkout <base> && git pull --ff-only
  ```
- **Nommer la branche** `<identifiant>-<slug>` :
  - `<identifiant>` = l'identifiant du ticket, repris tel qu'il est sur le board, sans le reconstruire.
  - `<slug>` = kebab-case court dérivé du titre du ticket (mots significatifs, sans les préfixes `PROJET > SOUS-PROJET >`).
  ```
  git checkout -b <identifiant>-<slug>
  ```
  - Si la branche existe déjà → ne pas écraser, juste `git checkout` dessus et le signaler.

### 3. Rappeler le livrable
- Lire le **contenu de la page** du ticket, pas seulement ses propriétés.
- En extraire ce qui définit le travail à faire : la section **Livrable** si elle existe, sinon l'**Objectif** du ticket.
- Le restituer à l'utilisateur de façon visible, pour cadrer le travail qui démarre.

## Restitution

Une ligne d'état + le livrable. Ex :
```
✅ ID-1931 → DOING · branche ID-1931-poc-backend (depuis dev)

🎯 Livrable : POC backend opérationnel, auth + standup démontrés.
```
Si une étape était déjà faite (statut déjà `{statut_en_cours}`, branche déjà existante), le dire explicitement.

## Anti-patterns

- ❌ Supposer un format d'identifiant plutôt que de lire la propriété qui le porte sur le board.
- ❌ Créer une branche sur un identifiant qui ne correspond à aucun ticket — stop et signaler.
- ❌ Brancher par-dessus des changements non commités sans prévenir.
- ❌ Repasser en `{statut_en_cours}` un ticket qui y est déjà (no-op silencieux suffisant).
- ❌ Écraser une branche existante du même nom.
- ❌ Deviner le ticket au hasard quand plusieurs matchent — demander.
- ❌ Oublier le rappel du livrable : c'est la valeur centrale du skill.
