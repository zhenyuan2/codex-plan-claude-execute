# Runner reference

The skill normally invokes the runner for you. This reference covers manual execution and troubleshooting.

[Back to the README](../README.md)

## Direct execution

From the repository root, inspect the available options:

```bash
bash plugins/codex-plan-claude-execute/skills/codex-plan-claude-execute/scripts/run-claude.sh --help
```

First display the acceptance commands and their SHA-256 without executing anything:

```bash
bash /path/to/codex-plan-claude-execute/plugins/codex-plan-claude-execute/skills/codex-plan-claude-execute/scripts/run-claude.sh \
  /path/to/project/.plans/pagination.md \
  --show-acceptance
```

To execute a prepared plan, use absolute paths when the skill and target project are in different directories. Pass the reviewed hash to bind execution to the commands you saw:

```bash
bash /path/to/codex-plan-claude-execute/plugins/codex-plan-claude-execute/skills/codex-plan-claude-execute/scripts/run-claude.sh \
  /path/to/project/.plans/pagination.md \
  --repo /path/to/project \
  --acceptance-sha256 <reviewed-hash> \
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
| `--model NAME` | Claude model override | Claude Code's configured default |
| `--allowed-tool RULE` | Additional allowed tool rule; repeatable | No additional rules |
| `--show-acceptance` | Print the acceptance block and SHA-256, then exit without executing | Off |
| `--acceptance-sha256 HASH` | Require the acceptance block to match an approved SHA-256 | Unset |
| `--allow-dangerous-acceptance` | Allow acceptance matching dangerous patterns after explicit approval | Off |
| `--pass-environment` | Give acceptance the full environment instead of filtering credential-like variables | Off |
| `--acceptance-wrapper TEMPLATE` | Run acceptance through an argv prefix; `{repo}` and `{script}` are substituted | Unset |

## Retries and stopping conditions

Automatic repair occurs only when Claude reports a completed implementation and acceptance then fails. The next call receives the failure output and resumes the Claude session when a session ID is available.

The runner stops on process failures, malformed output, permission denials, blocked or partial reports, model limits, and timeout. Codex must diagnose these conditions before deciding how to continue.

Limits apply to one runner invocation. A new invocation starts new counters; Codex must still account for earlier calls when enforcing the overall task limits.

## Cost reporting

The runner does not enforce a cost budget. Use `--max-turns` and `--timeout` as the enforced limits.

Each Claude call's result JSON is saved in `attempt-N/claude.json`. `summary.json` also records `reported_costs_usd`, a list of the cost values reported by completed model calls, in attempt order. A value is `null` when the CLI did not report a usable number. These values are client-side estimates, not billing data: they may be missing, differ from the provider's invoice, and on a resumed session may already include earlier session spend. They are not aggregated into a total and are not a measure of subscription quota.

## Permissions

The runner starts Claude Code with `--permission-mode dontAsk` and an explicit allowlist: `Read`, `Edit`, `Write`, `Glob`, and `Grep`. Commands that would require approval — including `mkdir`, `touch`, `rm`, `rmdir`, `mv`, `cp`, `sed`, and general build/test commands — are denied unless you add a matching rule, for example:

```bash
--allowed-tool 'Bash(pytest:*)'
```

The CLI's built-in read-only command set may still run without approval. Permission denials stop the run for diagnosis. Existing Claude settings and host restrictions also apply. Tool rules and `dontAsk` do not provide filesystem or network isolation. Build tools and general interpreters can execute arbitrary code.

Insufficient permission should be diagnosed, not automatically repaired by broadening access. Pushing, deploying, or other external writes require task authorization.

Acceptance is executed by the runner, not by Claude; the tool permissions above do not constrain it. See [Acceptance safety](#acceptance-safety).

## Acceptance safety

The acceptance block is LLM-authored shell, not a restricted test runner. The runner:

- prints the exact commands and their SHA-256 before execution; `--show-acceptance` displays them without running anything;
- can bind execution to the approved commands with `--acceptance-sha256`, so acceptance changed after review is rejected;
- refuses high-risk patterns — pipe-to-shell, recursive deletes, `git push`/`reset --hard`/`clean -f`, privilege escalation, remote access or upload, package publish, container push, deployment commands, and disk utilities — unless `--allow-dangerous-acceptance` is supplied after review;
- removes common credential-like environment variables and loader hooks from acceptance by default; use `--pass-environment` only when a check legitimately needs them;
- can run acceptance through an external sandbox with `--acceptance-wrapper`, for example:

```bash
--acceptance-wrapper 'docker run --rm --network none -v {repo}:{repo} -w {repo} IMAGE'
```

```bash
--acceptance-wrapper 'bwrap --ro-bind / / --bind {repo} {repo} --unshare-net --dev /dev --proc /proc --'
```

The wrapper template is split into an argv prefix before `{repo}` and `{script}` are substituted into each argument, preserving spaces and quotes in paths. The runner then appends `bash -e -o pipefail {script}`. An explicitly empty or whitespace-only wrapper, or an empty executable, is rejected before Claude runs. Use `{repo}` and `{script}` for mount or path arguments; if the template needs shell syntax, include an explicit `bash -c` in the template. The wrapper receives the sanitized environment and must be able to see `{script}`. If the wrapper itself needs credentials or provider settings such as `DOCKER_HOST`, use `--pass-environment` only after reviewing that exposure. Mount the plan directory too when it is outside the repository, and use an image with Bash and the project's test dependencies. The runner does not verify the wrapper or the sandbox configuration.

The pattern guard is best-effort, not a security boundary. For untrusted repositories, review the displayed commands and use a real sandbox; Claude's permission mode and Codex's approval do not apply to the acceptance shell.

## Logs

Logs are saved beside the plan under `runs/<unique-run>/`. For a plan in `.plans/`, this is `.plans/runs/<unique-run>/`.

Each run includes:

- `plan.md` and `acceptance.sh`: the task and validation snapshots.
- `before.*`: Git HEAD, status, staged diff, and unstaged diff when Git is available.
- `attempt-N/claude.json` and `claude.stderr`: executor output.
- `attempt-N/report.json`: the parsed execution report, when valid.
- `attempt-N/acceptance.stdout` and `acceptance.stderr`: validation output, when run.
- `summary.json`: status, reason, attempts, session information, per-attempt reported cost estimates, acceptance SHA-256, and plan hash.

The Git baseline is not a complete backup of untracked file contents. Review new files separately and preserve any necessary originals before execution.

Keep logs local unless you intend to share them; they can contain project content and diagnostic information.

## Git artifact exclusion

Before creating run artifacts, the runner adds local exclude entries to the plan repository's `.git/info/exclude` when Git is available:

- for a plan in a `.plans/` directory, the `.plans/` directory;
- for a plan elsewhere, the plan file and its `runs/` directory.

This keeps clean-tree acceptance checks from seeing runner-owned files and keeps plans and logs out of commits. The runner does not modify tracked `.gitignore` files. If the exclude file cannot be written, it prints a warning and continues; a clean-tree check may then see those artifacts.

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
| Acceptance hash mismatch | The acceptance block changed after approval; run `--show-acceptance`, review the new commands, and pass the new hash. |
| Acceptance refused as dangerous | Review the matched lines; re-run with `--allow-dangerous-acceptance` only if the commands are intended. |
| Acceptance needs a credential env var | Prefer an isolated runner; use `--pass-environment` only after confirming the check needs it. |
| Acceptance needs a sandbox | Use `--acceptance-wrapper` with a container or OS sandbox; verify mounts, `{script}`, and network policy. |
| The run stops on timeout | Inspect the summary and decide whether additional time is authorized. |
| Checks pass but the task is incomplete | Have Codex review the completion criteria, revise the plan, and account for remaining task limits. |

## Validation status

The runner and installer have been checked with isolated, offline tests. Real-model end-to-end validation remains unverified. Cost values are recorded as reported and are not aggregated or enforced. The acceptance guard is pattern-based; it does not replace review or a real sandbox.
