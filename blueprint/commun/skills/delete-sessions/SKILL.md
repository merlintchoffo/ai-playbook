---
name: delete-sessions
description: "Met à la corbeille des conversations Claude Code passées (liste /resume), récupérables avec recover-sessions. Utiliser quand l'utilisateur veut supprimer, effacer ou nettoyer des sessions de son historique."
disable-model-invocation: true
argument-hint: "[mot-clé | chemin absolu d'un projet]"
---

## Entrée

- Optionnel : un mot-clé (texte du premier message) ou le chemin absolu d'un autre projet. Sans rien, le projet courant.

## Sortie

- Un menu des conversations, de la plus récente à la plus ancienne.
- Après sélection : les conversations mises à la corbeille (aperçu, temps relatif, fichier).

---

## Comment faire

1. **Dossier des sessions** : `python3 <dossier du skill>/scripts/list_sessions.py --dossier-projet "<chemin absolu du projet>"`
   (projet courant par défaut). Pour « toutes mes conversations », parcourir `~/.claude/projects/*/`.

2. **Lister** : `python3 <dossier du skill>/scripts/list_sessions.py "<dossier>"`. Une ligne par fichier :
   `<temps relatif>\t<taille>\t<nb messages>\t<chemin>\t<aperçu>\t<RECENTE ou vide>`. Filtrer sur le mot-clé
   s'il y en a un.

3. **Session en cours** : son identifiant est dans le chemin du dossier scratchpad donné par le système
   (`…/<uuid>/scratchpad` → `<uuid>.jsonl`). L'exclure du menu : la mettre à la corbeille depuis
   l'intérieur ne l'efface pas, la session la recrée en perdant l'historique déjà écrit. Une autre
   session marquée `RECENTE` s'affiche « 🟢 modifiée il y a moins de 2 min » (peut-être ouverte ailleurs).

4. **Menu** : `AskUserQuestion`, `multiSelect: true`, une option par conversation : libellé = temps
   relatif + intitulé court ; description = aperçu, taille, nombre de messages, nom de fichier. Plus de
   4 conversations : regrouper les doublons évidents ou répartir sur plusieurs questions. Une seule
   conversation : ajouter l'option « Aucune, ne rien supprimer » (l'outil exige 2 options).

5. **Mettre à la corbeille** chaque fichier sélectionné : `gio trash "<chemin>"`. La sélection dans le
   menu vaut accord ; ne rien supprimer sans elle. Jamais `rm`. Confirmer ce qui est parti (aperçu,
   temps relatif) et rappeler que `/recover-sessions` le restaure.

Hors de Claude Code, `scripts/delete_sessions.sh [chemin du projet]` fait la même chose en mode interactif.
