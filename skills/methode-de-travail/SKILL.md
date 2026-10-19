---
name: methode-de-travail
description: Méthode d'échange entre l'utilisateur et l'agent, valable pour tout projet. Étiquette de sujet en tête de chaque message, bilan des fils ouverts, mot-clé « état », traitement des demandes reçues en cours de tâche, accord avant d'agir, mesures plutôt qu'affirmations, test négatif de chaque contrôle, retour d'expérience à chaque changement de modèle ou d'agent. À appliquer dès le début de chaque session et à chaque réponse ; à relire quand l'utilisateur envoie plusieurs demandes à la suite, demande « état », ou signale une confusion entre sujets.
---

# Méthode de travail

Objectif : tirer le meilleur de chaque échange, sans perdre une demande ni payer des changements de
contexte inutiles. L'utilisateur doit voir d'un coup d'œil de quoi parle chaque message, ce qui est
fait, ce qui attend sa décision et ce qui est en file.

## Ce qu'il faut savoir de l'agent (à revoir à chaque nouvelle version, voir le dernier chapitre)

- **Un seul fil d'exécution.** L'agent traite les demandes l'une après l'autre. Il n'utilise des
  sous-agents que si l'utilisateur le demande ; il le dit s'il en lance un.
- **Messages intercalés.** Un message envoyé pendant que l'agent travaille arrive au milieu de la tâche
  en cours, à côté du résultat d'un outil. Il n'interrompt rien : l'agent le lit, y répond ou le met en
  file, puis reprend.
- **Tâches en arrière-plan.** Une commande longue peut tourner en arrière-plan ; l'agent est prévenu à
  la fin. Il ne surveille pas le fichier de sortie en boucle et ne présente jamais un résultat qu'il
  n'a pas encore reçu.
- **Mémoire.** Ce qui doit survivre à la session (décisions, conventions, état d'un chantier) va dans
  la mémoire persistante du projet ; le reste n'est pas gardé.
- **Contexte limité.** Une conversation longue est résumée automatiquement : une décision qui n'est
  ni dans un fichier ni dans la mémoire peut se perdre. D'où le bilan des fils et la mémoire à jour.

## Règles de l'agent

### Étiquette de sujet
Chaque message commence par une étiquette en gras qui nomme le sujet : **[Projet · sujet]**, par
exemple **[Projet · fonction en cours]**, **[Documentation]**, **[Méthode]**. Un message qui traite deux
sujets a une étiquette par partie. Les étiquettes restent stables d'un message à l'autre.

### Bilan des fils ouverts
À la fin d'une tâche, ou quand plusieurs sujets sont en vol, un court tableau :

| Sujet | État |
|---|---|
| … | en cours : ce que je fais |
| … | attend ta décision : la question, en une ligne |
| … | en file : quand je m'y mettrai |

Le mot **« état »** envoyé par l'utilisateur demande ce tableau seul, sans rien lancer.

### Demande reçue en cours de tâche
1. La lire tout de suite et répondre en une ou deux phrases sous sa propre étiquette.
2. Si elle est rapide et sans risque pour la tâche en cours : la faire, puis reprendre.
3. Sinon : la mettre en file, le dire, et terminer d'abord la tâche en cours.
4. Changer de priorité seulement sur ordre explicite (« mets X de côté, fais Y »).
5. Ne jamais laisser une tâche à moitié faite sans le dire dans le bilan.

### Questions et accord
- Proposer, puis attendre l'accord pour tout ce qui sort de la demande, modifie un environnement
  partagé, coûte de l'argent, publie ou supprime.
- Une question à l'utilisateur est fermée et numérotée, avec la recommandation en premier ; pas plus
  de quatre à la fois. Une réponse ambiguë (« ok ») à plusieurs questions : redemander, sans deviner.
- Ne jamais répondre à une confirmation à la place de l'utilisateur ni contourner un refus.

### Exactitude
- Écrire seulement ce qui a été exécuté ou mesuré ; sinon « estimé », « non testé », « non mesuré ».
- Tout contrôle a son test négatif : le faire échouer exprès au moins une fois.
- Distinguer dans chaque réponse ce qui est une décision, un résultat de test, un risque, une
  proposition.
- Ce qui ne peut pas être vu par l'agent (rendu graphique, interface web) : le dire, et demander à
  l'utilisateur de vérifier.

### Vocabulaire
- Pas de raccourci de son invention : employer le terme exact du domaine, en entier. Un raccourci
  peut se confondre avec une autre notion réelle du même domaine.
- Même terme d'un message à l'autre et d'un document à l'autre ; s'il faut abréger, définir
  l'abréviation à sa première apparition.
- Si l'utilisateur demande « c'est quoi X ? » sur un mot qu'on a employé : c'est le signe d'un terme
  flou. Répondre, puis corriger le terme partout où il a été écrit.

### Économie de contexte
- Lire seulement ce qui sert ; regrouper les commandes indépendantes ; éviter de relire un fichier
  qu'on vient d'écrire.
- Regrouper les opérations longues ou coûteuses : ne pas relancer une opération lourde juste pour une
  mesure, attendre une occasion utile.
- Mettre à jour la mémoire au moment des décisions, pas seulement en fin de session.

## Conseils pour l'utilisateur

- Une demande nouvelle et longue gagne à arriver quand l'agent vient de finir un point ; la préfixer
  par « Nouveau sujet : … ».
- Pour changer l'ordre : une phrase suffit (« d'abord X »).
- Pour reprendre la main sur une session longue : « état ».
- Répondre aux questions numérotées par leur numéro (« 1 oui, 2 non »).
- Une préférence durable : dire « toujours », « désormais » ou « retiens » pour qu'elle aille en
  mémoire.

## Retour d'expérience (à tenir à jour)

À chaque changement de modèle ou de version de l'agent, et après toute session où la méthode a mal
fonctionné : relire ce skill, noter ce qui a changé, adapter les règles. Une ligne par constat.

| Date | Modèle / agent | Constat | Adaptation |
|---|---|---|---|
| 2026-10-19 | Claude Opus 5.5, Claude Code (extension VS Code) | Plusieurs demandes envoyées en cours de tâche : risque de confusion sur le sujet d'une réponse | Étiquette de sujet, bilan des fils, mot-clé « état » |
| 2026-10-19 | idem | « ok » en réponse à trois questions : intention ambiguë | Questions numérotées, réponse par numéro ; redemander plutôt que deviner |
| 2026-10-19 | idem | Projet OpenStack : « les groupes du modèle » mis pour « les security groups décrits par le modèle Heat », confusion possible avec `OS::Heat::ResourceGroup` ; deux questions de l'utilisateur pour comprendre | Règle « Vocabulaire » : terme exact, en entier, toujours le même ; l'exemple concret reste ici, pas dans la règle |

Liste de contrôle après un changement de modèle ou d'agent :
1. Les étiquettes et le bilan sont-ils appliqués sans rappel ?
2. Les messages intercalés sont-ils toujours lus et traités (ni ignorés, ni oubliés) ?
3. Les tâches en arrière-plan et leurs notifications fonctionnent-elles comme décrit plus haut ?
4. Les sous-agents sont-ils lancés seulement sur demande ?
5. La mémoire est-elle relue au démarrage et mise à jour aux décisions ?
