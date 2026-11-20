---
name: manage-hooks
description: Create, edit, configure, and debug Claude Code hooks. Use when configuring lifecycle events, command validation, notifications, automation, or hook configuration in settings.json.
disable-model-invocation: true
---

## Entrée

- The lifecycle event to hook and the expected behaviour.

## Sortie

- A hook script in `commun/hooks/`, smoke-checked.
- Its declaration for `~/.claude/settings.json`, applied only with a separate approval.

---

Configure Claude Code hooks as event-driven commands or prompts.

1. Identify the platform and load [router.md](references/router.md).
2. Load [claude-code.md](references/claude-code.md).
3. Pick the scope, file path, lifecycle event, and a command hook (deterministic) or prompt hook (reasoning, if supported).
4. Validate the native config and run the platform smoke check.

Keep one script per hook in the ai-playbook repo (`commun/hooks/`), installed by `synchroniser-skills`. Report unsupported features.

Load as needed: [hook-types.md](references/hook-types.md), [command-vs-prompt.md](references/command-vs-prompt.md), [matchers.md](references/matchers.md), [input-output-schemas.md](references/input-output-schemas.md), [examples.md](references/examples.md), [troubleshooting.md](references/troubleshooting.md).

Check `stop_hook_active` on Stop/SubagentStop. Use trusted absolute paths, timeouts, and `jq` validation. Keep blocking rules selective.
