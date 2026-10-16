#!/usr/bin/env node
// Cherche dans le code d'une interface ce qui permet une injection, et les champs secrets
// mal protégés. Node seul, sans dépendance. Code de sortie 1 si un défaut est trouvé.
//
// Usage : node verifier-injection.js <dossier|fichier>... [--ignorer <chemin>]...
//   Analyse (récursivement) .js .mjs .cjs .ts .jsx .tsx .vue .svelte .html .htm,
//   sauf node_modules, .git, dist, build, .next, coverage, *.min.js, *.d.ts.
//   --ignorer : chemin d'une bibliothèque tierce ou d'un dossier à exclure.
// Limite : repère des motifs dans le source ; ne remplace pas une revue de sécurité.
'use strict';

const fs = require('node:fs');
const path = require('node:path');

const DOSSIERS_EXCLUS = new Set(['node_modules', '.git', 'dist', 'build', '.next', '.nuxt', '.svelte-kit', 'coverage']);

// Code JavaScript / TypeScript, y compris JSX.
const JS = [
  [/\.(inner|outer)HTML\s*=/, 'innerHTML ou outerHTML (utiliser textContent / replaceChildren)'],
  [/insertAdjacentHTML/, 'insertAdjacentHTML'],
  [/document\.write/, 'document.write'],
  [/\beval\s*\(/, 'eval'],
  [/new\s+Function\s*\(/, 'new Function'],
  [/set(Timeout|Interval)\s*\(\s*['"`]/, 'setTimeout ou setInterval avec du texte'],
  [/\.html\s*\(/, '.html() (jQuery)'],
  [/\.setAttribute\s*\(\s*['"]on/i, "gestionnaire d'événement posé par setAttribute"],
  [/\.setAttribute\s*\(\s*['"]style['"]/i, 'attribut style posé par setAttribute (incompatible avec une CSP stricte)'],
  [/dangerouslySetInnerHTML/, 'dangerouslySetInnerHTML (React)'],
  [/bypassSecurityTrust\w*/, 'bypassSecurityTrust… (Angular)'],
];

// Gabarits de composants (Vue, Svelte, Angular) : HTML interprété.
const GABARITS = [
  [/\sv-html\s*=/, 'v-html (Vue)'],
  [/\{@html\b/, '{@html} (Svelte)'],
  [/\[(innerHTML|outerHTML)\]\s*=/, '[innerHTML] (Angular)'],
];

// Pages HTML statiques (prérequis d'une CSP stricte).
const HTML = [
  [/<script(?![^>]*\bsrc=)[^>]*>/i, 'script écrit dans la page'],
  [/\son[a-z]+\s*=/i, "gestionnaire d'événement dans le HTML (onclick=…)"],
  [/\sstyle\s*=/i, 'attribut style'],
  [/<style\b/i, 'balise <style> (mettre le CSS dans un fichier)'],
  [/javascript:/i, 'lien javascript:'],
];

function regles(fichier) {
  if (/\.html?$/i.test(fichier)) return [...HTML, ...GABARITS];
  if (/\.(vue|svelte)$/i.test(fichier)) return [...JS, ...GABARITS, [/javascript:/i, 'lien javascript:']];
  return JS;
}

function sansCommentaires(texte) {
  return texte.replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '').replace(/<!--[\s\S]*?-->/g, '');
}

function lister(cible, ignores, liste = []) {
  const absolu = path.resolve(cible);
  if (ignores.has(absolu)) return liste;
  if (fs.statSync(absolu).isDirectory()) {
    for (const nom of fs.readdirSync(absolu)) {
      if (!DOSSIERS_EXCLUS.has(nom)) lister(path.join(absolu, nom), ignores, liste);
    }
  } else if (/\.(m?js|cjs|tsx?|jsx|vue|svelte|html?)$/i.test(absolu) && !/\.(min\.js|d\.ts)$/i.test(absolu)) {
    liste.push(absolu);
  }
  return liste;
}

function analyser(fichier) {
  const brut = fs.readFileSync(fichier, 'utf8');
  const contenu = sansCommentaires(brut);
  const defauts = regles(fichier).filter(([motif]) => motif.test(contenu)).map(([, nom]) => nom);
  if (/\.(html?|vue|svelte)$/i.test(fichier)) {
    // Champ secret : jamais envoyé à un correcteur en ligne, ni mémorisé, ni modifié.
    for (const balise of brut.match(/<input\b[^>]*>/gi) || []) {
      if (!/type=["']password["']|\sdata-secret\b/i.test(balise)) continue;
      if (!/\sspellcheck=["']false["']/i.test(balise)) defauts.push(`champ secret sans spellcheck="false" : ${balise}`);
      if (!/\sautocapitalize=["']off["']/i.test(balise)) defauts.push(`champ secret sans autocapitalize="off" : ${balise}`);
      if (!/\sautocomplete=["'](off|new-password|current-password)["']/i.test(balise)) defauts.push(`champ secret sans autocomplete adapté : ${balise}`);
    }
  }
  return defauts;
}

function principal(argv) {
  const cibles = [];
  const ignores = new Set();
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === '--ignorer') ignores.add(path.resolve(argv[(i += 1)]));
    else cibles.push(argv[i]);
  }
  if (!cibles.length) {
    console.error('Usage : node verifier-injection.js <dossier|fichier>... [--ignorer <chemin>]');
    return 2;
  }
  const fichiers = cibles.flatMap((c) => lister(c, ignores));
  let total = 0;
  for (const fichier of fichiers) {
    const defauts = analyser(fichier);
    total += defauts.length;
    for (const defaut of defauts) console.log(`✗ ${path.relative(process.cwd(), fichier)} : ${defaut}`);
  }
  console.log(`${fichiers.length} fichier(s) analysé(s), ${total} défaut(s).`);
  return total ? 1 : 0;
}

process.exitCode = principal(process.argv.slice(2));
