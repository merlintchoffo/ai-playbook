---
name: recover-sessions
description: "Restaure des conversations Claude Code mises à la corbeille par delete-sessions. Utiliser quand l'utilisateur veut récupérer, restaurer ou annuler la suppression d'une session."
argument-hint: "[mot-clé]"
---

## Entrée

- Optionnel : un mot-clé (projet ou texte de l'aperçu) pour filtrer les sessions de la corbeille.

## Sortie

- Un menu des sessions présentes dans la corbeille, de la plus récemment supprimée à la plus ancienne.
- Après sélection : les sessions restaurées, avec leur chemin d'origine.

---

## Comment faire

**Règle bloquante** : ne restaurer un fichier qu'après un `AskUserQuestion` résolu dans ce même tour et
qui le désigne. Un accord antérieur, sur un autre sujet ou général, ne vaut pas.

1. **Lister** : `python3 <dossier du skill>/scripts/restore_sessions.py lister`. Une ligne par session :
   `<supprimé il y a>\t<taille>\t<nb messages>\t<nom dans la corbeille>\t<chemin d'origine>\t<aperçu>`.
   Filtrer sur le mot-clé s'il y en a un. Aucune session : le dire, sans menu.

2. **Menu** : `AskUserQuestion`, `multiSelect: true`, une option par session : libellé = « supprimée il y
   a … » + intitulé court ; description = aperçu, taille, nombre de messages, projet d'origine. Une seule
   session : ajouter « Aucune, ne rien restaurer ».

3. **Restaurer** les sessions choisies : `python3 <dossier du skill>/scripts/restore_sessions.py restaurer
   "<nom dans la corbeille>" …`. Le script remet chaque fichier à son chemin d'origine (lu dans la
   corbeille) et n'écrase jamais un fichier existant ; il le signale et sort en code 1.

4. Confirmer ce qui est restauré (aperçu, chemin) et ce qui ne l'est pas, avec la raison.
