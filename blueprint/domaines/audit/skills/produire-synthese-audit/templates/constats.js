"use strict";

/**
 * Slides « Non-conformités » et « Points sensibles » — même modèle de carte,
 * seul le pictogramme de la ligne d'impact change.
 *
 * Structure PROPOSÉE : une carte par constat, titre court à gauche,
 * constats à puces à droite, ligne d'impact signalée par un pictogramme.
 *
 * Le pictogramme est réservé à la CONSÉQUENCE du constat. Si l'entrée ne
 * formule pas de conséquence, la carte n'a pas de ligne d'impact : ne pas
 * en inventer une.
 */

const Ch = require("../lib/charte");
const { C, FONT } = Ch;

const FS = 10;          // corps des constats
const TITRE = 12.5;     // titre court de carte
const LIGNE = 0.19;     // hauteur d'une ligne de texte à 10 pt
const PAD = 0.16;       // marge haute et basse dans la carte
const AVANT_IMPACT = 0.07;
const HAUT_MIN = 0.62;

const X_TEXTE = 4.15;   // colonne des constats
const X_PICTO = 4.15;   // centre du pictogramme, dans la gouttière
const X_IMPACT = 4.34;  // texte de la ligne d'impact
const W_TEXTE = 8.3;
const W_TITRE = 2.4;    // s'arrête à 3,95 : ne touche pas le pictogramme

/** Nombre de lignes rendues, estimé d'après la longueur du texte. */
function nbLignes(texte, parLigne) {
  return Math.max(1, Math.ceil(Ch.nettoyer(texte).length / parLigne));
}

/** Géométrie d'une carte, déduite de son contenu. */
function mesurer(carte) {
  const lignesPuces = carte.constats.reduce((n, t) => n + nbLignes(t, 118), 0);
  const lignesTitre = Math.ceil(carte.titre.length / 26);
  const lignesImpact = carte.impact ? nbLignes(carte.impact, 112) : 0;

  const dyImpact = PAD + lignesPuces * LIGNE + AVANT_IMPACT;
  const hTexte = carte.impact
    ? dyImpact + lignesImpact * LIGNE + PAD
    : PAD + lignesPuces * LIGNE + PAD;

  return {
    h: Math.max(HAUT_MIN, hTexte, lignesTitre * 0.26 + 0.2),
    dyImpact,
    lignesPuces,
    centre: !carte.impact,
  };
}

function construire(pres, { type, titre, sousTitre, cartes }) {
  const estNC = type === "nc";
  const picto = estNC ? Ch.croix : Ch.alerte;
  const s = pres.addSlide();

  Ch.enTete(pres, s, titre, sousTitre);

  const mesures = cartes.map(mesurer);
  const totalH = mesures.reduce((a, m) => a + m.h, 0);
  const dispo = 6.95 - 1.36;
  const gap = cartes.length > 1
    ? Math.min(0.22, Math.max(0.05, (dispo - totalH) / (cartes.length - 1)))
    : 0;

  if (totalH + gap * (cartes.length - 1) > dispo + 0.01) {
    console.warn(
      `  ATTENTION  « ${titre} » : ${cartes.length} cartes pour ${dispo.toFixed(2)}" ` +
      "disponibles — raccourcir les constats ou scinder la slide."
    );
  }

  let cy = 1.36;
  cartes.forEach((carte, idx) => {
    const m = mesures[idx];

    s.addShape(pres.ShapeType.roundRect, {
      x: 0.6, y: cy, w: 12.13, h: m.h, rectRadius: 0.08,
      fill: { color: C.CARD }, line: { color: C.BORDER },
    });

    Ch.pastille(pres, s, { x: 1.0, y: cy + (m.h - 0.4) / 2, numero: idx + 1 });

    s.addText(carte.titre, {
      x: 1.55, y: cy + 0.06, w: W_TITRE, h: m.h - 0.12,
      isTextBox: true, margin: 0, valign: "middle",
      fontFace: FONT.sans, fontSize: TITRE, bold: true,
      color: C.NAVY, lineSpacingMultiple: 0.95,
    });

    // Sans ligne d'impact, le bloc de puces est centré dans la carte ;
    // avec, il part du haut pour que l'impact tombe juste en dessous.
    const yTexte = m.centre
      ? cy + (m.h - m.lignesPuces * LIGNE) / 2
      : cy + PAD;

    s.addText(Ch.puces(carte.constats), {
      x: X_TEXTE, y: yTexte, w: W_TEXTE, h: m.lignesPuces * LIGNE + 0.1,
      isTextBox: true, margin: 0, valign: "top",
      fontFace: FONT.sans, fontSize: FS, color: C.DARK, lineSpacingMultiple: 1.02,
    });

    if (carte.impact) {
      picto(pres, s, X_PICTO, cy + m.dyImpact + 0.1);
      s.addText(Ch.nettoyer(carte.impact), {
        x: X_IMPACT, y: cy + m.dyImpact, w: 12.45 - X_IMPACT, h: 0.5,
        isTextBox: true, margin: 0, valign: "top",
        fontFace: FONT.sans, fontSize: FS, color: C.DARK, lineSpacingMultiple: 1.02,
      });
    }

    cy += m.h + gap;
  });

  const resume = cartes
    .map((c, i) => `${i + 1}) ${c.titre} : ${Ch.nettoyer(c.constats[0])}`)
    .join(". ");
  s.addNotes(`${cartes.length} ${estNC ? "non-conformités" : "points sensibles"}. ${resume}.`);

  return s;
}

module.exports = { construire };
