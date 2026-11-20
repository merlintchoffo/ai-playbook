---
name: manage-skills
description: Create, edit, audit, or prune Claude Code skills. Use when writing or reviewing SKILL.md files, frontmatter, references, scripts, or skill discovery.
---

## Entrée

- The **skill to create, edit, audit or prune**, and what it must do.

## Sortie

- A **SKILL.md** (and its references or scripts) that follows the repo conventions, placed in the ai-playbook repo, with a valid frontmatter.

---

## Conventions that prevail

`commun/rules/ecriture-skills-et-agents.md` is the authority. In short: `## Entrée` and `## Sortie`
as bullet lists right after the frontmatter, then `---`, then the "how"; a skill name starts with a
verb, an agent name ends in `-er`; the trigger is written "Use when" (or "Utiliser quand"); no
unquoted `: ` in a frontmatter value. Where this skill and that rule differ, the rule wins.

## Target

- One job. Imperative. Every line changes behavior.
- Body under ~40 lines unless the job is genuinely multi-branch.
- Description 50–300 chars: capability first, then `Use when` + trigger words.
- No changelog or theory, no restating model defaults. A README only if the skill is meant to be shared outside this repo.
- References only for platform or schema detail the body cannot hold. Name the file and when to open it.
- Skills with side effects outside the repo (push, merge, board update) or user-only workflows: `disable-model-invocation: true`.

## Write

1. Confirm 2–3 trigger prompts with the user.
2. Place the skill under `commun/skills/<name>/` if it applies to any project, or `domaines/<domaine>/skills/<name>/` if it describes one kind of project; install it with `synchroniser-skills`.
3. Write frontmatter, then `## Entrée` / `## Sortie`, then the body: inspect → act → return → stop.
4. Check the description against [description-recommandation.md](references/description-recommandation.md) and the frontmatter against [claude-code.md](references/claude-code.md).

Source of truth: the ai-playbook repo; installed copies live in `~/.claude/skills/<name>/` (commun) or `<projet>/.claude/skills/<name>/` (domaine). Glossary: [skill-writing-glossary.md](references/skill-writing-glossary.md).

## Audit

For each line: would removing it change behavior? Delete no-ops, duplicates, and stale rules. State the positive target; keep prohibitions only as hard guardrails.

Online research: official Claude Code documentation via web search.

Never create a skill whose name masks a built-in skill (for example `update-config`).
