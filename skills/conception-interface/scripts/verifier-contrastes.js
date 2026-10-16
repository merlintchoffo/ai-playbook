#!/usr/bin/env node
// Contrastes WCAG 2.2 (niveau AA) des couleurs d'un thème. Node seul, sans dépendance.
// Code de sortie 1 si une paire est sous son seuil.
//
// Usage :
//   node verifier-contrastes.js <fichier.css|.scss|.less> [--paires paires.json]
//   node verifier-contrastes.js --couleurs theme.json [--couleurs sombre.json] [--paires paires.json]
//
// Sources de couleurs :
//   - CSS : chaque bloc qui définit --fond (un par thème : :root, .theme-sombre…) ;
//     les variables de :root sont héritées ; var(--x) est résolu.
//   - SCSS / LESS : les variables $nom / @nom du fichier forment un thème.
//   - JSON (--couleurs) : un thème par fichier, objets imbriqués aplatis
//     ({ "blue": { "500": "#3b82f6" } } → "blue-500" ; clé DEFAULT → nom du parent).
//     Pour Tailwind : exporter theme.colors de la config résolue dans un JSON.
// Couleurs lues : #rgb, #rrggbb, rgb()/rgba() et hsl()/hsla() opaques. Les autres
// (transparence, color-mix…) sont signalées « non lues », jamais comptées réussies.
//
// Paires : par défaut celles de assets/css-de-base.css (encre, fond, doux, action…).
// paires.json : [["text", "background", 4.5, "texte courant"], ["border", "background", 3, "bordure des champs"]]
'use strict';

const fs = require('node:fs');
const path = require('node:path');

const PAIRES_PAR_DEFAUT = [
  ['encre', 'fond', 4.5, 'texte courant'],
  ['encre', 'fond-2', 4.5, 'texte des panneaux'],
  ['doux', 'fond', 4.5, 'texte secondaire'],
  ['doux', 'fond-2', 4.5, 'texte secondaire des panneaux'],
  ['action', 'fond', 4.5, 'liens'],
  ['action-encre', 'action', 4.5, 'texte des boutons principaux'],
  ['danger', 'fond', 4.5, 'erreurs'],
  ['danger', 'danger-fond', 4.5, 'messages de danger'],
  ['attention-encre', 'attention-fond', 4.5, "messages d'attention"],
  ['reussite', 'fond', 4.5, 'réussite'],
  ['champ-bordure', 'fond', 3, 'bordure des champs (côté page)'],
  ['champ-bordure', 'champ', 3, 'bordure des champs (côté champ)'],
  ['action', 'fond', 3, 'contour de focus'],
];

// ---------- Lecture des thèmes ----------

function themesCss(css) {
  const texte = css.replace(/\/\*[\s\S]*?\*\//g, '');
  const blocs = [];
  for (const m of texte.matchAll(/([^{}]+)\{([^{}]*)\}/g)) {
    const variables = {};
    for (const v of m[2].matchAll(/--([\w-]+)\s*:\s*([^;]+);/g)) variables[v[1]] = v[2].trim();
    if (Object.keys(variables).length) blocs.push({ nom: m[1].trim().replace(/\s+/g, ' '), variables });
  }
  const racine = Object.assign({}, ...blocs.filter((b) => b.nom.split(',').map((s) => s.trim()).includes(':root')).map((b) => b.variables));
  return blocs.filter((b) => 'fond' in b.variables).map((b) => ({ nom: b.nom, variables: { ...racine, ...b.variables } }));
}

function themePreprocesseur(texte, nom) {
  const variables = {};
  for (const v of texte.replace(/\/\*[\s\S]*?\*\//g, '').matchAll(/^\s*[$@]([\w-]+)\s*:\s*([^;]+);/gm)) {
    variables[v[1]] = v[2].replace(/!default|!important/g, '').trim();
  }
  return { nom, variables };
}

function aplatir(objet, prefixe = '', resultat = {}) {
  for (const [cle, valeur] of Object.entries(objet)) {
    const nom = cle === 'DEFAULT' ? prefixe : prefixe ? `${prefixe}-${cle}` : cle;
    if (valeur && typeof valeur === 'object') aplatir(valeur, nom, resultat);
    else resultat[nom] = String(valeur);
  }
  return resultat;
}

// ---------- Couleurs ----------

function resoudre(valeur, variables, profondeur = 0) {
  const m = /^var\(\s*--([\w-]+)\s*(?:,\s*(.+))?\)$/.exec(valeur || '');
  if (!m || profondeur > 10) return valeur;
  return resoudre(variables[m[1]] ?? m[2], variables, profondeur + 1);
}

function rgb(valeur) {
  const v = (valeur || '').trim().toLowerCase();
  let m = /^#([0-9a-f]{3}|[0-9a-f]{6})$/.exec(v);
  if (m) {
    const hex = m[1].length === 3 ? m[1].replace(/./g, (c) => c + c) : m[1];
    return [0, 2, 4].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255);
  }
  const nombres = (s) => s.split(/[\s,/]+/).filter(Boolean);
  m = /^rgba?\(([^)]+)\)$/.exec(v);
  if (m) {
    const [r, g, b, a] = nombres(m[1]);
    if (a !== undefined && parseFloat(a) < (a.endsWith('%') ? 100 : 1)) return null;
    return [r, g, b].map((c) => (c.endsWith('%') ? parseFloat(c) / 100 : parseFloat(c) / 255));
  }
  m = /^hsla?\(([^)]+)\)$/.exec(v);
  if (m) {
    const [h, s, l, a] = nombres(m[1]);
    if (a !== undefined && parseFloat(a) < (a.endsWith('%') ? 100 : 1)) return null;
    const [H, S, L] = [parseFloat(h), parseFloat(s) / 100, parseFloat(l) / 100];
    const k = (n) => (n + H / 30) % 12;
    const x = S * Math.min(L, 1 - L);
    return [0, 8, 4].map((n) => L - x * Math.max(-1, Math.min(k(n) - 3, 9 - k(n), 1)));
  }
  return null;
}

function luminance(canaux) {
  const [r, g, b] = canaux.map((c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function contraste(a, b) {
  const [clair, sombre] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (clair + 0.05) / (sombre + 0.05);
}

// ---------- Principal ----------

function principal(argv) {
  const themes = [];
  let paires = PAIRES_PAR_DEFAUT;
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === '--paires') paires = JSON.parse(fs.readFileSync(argv[(i += 1)], 'utf8'));
    else if (argv[i] === '--couleurs') {
      const fichier = argv[(i += 1)];
      themes.push({ nom: path.basename(fichier), variables: aplatir(JSON.parse(fs.readFileSync(fichier, 'utf8'))) });
    } else {
      const texte = fs.readFileSync(argv[i], 'utf8');
      if (/\.(scss|sass|less)$/i.test(argv[i])) themes.push(themePreprocesseur(texte, path.basename(argv[i])));
      themes.push(...themesCss(texte));
    }
  }
  if (!themes.length) {
    console.error('Usage : node verifier-contrastes.js <fichier.css|.scss|.less> | --couleurs theme.json [--paires paires.json]');
    console.error('(un fichier CSS doit définir --fond dans au moins un bloc ; sinon, décrire les paires avec --paires)');
    return 2;
  }
  let echecs = 0;
  let nonVerifiees = 0;
  for (const theme of themes) {
    console.log(`\n${theme.nom}`);
    for (const [texte, fond, seuil, usage] of paires) {
      const valeurs = [texte, fond].map((n) => resoudre(theme.variables[n], theme.variables));
      const [a, b] = valeurs.map(rgb);
      if (!a || !b) {
        nonVerifiees += 1;
        const raison = valeurs.some((v) => v === undefined) ? 'variable absente' : 'couleur non lue';
        console.log(`  ? ${usage} (${texte} sur ${fond}) : non vérifiée (${raison})`);
        continue;
      }
      const ratio = contraste(a, b);
      if (ratio < seuil) echecs += 1;
      console.log(`  ${ratio >= seuil ? '✓' : '✗'} ${usage} (${texte} sur ${fond}) : ${ratio.toFixed(2)}:1, seuil ${seuil}:1`);
    }
  }
  console.log(`\n${echecs} paire(s) sous le seuil, ${nonVerifiees} non vérifiée(s).`);
  return echecs ? 1 : 0;
}

process.exitCode = principal(process.argv.slice(2));
