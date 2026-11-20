# Gabarit et composants

Tout ce qui suit est **proposé** : le retenir quand il sert le parcours, l'écarter sinon.
Les classes correspondent à `assets/css-de-base.css`.

## Gabarit

```
┌ bande : zone · étape ─────────────────── environnement · Aide · Réglages ┐
├ bandeau d'environnement de test (si applicable) ─────────────────────────────┤
├ fil d'étapes (parcours en plusieurs pages) ─────────────────────────────────┤
│ rail          │ action (≤ 640 px, centrée)          │ contexte             │
│ menu ou       │ titre, contenu, boutons             │ récapitulatif,       │
│ progression   │ (secondaire à gauche, principal     │ compte, conseils     │
│               │  à droite)                          │                      │
└───────────────┴─────────────────────────────────────┴──────────────────────┘
tiroirs <dialog> à droite : Aide, Réglages, Détails techniques
```

- **Rail** : menu des opérations (application libre) ou progression (parcours linéaire,
  étapes faites ✓, étape courante ●, futures ○). Titre de groupe = même style que les
  titres du contexte, séparé par un filet. Entrées indisponibles visiblement grisées.
- **Action** : une seule chose à faire par écran ; le bouton principal à droite.
- **Contexte** : ce qu'il faut garder sous les yeux (récapitulatif, solde, guide).
- **Petits écrans** : rail, puis action, puis contexte ; `.gabarit--guide-avant` quand
  le contexte est un mode d'emploi à lire avant d'agir.
- **Tiroirs** : aide et détails techniques. Ce qui doit être vérifié n'y va jamais.

## Composants

| Composant | Quand | Règles |
|---|---|---|
| Bande | toute page | zone/étape à gauche ; à droite le même élément présenté pareil partout (ex. « Environnement » + menu si modifiable, + valeur en gras sinon) |
| Bandeau d'environnement | environnement de test ou factice | couleur réservée ; texte vrai seulement s'il est vérifié |
| Fil d'étapes | parcours sur plusieurs pages | étape courante soulignée ; numérotation unique partout (fichiers, titres, fil) |
| Choix segmenté (`.choix`) | 2 à 4 options exclusives | `aria-pressed` ; une valeur par défaut choisie, la moins risquée |
| Grand choix (`.option`) | début de parcours (créer / restaurer) | titre + une phrase |
| Champ + aide + erreur | saisie | erreur sous le champ, en rouge seulement si elle bloque |
| Champ secret | mot de passe, phrase secrète | masqué, bouton Afficher, pas de Copier ; attributs anti-fuite ; vidé après usage |
| Dépôt de fichier | import | zone + « Parcourir… » ; champ caché mais focus visible |
| Messages (4 niveaux) | info, attention, danger, réussite | toujours un mot qui dit le niveau ; dire quoi faire ensuite |
| Jauge | robustesse, progression | le texte dit le niveau ; sous le seuil, l'action est bloquée et on dit pourquoi |
| Bouton à appui maintenu | action irréversible (supprimer, payer, publier, envoyer) | se remplit pendant le maintien ; clavier (Espace) ; appui trop court → consigne visible |
| Récapitulatif | avant une action qui engage | tout ce qui sera fait, en clair ; données longues découpées en blocs lisibles |
| Tiroir | aide, réglages, détails | `<dialog>` natif, fermeture au clic sur le fond |

## Comportements partagés

Les mettre dans **un** script commun, déclarés par attributs (`data-…`) dans le HTML :
choix segmenté, appui maintenu, tiroirs, bascule Afficher/Masquer d'un secret, mise en
forme d'un montant ou d'un identifiant. Le texte toujours via `textContent`.

## Vocabulaire

- Un même concept porte le même mot partout (pas « Compte » ici et « Profil » là).
- Mot simple d'abord, terme technique ensuite si utile, détail brut replié.
- Pas de jargon interne dans l'interface (« selon le fichier », codes d'erreur bruts) :
  traduire en ce que l'utilisateur doit savoir et faire.
