# codex-plan-claude-execute

Codex plans and reviews; Claude Code implements in headless mode. Invoke with `$codex-plan-claude-execute`. See `SKILL.md` for the workflow and authorization rules.

Requires Python 3, Bash, and an installed/authenticated Claude Code CLI supporting `--max-turns`, `--output-format json`, and (when selected) `--max-budget-usd`. CLI failures stop without automatic retries.

```bash
bash scripts/run-claude.sh --help
```

Development tests are local-only and are not included in Git distribution. Runtime execution does not require them.

Flags: `--repo PATH`, `--attempts N` (3), `--max-turns N` (60), `--timeout SECONDS` (1800), `--max-budget USD` (total reported budget per invocation), `--model NAME`, repeated `--allowed-tool RULE`.

Migration from 0.1: `--loose` and space-split `--allowed-tools` were removed. Add individual task-needed rules with `--allowed-tool`. `--max-budget` now covers one whole invocation, not each attempt. Plans must contain exactly one acceptance block; update the current plan rather than appending additional blocks. Acceptance runs as one Bash script with `-e -o pipefail`. Python is required for strict result parsing. Logs now live in unique `.plans/runs/` directories.

Only failed acceptance after a completed report triggers automatic repair. Malformed output, blocked/partial reports, permission denials, process failures, and model limits stop. Exit 0 still requires independent Codex review.

Permission rules are auto-approval configuration, not an isolation boundary. Existing Claude settings, hooks, and repository instructions may apply. Host sandbox restrictions remain authoritative. API/provider billing depends on the active CLI authentication configuration; reported USD is not a guaranteed invoice cap.
