---
name: step-02c-red
description: Write failing tests from the approved APEX acceptance criteria before any implementation (test-first).
---

# Step 2c: Red (test-first)

Do not edit production code in this step.

## 1. Decide whether this step applies

- `{test_authoring}=off` → skip: record the reason and load `{execution_step}`.
- `{test_authoring}=on` → apply.
- `{test_authoring}=risk-based` → apply when the risk class is Medium or higher; for Low, skip and record the reason.
- An acceptance criterion with no automatable observable behavior (pure documentation, visual-only change) is listed as "not test-first" with the reason and the evidence that will replace it.

## 2. Inspect test infrastructure

Find the existing runner, conventions, fixtures, isolation rules and nearby examples. Reuse project patterns. If the project has no test runner, record it and ask before adding one.

## 3. Write one test per acceptance criterion

For each criterion in `{run_dir}/tasks.json`, write the smallest test that checks its observable behavior through the public interface, not implementation details. Add boundary or failure cases only where the plan names them as risks.

## 4. Prove the red

Run the new tests. Each must fail **for the expected reason**: the behavior is missing or wrong. A failure caused by a syntax error, a missing import, a wrong fixture or an unavailable service is not a red: fix the test and rerun. A test that already passes either reveals existing behavior (record it and adjust the criterion) or tests nothing (rewrite it).

Record, for each test: criterion, file, command, and failure reason.

```bash
python3 "{skill_dir}/scripts/apex-state.py" event --root "$PWD" --run-id "{run_id}" --phase red --status complete --message "Failing tests recorded for acceptance criteria"
python3 "{skill_dir}/scripts/apex-state.py" checkpoint --root "$PWD" --run-id "{run_id}" --phase red --message "Ready to do"
```

## Completion

Load the exact `{execution_step}` persisted by `step-02-plan.md`. During Do, the red tests are the primary feedback: a task is done when its tests turn green without weakening them. Changing a red test during Do requires recording why the test, not the code, was wrong.
