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

The default destination is `~/.agents/skills/codex-plan-claude-execute/`. See [Updating](#updating) to replace an existing installation.

To install into a project:

```bash
python3 install.py --dest /path/to/project/.agents/skills/codex-plan-claude-execute
```

Alternatively, register the cloned repository as a local marketplace with `codex plugin marketplace add .`, then run the plugin installation command above.

When switching installation methods, move the previous installation outside the skill search directories first.

</details>

## Updating

For the recommended GitHub marketplace installation:

```bash
codex plugin marketplace upgrade codex-plan-claude-execute-marketplace
codex plugin list
```

This fetches the latest marketplace repository and refreshes its installed plugin cache, including the skill. To update all configured Git marketplaces, run `codex plugin marketplace upgrade` without a marketplace name.

For a manual installation, run these commands from your cloned repository:

```bash
git pull --ff-only
python3 install.py --replace
```

The installer backs up the previous skill and prints its location. If you originally used `--dest`, pass the same destination when updating:

```bash
python3 install.py --replace --dest /path/to/project/.agents/skills/codex-plan-claude-execute
```

Running `git pull` alone does not update a manually installed skill because the installed directory is a separate copy. After updating, start a new Codex session to load the updated skill.

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
Use $codex-plan-claude-execute to add a dark mode toggle to this website.
Create a plan, have Claude Code implement it, then review and test the changes yourself.
```

Codex prepares the plan, invokes Claude Code, and checks the result. You do not need to run the execution script yourself.

## How it works

1. **Plan:** Codex reads project instructions and existing changes, then defines tasks and acceptance checks.
2. **Execute:** Claude Code implements the plan and reports completion or blockers.
3. **Validate:** The runner displays the acceptance commands and hash, executes them, and retries failed acceptance within the configured limits. Destructive-looking commands require explicit approval.
4. **Review:** Codex inspects the changes and evidence before declaring the task complete.

Existing authorization is respected. Claude Code starts with an explicit file-tool allowlist; additional command permissions are opt-in, and material scope changes are handled explicitly.

## Advanced usage

See the [runner reference](docs/runner.md) for direct execution, acceptance review and sandboxing, model and permission options, cost reporting, logs, and troubleshooting.
