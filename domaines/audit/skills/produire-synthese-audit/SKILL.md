---
name: produire-synthese-audit
description: Produire les slides PowerPoint d'une synthèse managériale d'audit de conformité (score global, non-conformités, points sensibles, recommandations) à partir des résultats quantitatifs et des constats. Utiliser quand l'utilisateur fournit les résultats d'un audit et demande les slides de synthèse.
---

## Entrée

- Les **résultats d'un audit de conformité** : tableau quantitatif, répartitions, non-conformités, points sensibles, recommandations (souvent partiels).

## Sortie

- Un **fichier `.pptx` par slide** (ou un deck avec `--assemble`), généré depuis un fichier de données JSON conservé.
- Quelques lignes sur les **arbitrages** pris et les **incohérences** détectées dans l'entrée.

---


# Synthèse managériale d'audit de conformité (.pptx)

Produit des slides destinées à un comité de direction à partir des résultats d'un audit technique. L'auditeur fournit des chiffres et des constats bruts ; la slide doit être lisible en trente secondes par un lecteur non technique, sans perdre l'information.

**Charte et contrôles sont imposés. Structure et découpage sont proposés.** Cette distinction gouverne tout le reste : la palette, la formule du taux et les contrôles de cohérence ne se négocient pas d'un audit à l'autre, sinon les synthèses cessent d'être comparables ; le nombre de slides, les regroupements et les titres suivent le contenu réel.

Ce dossier est autonome : il n'appelle aucun outil propre à un environnement particulier. `lib/`, `templates/` et `scripts/` sont à côté de ce fichier.

## Sources acceptées

L'une ou plusieurs de ces sources, rarement toutes à la fois :

- **Tableau de résultats quantitatifs** (capture d'écran de tableur ou texte) : une ligne par catégorie avec total de règles, conforme, non conforme, point sensible, non applicable, à vérifier, taux de conformité ; plus un TOTAL.
- **Répartition par qualification** : trois blocs — par impact architectural (critique / majeur / modéré / mineur), par complexité de remédiation (stratégique / chantier dédié / action ponctuelle / activité récurrente), par portée (transverse / environnement / composant / locale).
- **Liste des non-conformités** (NC-1, NC-2, …) et **liste des points sensibles** (PS-1, PS-2, …), en texte libre, souvent avec des références internes (`cf. NETWORK-04`) et des noms techniques.
- **Liste de recommandations** numérotées, non regroupées.

Les entrées sont partielles et évoluent entre deux échanges. Le périmètre change d'une version à l'autre : nombre de règles, noms de catégories, nombre d'écarts. Ne jamais réutiliser un chiffre d'un échange antérieur sans le revérifier contre la source la plus récente.

Ne rien inventer qui ne soit déductible de l'entrée. Ce qui manque est signalé, pas comblé en silence.

**Consolider l'entrée dans un fichier de données** au format de `exemples/audit-exemple.json` : une seule source de vérité, sur laquelle portent les contrôles et dont découlent toutes les slides. Si la structure de l'audit ne s'y prête pas, écrire un script de génération dédié qui importe `lib/charte.js` — la charte reste la même.

## Livrables

Un fichier `.pptx` par slide, écrit dans le dossier de sortie passé en argument. `--assemble` produit un deck unique à la place.

Noms de fichiers stables : `score_global.pptx`, `non_conformites.pptx`, `points_sensibles.pptx`, `recommandations.pptx`.

Conserver le fichier de données et les scripts : les mises à jour de chiffres sont fréquentes et se font en modifiant le JSON, jamais en éditant le `.pptx`.

Dire en quelques lignes ce qui a été produit, les arbitrages de découpage ou de rédaction pris, et les incohérences détectées dans l'entrée. Pas de recap des étapes.

## Structure

### Imposée — identique sur toutes les slides

Appliquée par `lib/charte.js`, fonction `enTete()` :

- Format `LAYOUT_WIDE` (13,33 × 7,5 pouces), marges à 0,6, contenu sur 12,13 de large.
- **Eyebrow** `AUDIT DE CONFORMITÉ · SYNTHÈSE MANAGÉRIALE`, Calibri 10 gras, ambre, `charSpacing: 1.5`.
- **Titre** Cambria 30 gras navy ; **sous-titre** Calibri 11 gris, une ligne de cadrage chiffrée.
- **Notes du présentateur** sur chaque slide, mises à jour en même temps que les chiffres.

### Proposée — « Score global de conformité »

`templates/score_global.js`. Quatre zones : cartes KPI en haut à droite, bandeau du score avec jauge, taux par catégorie à gauche (**tri par taux croissant** — le lecteur doit voir le problème en premier), qualification des écarts à droite en trois blocs. Note de bas de page rappelant la formule.

### Proposée — « Non-conformités » et « Points sensibles »

`templates/constats.js`, même modèle pour les deux : une carte par constat, pastille rouge numérotée, titre court à gauche, constats à puces à droite. Les hauteurs se calculent depuis le contenu ; le template avertit si les cartes débordent de la slide.

### Proposée — « Recommandations »

`templates/recommandations.js`. Tableau à six colonnes : chantier, actions, responsable, délai, priorité (pastille colorée), effort.

Regrouper les recommandations en chantiers cohérents **sans perdre une seule action**. Une recommandation couvrant deux sujets distincts se scinde en deux puces plutôt que d'être résumée. Si aucun regroupement n'est défendable, garder une ligne par recommandation.

## Règles

### Calcul du taux — imposé

```
taux = (conformes + 0,5 × points sensibles) / règles applicables
règles applicables = total − non applicables
```

Les non applicables sont exclues du dénominateur, jamais comptées comme conformes. Même calcul pour le taux global et pour chaque catégorie. Implémenté une seule fois dans `lib/charte.js` (`taux()`), vérifié par `scripts/check_coherence.py`.

La note de bas de page énonce la formule **sans introduire de variable comme `n`** : une lettre qui n'apparaît pas dans l'équation envoie le lecteur la chercher. `Ch.noteFormule()` produit la formulation retenue.

### Couleurs et seuils — imposés

Définis dans `lib/charte.js`, objet `C`. Navy `1E2761` titres ; rouge `D64550` non-conformités ; ambre `E8A33D` eyebrow et jauge ; orange `E8901F` points sensibles ; vert `0E9F6E` conformes ; bleu `3B6BD6` remédiation.

Seuils des taux : vert ≥ 90 %, ambre 60–89 %, rouge < 60 % (`couleurTaux()`). Ne pas les ajuster pour flatter un résultat.

### Pictogrammes — imposés

Croix rouge pour une non-conformité (`Ch.croix`), triangle orange à point d'exclamation pour un point sensible (`Ch.alerte`). **Toujours en vectoriel, jamais en émoji** : un caractère émoji rend en noir et blanc ou en carré vide selon le poste et le vidéoprojecteur.

Le pictogramme est réservé à la **ligne d'impact** — la conséquence du constat, distincte du constat. Si l'entrée ne formule pas de conséquence, la carte n'a pas de ligne d'impact ; ne pas en inventer une.

### Rédaction — imposée

- Titres courts de carte inventés quand l'entrée n'en fournit pas, et signalés comme tels.
- Backticks et astérisques de l'entrée retirés du texte de la slide (`Ch.nettoyer`, appliqué par `Ch.puces`).
- Les colonnes responsable / délai / priorité / effort sont **toujours présentes** mais leurs valeurs sont déduites, donc marquées comme proposées dans le sous-titre (« responsables, délais et charges à valider ») et dans la réponse.
- Jamais de comparaison de taux entre deux versions dont le périmètre a changé sans le dire : un passage de 79,5 % à 73,4 % combine souvent dégradation réelle et élargissement du référentiel.

### Technique pptxgenjs — imposée

- `pres.layout = "LAYOUT_WIDE"` **avant** le premier `addSlide()`.
- Couleurs hexadécimales sans `#` et sans canal alpha. Un `#` ou 8 chiffres corrompent le fichier.
- `isTextBox: true` et `margin: 0` sur chaque `addText` à aligner sur une forme.
- `rectRadius` ne fonctionne que sur `roundRect`.
- Ne jamais partager un objet d'options entre deux appels : `pptxgenjs` le modifie en place.
- **Un seul run par puce.** Mélanger plusieurs runs avec changement de police dans un même paragraphe à puce casse les puces et scinde les lignes. Conséquence assumée : pas de chasse fixe sur les termes techniques dans une puce — le signaler et laisser l'utilisateur le faire dans PowerPoint s'il y tient. `Ch.puces()` respecte cette contrainte.

## Procédure

Prérequis, une seule fois : `npm install` et `pip install -r requirements.txt`. Le rendu d'aperçu demande LibreOffice et poppler-utils (`scripts/render_preview.sh` indique la commande d'installation s'ils manquent).

1. **Relever les chiffres** de l'entrée et les porter dans le fichier de données. Ne pas repartir des valeurs d'un échange antérieur.
2. **Contrôler avant de générer** :
   ```bash
   python3 scripts/check_coherence.py audit.json
   ```
   Toute erreur est levée avec l'auditeur avant la suite. Le script sort 1 en cas d'incohérence.
3. **Générer** :
   ```bash
   node build.js audit.json sortie
   ```
4. **Valider** :
   ```bash
   python3 scripts/validate_pptx.py sortie/*.pptx
   ```
5. **Rendre et inspecter visuellement** — obligatoire, jamais sauté :
   ```bash
   scripts/render_preview.sh sortie/score_global.pptx
   ```
   Ouvrir chaque image produite. Vérifier en priorité : texte débordant d'une carte, chevauchement du pictogramme et du texte, colonne droite tronquée, puce manquante, valeur restée à l'ancienne version. La validation XML ne voit rien de tout cela.
6. **Corriger dans le fichier de données ou le template**, jamais dans le `.pptx`, puis régénérer et réinspecter.
7. **Livrer** et signaler les arbitrages.

## Contrôles

`scripts/check_coherence.py` vérifie, avant toute génération :

- la somme des statuts de chaque catégorie face à son total déclaré ;
- les totaux déclarés face à la somme des catégories ;
- le taux global et chaque taux de catégorie, recalculés par la formule ;
- chacune des trois répartitions face au nombre d'écarts (NC + PS) ;
- le nombre de constats détaillés face aux compteurs — un écart ici signifie que la slide de constats sera décalée du tableau.

Il a rattrapé deux erreurs réelles en production : un compteur resté à l'ancienne valeur après mise à jour, et une répartition incohérente avec le nombre d'écarts.

`scripts/validate_pptx.py` vérifie ensuite que l'archive OOXML est saine, que la présentation se relit, qu'aucune forme ne déborde du cadre, qu'aucun texte de remplissage ne subsiste et que les couleurs sont bien formées.

## Pièges

**Mise à jour partielle.** Changer un taux de catégorie modifie mécaniquement le taux global, les compteurs et parfois les répartitions. Quand l'auditeur demande de ne changer qu'une valeur, appliquer sa consigne à la lettre puis signaler l'incohérence induite et proposer de la répercuter — ne pas corriger silencieusement.

**Même constat des deux côtés.** Un constat peut apparaître à la fois en NC et en PS si les référentiels diffèrent. Le signaler plutôt que d'arbitrer seul : la question sera posée en comité.

**Noms anonymisés.** Les entrées contiennent parfois `xxxxx_xxxx` ou des placeholders. Les conserver tels quels et rappeler qu'ils sont à remplacer avant diffusion.

**Constat trop maigre.** Un point sensible réduit à cinq mots produit une carte vide à côté des autres. Le signaler et demander le détail plutôt que de meubler.

**Recommandation à sujets multiples.** Une recommandation qui enchaîne deux actions de nature différente se scinde en deux puces. Si cela remet en cause le décompte des écarts affiché ailleurs, le dire.

**Trop de cartes pour une slide.** `templates/constats.js` avertit sur la sortie standard quand le contenu dépasse la hauteur disponible. Raccourcir les constats ou scinder la slide ; ne pas réduire la police sous 9 pt.
