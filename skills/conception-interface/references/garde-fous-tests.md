# Garde-fous à transposer en tests

Adapter à l'outillage du projet (Playwright, Cypress, Vitest + jsdom, pytest + Selenium…).
Les exemples sont en Playwright ; la logique se transpose. Si le projet n'a aucun test,
proposer le minimum : le lanceur de tests natif du langage + un navigateur piloté.

## Organisation

- **Tests de caractérisation d'abord** : ce que l'existant fait et qui doit rester vrai
  (calculs, formats de fichiers, résultats). Écrits sur l'ancienne interface, ils doivent
  passer tels quels sur la nouvelle.
- **Pilotes de page** : une classe par page, seule à connaître les sélecteurs. Les tests
  disent l'intention (`p.validerCommande(panier)`). Après la refonte, on réécrit le pilote,
  pas les tests.
- **Repères stables** : `data-champ="montant"` plutôt que des classes de style.
- **Serveurs simulés** : intercepter les requêtes et répondre localement ; bloquer et noter
  tout le reste. Aucun test ne sort vers internet.

## Scripts du skill → tests du projet

Les deux scripts (`verifier-injection.js`, `verifier-contrastes.js`) peuvent être lancés
tels quels dans l'intégration continue, ou réécrits comme test unitaire (même logique :
lire les fichiers, chercher les motifs, calculer les ratios).

## CSP

```js
for (const chemin of PAGES) {
  test(`${chemin} · politique stricte déclarée`, async ({ page }) => {
    await page.goto(url(chemin));
    const csp = await page.getAttribute('meta[http-equiv="Content-Security-Policy"]', 'content');
    expect(csp).toContain("default-src 'none'");
    expect(csp).not.toMatch(/unsafe-inline|unsafe-eval/);
  });
}
// Parcours complet sans violation : écouter la console.
const violations = [];
page.on('console', (m) => { if (/Content Security Policy/i.test(m.text())) violations.push(m.text()); });
// … parcours …
expect(violations).toEqual([]);
// Connexion interdite réellement bloquée :
expect(await page.evaluate(() => fetch('https://example.org/').then(() => 'joint', () => 'bloqué'))).toBe('bloqué');
```

## Clavier

```js
async function tabulerJusqua(page, selecteur) {
  for (let i = 0; i < 60; i += 1) {
    await page.keyboard.press('Tab');
    if (await page.evaluate((s) => document.activeElement?.matches(s), selecteur)) return;
  }
  throw new Error(`${selecteur} inatteignable au clavier`);
}
// Contour visible sur chaque élément atteint (champ de fichier caché : regarder son bouton).
const style = getComputedStyle(el.classList.contains('visuellement-cache') ? el.previousElementSibling : el);
const visible = style.outlineStyle !== 'none' && parseFloat(style.outlineWidth) > 0;
// Appui maintenu au clavier :
await page.keyboard.down(' '); await expect(resultat).toBeVisible(); await page.keyboard.up(' ');
```

Faire au moins un parcours critique entièrement au clavier.

## Cohérence entre pages

Un test par élément partagé, sur toutes les pages : même conteneur, même libellé,
même forme (ex. « l'en-tête présente Environnement puis sa valeur » sur les N pages).

## Ordre sur petits écrans

```js
await page.setViewportSize({ width: 390, height: 900 });
const haut = async (s) => (await page.locator(s).boundingBox()).y;
expect(await haut('main')).toBeLessThan(await haut('aside'));
```

## Valeurs par défaut

Tester l'état à l'ouverture : option sélectionnée, bouton actif, bandeau affiché.
Un défaut choisi par hasard (première option d'un menu) ne se voit dans aucun autre test.

## Secrets

- Après usage, les champs secrets sont vides.
- Le secret n'apparaît nulle part dans la page : `textContent` du `body` (pas
  `innerText`, qui ignore le contenu replié).
- Pas de bouton « Copier » près d'un secret.

## Prouver un test

Si un test passe du premier coup, casser volontairement le code (retirer un blocage,
afficher le secret) et vérifier qu'il échoue, puis restaurer.

## Captures

Le navigateur de test sert aussi à la revue visuelle : capturer chaque état (bureau
1280 px, mobile 390 px), les regarder, et pour un changement de mise en page, produire
un avant/après en injectant le CSS proposé (`page.addStyleTag`) sans toucher au code.
Pièges : un chemin de fichier avec accents peut faire échouer le dépôt de fichier
(écrire dans un dossier temporaire) ; `toContainText` lit aussi le texte caché.
