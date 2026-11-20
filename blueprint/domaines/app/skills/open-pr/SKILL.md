---
name: open-pr
description: Passe le verrou qualité (lint, typecheck, test), pousse la branche et ouvre la PR vers la branche d'intégration, sans merger ni toucher au ticket. Utiliser quand l'utilisateur dit « ouvre la PR », « open pr », « envoie en review ».
disable-model-invocation: true
---

## Entrée

- La **branche courante**, considérée comme terminée par l'utilisateur : travail commité, pas encore poussé.

## Sortie

- L'**URL de la PR** ouverte vers `{branche_integration}` (ou, avec `forge` = `aucune`, le lien pour la créer dans le navigateur).

---

## Paramètres du projet

Lire `.claude/workflow-ticket.md` à la racine du projet (modèle : `modeles-config/workflow-ticket.md` du
domaine `app`). Clés utilisées ici : `branche_integration`, `lint`, `typecheck`, `test`, `forge`, `outil`. Fichier ou clé absent : valeur par défaut du
modèle, signalée une fois. Dans la suite, `{clé}` désigne la valeur lue.

Le skill s'arrête là. Il ne merge pas, et **ne touche pas au ticket** : tant que rien n'est mergé ni déployé, il n'y a rien à tester — le ticket reste où il est et n'ira en `TESTING` qu'après le merge et le déploiement.

## Étapes

1. **Vérifier le point de départ.** `git status` et branche courante. S'il reste des changements non commités, le signaler et demander — ne pas commiter à la place de l'utilisateur.
2. **Passer le verrou.** `{lint}`, puis `{typecheck}`, puis `{test}`.
3. **Pousser.** `git push -u origin <branche>`.
4. **Ouvrir la PR.** Avec `forge` = `gh` : `gh pr create --base {branche_integration} --head <branche>`, titre clair et corps dérivé des commits de la branche ; afficher l'URL. Avec `forge` = `aucune` : donner le lien de création de PR affiché par `git push` (ou celui de la page du dépôt), avec un titre et un corps prêts à coller.

## Règles

- **Le verrou est bloquant.** Au premier rouge : on s'arrête, on montre la sortie réelle de la commande, et **rien n'est poussé**. Ne jamais contourner un test qui échoue ni le désactiver pour pouvoir pousser.
- **⛔ Ne jamais merger.** Le merge vers `{branche_integration}` est une décision explicite de l'utilisateur, donnée pour CETTE PR précise (cf. la rule Git du repo). Ouvrir la PR ne vaut pas autorisation.
- **Un seul repo à la fois** : celui de la branche courante. Ne pas pousser ni ouvrir de PR pour un autre repo.
- **Rapporter l'état réel.** Si une étape échoue (push refusé, `gh` non authentifié), le dire franchement avec l'erreur — ne pas prétendre que c'est fait.
