"use strict";

/**
 * Slide « Recommandations » : tableau de plan d'action.
 *
 * Structure PROPOSÉE : un chantier par ligne, actions à puces, puis
 * responsable, délai, priorité, effort.
 *
 * Les colonnes de pilotage sont TOUJOURS présentes — un plan d'action sans
 * responsable ni délai ne sert à rien en comité — mais leurs valeurs sont
 * déduites, donc signalées comme à valider dans le sous-titre et dans la
 * réponse à l'auditeur.
 *
 * Regrouper les recommandations SANS PERDRE UNE SEULE ACTION. Une
 * recommandation couvrant deux sujets distincts se scinde en deux puces
 * plutôt que d'être résumée.
 */

const Ch = require("../lib/charte");
const { C, FONT, PRIO } = Ch;

const COL = {
  dom: [0.78, 1.78],
  act: [2.72, 5.9],
  resp: [8.72, 1.35],
  del: [10.15, 0.9],
  prio: [11.12, 0.8],
  eff: [12.0, 0.73],
};
const FS = 9;

function hauteurLigne(chantier) {
  const lignes = chantier.actions.reduce(
    (n, t) => n + Math.max(1, Math.ceil(Ch.nettoyer(t).length / 96)), 0
  );
  return Math.max(0.52, 0.22 + lignes * 0.21);
}

function construire(pres, { chantiers, nbRecommandations }) {
  const s = pres.addSlide();
  const total = nbRecommandations
    || chantiers.reduce((n, c) => n + c.actions.length, 0);

  Ch.enTete(
    pres, s,
    "Recommandations",
    `${total} recommandations regroupées en ${chantiers.length} chantiers · ` +
    "responsables, délais et charges à valider"
  );

  const HY = 1.28, HH = 0.32;
  s.addShape(pres.ShapeType.rect, {
    x: 0.6, y: HY, w: 12.13, h: HH,
    fill: { color: C.NAVY }, line: { color: C.NAVY },
  });
  [
    ["Chantier", COL.dom], ["Actions recommandées", COL.act],
    ["Responsable", COL.resp], ["Délai", COL.del],
    ["Priorité", COL.prio], ["Effort", COL.eff],
  ].forEach(([lbl, col]) => {
    s.addText(lbl, {
      x: col[0], y: HY, w: col[1], h: HH, isTextBox: true, margin: 0,
      valign: "middle", fontFace: FONT.sans, fontSize: 9.5,
      bold: true, color: C.WHITE, charSpacing: 0.6,
    });
  });

  let ry = HY + HH;
  chantiers.forEach((ch, i) => {
    const h = hauteurLigne(ch);

    s.addShape(pres.ShapeType.rect, {
      x: 0.6, y: ry, w: 12.13, h,
      fill: { color: i % 2 ? C.CARD : C.WHITE },
      line: { color: C.BORDER, width: 0.75 },
    });
    s.addText(ch.nom, {
      x: COL.dom[0], y: ry + 0.05, w: COL.dom[1], h: h - 0.1,
      isTextBox: true, margin: 0, valign: "middle",
      fontFace: FONT.sans, fontSize: 10, bold: true,
      color: C.NAVY, lineSpacingMultiple: 0.95,
    });
    s.addText(Ch.puces(ch.actions, 3), {
      x: COL.act[0], y: ry + 0.08, w: COL.act[1], h: h - 0.16,
      isTextBox: true, margin: 0, valign: "middle",
      fontFace: FONT.sans, fontSize: FS, color: C.DARK, lineSpacingMultiple: 1.0,
    });
    s.addText(ch.responsable || "À désigner", {
      x: COL.resp[0], y: ry + 0.05, w: COL.resp[1], h: h - 0.1,
      isTextBox: true, margin: 0, valign: "middle",
      fontFace: FONT.sans, fontSize: FS, color: C.DARK, lineSpacingMultiple: 0.95,
    });
    s.addText(ch.delai || "—", {
      x: COL.del[0], y: ry + 0.05, w: COL.del[1], h: h - 0.1,
      isTextBox: true, margin: 0, valign: "middle",
      fontFace: FONT.sans, fontSize: FS, color: C.DARK,
    });

    const p = PRIO[ch.priorite] || PRIO.Moyenne;
    s.addShape(pres.ShapeType.roundRect, {
      x: COL.prio[0], y: ry + h / 2 - 0.115, w: 0.76, h: 0.23, rectRadius: 0.115,
      fill: { color: p.bg }, line: { color: p.bg },
    });
    s.addText(ch.priorite || "Moyenne", {
      x: COL.prio[0], y: ry + h / 2 - 0.115, w: 0.76, h: 0.23,
      isTextBox: true, margin: 0, align: "center", valign: "middle",
      fontFace: FONT.sans, fontSize: 8.5, bold: true, color: p.fg,
    });
    s.addText(ch.effort || "—", {
      x: COL.eff[0], y: ry + 0.05, w: COL.eff[1], h: h - 0.1,
      isTextBox: true, margin: 0, valign: "middle",
      fontFace: FONT.sans, fontSize: FS, color: C.DARK,
    });

    ry += h;
  });

  const hautes = chantiers.filter((c) => c.priorite === "Haute").map((c) => c.nom);
  s.addNotes(
    `Les ${total} recommandations sont regroupées en ${chantiers.length} chantiers, ` +
    "sans perte de contenu. " +
    (hautes.length ? `Priorité haute : ${hautes.join(", ")}. ` : "") +
    "Les responsables, délais et charges indiqués sont une proposition à arbitrer " +
    "avec les équipes."
  );

  return s;
}

module.exports = { construire };
