#!/usr/bin/env bash
# Python owns validation, process supervision, and exit status.
set -eu
command -v python3 >/dev/null 2>&1 || { echo 'error: python3 is required' >&2; exit 2; }
exec python3 "$(cd "$(dirname "$0")" && pwd)/run_claude.py" "$@"
