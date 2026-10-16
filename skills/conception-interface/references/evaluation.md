# Évaluation comparative et essai témoin

## Avant / après (tout projet qui a déjà une interface)

1. **État des lieux, avant toute modification** : captures de chaque écran (bureau
   1280 px, mobile 390 px) ; résultats des deux scripts ; éléments inatteignables au
   clavier ou sans contour ; incohérences entre pages ; valeurs par défaut risquées.
   Les consigner dans le document des décisions.
2. **Après chaque lot** : mêmes mesures, captures avant/après.
3. **À la fin** : tableau avant/après, chiffré quand c'est possible (« 14 injections → 0,
   6 contrastes insuffisants → 0 »), captures pour ce qui ne se compte pas.

## Retour d'expérience

Ajouter quelques lignes datées (modèle dans `retours.md`) : ce qui a servi, ce qui a
manqué ou gêné, les nouveaux pièges. Les écrire dans **`retours-prives.md`**, dans le
dossier du skill (le créer s'il n'existe pas) : il est exclu par `.gitignore`, car un
retour cite souvent un projet, un client ou des chiffres privés. Ne verser dans
`retours.md`, publié, qu'une version anonymisée, et seulement à la demande de
l'utilisateur. Ne modifier une règle du skill que lorsque plusieurs retours convergent.

## Essai témoin (facultatif)

Mesure l'apport du skill lui-même, ce que l'avant/après ne peut pas faire. À proposer
sur les deux ou trois premiers projets réels et après une modification importante du
skill ; **jamais sans l'accord de l'utilisateur** (il coûte deux refontes au lieu d'une).

1. Deux copies du projet au même commit (une `git worktree` chacune).
2. La même demande écrite confiée à deux agents indépendants, l'un avec ce skill,
   l'autre sans ; aucun ne voit le travail de l'autre.
3. Les mêmes mesures sur les deux résultats.
4. Comparaison à l'aveugle : l'utilisateur reçoit les captures marquées A et B, choisit,
   puis on révèle laquelle vient du skill. Consigner dans `retours-prives.md`.

Limites à dire : un essai ne vaut pas preuve générale (deux ou trois donnent une
tendance) ; il compare le travail autonome, pas la co-conception. Demandes types dans
`evals/evals.json`.
