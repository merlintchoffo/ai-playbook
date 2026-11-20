# ai-playbook

Configurations de travail pour Claude Code : règles, skills, agents et hooks qui font suivre à
l'agent un process défini, au lieu d'en improviser un.

## Organisation

```
ai-playbook/
├── handoffs/                passations entre sessions, non versionnées
└── blueprint/
    ├── commun/              vaut pour tout projet → installé dans ~/.claude
    │   ├── rules/           règles chargées à chaque session (methode-de-travail)
    │   ├── skills/          skills transverses (synchroniser-skills, grill-me, handoff, recap, delete-sessions, recover-sessions, manage-*…)
    │   ├── hooks/           hooks (bloquer-commandes-interdites)
    │   ├── outils/          commandes lancées depuis le dépôt (sauvegarde-claude.sh), non installées
    │   └── historique/      évolutions des règles, non installé
    └── domaines/            décrit un type de projet → installé dans <projet>/.claude, sur demande
        ├── app/             développement d'application web : workflow d'un ticket, UI, tests
        └── audit/          synthèse managériale d'audit de conformité (.pptx)
```

Le critère : **ce qui resterait vrai sur n'importe quel projet va dans `blueprint/commun/`** ; ce qui
décrit un type de projet (sa stack, son workflow, ses conventions) va dans un domaine, et n'est
installé que dans les projets de ce type.

## Installer

Avec le skill `synchroniser-skills` (le dépôt fait seule référence, seule la version commitée
est installée) :

- `/synchroniser-skills comparer` puis `installer` : le commun, dans `~/.claude` ;
- `/synchroniser-skills installer app <chemin du projet>` : le domaine app, dans ce projet.

Avant une modification risquée de `~/.claude` : `bash blueprint/commun/outils/sauvegarde-claude.sh sauvegarder`.

## Conventions d'écriture des skills et des agents

- Un skill porte un nom qui commence par un **verbe** (`write-code`, `concevoir-interface`) ; un
  agent, un nom de métier en **`-er`** (`code-reviewer`).
- Le `name` de l'en-tête est égal au nom du dossier (ou du fichier, pour un agent).
- Dans l'en-tête YAML, une valeur sans guillemets ne contient jamais `: ` (deux-points suivi d'une
  espace) : l'en-tête devient invalide.

Contenus tiers et licences : [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
