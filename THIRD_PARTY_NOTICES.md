# Contenus tiers

## AIBlueprint

- **Source** : dépôt `aiblueprint` (paquet npm `aiblueprint`, auteur « AIBlueprint »), dossier
  `agents-config/skills/`, commit `59690e6b544535daf7e4bc7c8bd0e0f63754f21b` (2026-10-21).
- **Licence** : MIT, déclarée dans le `package.json` et le README de la source. Le fichier `LICENSE`
  cité par le README est absent de la source ; le texte MIT standard est reproduit ci-dessous.
- **Skills importés** (nom d'origine → nom et emplacement ici) : `agents-manager` → `commun/skills/manage-agents`,
  `hooks-manager` → `commun/skills/manage-hooks`, `rules-manager` → `commun/skills/manage-rules`,
  `skill-manager` → `commun/skills/manage-skills`, `audit-memories`, `grill-me` → `commun/skills/`,
  `apex`, `audit-test` → `domaines/app/skills/`.
- **Modifications** :
  - Retirés : fichiers propres à Codex et Cursor (`agents/openai.yaml`, `assets/codex-icon.svg`,
    `references/codex.md`, `references/cursor.md`, `scripts/setup-codex-icons.ts`), et
    `skill-manager/scripts/inspect-description.ts` (dépend de Bun, absent).
  - Chemins `~/.agents/…` et `.agents/apex/` remplacés par `~/.claude/…` et `.claude/apex/`
    (script et tests d'`apex` compris) ; `trash` remplacé par `gio trash` ; `apply_patch` remplacé par
    l'outil Edit ; renvois aux skills absents `$find-docs` et `$exa-search` retirés.
  - Descriptions de `hooks-manager`, `skill-manager` et `rules-manager` limitées à Claude Code et
    rattachées au dépôt ai-playbook (`commun/skills/`, `commun/rules/`, `commun/hooks/`, `synchroniser-skills`).
  - Alignement sur la règle `methode-de-travail` : `apex` ne délègue à un sous-agent qu'avec
    l'accord de l'utilisateur ; `grill-me` est déclaré exception à « quatre questions au plus ».
  - `apex` : étape test-first ajoutée (`steps/step-02c-red.md`, tests rouges écrits après le plan,
    avant l'implémentation) ; phase « Execute » renommée « Do ».

```
MIT License

Copyright (c) AIBlueprint

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## OpenClaw (via AIBlueprint)

`domaines/app/skills/audit-test/` est lui-même adapté de
`https://github.com/openclaw/openclaw/tree/main/.agents/skills/test-audit` — MIT,
Copyright (c) 2026 OpenClaw Foundation. Sa licence est conservée dans `domaines/app/skills/audit-test/LICENSE`.

## Idée reprise sans copie

`commun/hooks/bloquer-commandes-interdites.py` et `commun/skills/synchroniser-skills/` sont écrits pour ce dépôt ;
ils s'inspirent de `codex-config/hooks/command-deny-list.ts` et de `.claude/skills/update-config/`
d'AIBlueprint, sans en reprendre le code.
