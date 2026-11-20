# Appliquer le skill selon la pile technique

Principe : **garder la pile existante** sauf raison explicite de la quitter (poids,
dette, sécurité) discutée avec l'utilisateur. Les règles s'appliquent à toutes les piles ;
seule leur traduction change.

## Framework CSS (Tailwind, Bootstrap, Bulma…)

- **Sens des couleurs** : le rattacher aux couleurs du thème du framework (config
  Tailwind `theme.colors`, variables Bootstrap `$primary`, `$danger`…) : `primary` = agir,
  `warning` = vérifier, `danger` = bloquant, `success` = réussi seulement. Ne pas utiliser
  `danger` ou `success` pour décorer.
- **« Aucun style dans le HTML »** vise l'attribut `style`, pas les classes : les classes
  utilitaires Tailwind sont légitimes. Éviter en revanche les valeurs arbitraires
  (`text-[#777]`) qui contournent le thème.
- **Composants partagés** : composants du projet (`@apply` avec parcimonie, ou
  composants du framework JS), pas de classes répétées à l'identique de page en page.
- **Contrastes** : Bootstrap → `node scripts/verifier-contrastes.js _variables.scss
  --paires paires.json` ; Tailwind → exporter les couleurs résolues puis
  `--couleurs couleurs.json` :
  ```sh
  node -e "const r=require('tailwindcss/resolveConfig');console.log(JSON.stringify(r(require('./tailwind.config.js')).theme.colors))" > couleurs.json
  ```
  (Tailwind 4 : thème en variables CSS `@theme` → lire le CSS directement.)

## Framework de composants (React, Vue, Svelte, Angular)

- **Injection** : l'équivalent d'`innerHTML` est `dangerouslySetInnerHTML` (React),
  `v-html` (Vue), `{@html}` (Svelte), `[innerHTML]` / `bypassSecurityTrust…` (Angular) :
  les proscrire ; afficher du texte par liaison normale (`{texte}`, `{{ texte }}`).
  `scripts/verifier-injection.js` les détecte.
- **Comportements partagés** (choix segmenté, appui maintenu, tiroir) : un composant
  chacun, utilisé partout.
- **Pilotes de test** : mêmes principes ; s'appuyer sur `data-testid` ou les rôles ARIA.
- **Champs secrets** : en JSX, `spellCheck={false}`, `autoCapitalize="off"`,
  `autoComplete="current-password"` (le script ne contrôle les attributs que dans les
  gabarits HTML, Vue et Svelte : vérifier le JSX à la main ou par test).

## CSS-in-JS (styled-components, Emotion…)

- Ces bibliothèques injectent des balises `<style>` : une CSP stricte exige un **nonce**
  (ou une empreinte) transmis à la bibliothèque, pas `'unsafe-inline'`.
- Garder les couleurs dans un objet de thème unique (équivalent des variables CSS).

## Rendu serveur (Next, Nuxt, SvelteKit…)

- CSP par en-tête HTTP plutôt que par `<meta>` ; nonce par requête pour les scripts
  d'hydratation.
- Tester la CSP sur la version construite (`build` + serveur), pas seulement en dev.

## Pages statiques, sans build

- Scripts classiques si les pages s'ouvrent en `file://` (les modules ES y échouent) ;
  CSP par `<meta>` ; tout embarquer localement (polices, bibliothèques).

## Dans tous les cas

Tester la CSP dans les conditions réelles : certaines piles posent des styles en ligne
via `setAttribute('style', …)` (bloqué par une CSP stricte) quand d'autres passent par
`element.style` (autorisé). Seul un essai dans le navigateur tranche.
