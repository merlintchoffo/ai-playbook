---
name: "audit-synthese-pptx"
description: "Produire les slides PowerPoint d'une synthèse managériale d'audit de conformité (score global, non-conformités, points sensibles, recommandations) à partir des résultats quantitatifs et des constats."
---

# Synthèse managériale d'audit de conformité (.pptx)

Produit des slides destinées à un comité de direction à partir des résultats d'un audit technique. L'auditeur fournit des chiffres et des constats bruts ; la slide doit être lisible en trente secondes par un lecteur non technique, sans perdre l'information.

**Charte et contrôles sont imposés. Structure et découpage sont proposés.** Cette distinction gouverne tout le reste : la palette, la formule du taux et les contrôles de cohérence ne se négocient pas d'un audit à l'autre, sinon les synthèses cessent d'être comparables ; le nombre de slides, les regroupements et les titres suivent le contenu réel.

## Entrée

L'une ou plusieurs de ces sources, rarement toutes à la fois :

- **Tableau de résultats quantitatifs** (capture d'écran de tableur ou texte) : une ligne par catégorie avec total de règles, conforme, non conforme, point sensible, non applicable, à vérifier, taux de conformité ; plus un TOTAL.
- **Répartition par qualification** : trois blocs — par impact architectural (critique / majeur / modéré / mineur), par complexité de remédiation (stratégique / chantier dédié / action ponctuelle / activité récurrente), par portée (transverse / environnement / composant / locale).
- **Liste des non-conformités** (NC-1, NC-2, …) et **liste des points sensibles** (PS-1, PS-2, …), en texte libre, souvent avec des références internes (`cf. NETWORK-04`, `cf. ARCH-03`) et des noms techniques.
- **Liste de recommandations** numérotées, non regroupées.

Les entrées sont partielles et évoluent entre deux échanges. Le périmètre change d'une version à l'autre : nombre de règles, noms de catégories, nombre d'écarts. Ne jamais réutiliser un chiffre d'un échange antérieur sans le revérifier contre la source la plus récente.

Ne rien inventer qui ne soit déductible de l'entrée. Ce qui manque est signalé dans la réponse, pas comblé en silence.

## Sortie

Un fichier `.pptx` par slide demandée, généré avec `pptxgenjs`, livré avec `SendUserFile`.

Une slide = un fichier, sauf demande explicite d'assemblage. Noms de fichiers explicites et stables : `score_global_conformite.pptx`, `non_conformites.pptx`, `points_sensibles.pptx`, `recommandations.pptx`.

Conserver le script de génération (`gen_<slide>.js`) dans le répertoire de travail : les mises à jour de chiffres sont fréquentes et se font par modification du script, jamais par édition du XML.

La réponse qui accompagne le fichier tient en quelques lignes : ce qui a été produit, les arbitrages de découpage ou de rédaction pris, et les incohérences détectées dans l'entrée. Pas de recap des étapes.

## Structure

### Imposée — identique sur toutes les slides

- Format `LAYOUT_WIDE` (13,33 × 7,5 pouces). Marge gauche et droite à 0,6 ; contenu sur 12,13 de large.
- **Eyebrow** : `AUDIT DE CONFORMITÉ · SYNTHÈSE MANAGÉRIALE`, Calibri 10 gras, ambre `E8A33D`, `charSpacing: 1.5`, en `x: 0.6, y: 0.28`.
- **Titre** : Cambria 30 gras, navy `1E2761`, en `y: 0.52`.
- **Sous-titre** : Calibri 11, gris `6E7688`, en `y: 1.02` — une ligne de cadrage chiffrée.
- **Notes du présentateur** sur chaque slide (`addNotes`), reprenant le message clé à l'oral. Elles doivent être mises à jour en même temps que les chiffres.

### Proposée — slide « Score global de conformité »

Quatre zones de haut en bas :

1. **Cartes KPI** en haut à droite : conformes (vert `0E9F6E` sur `EAF6F1`), non conformes (rouge `D64550` sur `FBECEE`), points sensibles (`C98518` sur `FDF3E3`), non applicables (`5F6B7A` sur `F1F2F5`). `x: 6.85 + i * 1.5, y: 0.36, w: 1.38, h: 0.84`, valeur 21pt gras centrée, libellé 9pt dessous.
2. **Bandeau du score global** : `x: 0.6, y: 1.44, w: 12.13, h: 0.94`, fond `F5F7FB`, bordure `E3E8F1`. Taux en 32pt gras navy, mention « de conformité globale » à côté, jauge de `x: 4.45` sur `w: 7.9` remplie à hauteur du taux, et sous la jauge la fraction en clair (« 30 règles conformes sur 47 règles applicables »).
3. **Colonne gauche — taux par catégorie** : libellé `x: 0.65, w: 2.3` ; piste `x: 3.05, w: 2.85` ; pourcentage aligné à droite en `x: 5.95` ; total de règles entre parenthèses en gris `x: 6.7`. Pas de titre de colonne, un en-tête de section en 11pt gras navy à `y: 2.58`.
4. **Colonne droite — qualification des écarts** : séparée par une ligne verticale à `x: 7.28`. Trois blocs titrés 10pt gras `4A5468`, libellé `x: 7.55`, piste `x: 9.3, w: 2.95` à l'échelle du total d'écarts, valeur `x: 12.33`.

Note de bas de page en 8,5pt gris italique à `y: 6.86`, rappelant la formule.

### Proposée — slides « Non-conformités » et « Points sensibles »

Une carte par constat, empilées : rectangle arrondi `x: 0.6, w: 12.13`, fond `F7F9FC`, bordure `E3E8F1`, `rectRadius: 0.08`.

Dans chaque carte : pastille ronde rouge numérotée (`x: 1.0, w: 0.4`, chiffre blanc 13,5pt gras centré), titre court 12,5pt gras navy (`x: 1.55, w: 2.5`), constats à puces 10pt (`x: 4.15, w: 8.3`).

Les hauteurs de carte se calent sur le contenu : environ 0,62 pour une puce courte, 0,8 pour deux, 1,0 à 1,2 pour trois. Espacement entre cartes de 0,16 à 0,22.

### Proposée — slide « Recommandations »

Tableau à six colonnes : chantier, actions recommandées, responsable, délai, priorité, effort. En-tête à fond navy, texte blanc 9,5pt gras. Lignes alternées blanc / `F7F9FC`, bordure `E3E8F1` à 0,75.

Priorité rendue par une pastille arrondie colorée : haute (`C0303C` sur `FBECEE`), moyenne (`B07714` sur `FDF3E3`), basse (`5F6B7A` sur `F1F2F5`).

Regrouper les recommandations en chantiers cohérents **sans perdre une seule action**. Une recommandation couvrant deux sujets distincts se scinde en deux puces plutôt que d'être résumée. Si aucun regroupement n'est défendable, garder une ligne par recommandation.

## Règles

### Calcul du taux — imposé

```
taux = (conformes + 0,5 × points sensibles) / règles applicables
règles applicables = total − non applicables
```

Les non applicables sont exclues du dénominateur, jamais comptées comme conformes. Le même calcul s'applique au taux global et à chaque catégorie.

La note de bas de page énonce la formule **sans introduire de variable comme `n`** : une lettre qui n'apparaît pas dans l'équation envoie le lecteur la chercher. Formulation retenue :

> Taux de conformité = (conformes + 0,5 × points sensibles) / règles applicables ; les N règles non applicables sont exclues du dénominateur. Le nombre entre parenthèses indique le total de règles évaluées dans la catégorie.

### Couleurs — imposé

| Rôle | Hex | Usage |
|---|---|---|
| Navy | `1E2761` | titres, valeurs chiffrées, en-tête de tableau |
| Rouge | `D64550` | non-conformités, taux < 60 %, pastilles numérotées |
| Ambre | `E8A33D` | eyebrow, jauge globale, taux 60–89 % |
| Orange | `E8901F` | pictogramme des points sensibles |
| Vert | `0E9F6E` | conformes, taux ≥ 90 % |
| Bleu | `3B6BD6` | complexité de remédiation |
| Texte | `2B3245` corps, `6E7688` secondaire, `9AA3B0` tertiaire |  |
| Surfaces | `F7F9FC` carte, `F5F7FB` bandeau, `EDEFF4` piste, `E3E8F1` bordure |  |

Seuils de couleur des taux : vert ≥ 90 %, ambre 60–89 %, rouge < 60 %. Ne pas les ajuster pour flatter un résultat.

### Pictogrammes — imposé

Croix rouge pour une non-conformité, triangle orange avec point d'exclamation pour un point sensible. **Toujours en vectoriel, jamais en émoji** : un caractère émoji rend en noir et blanc ou en carré vide selon le poste et le vidéoprojecteur.

```js
function cross(sl, cx, cy) {                       // non-conformité
  [45, -45].forEach((rot) => {
    sl.addShape(pres.ShapeType.roundRect, {
      x: cx - 0.095, y: cy - 0.027, w: 0.19, h: 0.054,
      rectRadius: 0.022, rotate: rot,
      fill: { color: "D64550" }, line: { color: "D64550" },
    });
  });
}

function warn(sl, cx, cy) {                        // point sensible
  sl.addShape(pres.ShapeType.triangle, {
    x: cx - 0.13, y: cy - 0.11, w: 0.26, h: 0.23,
    fill: { color: "E8901F" }, line: { color: "E8901F" },
  });
  sl.addText("!", {
    x: cx - 0.13, y: cy - 0.07, w: 0.26, h: 0.19, isTextBox: true, margin: 0,
    align: "center", valign: "middle",
    fontFace: "Calibri", fontSize: 10.5, bold: true, color: "FFFFFF",
  });
}
```

Le pictogramme est réservé à la **ligne d'impact** — la conséquence du constat, distincte du constat lui-même. Si l'entrée ne formule pas de conséquence, la carte n'a pas de ligne d'impact ; ne pas en inventer une.

### Rédaction — imposé

- Tri des catégories par taux **croissant** : le lecteur doit voir le problème en premier.
- Titres courts de carte inventés quand l'entrée n'en fournit pas, et signalés comme tels dans la réponse.
- Backticks, astérisques et autres marqueurs Markdown de l'entrée : retirés du texte de la slide.
- Les colonnes responsable / délai / priorité / effort sont **toujours présentes** mais leurs valeurs sont déduites, donc explicitement marquées comme proposées dans le sous-titre de la slide (« responsables, délais et charges à valider ») et dans la réponse.
- Jamais de comparaison de taux entre deux versions dont le périmètre a changé sans le dire : un passage de 79,5 % à 73,4 % combine souvent dégradation réelle et élargissement du référentiel.

### Technique pptxgenjs — imposé

- `pres.layout = "LAYOUT_WIDE"` **avant** le premier `addSlide()`.
- Couleurs hexadécimales sans `#` et sans canal alpha : `color: "D64550"`. Un `#` ou 8 chiffres corrompent le fichier.
- `isTextBox: true` et `margin: 0` sur chaque `addText` dont le texte doit s'aligner sur une forme.
- `rectRadius` ne fonctionne que sur `roundRect`.
- Ne jamais partager un objet d'options entre deux appels : `pptxgenjs` le modifie en place.
- **Un seul run par puce.** Mélanger plusieurs runs avec changement de police dans un même paragraphe à puce casse les puces et scinde les lignes. Conséquence : pas de chasse fixe sur les termes techniques dans un paragraphe à puce — le signaler et laisser l'utilisateur le faire dans PowerPoint s'il y tient.

```js
const runs = items.map((t, i) => ({
  text: t,
  options: {
    bullet: { indent: 13 },
    breakLine: i < items.length - 1,
    paraSpaceAfter: i < items.length - 1 ? 4 : 0,
  },
}));
```

## Procédure

1. **Relever les chiffres** de l'entrée et les recalculer. Ne pas repartir des valeurs d'un échange antérieur.
2. **Écrire le script de contrôle** (voir plus bas) et l'exécuter. Toute anomalie est levée auprès de l'utilisateur avant de générer quoi que ce soit.
3. **Écrire `gen_<slide>.js`** avec les données en tête de fichier, séparées de la mise en page.
4. **Générer et valider** :
   ```bash
   node gen_<slide>.js
   python /mnt/skills/public/pptx/scripts/office/validate.py <slide>.pptx
   ```
5. **Rendre et inspecter visuellement** — obligatoire, jamais sauté :
   ```bash
   python /mnt/skills/public/pptx/scripts/office/soffice.py --headless --convert-to pdf <slide>.pptx
   rm -f sl-*.jpg && pdftoppm -jpeg -r 150 <slide>.pdf sl
   ```
   Lire l'image produite. Vérifier en priorité : texte débordant d'une carte, chevauchement du pictogramme et du texte, colonne droite tronquée, puce manquante, valeur restée à l'ancienne version.
6. **Corriger dans le script**, jamais dans le XML, puis régénérer et réinspecter.
7. **Livrer** avec `SendUserFile` et signaler les arbitrages.

## Contrôles

Écrire ce script dans le répertoire de travail et l'exécuter avant chaque génération. Il a rattrapé deux erreurs réelles : un compteur KPI resté à l'ancienne valeur après mise à jour, et un total de répartition incohérent avec le nombre d'écarts.

```python
# check_coherence.py — adapter les valeurs aux données de l'audit en cours
TOTAL, CONF, NC, PS, NA = 49, 30, 8, 9, 2
CATS = [  # (nom, total_regles, taux_affiche)
    ("Contrôle d'accès", 3, 50.0),
]
IMPACT = {"critique": 0, "majeur": 5, "modéré": 8, "mineur": 4}
REMED  = {"stratégique": 1, "chantier": 3, "ponctuelle": 13, "récurrente": 0}
PORTEE = {"transverse": 3, "environnement": 6, "composant": 8, "locale": 0}

err = []
if CONF + NC + PS + NA != TOTAL:
    err.append(f"Somme des statuts {CONF+NC+PS+NA} != total {TOTAL}")

applicables = TOTAL - NA
taux = (CONF + 0.5 * PS) / applicables * 100
print(f"Taux global calculé : {taux:.1f} % sur {applicables} règles applicables")

ecarts = NC + PS
for nom, bloc in (("impact", IMPACT), ("remédiation", REMED), ("portée", PORTEE)):
    if sum(bloc.values()) != ecarts:
        err.append(f"Répartition par {nom} = {sum(bloc.values())}, attendu {ecarts} (NC+PS)")

if sum(c[1] for c in CATS) not in (TOTAL, 0):
    err.append(f"Somme des règles par catégorie {sum(c[1] for c in CATS)} != total {TOTAL}")

print("\n".join(err) if err else "Cohérence OK")
```

Avant de livrer, vérifier en plus, sur l'image rendue :

- Chaque compteur KPI correspond au tableau source.
- Le taux affiché est celui que le script a calculé, et la jauge est remplie à cette proportion.
- La fraction sous la jauge cite le bon nombre de règles applicables.
- Le titre de la section de droite annonce le bon nombre d'écarts, avec le détail NC · PS.
- L'échelle des barres de qualification est le total d'écarts, pas une valeur figée.
- Les notes du présentateur ne citent aucun chiffre périmé.

## Pièges

**Mise à jour partielle.** Changer un taux de catégorie modifie mécaniquement le taux global, les compteurs et parfois les répartitions. Quand l'utilisateur demande de ne changer qu'une valeur, appliquer sa consigne à la lettre puis signaler l'incohérence induite et proposer de la répercuter — ne pas corriger silencieusement.

**Même constat des deux côtés.** Un constat peut apparaître à la fois en NC et en PS si les référentiels diffèrent. Le signaler plutôt que d'arbitrer seul : la question sera posée en comité.

**Noms anonymisés.** Les entrées contiennent parfois `xxxxx_xxxx` ou des placeholders. Les conserver tels quels et rappeler qu'ils sont à remplacer avant diffusion.

**Constat trop maigre.** Un point sensible réduit à cinq mots produit une carte vide à côté des autres. Le signaler et demander le détail plutôt que de meubler.

**Recommandation à sujets multiples.** Une recommandation qui enchaîne deux actions de nature différente se scinde en deux puces. Si cela remet en cause le décompte des écarts affiché ailleurs, le dire.
