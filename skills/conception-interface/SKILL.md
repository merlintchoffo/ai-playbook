---
name: conception-interface
description: Démarche pour concevoir, refondre ou harmoniser l'interface d'une application web (pages, écrans, formulaires), quelle que soit la pile (HTML/CSS, Tailwind, Bootstrap, React, Vue, Svelte, Angular) — co-conception avant le code, code couleur à sens unique, composants partagés, garde-fous testés (anti-injection, CSP, contrastes WCAG, clavier, cohérence entre pages). À utiliser dès qu'on demande de créer, refaire, moderniser ou « rendre moins moche » une interface, de choisir couleurs ou composants, ou de vérifier l'accessibilité et la cohérence visuelle de plusieurs écrans. Pas pour retoucher un style isolé.
---

# Conception d'interface

Une bonne interface tient moins à son apparence qu'à la démarche qui la produit et aux
garde-fous qui la vérifient. Ce skill impose peu (des invariants dont l'oubli produit des
défauts réels) et propose le reste. Il s'adapte à la pile et à l'outillage du projet :
**garder le framework existant** sauf raison explicite d'en changer
(→ `references/selon-la-pile.md`).

## Entrée

Lire le code et la doc d'abord ; ne demander à l'utilisateur que ce qui manque :
les écrans et parcours ; le public (technique, grand public, les deux → mot simple
d'abord, terme technique ensuite, détail replié) ; **les risques du domaine** (ce qui est
irréversible ou coûteux : ils dictent couleurs et gestes de confirmation) ; la pile et les
tests existants ; les contraintes d'exécution (hors ligne, `file://`, CSP, CDN) ; les audits.

## Sortie

Chaque livrable validé avant le suivant : diagnostic de l'existant → maquettes sobres
(storyboard, pas de pixel près) → plan par lots avec décisions ouvertes → thème
(variables) et page d'échantillons → pages migrées par lot, avec tests → garde-fous
transposés en tests du projet → captures avant/après → document des décisions et
limites connues. Interface existante : en plus, tableau avant/après et retour
d'expérience (→ `references/evaluation.md`).

## Démarche

1. **Débattre avant de coder** : au plus deux options argumentées, une recommandation,
   l'utilisateur tranche. Pas d'esthétique « générée » (dégradés, verre dépoli, émojis en
   icônes, ornements) : l'originalité vient de la structure, pas du décor. Viser le plus simple.
2. **Caractériser l'existant par des tests** avant de toucher l'interface ; la
   connaissance du DOM dans des **pilotes de page**, pour que les tests survivent à la refonte.
3. **Par lot** : test rouge, code, test vert ; si tout passe du premier coup, casser
   volontairement le code pour prouver le test. Dire quand un test a été écrit après.
4. **Tour visuel** de toutes les pages (bureau et mobile) à chaque fin de lot, par
   captures du navigateur de test.
5. **Montrer avant de changer une mise en page** : avant/après en injectant le CSS
   proposé dans le navigateur de capture, sans toucher au code.
6. **Appliquer une remarque partout et entièrement** : même défaut cherché sur toutes les
   pages ; affichage *et* comportement.

## Structure

| Imposée (sauf raison explicite) | Proposée (→ références) |
|---|---|
| **Une couleur = un sens**, toujours doublée d'un mot | Palette, zones de luminosité selon le domaine |
| Couleurs définies une seule fois (variables ou thème du framework) | Police Atkinson Hyperlegible (texte + données) |
| Composants partagés, aucun copier-coller entre pages | Gabarit menu · action · contexte, tiroirs `<dialog>` |
| Un même élément s'affiche pareil sur toutes les pages | Catalogue de composants |
| Petits écrans : l'action d'abord, sauf mode d'emploi à lire avant d'agir | Bande d'en-tête, fil d'étapes, bandeau d'environnement de test |
| Ce qui doit être vérifié n'est jamais caché (tiroir, repli) | Détails techniques en tiroir |
| Valeur par défaut = l'option la moins risquée | Appui maintenu pour l'irréversible |

Sens proposés : bleu agir · jaune vérifier · rouge danger, irréversible ou bloquant
(jamais une situation normale) · vert réussi seulement · une couleur réservée à
l'environnement de test.

## Règles

1. **Aucune injection** : texte par `textContent` ou liaison normale du framework ;
   jamais `innerHTML`, `insertAdjacentHTML`, `document.write`, `eval`, `new Function`,
   `dangerouslySetInnerHTML`, `v-html`, `{@html}`, `[innerHTML]` ; pas de script, `on…=`
   ni `style=` écrits dans le HTML.
2. **CSP stricte** (`default-src 'none'` puis le nécessaire), testée dans les conditions
   réelles ; toute nouvelle connexion s'y ajoute.
3. **Contrastes WCAG AA** : 4,5:1 texte, 3:1 bordures de champs et composants, calculés
   depuis le thème, jamais de mémoire.
4. **Clavier** : tout sans souris, contour de focus visible partout.
5. **Champs secrets** : sans correcteur, majuscule ni mémorisation automatiques ; pas de
   bouton « Copier ».
6. **Aucune étiquette rassurante non vérifiée** (« sûr », « fictif », « vérifié »).
7. **Un geste sans effet visible est un défaut** : un bouton qui ignore un clic dit pourquoi.

## Vérifications

```sh
node <skill>/scripts/verifier-injection.js <dossiers…> [--ignorer <chemin>]   # règles 1, 5
node <skill>/scripts/verifier-contrastes.js <theme.css|.scss|.less>           # règle 3
node <skill>/scripts/verifier-contrastes.js --couleurs theme.json --paires paires.json
```

Node seul, code d'erreur si défaut. Les intégrer ensuite comme tests du projet. CSP,
clavier, cohérence, ordre sur mobile : tests à transposer (→ `references/garde-fous-tests.md`).

## Pièges connus

- `<select>` qui s'ouvre sur la première option, la plus risquée : invisible des tests.
- Rouge pour une situation normale (liste vide) : jaune, et dire quoi faire.
- Harmoniser l'affichage d'un élément mais pas sa sélection.
- Espace fine U+202F quasi invisible dans certaines polices : mesurer, sinon U+00A0.
- `innerText` ignore le contenu replié (chercher un secret avec `textContent`).
- Valeur non modifiable encadrée comme un bouton.
- Récapitulatif en double au-dessus du détail sur mobile.

## Références

- `references/selon-la-pile.md` — traduction des règles par pile (Tailwind, Bootstrap, React, Vue, CSS-in-JS, SSR).
- `references/couleurs.md` — sens, zones, construction de la palette, seuils.
- `references/gabarit-et-composants.md` — gabarit, composants, vocabulaire.
- `references/garde-fous-tests.md` — tests à transposer.
- `references/evaluation.md` — avant/après, retours d'expérience (`retours-prives.md`), essai témoin.
- `assets/css-de-base.css` — thème clair/sombre et composants de départ (sans framework).
