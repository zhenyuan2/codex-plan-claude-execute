---
name: codex-plan-claude-execute
description: Codex plans the task, Claude Code implements it, and Codex verifies the result. Use when the user requests this division of work, with bounded acceptance-based repair. Discussion or review of this skill does not itself request delegation.
---

# Codex Plan → Claude Execute

Codex owns task scope, planning, and final review. Claude Code implements the plan. Honor explicit executor choice even for small tasks; scale planning detail to the task.

## 1. Prepare

Read relevant repository instructions and files. Identify the execution root, existing user changes, acceptance checks, and authorization boundaries. Resolve material ambiguity before execution; routine implementation choices need not block work.

Read [references/plan-template.md](references/plan-template.md). Write one current plan at `.plans/<slug>.md`, with a self-contained goal, relevant context, bounded tasks, completion criteria, and exactly one acceptance block. Include existing user authorization, prohibited changes, and any allowed external actions. The plan conveys task requirements; repository and host instructions still apply.

Show the plan summary, including the exact acceptance block and its SHA-256. The runner prints both, and `--show-acceptance` displays them without executing. If the user already authorized planning and execution, proceed; if they have not approved those specific commands, ask. Pass the approved hash with `--acceptance-sha256` so acceptance commands changed after review are rejected.

## 2. Execute

Run from the intended project, specifying its absolute root when nested repositories or non-Git folders could be ambiguous:

```bash
bash "<skill_dir>/scripts/run-claude.sh" .plans/<slug>.md --repo /absolute/project/path --acceptance-sha256 <approved-hash> --attempts 3 --timeout 1800
```

`<skill_dir>` is this skill's directory. Python 3, Bash, and an authenticated Claude Code CLI are required. Use `--help` for flags. Output is saved internally; no outer `tee` pipeline is needed. If adding one, preserve the runner exit code with `pipefail`. Run `--show-acceptance` first to display the acceptance block and hash without executing.

The runner starts Claude Code in `dontAsk` mode with an explicit allowlist of `Read`, `Edit`, `Write`, `Glob`, and `Grep`. Commands that would require approval (including `mkdir`, `touch`, `rm`, `rmdir`, `mv`, `cp`, `sed`, and general build/test commands) are denied unless you add a task-needed rule with `--allowed-tool`, for example `--allowed-tool 'Bash(pytest:*)'`. The CLI's built-in read-only command set may still run without approval. Permission denials stop the run for diagnosis. Permissions also depend on Claude settings and the host environment. Tool rules and `dontAsk` are not filesystem/network isolation; general interpreters and build tools can execute arbitrary code. Never automatically broaden permissions or use permission-bypass flags to repair a failure.

Acceptance is executed by the runner, not by Claude, so its permissions do not apply to it. The runner prints the commands and hash; dangerous patterns are refused unless `--allow-dangerous-acceptance` is passed after explicit approval. Acceptance runs with credential-like environment variables and loader hooks removed by default; use `--pass-environment` only if a check legitimately needs them. Use `--acceptance-wrapper` to run acceptance under a container or OS sandbox.

`--attempts` limits model calls in one invocation. `--timeout` limits total model/acceptance runtime (default 1800 seconds). The runner does not enforce a cost budget; per-call cost figures in the logs are client-side estimates that may be missing or session-cumulative. Track the plan's model-call and time limits across invocations, and do not start another invocation merely to reset exhausted limits.

The runner snapshots the plan and acceptance, saves the Git baseline when available, and stores per-attempt logs under `.plans/runs/<unique-run>/`. It adds a local `.git/info/exclude` entry for the plan artifacts so clean-tree acceptance checks are not polluted. It retries only after a completed executor report followed by failed acceptance. Process, protocol, permission, blocked/partial, and model-limit errors stop for Codex diagnosis. Do not edit implementation files concurrently with Claude.

Exit codes:
- `0`: execution reported done and automated acceptance passed; Codex review is still pending.
- `1`: stopped, timed out, blocked, or repair attempts exhausted.
- `2`: argument, environment, plan, or output-protocol error.

## 3. Review and finish

Read [references/verification.md](references/verification.md). Inspect actual changes against the baseline, including staged and new files, and verify completion criteria. Executor claims or passing checks alone are insufficient.

If review finds an implementation gap, update the current plan and record what superseded the prior requirements. Use a new run only within the remaining authorized task limits; otherwise report the gap. Prior run snapshots preserve history. Never weaken acceptance merely to obtain success.

Report scope, validation evidence, attempts, known cost information, and unresolved issues. Keep machine `acceptance_passed` separate from Codex's final review verdict. Do not auto-commit, push, deploy, or send messages unless already authorized.
