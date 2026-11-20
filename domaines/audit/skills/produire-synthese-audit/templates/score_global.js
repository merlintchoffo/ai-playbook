"use strict";

/**
 * Slide « Score global de conformité ».
 *
 * Structure PROPOSÉE : quatre zones (cartes KPI, bandeau du score,
 * taux par catégorie à gauche, qualification des écarts à droite).
 * Adapter librement au contenu réel ; la charte, elle, reste imposée.
 */

const Ch = require("../lib/charte");
const { C, FONT, KPI_TINT } = Ch;

function construire(pres, data) {
  const s = pres.addSlide();

  const cats = data.categories;
  const somme = (k) => cats.reduce((n, c) => n + (c[k] || 0), 0);
  const total = somme("total");
  const conf = somme("conformes");
  const nc = somme("non_conformes");
  const ps = somme("points_sensibles");
  const na = somme("non_applicables");
  const applicables = total - na;
  const ecarts = nc + ps;
  const tGlobal = Ch.taux(conf, ps, applicables);

  Ch.enTete(
    pres, s,
    "Score global de conformité",
    `${total} règles évaluées · ${cats.length} catégories · ${ecarts} écarts à traiter` +
      (data.qualification?.impact?.critique
        ? ` · ${data.qualification.impact.critique} écart(s) critique(s)`
        : " · aucun écart critique")
  );

  // --- Cartes KPI -------------------------------------------------------
  const kpis = [
    { v: conf, l: "Conformes", t: KPI_TINT.conformes },
    { v: nc, l: "Non conformes", t: KPI_TINT.nonConformes },
    { v: ps, l: "Points sensibles", t: KPI_TINT.pointsSensibles },
    { v: na, l: "Non applicables", t: KPI_TINT.nonApplicables },
  ];
  kpis.forEach((k, i) => {
    const x = 6.85 + i * 1.5;
    s.addShape(pres.ShapeType.roundRect, {
      x, y: 0.36, w: 1.38, h: 0.84, rectRadius: 0.08,
      fill: { color: k.t.bg }, line: { color: k.t.bg },
    });
    s.addText(String(k.v), {
      x, y: 0.42, w: 1.38, h: 0.38, isTextBox: true, margin: 0, align: "center",
      fontFace: FONT.sans, fontSize: 21, bold: true, color: k.t.fg,
    });
    s.addText(k.l, {
      x, y: 0.8, w: 1.38, h: 0.24, isTextBox: true, margin: 0, align: "center",
      fontFace: FONT.sans, fontSize: 9, color: "5F6B7A",
    });
  });

  // --- Bandeau du score global -----------------------------------------
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.6, y: 1.44, w: 12.13, h: 0.94, rectRadius: 0.1,
    fill: { color: C.BANNER }, line: { color: C.BORDER },
  });
  s.addText(Ch.pct(tGlobal), {
    x: 0.92, y: 1.58, w: 1.75, h: 0.66, isTextBox: true, margin: 0,
    fontFace: FONT.sans, fontSize: 32, bold: true, color: C.NAVY, valign: "middle",
  });
  s.addText("de conformité\nglobale", {
    x: 2.62, y: 1.58, w: 1.6, h: 0.66, isTextBox: true, margin: 0,
    fontFace: FONT.sans, fontSize: 11.5, color: "5F6B7A",
    valign: "middle", lineSpacingMultiple: 0.95,
  });
  const TX = 4.45, TW = 7.9;
  Ch.barre(pres, s, {
    x: TX, y: 1.76, w: TW, h: 0.3, ratio: tGlobal / 100,
    color: Ch.couleurTaux(tGlobal), radius: 0.15,
  });
  s.addText(`${conf} règles conformes sur ${applicables} règles applicables`, {
    x: TX, y: 2.06, w: TW, h: 0.24, isTextBox: true, margin: 0,
    fontFace: FONT.sans, fontSize: 9, color: C.MUTED,
  });

  // --- Titres de sections ----------------------------------------------
  s.addText("TAUX DE CONFORMITÉ PAR CATÉGORIE", {
    x: 0.65, y: 2.58, w: 6.4, h: 0.26, isTextBox: true, margin: 0,
    fontFace: FONT.sans, fontSize: 11, bold: true, color: C.NAVY, charSpacing: 1,
  });
  s.addText(`QUALIFICATION DES ${ecarts} ÉCARTS (${nc} NC · ${ps} PS)`, {
    x: 7.5, y: 2.58, w: 5.23, h: 0.26, isTextBox: true, margin: 0,
    fontFace: FONT.sans, fontSize: 11, bold: true, color: C.NAVY, charSpacing: 1,
  });
  s.addShape(pres.ShapeType.line, {
    x: 7.28, y: 2.62, w: 0, h: 4.05, line: { color: C.BORDER, width: 1 },
  });

  // --- Colonne gauche : tri par taux CROISSANT (imposé) -----------------
  const lignes = cats
    .map((c) => {
      const app = c.total - (c.non_applicables || 0);
      return { ...c, t: Ch.taux(c.conformes || 0, c.points_sensibles || 0, app) };
    })
    .sort((a, b) => a.t - b.t || a.nom.localeCompare(b.nom, "fr"));

  const LT = 3.05, LW = 2.85;
  const pas = lignes.length > 10 ? 3.6 / lignes.length : 0.36;
  lignes.forEach((c, i) => {
    const y = 2.96 + i * pas;
    s.addText(c.nom, {
      x: 0.65, y, w: 2.3, h: 0.28, isTextBox: true, margin: 0, valign: "middle",
      fontFace: FONT.sans, fontSize: 9.5, color: C.DARK,
    });
    Ch.barre(pres, s, {
      x: LT, y: y + 0.06, w: LW, h: 0.16,
      ratio: c.t / 100, color: Ch.couleurTaux(c.t), radius: 0.08,
    });
    s.addText(Ch.pct(c.t), {
      x: 5.95, y, w: 0.72, h: 0.28, isTextBox: true, margin: 0,
      valign: "middle", align: "right",
      fontFace: FONT.sans, fontSize: 9.5, bold: true, color: C.NAVY,
    });
    s.addText(`(${c.total})`, {
      x: 6.7, y, w: 0.42, h: 0.28, isTextBox: true, margin: 0, valign: "middle",
      fontFace: FONT.sans, fontSize: 8.5, color: C.GRAY,
    });
  });

  // --- Colonne droite : qualification -----------------------------------
  const q = data.qualification || {};
  const blocs = [
    {
      titre: "Par impact architectural",
      lignes: [
        ["Critique", q.impact?.critique || 0, C.RED],
        ["Majeur", q.impact?.majeur || 0, C.AMBER],
        ["Modéré", q.impact?.modere || 0, C.AMBER_SOFT],
        ["Mineur", q.impact?.mineur || 0, C.GREEN],
      ],
    },
    {
      titre: "Par complexité de remédiation",
      lignes: [
        ["Stratégique", q.remediation?.strategique || 0, C.NAVY],
        ["Chantier dédié", q.remediation?.chantier_dedie || 0, C.BLUE],
        ["Action ponctuelle", q.remediation?.action_ponctuelle || 0, C.BLUE],
        ["Activité récurrente", q.remediation?.activite_recurrente || 0, C.BLUE_SOFT],
      ],
    },
    {
      titre: "Par portée",
      lignes: [
        ["Transverse", q.portee?.transverse || 0, C.RED],
        ["Environnement", q.portee?.environnement || 0, C.AMBER],
        ["Composant", q.portee?.composant || 0, C.AMBER_SOFT],
        ["Locale", q.portee?.locale || 0, C.GREEN],
      ],
    },
  ];

  const MAXV = Math.max(ecarts, 1);
  const RT = 9.3, RW = 2.95;
  let by = 2.95;
  blocs.forEach((b) => {
    s.addText(b.titre, {
      x: 7.5, y: by, w: 5.2, h: 0.24, isTextBox: true, margin: 0, valign: "middle",
      fontFace: FONT.sans, fontSize: 10, bold: true, color: "4A5468",
    });
    b.lignes.forEach(([lbl, v, col], j) => {
      const y = by + 0.26 + j * 0.24;
      s.addText(lbl, {
        x: 7.55, y, w: 1.6, h: 0.22, isTextBox: true, margin: 0, valign: "middle",
        fontFace: FONT.sans, fontSize: 9, color: C.DARK,
      });
      Ch.barre(pres, s, {
        x: RT, y: y + 0.045, w: RW, h: 0.13,
        ratio: v / MAXV, color: col, radius: 0.065,
      });
      s.addText(String(v), {
        x: 12.33, y, w: 0.4, h: 0.22, isTextBox: true, margin: 0, valign: "middle",
        fontFace: FONT.sans, fontSize: 9.5, bold: v > 0,
        color: v > 0 ? C.NAVY : C.GRAY,
      });
    });
    by += 0.26 + 4 * 0.24 + 0.2;
  });

  Ch.noteFormule(s, na);

  const pires = lignes.slice(0, 3)
    .map((c) => `${c.nom} (${Ch.pct(c.t, 0)})`).join(", ");
  s.addNotes(
    `Synthèse : ${Ch.pct(tGlobal)} de conformité globale sur ${applicables} règles ` +
    `applicables (${conf} conformes, ${nc} non conformes, ${ps} points sensibles, ` +
    `${na} non applicables). Les écarts se concentrent sur ${pires}. ` +
    `${ecarts} écarts à qualifier au total.`
  );

  return s;
}

module.exports = { construire };
