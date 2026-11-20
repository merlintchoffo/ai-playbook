"use strict";

/**
 * Charte graphique de la synthèse managériale d'audit de conformité.
 *
 * Cette partie est IMPOSÉE : elle garantit qu'un audit à l'autre les slides
 * restent comparables. Ne pas modifier les couleurs, les seuils ni la formule
 * sans décision explicite — un seuil ajusté fausse la comparaison d'un audit
 * au suivant.
 */

const C = {
  NAVY: "1E2761",
  DARK: "2B3245",
  MUTED: "6E7688",
  GRAY: "9AA3B0",
  RED: "D64550",
  AMBER: "E8A33D",
  ORANGE: "E8901F",
  GREEN: "0E9F6E",
  BLUE: "3B6BD6",
  AMBER_SOFT: "F0C46A",
  BLUE_SOFT: "8AA9EA",
  TRACK: "EDEFF4",
  CARD: "F7F9FC",
  BANNER: "F5F7FB",
  BORDER: "E3E8F1",
  WHITE: "FFFFFF",
};

const KPI_TINT = {
  conformes: { fg: C.GREEN, bg: "EAF6F1" },
  nonConformes: { fg: C.RED, bg: "FBECEE" },
  pointsSensibles: { fg: "C98518", bg: "FDF3E3" },
  nonApplicables: { fg: "5F6B7A", bg: "F1F2F5" },
};

const PRIO = {
  Haute: { bg: "FBECEE", fg: "C0303C" },
  Moyenne: { bg: "FDF3E3", fg: "B07714" },
  Basse: { bg: "F1F2F5", fg: "5F6B7A" },
};

const FONT = { sans: "Calibri", serif: "Cambria" };

/** Grille commune — LAYOUT_WIDE 13,33 x 7,5 pouces. */
const GRID = {
  W: 13.33,
  H: 7.5,
  MARGIN: 0.6,
  CONTENT_W: 12.13,
  EYEBROW_Y: 0.28,
  TITLE_Y: 0.52,
  SUBTITLE_Y: 1.02,
};

const EYEBROW = "AUDIT DE CONFORMITÉ · SYNTHÈSE MANAGÉRIALE";

/**
 * Formule imposée. Les non applicables sont exclues du dénominateur,
 * jamais comptées comme conformes.
 */
function taux(conformes, pointsSensibles, applicables) {
  if (!applicables) return 0;
  return ((conformes + 0.5 * pointsSensibles) / applicables) * 100;
}

/** Seuils imposés : vert >= 90, ambre 60-89, rouge < 60. */
function couleurTaux(t) {
  return t >= 90 ? C.GREEN : t >= 60 ? C.AMBER : C.RED;
}

/** Format français : 73,4 % */
function pct(t, decimales = 1) {
  return t.toFixed(decimales).replace(".", ",") + " %";
}

/** En-tête commun à toutes les slides. */
function enTete(pres, slide, titre, sousTitre) {
  slide.background = { color: C.WHITE };
  slide.addText(EYEBROW, {
    x: GRID.MARGIN, y: GRID.EYEBROW_Y, w: 7.0, h: 0.25,
    isTextBox: true, margin: 0,
    fontFace: FONT.sans, fontSize: 10, bold: true,
    color: C.AMBER, charSpacing: 1.5,
  });
  slide.addText(titre, {
    x: GRID.MARGIN, y: GRID.TITLE_Y, w: 7.0, h: 0.5,
    isTextBox: true, margin: 0,
    fontFace: FONT.serif, fontSize: 30, bold: true, color: C.NAVY,
  });
  if (sousTitre) {
    slide.addText(sousTitre, {
      x: GRID.MARGIN, y: GRID.SUBTITLE_Y, w: 8.5, h: 0.26,
      isTextBox: true, margin: 0,
      fontFace: FONT.sans, fontSize: 11, color: C.MUTED,
    });
  }
}

/**
 * Pictogramme de non-conformité : croix rouge vectorielle.
 * Jamais d'émoji — un caractère émoji rend en noir et blanc ou en carré
 * vide selon le poste et le vidéoprojecteur.
 */
function croix(pres, slide, cx, cy) {
  [45, -45].forEach((rotate) => {
    slide.addShape(pres.ShapeType.roundRect, {
      x: cx - 0.095, y: cy - 0.027, w: 0.19, h: 0.054,
      rectRadius: 0.022, rotate,
      fill: { color: C.RED }, line: { color: C.RED },
    });
  });
}

/** Pictogramme de point sensible : triangle orange avec point d'exclamation. */
function alerte(pres, slide, cx, cy) {
  slide.addShape(pres.ShapeType.triangle, {
    x: cx - 0.13, y: cy - 0.11, w: 0.26, h: 0.23,
    fill: { color: C.ORANGE }, line: { color: C.ORANGE },
  });
  slide.addText("!", {
    x: cx - 0.13, y: cy - 0.07, w: 0.26, h: 0.19,
    isTextBox: true, margin: 0, align: "center", valign: "middle",
    fontFace: FONT.sans, fontSize: 10.5, bold: true, color: C.WHITE,
  });
}

/**
 * Construit les runs d'une liste à puces.
 *
 * UN SEUL RUN PAR PUCE. Mélanger plusieurs runs avec changement de police
 * dans un même paragraphe à puce casse les puces et scinde les lignes.
 * Conséquence assumée : pas de chasse fixe sur les termes techniques.
 */
function puces(items, espaceApres = 4) {
  return items.map((texte, i) => ({
    text: nettoyer(texte),
    options: {
      bullet: { indent: 13 },
      breakLine: i < items.length - 1,
      paraSpaceAfter: i < items.length - 1 ? espaceApres : 0,
    },
  }));
}

/** Retire les marqueurs Markdown que l'entrée traîne souvent. */
function nettoyer(texte) {
  return String(texte)
    .replace(/`/g, "")
    .replace(/\*\*/g, "")
    .replace(/^\s*[-*]\s+/, "")
    .trim();
}

/** Barre de progression : piste grise + remplissage coloré. */
function barre(pres, slide, { x, y, w, h, ratio, color, radius }) {
  const r = radius != null ? radius : h / 2;
  slide.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, rectRadius: r,
    fill: { color: C.TRACK }, line: { color: C.TRACK },
  });
  if (ratio > 0) {
    slide.addShape(pres.ShapeType.roundRect, {
      x, y, w: Math.max(w * ratio, h * 0.75), h, rectRadius: r,
      fill: { color }, line: { color },
    });
  }
}

/** Pastille ronde numérotée (rouge) des slides de constats. */
function pastille(pres, slide, { x, y, d = 0.4, numero }) {
  slide.addShape(pres.ShapeType.ellipse, {
    x, y, w: d, h: d,
    fill: { color: C.RED }, line: { color: C.RED },
  });
  slide.addText(String(numero), {
    x, y, w: d, h: d, isTextBox: true, margin: 0,
    align: "center", valign: "middle",
    fontFace: FONT.sans, fontSize: 13.5, bold: true, color: C.WHITE,
  });
}

/** Note de bas de page rappelant la formule. Pas de variable `n`. */
function noteFormule(slide, nonApplicables) {
  const na = nonApplicables === 1
    ? "la règle non applicable est exclue"
    : `les ${nonApplicables} règles non applicables sont exclues`;
  slide.addText(
    "Taux de conformité = (conformes + 0,5 × points sensibles) / règles applicables ; " +
    `${na} du dénominateur. Le nombre entre parenthèses indique le total de règles ` +
    "évaluées dans la catégorie.",
    {
      x: 0.65, y: 6.86, w: 12.05, h: 0.3, isTextBox: true, margin: 0,
      fontFace: FONT.sans, fontSize: 8.5, color: C.GRAY, italic: true,
    }
  );
}

module.exports = {
  C, KPI_TINT, PRIO, FONT, GRID, EYEBROW,
  taux, couleurTaux, pct,
  enTete, croix, alerte, puces, nettoyer, barre, pastille, noteFormule,
};
