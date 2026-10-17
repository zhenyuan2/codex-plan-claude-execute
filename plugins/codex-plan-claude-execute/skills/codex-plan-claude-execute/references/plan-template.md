# Current plan template

Keep one effective plan; prior runs preserve snapshots. Scale detail to task complexity.

````markdown
# Plan: <goal>

## Context and scope
- Execution root: <absolute directory>
- Relevant files and repository instructions: <paths and facts>
- Existing user changes to preserve: <baseline summary>
- Authorized actions: <implementation and any explicitly authorized external actions>
- Out of scope: <boundaries>
- Limits: <total model calls across invocations and time; optional user cost guidance is not enforced by the runner>

## Tasks
- <Expected change, relevant files, and observable completion criterion>

## Acceptance
<!-- ACCEPTANCE:BEGIN -->
```bash
# Runs once per completed attempt as a single bash -e -o pipefail script.
# Commands must be safe to repeat and runnable from the execution root.
# The runner prints this block and its SHA-256 before execution.
# Destructive commands require --allow-dangerous-acceptance; prefer a maintained script.
<meaningful validation commands>
```
<!-- ACCEPTANCE:END -->

## Review requirements
- <Behavior or artifacts requiring Codex inspection beyond automated checks>

## Revision notes
- <If revised: what changed, why, and which requirements it replaces>
````

Use exactly one complete acceptance block. Shell variables and working directory changes persist inside it. Normal Bash conditional/error-handling semantics still apply; do not suppress failures accidentally. For complex logic, call a maintained test script with meaningful exit codes. Avoid deployments, migrations, or other non-repeatable operations in acceptance.

Do not insert conversation-dependent references such as “as discussed”. State material constraints explicitly. The executor must report blocked if ambiguity affects scope, data, interfaces, or permissions.
