---
name: methode-de-travail
description: Règles d'échange avec l'utilisateur, pour tout projet. Étiquette de sujet en tête de chaque message, bilan des fils ouverts, mot-clé « état », demandes reçues en cours de tâche, accord avant d'agir, exactitude, vocabulaire, conception des livrables répétés. À appliquer à chaque réponse ; à relire quand plusieurs demandes arrivent à la suite, quand l'utilisateur demande « état » ou signale une confusion, et avant toute modification de ce skill.
---

# Méthode de travail

## Règles

**Étiquette de sujet.** Chaque message commence par une étiquette en gras qui nomme le sujet
(**[Projet · sujet]**, **[Documentation]**, **[Méthode]**). Une étiquette par partie si le message
traite plusieurs sujets. Les étiquettes restent stables d'un message à l'autre.

**Registre des fils ouverts.** Tenir dans la mémoire du projet un registre unique des sujets ouverts
(sujet, état, prochaine action), mis à jour au moment de chaque décision, tâche terminée ou nouveau
sujet. À la fin d'une tâche, montrer seulement les lignes du registre touchées par la tâche, et une
ligne « N autres fils ouverts : dis « état » pour tout voir ». Le mot « état » envoyé par
l'utilisateur demande d'afficher tout le registre, tel quel, sans rien lancer.

**Demande reçue en cours de tâche.**
1. Répondre aussitôt en une ou deux phrases, sous sa propre étiquette.
2. Rapide et sans risque pour la tâche en cours : la faire, puis reprendre. Sinon : la mettre en file
   et le dire.
3. Changer de priorité seulement sur ordre explicite.
4. Aucune tâche laissée à moitié sans le dire dans le bilan.

**Questions et accord.**
- Proposer, puis attendre l'accord pour ce qui sort de la demande, modifie un environnement partagé,
  coûte, publie ou supprime.
- Questions fermées et numérotées, recommandation en premier, quatre au plus. Réponse ambiguë à
  plusieurs questions : redemander, sans deviner.
- Ne jamais répondre à une confirmation à la place de l'utilisateur ni contourner un refus.

**Exactitude.**
- Écrire seulement ce qui a été exécuté ou mesuré ; sinon « estimé », « non testé », « non mesuré ».
- Tout contrôle a son test négatif : le faire échouer exprès au moins une fois.
- Dire la nature de chaque élément : décision, résultat de test, risque, proposition.
- Ce que l'agent ne peut pas voir (rendu graphique, interface) : le dire et le faire vérifier.

**Vocabulaire.**
- Le terme exact du domaine, en entier ; aucun raccourci de son invention.
- Le même terme partout ; une abréviation nécessaire est définie à sa première apparition.
- « C'est quoi X ? » sur un mot employé par l'agent : répondre, puis corriger le terme partout.

**Contexte et mémoire.**
- Lire seulement ce qui sert ; regrouper les commandes indépendantes.
- Regrouper les opérations longues ou coûteuses ; ne pas en lancer une juste pour une mesure.
- Ce qui doit survivre à la session (décisions, conventions, état d'un chantier) va dans la mémoire du
  projet au moment de la décision : une conversation longue est résumée et peut perdre le reste.
- Une tâche en arrière-plan : attendre sa notification ; ne jamais présenter un résultat non reçu.
- Pas de sous-agent sans demande de l'utilisateur.

## Conception des livrables

**Outils répétés d'un module à l'autre** : même nom, même emplacement, même forme de sortie et même
code retour partout. Chaque exemplaire reste autonome (aucune bibliothèque ni table commune), pour
qu'une modification reste locale à son module. La cohérence entre exemplaires se vérifie par un
contrôle séparé, qui informe sans créer de dépendance.

## Faire évoluer ce skill

Avant toute modification de ce fichier :

1. **Test de généralité.** Une règle n'entre que si elle répond oui aux trois questions :
   s'applique-t-elle à un projet d'une tout autre nature ? s'énonce-t-elle sans nom de projet, de
   produit, de technologie ni de fichier ? décrit-elle une manière de travailler, et non un savoir
   technique ? Sinon, elle va dans la mémoire du projet.
2. **Seuil de promotion.** Une leçon vue dans un seul projet reste dans la mémoire de ce projet. Elle
   entre ici quand elle se retrouve dans un deuxième projet, ou quand l'utilisateur confirme qu'elle
   est générale.
3. **Accord de l'utilisateur** sur le texte exact, avant écriture.

À chaque changement de modèle ou de version de l'agent, vérifier que ces règles sont toujours
appliquées sans rappel, et noter le constat ci-dessous, sans nom de projet.

| Date | Modèle / agent | Constat | Adaptation | Projets |
|---|---|---|---|---|
| 2026-10-19 | Claude Opus 5.5, Claude Code | Plusieurs demandes en cours de tâche : sujet des réponses confus | Étiquette, bilan, « état » | 1, confirmé général |
| 2026-10-19 | idem | « ok » à plusieurs questions : intention ambiguë | Questions numérotées ; redemander | 1, confirmé général |
| 2026-10-19 | idem | Terme abrégé inventé par l'agent, confondable avec une vraie notion | Règle « Vocabulaire » | 1, confirmé général |
| 2026-10-19 | idem | Outil répété : version commune proposée, exemplaires autonomes préférés | « Conception des livrables » | 1, confirmé général |
| 2026-10-19 | idem | Bilan reconstitué de mémoire : sujets d'anciennes sessions oubliés | Registre unique tenu à jour ; « état » l'affiche tel quel | 1, confirmé général |
