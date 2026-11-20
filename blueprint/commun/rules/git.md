# Git — règles globales

## A propos des commits

- Fait des Conventional Commits.
- Ne commit pas sans mon autorisation.

## ⛔️ Merge = accord explicite OBLIGATOIRE

**Ne JAMAIS merger une PR (ou une branche) vers `main` sans l'accord explicite de l'utilisateur, donné pour CETTE PR précise.**

- Un « push et merge » donné pour une PR ne vaut PAS autorisation pour les suivantes. Une autorisation de merge est **ponctuelle**, jamais permanente.
- Le workflow par défaut s'arrête à : commit → push (si autorisé) → ouvrir la PR → **STOP**. L'utilisateur review et décide du merge.
- Même pour une retouche d'une ligne, même si ça semble évident : la PR attend.

## Identité de l'auteur

- Avant chaque commit, lire `git config user.name` et `git config user.email`. Si l'identité est absente ou d'apparence fictive (domaine `.local`, `example`, `localhost`, nom générique), ne pas commiter : demander à l'utilisateur son nom et une adresse rattachée à son compte de forge (ou l'adresse anonyme que la forge fournit), puis la poser dans le dépôt seulement (`git config`, sans `--global` sauf demande).
- Jamais de ligne `Co-authored-by` ni de mention de l'agent dans un commit ou une pull request.
- Avant chaque commit, si le dépôt a un dossier `.githooks/`, lire `git config --show-origin --get core.hooksPath`. Activer `.githooks/` fait exécuter le code de l'auteur du dépôt : n'agir sans demander que si `.githooks/` contient seulement `commit-msg`, identique à celui d'ai-playbook.
  - `.githooks` : rendre `.githooks/commit-msg` exécutable s'il ne l'est pas.
  - absent : s'il n'existe dans `.git/hooks/` aucun fichier exécutable sans suffixe `.sample`, régler `core.hooksPath .githooks` dans le dépôt ; sinon, demander.
  - autre valeur : demander, ne jamais écraser.

  Signaler tout réglage fait.
