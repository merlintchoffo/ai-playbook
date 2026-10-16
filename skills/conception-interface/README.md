# conception-interface

Un skill pour [Claude Code](https://docs.claude.com/en/docs/claude-code/skills) qui guide
la conception ou la refonte de l'interface d'une application web : sobre, cohérente
d'une page à l'autre, accessible, et vérifiée par des tests plutôt qu'à l'œil — avec du
HTML/CSS simple comme avec Tailwind, Bootstrap, React, Vue, Svelte ou Angular.

Il ne fournit pas un thème à plaquer. Il apporte une **démarche** (débattre avant de
coder, caractériser l'existant, avancer par lots testés, montrer avant de changer) et
des **garde-fous** que le projet garde ensuite comme tests.

## Ce que le skill impose, et ce qu'il propose

| Imposé | Proposé |
|---|---|
| Une couleur = un sens, toujours doublée d'un mot | Palette, police (Atkinson Hyperlegible), zones selon le domaine |
| Couleurs définies une seule fois (variables ou thème du framework), aucun style ni script dans le HTML | Gabarit menu · action · contexte, tiroirs `<dialog>` |
| Un même élément présenté pareil sur toutes les pages | Catalogue de composants |
| Aucune injection (`textContent` seulement), CSP stricte | Geste de confirmation proportionné au risque |
| Contrastes WCAG AA, clavier complet, focus visible | Bandeau d'environnement de test |
| Valeur par défaut = l'option la moins risquée | |

Le skill garde le framework en place (sauf raison d'en changer) et s'adapte à
l'outillage de test du projet (Playwright, Cypress, Vitest…) au lieu d'en imposer un.

## Contenu

```
conception-interface/
├── SKILL.md                        la démarche, lue par Claude
├── scripts/
│   ├── verifier-injection.js       injections et champs secrets mal protégés
│   └── verifier-contrastes.js      ratios WCAG calculés depuis les variables CSS
├── references/
│   ├── selon-la-pile.md            règles traduites par pile (Tailwind, React, Vue, SSR…)
│   ├── couleurs.md                 sens des couleurs, zones, palette, seuils
│   ├── gabarit-et-composants.md    gabarit, composants, vocabulaire
│   ├── garde-fous-tests.md         tests à transposer (CSP, clavier, cohérence…)
│   └── evaluation.md               avant/après, retours d'expérience, essai témoin
├── assets/css-de-base.css          variables et composants de départ (thèmes clair et sombre)
├── evals/evals.json                demandes types pour évaluer le skill
├── retours.md                      modèle et retours anonymisés
└── .gitignore                      exclut retours-prives.md
```

## Installation

Copier le dossier dans les skills personnels de Claude Code :

```sh
git clone <url-du-depot> ~/.claude/skills/conception-interface
```

ou dans un projet précis : `.claude/skills/conception-interface/`. Claude l'utilise
ensuite de lui-même dès qu'une demande porte sur une interface (« refais cette page »,
« harmonise ces écrans », « vérifie les contrastes »…).

## Les scripts, seuls

Ils ne demandent que Node.js (aucune dépendance) et renvoient un code d'erreur en cas
de défaut, ce qui permet de les lancer en intégration continue :

```sh
node scripts/verifier-injection.js src/ public/ --ignorer public/vendor/lib.min.js
node scripts/verifier-contrastes.js src/styles/theme.css
node scripts/verifier-contrastes.js _variables.scss --paires mes-paires.json
node scripts/verifier-contrastes.js --couleurs tailwind-couleurs.json --paires mes-paires.json
```

`verifier-injection.js` analyse `.js`, `.ts`, `.jsx`, `.tsx`, `.vue`, `.svelte` et `.html`
(dossiers `node_modules`, `dist`, `build`… ignorés) et repère aussi les équivalents
d'`innerHTML` des frameworks : `dangerouslySetInnerHTML`, `v-html`, `{@html}`,
`[innerHTML]`, `bypassSecurityTrust…`.

`verifier-contrastes.js` lit les thèmes d'un CSS (chaque bloc qui définit `--fond`), les
variables d'un SCSS ou LESS, ou un JSON de couleurs (par exemple les couleurs résolues de
Tailwind, objets imbriqués aplatis en `gray-400`), et contrôle des paires texte/fond. Si vos variables portent d'autres noms, décrivez les
paires dans un fichier JSON :

```json
[["text", "background", 4.5, "texte courant"], ["input-border", "background", 3, "bordure des champs"]]
```

Limites : `verifier-injection.js` repère des motifs dans le code source ; il ne remplace
pas une revue de sécurité, et ne contrôle pas les attributs des champs secrets en JSX.
`verifier-contrastes.js` lit `#rgb`, `#rrggbb`, `rgb()` et `hsl()` opaques ; il signale
comme « non vérifiées » les paires qu'il ne peut pas calculer (transparence, `color-mix`…).

## Améliorer le skill

Après un projet réel, Claude ajoute une entrée à `retours-prives.md` (créé au besoin,
exclu par `.gitignore`, car il cite des projets réels) : ce qui a servi, ce qui a manqué,
les nouveaux pièges. Seuls des retours anonymisés vont dans `retours.md`, publié.
Le skill décrit aussi un **essai témoin** facultatif (même
demande confiée à un agent avec et sans le skill, comparaison à l'aveugle) pour mesurer
son apport réel. Les contributions et retours sont bienvenus.

## Licence

À préciser.
