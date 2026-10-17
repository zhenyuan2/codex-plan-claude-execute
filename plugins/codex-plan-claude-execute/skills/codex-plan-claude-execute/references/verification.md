# Independent Codex review

1. Read the run's `summary.json`, per-attempt report, acceptance stdout/stderr, and acceptance SHA-256. Exit 0 means automated acceptance passed, not that the task is complete. Confirm the hash matches the commands the user approved; treat a mismatch as a blocker.
2. Compare actual changes with the saved `before.*` baseline. Inspect unstaged and staged diffs and the contents of new files. Preserve pre-existing user changes; do not attribute the entire working tree to Claude. For non-Git work, arrange relevant file copies or hashes before execution and compare them afterward.
3. Check each completion criterion, out-of-scope changes, deleted/skipped/weakened tests, and altered validation tooling. Review the implementation, not only the report or diff statistics. A snapshot hash is provenance, not isolation from an executor that can write files.
4. Assess validation evidence. Re-run targeted checks when changes, uncertain evidence, or significant risk justify it. Do not blindly repeat expensive or side-effectful commands. If acceptance is not safe to repeat, correct the plan before invoking the runner.
5. Record the review verdict separately from machine acceptance status. If repairs are needed, revise the current plan and count new invocations against remaining task limits; do not silently reset task limits. Report blockers with the logs and decisions needed to proceed.

Plans/logs can contain private project information. Keep them local and out of commits unless the user wants them included. The runner adds local `.git/info/exclude` entries for its plan artifacts; it does not modify tracked ignore rules or automatically clean the working tree.
