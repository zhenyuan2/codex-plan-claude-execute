# codex-plan-claude-execute

Codex plans and reviews; Claude Code implements in headless mode. Invoke with `$codex-plan-claude-execute`. See `SKILL.md` for the workflow and authorization rules.

Requires Python 3, Bash, and an installed/authenticated Claude Code CLI supporting `--max-turns`, `--output-format json`, `--permission-mode dontAsk`, and `--allowedTools`. CLI failures stop without automatic retries.

```bash
bash scripts/run-claude.sh --help
```

Development tests are local-only and are not included in Git distribution. Runtime execution does not require them.

Flags: `--repo PATH`, `--attempts N` (3), `--max-turns N` (60), `--timeout SECONDS` (1800), `--model NAME`, repeated `--allowed-tool RULE`, `--show-acceptance`, `--acceptance-sha256 HASH`, `--allow-dangerous-acceptance`, `--pass-environment`, `--acceptance-wrapper TEMPLATE`.

Migration from 0.3: the runner now uses `dontAsk` with an explicit file-tool allowlist instead of `acceptEdits`; add task-needed command rules with `--allowed-tool`. Migration from 0.2: `--max-budget` and total cost enforcement were removed. Use `--max-turns` and `--timeout` as limits; per-attempt cost estimates remain in the logs. Migration from 0.1: `--loose` and space-split `--allowed-tools` were removed. Add individual task-needed rules with `--allowed-tool`. Plans must contain exactly one acceptance block; update the current plan rather than appending additional blocks. Acceptance runs as one Bash script with `-e -o pipefail`. Python is required for strict result parsing. Logs now live in unique `.plans/runs/` directories.

Acceptance safety: the runner prints the acceptance block and SHA-256 before executing. Use `--show-acceptance` to inspect it and `--acceptance-sha256` to bind execution to the approved hash. Dangerous patterns — pipe-to-shell, recursive deletes, `git push`/`reset --hard`/`clean -f`, privilege escalation, remote access or upload, publish, container push, deployment commands, and disk utilities — are refused unless `--allow-dangerous-acceptance` is supplied after review. Acceptance runs with credential-like environment variables and loader hooks removed by default; `--pass-environment` opts out. `--acceptance-wrapper` runs acceptance through an external sandbox such as Docker or bubblewrap.

Only failed acceptance after a completed report triggers automatic repair. Malformed output, blocked/partial reports, permission denials, process failures, and model limits stop. Exit 0 still requires independent Codex review. The runner adds local `.git/info/exclude` entries for its plan artifacts; tracked ignore rules are not modified.

Permission rules are auto-approval configuration, not an isolation boundary. The runner uses `dontAsk` mode with an explicit `Read`/`Edit`/`Write`/`Glob`/`Grep` allowlist; commands that would require approval, including `rm`, `mv`, `cp`, and `sed`, are denied unless explicitly allowed with `--allowed-tool`. The CLI's built-in read-only command set may still run without approval. Existing Claude settings, hooks, and repository instructions may apply. Host sandbox restrictions remain authoritative. Reported cost estimates are not billing data; API/provider billing depends on the active CLI authentication configuration.
