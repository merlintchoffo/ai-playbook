#!/usr/bin/env node
"use strict";

/**
 * Génère les slides de la synthèse managériale à partir d'un fichier de données.
 *
 *   node build.js audit.json [dossier_sortie]
 *
 * Une slide = un fichier .pptx, sauf --assemble qui produit un seul deck.
 * Les slides absentes du fichier de données sont simplement ignorées.
 */

const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const scoreGlobal = require("./templates/score_global");
const constats = require("./templates/constats");
const recommandations = require("./templates/recommandations");

function nouveauDeck() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // avant tout addSlide()
  return pres;
}

async function main() {
  const args = process.argv.slice(2).filter((a) => a !== "--assemble");
  const assemble = process.argv.includes("--assemble");

  if (!args[0]) {
    console.error("Usage : node build.js audit.json [dossier_sortie] [--assemble]");
    process.exit(2);
  }

  const data = JSON.parse(fs.readFileSync(args[0], "utf8"));
  const out = args[1] || "sortie";
  fs.mkdirSync(out, { recursive: true });

  const deckUnique = assemble ? nouveauDeck() : null;
  const ecrits = [];

  const slides = [
    {
      nom: "score_global",
      actif: Array.isArray(data.categories) && data.categories.length > 0,
      build: (pres) => scoreGlobal.construire(pres, data),
    },
    {
      nom: "non_conformites",
      actif: Array.isArray(data.non_conformites) && data.non_conformites.length > 0,
      build: (pres) => constats.construire(pres, {
        type: "nc",
        titre: "Non-conformités",
        sousTitre: `${data.non_conformites.length} écarts constatés · correction requise`,
        cartes: data.non_conformites,
      }),
    },
    {
      nom: "points_sensibles",
      actif: Array.isArray(data.points_sensibles_detail)
        && data.points_sensibles_detail.length > 0,
      build: (pres) => constats.construire(pres, {
        type: "ps",
        titre: "Points sensibles",
        sousTitre: `${data.points_sensibles_detail.length} constats à traiter en priorité`,
        cartes: data.points_sensibles_detail,
      }),
    },
    {
      nom: "recommandations",
      actif: Array.isArray(data.chantiers) && data.chantiers.length > 0,
      build: (pres) => recommandations.construire(pres, {
        chantiers: data.chantiers,
        nbRecommandations: data.nb_recommandations,
      }),
    },
  ];

  for (const slide of slides) {
    if (!slide.actif) {
      console.log(`  ignorée   ${slide.nom} (pas de données)`);
      continue;
    }
    if (assemble) {
      slide.build(deckUnique);
      console.log(`  ajoutée   ${slide.nom}`);
    } else {
      const pres = nouveauDeck();
      slide.build(pres);
      const fichier = path.join(out, `${slide.nom}.pptx`);
      await pres.writeFile({ fileName: fichier });
      ecrits.push(fichier);
      console.log(`  écrite    ${fichier}`);
    }
  }

  if (assemble) {
    const fichier = path.join(out, "synthese_manageriale.pptx");
    await deckUnique.writeFile({ fileName: fichier });
    ecrits.push(fichier);
    console.log(`  écrite    ${fichier}`);
  }

  if (!ecrits.length) {
    console.error("\nAucune slide produite : le fichier de données est vide.");
    process.exit(1);
  }

  console.log("\nÉtapes suivantes, dans cet ordre :");
  console.log(`  python3 scripts/validate_pptx.py ${ecrits.join(" ")}`);
  ecrits.forEach((f) => console.log(`  scripts/render_preview.sh ${f}`));
  console.log("  puis ouvrir chaque aperçu — la validation XML ne voit pas un");
  console.log("  débordement de texte ni un chiffre resté à l'ancienne valeur.");
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
