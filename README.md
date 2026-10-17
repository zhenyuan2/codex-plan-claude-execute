# codex-plan-claude-execute

**Codex plans → Claude Code implements → Codex verifies.**

An installable Codex skill for delegating implementation to Claude Code CLI, with independent acceptance checks, bounded repair attempts, and per-attempt logs. It uses Claude Code's configured default model unless you explicitly select one.

Install this skill into **Codex**, not Claude Code: Codex orchestrates the task and Claude Code executes it.

## Quick install from GitHub

Add the marketplace, install the plugin, and verify that it is listed:

```bash
codex plugin marketplace add zhenyuan2/codex-plan-claude-execute
codex plugin add codex-plan-claude-execute@codex-plan-claude-execute-marketplace
codex plugin list
```

No manual clone is required for this method. Your Codex CLI must support `codex plugin`. If it does not, use the direct skill installation below.

Choose either plugin installation or direct installation to avoid duplicate skill discovery. If switching from an existing direct installation, back it up and move it outside the skill search directories first.

## Requirements

- macOS or Linux, Python 3.8+, and Bash.
- Claude Code installed and authenticated; `claude --version` should work.
- Network access to the configured model service and permission for Claude Code to write its session state.
- Codex, with plugin commands available if using marketplace installation.

The installer does not install dependencies or change authentication settings.

## Usage

In Codex, ask:

```text
Use $codex-plan-claude-execute to inspect this project and make a plan,
delegate implementation to Claude Code, then verify the result.

Task: Add pagination to the existing search API and cover it with relevant tests.
```

### Workflow

1. **Plan:** Codex reads repository instructions and existing changes, then writes a self-contained plan with completion criteria and one acceptance block.
2. **Implement:** Claude Code implements the plan and reports whether it is done, partial, or blocked.
3. **Validate and repair:** The runner executes acceptance checks. Only failed acceptance after a completed implementation triggers automatic repair, within the configured limits.
4. **Review:** Codex inspects the actual changes and validation evidence before declaring the task complete.

Existing execution authorization is respected. Material scope changes or additional permissions still require explicit handling.

## Alternative installation methods

### Direct skill installation

Clone the repository and run the installer:

```bash
git clone https://github.com/zhenyuan2/codex-plan-claude-execute.git
cd codex-plan-claude-execute
python3 install.py
```

The default destination is `~/.agents/skills/codex-plan-claude-execute/`. Existing installations are not overwritten by default.

To replace an existing installation and back it up first:

```bash
python3 install.py --replace
```

Backups are stored in `.skill-backups/` next to the parent skills directory. The installer prints the exact backup path.

To install into a specific project, provide the full destination skill directory:

```bash
python3 install.py --dest /path/to/project/.agents/skills/codex-plan-claude-execute
```

Direct installation only copies files. It does not invoke a model or modify Codex configuration.

### Local marketplace installation

From the cloned repository root:

```bash
codex plugin marketplace add .
codex plugin add codex-plan-claude-execute@codex-plan-claude-execute-marketplace
```

The package uses the compatible `.claude-plugin/marketplace.json` and plugin manifest structure. Codex remains the intended host.

## Runner options

The runner is located at:

```text
plugins/codex-plan-claude-execute/skills/codex-plan-claude-execute/scripts/run-claude.sh
```

| Option | Purpose |
|---|---|
| `--repo PATH` | Explicit execution directory |
| `--attempts N` | Maximum model calls per runner invocation; default: 3 |
| `--max-turns N` | Maximum turns per Claude call; default: 60 |
| `--timeout SECONDS` | Total model and acceptance runtime; default: 1800 seconds |
| `--max-budget USD` | Optional cumulative CLI-reported cost budget per invocation |
| `--model NAME` | Optional Claude model override |
| `--allowed-tool RULE` | Additional auto-approved tool rule; repeatable |

### Budget accounting

`--max-budget` uses Claude's `total_cost_usd`; it is not a hard billing cap. The runner currently adds the cost reported by each call. Cost reporting after `--resume` has not been verified against a real model session: if the CLI returns cumulative session cost, the runner may stop early. Do not use this as precise financial accounting.

### Permissions

File tools are auto-approved by default. Add command permissions only as needed for the task. Tool approval is not an operating-system sandbox and does not implicitly authorize pushing code, deploying, or other external actions.

## Logs and exit codes

Runs are saved under the project's `.plans/runs/<unique-run>/` directory, including:

- Plan and acceptance snapshots.
- A Git baseline when available.
- Per-attempt model output and acceptance logs.
- A machine-readable summary.

| Exit code | Meaning |
|---|---|
| `0` | Automated acceptance passed; independent Codex review is still required |
| `1` | Execution stopped, timed out, was blocked, or exhausted repair attempts |
| `2` | Argument, environment, plan, or output-protocol error |

## Check the runner

From the repository root:

```bash
bash plugins/codex-plan-claude-execute/skills/codex-plan-claude-execute/scripts/run-claude.sh --help
```

Development tests are kept locally and excluded from Git distribution. They are not required to run the skill. Offline checks have been completed; real-model end-to-end validation has not.

## Repository structure

```text
.claude-plugin/marketplace.json
plugins/codex-plan-claude-execute/
  .claude-plugin/plugin.json
  skills/codex-plan-claude-execute/
    SKILL.md
    LICENSE
    agents/openai.yaml
    references/
    scripts/
install.py
LICENSE
README.md
```

## Uninstall

For a direct installation, move the installed `codex-plan-claude-execute` directory outside the skill search directories.

For a plugin installation:

```bash
codex plugin remove codex-plan-claude-execute@codex-plan-claude-execute-marketplace
```

## References

- [cc-skill-codex](https://github.com/wywwzjj/cc-skill-codex) — inspiration for the marketplace/plugin/skill packaging structure. This project implements only the Codex → Claude Code planning and execution workflow.
- [OpenAI plugin documentation](https://developers.openai.com/codex/plugins/).

## License

[MIT](LICENSE).
