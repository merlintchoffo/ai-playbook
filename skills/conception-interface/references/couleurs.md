# Couleurs

## Le principe : une couleur = un sens

Chaque couleur porte **un seul** sens dans toute l'application, et ce sens est
**toujours doublé d'un mot** (titre, libellé, icône textuelle ✓ ✗). Un daltonien, un
écran noir et blanc ou un lecteur d'écran doivent recevoir la même information.

| Couleur | Sens | Exemples | Jamais pour |
|---|---|---|---|
| Bleu | agir | bouton principal, lien, focus, appui maintenu | décorer, signaler un état |
| Jaune | vérifier, attention | « vérifiez l'adresse », compte pas encore créé, dérogation acceptée | une erreur bloquante |
| Rouge | danger, irréversible, **bloquant** | suppression, erreur qui empêche de continuer, alarme tant qu'elle bloque | une situation normale (liste vide, compte neuf), une consigne de routine |
| Vert | réussi, **seulement** | « Paiement accepté », « Vérifié » | un bouton, une décoration |
| Couleur réservée (par exemple violet) | environnement de test / factice | bandeau « Environnement de test · données fictives » | quoi que ce soit d'autre |
| Gris (doux) | secondaire | aides, libellés, désactivé | du texte important |

Le domaine n'a pas de couleur : pas de couleur par produit, par catégorie, par client.
Une nouvelle couleur demande un nouveau sens, discuté avec l'utilisateur.

## Zones par luminosité

Quand le domaine a des espaces qu'il ne faut pas confondre (production / test,
espace public / administration, consultation / zone sensible), les distinguer par la **luminosité** plutôt
que par une teinte : page claire + bande sombre d'un côté, l'exact négatif de l'autre.
La teinte reste libre pour les sens ci-dessus. La zone impose la luminosité : pas de
bascule clair/sombre laissée à l'utilisateur, sauf besoin d'accessibilité.

Ne créer des zones que si le domaine les exige ; sinon un seul thème.

## Construire la palette

1. Partir des **variables** de `assets/css-de-base.css` (noms : fond, fond-2, encre,
   doux, filet, champ, champ-bordure, bande, action, attention-*, danger-*, reussite).
2. Ajuster les teintes au projet, **une seule fois** dans les variables.
3. Pour un thème sombre : mêmes sens, couleurs éclaircies (le bleu d'action devient
   pastel, le rouge saumon) ; le texte d'un bouton plein devient sombre.
4. Vérifier : `node scripts/verifier-contrastes.js <fichier.css>` (paires par défaut),
   ou `--paires paires.json` si les noms diffèrent.
5. Transposer la vérification en test du projet, pour que toute retouche de couleur
   soit contrôlée.

## Seuils (WCAG 2.2, niveau AA)

- Texte normal : **4,5:1** ; grand texte (≥ 24 px, ou ≥ 19 px gras) : 3:1.
- Composants et bordures de champs, contour de focus : **3:1** avec ce qui les entoure
  (le fond de la page **et** le fond du champ).
- Les éléments désactivés sont exemptés, mais doivent rester identifiables comme tels.

Défaut typique trouvé par la vérification : bordures de champs trop pâles (autour de 2:1).
