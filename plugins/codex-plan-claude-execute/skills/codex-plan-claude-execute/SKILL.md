---
name: codex-plan-claude-execute
description: Codex plans the task, Claude Code implements it, and Codex verifies the result. Use when the user requests this division of work, with bounded acceptance-based repair. Discussion or review of this skill does not itself request delegation.
---

# Codex Plan → Claude Execute

Codex owns task scope, planning, and final review. Claude Code implements the plan. Honor explicit executor choice even for small tasks; scale planning detail to the task.

## 1. Prepare

Read relevant repository instructions and files. Identify the execution root, existing user changes, acceptance checks, and authorization boundaries. Resolve material ambiguity before execution; routine implementation choices need not block work.

Read [references/plan-template.md](references/plan-template.md). Write one current plan at `.plans/<slug>.md`, with a self-contained goal, relevant context, bounded tasks, completion criteria, and exactly one acceptance block. Include existing user authorization, prohibited changes, and any allowed external actions. The plan conveys task requirements; repository and host instructions still apply.

Show a concise plan summary. If the user already authorized planning and execution, proceed. Ask only when a material decision or additional authorization is missing, not for routine reconfirmation.

## 2. Execute

Run from the intended project, specifying its absolute root when nested repositories or non-Git folders could be ambiguous:

```bash
bash "<skill_dir>/scripts/run-claude.sh" .plans/<slug>.md --repo /absolute/project/path --attempts 3 --timeout 1800
```

`<skill_dir>` is this skill's directory. Python 3, Bash, and an authenticated Claude Code CLI are required. Use `--help` for flags. Output is saved internally; no outer `tee` pipeline is needed. If adding one, preserve the runner exit code with `pipefail`.

Default auto-approved tools are file tools; add only task-needed command rules using repeated `--allowed-tool 'Bash(...)'` options. Permissions also depend on Claude settings and the host environment. Tool rules and `acceptEdits` are not filesystem/network isolation. General interpreters and build tools can execute arbitrary code. Never automatically broaden permissions or use permission-bypass flags to repair a failure.

`--attempts` limits model calls in one invocation. `--timeout` limits total model/acceptance runtime (default 1800 seconds). Optional `--max-budget USD` allocates the remaining reported budget to each call; it is not a billing guarantee and CLI/provider accounting may vary. Record all invocations toward the task budget. Do not start another invocation merely to reset exhausted limits.

The runner snapshots the plan and acceptance, saves the Git baseline when available, and stores per-attempt logs under `.plans/runs/<unique-run>/`. It retries only after a completed executor report followed by failed acceptance. Process, protocol, permission, blocked/partial, and model-limit errors stop for Codex diagnosis. Do not edit implementation files concurrently with Claude.

Exit codes:
- `0`: execution reported done and automated acceptance passed; Codex review is still pending.
- `1`: stopped, timed out, blocked, or repair attempts exhausted.
- `2`: argument, environment, plan, or output-protocol error.

## 3. Review and finish

Read [references/verification.md](references/verification.md). Inspect actual changes against the baseline, including staged and new files, and verify completion criteria. Executor claims or passing checks alone are insufficient.

If review finds an implementation gap, update the current plan and record what superseded the prior requirements. Use a new run only within the remaining authorized task limits; otherwise report the gap. Prior run snapshots preserve history. Never weaken acceptance merely to obtain success.

Report scope, validation evidence, attempts, known cost information, and unresolved issues. Keep machine `acceptance_passed` separate from Codex's final review verdict. Do not auto-commit, push, deploy, or send messages unless already authorized.
