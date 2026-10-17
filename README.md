# codex-plan-claude-execute

**Codex plans. Claude Code implements. Codex reviews.**

Delegate implementation to Claude Code while Codex owns the plan and final review. Automated acceptance checks and bounded repair attempts help verify the changes before you get the result.

## Requirements

- **Codex**, with `codex plugin` support for marketplace installation.
- **Claude Code**, installed and authenticated.
- **macOS or Linux**, with Python 3.8+ and Bash.

Claude Code needs access to its configured model service and permission to save session state. Your configured Claude model is used by default.

## Installation

Install into **Codex** by adding the GitHub marketplace and its plugin:

```bash
codex plugin marketplace add zhenyuan2/codex-plan-claude-execute
codex plugin add codex-plan-claude-execute@codex-plan-claude-execute-marketplace
codex plugin list
```

No manual clone is needed. Choose one installation method to avoid duplicate skills.

<details>
<summary>Manual and project-level installation</summary>

Clone the repository and install the standalone skill:

```bash
git clone https://github.com/zhenyuan2/codex-plan-claude-execute.git
cd codex-plan-claude-execute
python3 install.py
```

The default destination is `~/.agents/skills/codex-plan-claude-execute/`. To update an existing installation, use `python3 install.py --replace`; the installer backs up the old version and prints its location.

To install into a project:

```bash
python3 install.py --dest /path/to/project/.agents/skills/codex-plan-claude-execute
```

Alternatively, register the cloned repository as a local marketplace with `codex plugin marketplace add .`, then run the plugin installation command above.

When switching installation methods, move the previous installation outside the skill search directories first.

</details>

<details>
<summary>Uninstall</summary>

For a plugin installation:

```bash
codex plugin remove codex-plan-claude-execute@codex-plan-claude-execute-marketplace
```

For a manual installation, move the installed skill directory outside the skill search directories.

</details>

## Usage

Ask Codex:

```text
Use $codex-plan-claude-execute to add pagination to the search API.
Have Claude Code implement the changes, then review and verify the result.
```

Codex prepares the plan, invokes Claude Code, and checks the result. You do not need to run the execution script yourself.

## How it works

1. **Plan:** Codex reads project instructions and existing changes, then defines tasks and acceptance checks.
2. **Execute:** Claude Code implements the plan and reports completion or blockers.
3. **Validate:** The runner executes the checks and retries failed acceptance within the configured limits.
4. **Review:** Codex inspects the changes and evidence before declaring the task complete.

Existing authorization is respected. Additional permissions or material scope changes are handled explicitly.

## Advanced usage

See the [runner reference](docs/runner.md) for direct execution, model and permission options, budgets, logs, and troubleshooting.
