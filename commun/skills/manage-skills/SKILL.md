---
name: manage-skills
description: Create, edit, audit, or prune Claude Code skills. Use for SKILL.md, frontmatter, references, scripts, and skill discovery.
---

Write skills the way `$analyze`, `$plan`, `$implement`, `$code-review`, and `$verify` are written.

## Target

- One job. Imperative. Every line changes behavior.
- Body under ~40 lines unless the job is genuinely multi-branch.
- Description 50–300 chars: capability first, then `Use when` + trigger words.
- No README, changelog, or theory. No restating model defaults.
- References only for platform or schema detail the body cannot hold. Name the file and when to open it.
- User-only workflows: `disable-model-invocation: true`.

## Write

1. Confirm 2–3 trigger prompts with the user.
2. Place the skill in the ai-playbook repo under `skills/<name>/`; install it with `synchroniser-skills`.
3. Write frontmatter, then the body: inspect → act → return → stop.
4. Check the description against [description-recommandation.md](references/description-recommandation.md) and the frontmatter against [claude-code.md](references/claude-code.md).

Source of truth: the ai-playbook repo (`skills/<name>/`); installed copies live in `~/.claude/skills/<name>/`. Glossary: [skill-writing-glossary.md](references/skill-writing-glossary.md).

## Audit

For each line: would removing it change behavior? Delete no-ops, duplicates, and stale rules. State the positive target; keep prohibitions only as hard guardrails.

Online research: official Claude Code documentation via web search.

Never create a skill whose name masks a built-in skill (for example `update-config`).
