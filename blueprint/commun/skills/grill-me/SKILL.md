---
name: grill-me
description: Grill the user in rapid batches to sharpen a plan, decision, or idea. Use when the user asks for Grill Me, wants a rigorous interview, or uses a grill trigger phrase.
disable-model-invocation: true
---

## Entrée

- A plan, decision or idea to sharpen.

## Sortie

- Batches of up to 10 numbered questions, each with a recommended answer.
- A decision brief (goal, scope, constraints, approach, rejected alternatives, risks, acceptance criteria), confirmed before any action.

---

Explicit exception to the methode-de-travail rule « four closed questions at most »: the user invoked this skill to be questioned in depth.

Stress-test the user's thinking until both sides share a precise, actionable understanding.

1. Resolve discoverable facts from the environment. Ask only decisions the user can make.
2. Ask exactly 10 numbered questions in one batch. Lead with the highest-leverage unresolved decisions. Include a concise **Recommended answer** on every question.
3. Invite one grouped reply. Short answers keyed `1` through `10` are enough. Accept terse answers, skips, or blanket acceptance of the recommendations.
4. Summarize what is established, investigate new facts, then ask the next batch. If fewer than 10 decisions remain, ask only those.
5. Present a compact decision brief: goal, scope, constraints, chosen approach, rejected alternatives, risks, and acceptance criteria.
6. Get explicit confirmation before acting on it.

Challenge assumptions. Compare credible alternatives. Match the user's language. Do not implement until the brief is confirmed.
