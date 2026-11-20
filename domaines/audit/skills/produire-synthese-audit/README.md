# produire-synthese-audit

Génération des slides de synthèse managériale d'un audit de conformité : score global, non-conformités, points sensibles, plan de recommandations.

Utilisable de deux façons : comme **skill** (`SKILL.md` décrit la méthode, les règles et les arbitrages) ou comme **outil en ligne de commande**, indépendamment de tout agent.

## Installation

```bash
npm install                        # pptxgenjs
pip install -r requirements.txt    # python-pptx, pour la validation
```

Le rendu d'aperçu demande en plus LibreOffice et poppler-utils :

```bash
# Debian / Ubuntu
sudo apt-get install libreoffice-impress poppler-utils
# macOS
brew install --cask libreoffice && brew install poppler
```

## Usage

```bash
python3 scripts/check_coherence.py audit.json     # 1. contrôler AVANT de générer
node build.js audit.json sortie                   # 2. générer
python3 scripts/validate_pptx.py sortie/*.pptx    # 3. valider
scripts/render_preview.sh sortie/score_global.pptx # 4. rendre et REGARDER
```

L'ordre compte. Le contrôle de cohérence passe avant la génération : produire quatre slides sur des chiffres faux coûte plus cher que de lever l'incohérence avec l'auditeur. Et l'inspection visuelle n'est pas optionnelle — la validation XML ne voit ni un texte qui déborde de sa carte, ni un chiffre resté à l'ancienne valeur.

Pour un deck unique au lieu de quatre fichiers :

```bash
node build.js audit.json sortie --assemble
```

Pour essayer sans données réelles :

```bash
npm run check && npm run build && npm run validate
```

## Fichier de données

Une seule source de vérité : `exemples/audit-exemple.json`, à copier et remplir. Les contrôles portent sur elle, et les quatre slides en découlent. Les sections absentes sont ignorées — un fichier sans `chantiers` produit trois slides.

| Clé | Contenu |
|---|---|
| `categories` | une entrée par catégorie : `total`, `conformes`, `non_conformes`, `points_sensibles`, `non_applicables` |
| `totaux` | facultatif ; s'il est présent, il est confronté à la somme des catégories |
| `qualification` | les trois répartitions : `impact`, `remediation`, `portee` |
| `non_conformites` | une carte par NC : `titre`, `constats[]`, `impact` facultatif |
| `points_sensibles_detail` | idem pour les PS |
| `chantiers` | regroupements de recommandations : `nom`, `actions[]`, `responsable`, `delai`, `priorite`, `effort` |

Les champs `taux` sont facultatifs : s'ils figurent dans le fichier, `check_coherence.py` les confronte au calcul plutôt que de les croire.

## Organisation

```
lib/charte.js          palette, formule, pictogrammes, helpers — la partie imposée
templates/             un module par slide — la partie adaptable
scripts/               contrôle de cohérence, validation, rendu d'aperçu
exemples/              fichier de données complet et cohérent
build.js               orchestration
```

La séparation n'est pas cosmétique : `lib/charte.js` garantit qu'un audit à l'autre les slides restent comparables, les templates suivent le contenu réel. Modifier une couleur ou un seuil dans `charte.js` change toutes les synthèses passées et futures — à faire sciemment.

## Ce qui est imposé, ce qui est proposé

| Imposé | Proposé |
|---|---|
| Palette, typographie, grille | Nombre de slides et de cartes |
| Formule du taux et seuils de couleur | Regroupement des recommandations |
| Croix rouge = NC, triangle orange = PS | Titres courts des cartes |
| Contrôles avant livraison | Responsables, délais, priorité, effort |
| Icônes vectorielles, jamais d'émoji | Découpage constat / impact |

Les quatre colonnes de pilotage illustrent la nuance : leur **présence** est imposée — un plan d'action sans responsable ni délai ne sert à rien en comité — mais leurs **valeurs** sont déduites, et la slide le dit.

## Formule du taux

```
taux = (conformes + 0,5 × points sensibles) / (total − non applicables)
```

Les non applicables sont exclues du dénominateur, jamais comptées comme conformes. Seuils de couleur : vert ≥ 90 %, ambre 60–89 %, rouge < 60 %.

## Installation comme skill

Copier le dossier sous `skills/` d'un dépôt de playbooks, ou sous `~/.claude/skills/`. Le nom du dossier doit correspondre au champ `name` du frontmatter de `SKILL.md`.

Pour l'utiliser depuis claude.ai, il faut l'enregistrer sur le compte : le fichier seul ne suffit pas, et les deux copies divergeront. Décider laquelle fait foi — pour un playbook d'équipe relu en pull request, c'est généralement Git.

## Avertissement sur l'exemple

`exemples/audit-exemple.json` est **anonymisé** : noms de systèmes fictifs, constats génériques. Il est cohérent et sert de référence de format. Ne pas y verser de données d'audit réelles si le dépôt est partagé — les constats d'un audit décrivent des vulnérabilités exploitables.
