# Runner reference

The skill normally invokes the runner for you. This reference covers manual execution and troubleshooting.

[Back to the README](../README.md)

## Direct execution

From the repository root, inspect the available options:

```bash
bash plugins/codex-plan-claude-execute/skills/codex-plan-claude-execute/scripts/run-claude.sh --help
```

To execute a prepared plan, use absolute paths when the skill and target project are in different directories:

```bash
bash /path/to/codex-plan-claude-execute/plugins/codex-plan-claude-execute/skills/codex-plan-claude-execute/scripts/run-claude.sh \
  /path/to/project/.plans/pagination.md \
  --repo /path/to/project \
  --attempts 3 \
  --timeout 1800
```

The runner requires Python 3, Bash, and an authenticated Claude Code CLI supporting the selected flags. It does not install dependencies or change login settings.

Use the [plan template](../plugins/codex-plan-claude-execute/skills/codex-plan-claude-execute/references/plan-template.md) to prepare the task. Plans must contain exactly one complete acceptance block. The runner executes that block as one Bash script with `-e -o pipefail`, so variables and directory changes persist within the block. Checks must be safe to repeat; do not include deployments or other non-repeatable operations.

## Options

| Option | Purpose | Default |
|---|---|---|
| `--repo PATH` | Explicit project execution directory | Inferred from the plan location and Git |
| `--attempts N` | Maximum model calls per runner invocation | 3 |
| `--max-turns N` | Maximum turns per Claude call | 60 |
| `--timeout SECONDS` | Total model and acceptance runtime | 1800 |
| `--max-budget USD` | Cumulative CLI-reported cost budget per invocation | Unset |
| `--model NAME` | Claude model override | Claude Code's configured default |
| `--allowed-tool RULE` | Additional auto-approved tool rule; repeatable | No additional rules |

## Retries and stopping conditions

Automatic repair occurs only when Claude reports a completed implementation and acceptance then fails. The next call receives the failure output and resumes the Claude session when a session ID is available.

The runner stops on process failures, malformed output, permission denials, blocked or partial reports, model limits, and timeout. Codex must diagnose these conditions before deciding how to continue.

Limits apply to one runner invocation. A new invocation starts new counters; Codex must still account for earlier calls when enforcing the overall task limits.

## Budget accounting

`--max-budget` uses the CLI's `total_cost_usd` field. With a budget of USD 2, the first call receives `--max-budget-usd 2`. If it reports USD 0.60, the next call receives a remaining budget of USD 1.40. No further call starts once the reported budget is exhausted.

When a budget is set, missing or invalid cost data stops the run. Acceptance commands' own costs are not included.

This is not a hard billing cap or a measure of subscription quota. The runner currently adds costs reported by each call. The semantics of `total_cost_usd` after `--resume` have not been verified with a real model session: if the CLI reports cumulative session cost, this calculation may double-count usage and stop early. Provider accounting and actual billing may differ.

## Permissions

The default auto-approved tools are `Read`, `Edit`, `Write`, `Glob`, and `Grep`. Add only the command rules needed for the task, for example:

```bash
--allowed-tool 'Bash(pytest:*)'
```

Existing Claude settings and host restrictions also apply. Tool rules and `acceptEdits` do not provide filesystem or network isolation. Build tools and general interpreters can execute arbitrary code.

Insufficient permission should be diagnosed, not automatically repaired by broadening access. Pushing, deploying, or other external writes require task authorization.

## Logs

Logs are saved beside the plan under `runs/<unique-run>/`. For a plan in `.plans/`, this is `.plans/runs/<unique-run>/`.

Each run includes:

- `plan.md` and `acceptance.sh`: the task and validation snapshots.
- `before.*`: Git HEAD, status, staged diff, and unstaged diff when Git is available.
- `attempt-N/claude.json` and `claude.stderr`: executor output.
- `attempt-N/report.json`: the parsed execution report, when valid.
- `attempt-N/acceptance.stdout` and `acceptance.stderr`: validation output, when run.
- `summary.json`: status, reason, attempts, session information, reported cost, and plan hash.

The Git baseline is not a complete backup of untracked file contents. Review new files separately and preserve any necessary originals before execution.

Keep logs local unless you intend to share them; they can contain project content and diagnostic information.

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Automated acceptance passed; independent Codex review is still pending |
| `1` | Execution stopped, timed out, was blocked, or exhausted repair attempts |
| `2` | Argument, environment, plan, or output-protocol error |

A successful exit is not a substitute for the [review checklist](../plugins/codex-plan-claude-execute/skills/codex-plan-claude-execute/references/verification.md).

## Troubleshooting

| Symptom | Next step |
|---|---|
| Claude is missing or authentication fails | Check `claude --version` and authenticate Claude Code interactively. |
| A CLI flag is rejected | Check the installed Claude version and its supported flags. |
| The plan is rejected | Check for one complete, nonempty acceptance block and valid Bash syntax. |
| The executor reports blocked or permission denied | Read its report and stderr; resolve the specific constraint before retrying. |
| Acceptance fails | Read the acceptance logs and inspect the implementation against the plan. |
| The run stops on budget or timeout | Inspect the summary and decide whether additional time or budget is authorized. |
| Checks pass but the task is incomplete | Have Codex review the completion criteria, revise the plan, and account for remaining task limits. |

## Validation status

The runner and installer have been checked with isolated, offline tests. Real-model end-to-end validation and resumed-session cost semantics remain unverified.
