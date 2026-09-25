#!/usr/bin/env python3
"""PreToolUse hook: block destructive, costly or secret-leaking shell commands.

Exit code 2 blocks the command and shows the reason to Claude.
"""

import json
import re
import sys

RULES: list[tuple[str, str]] = [
    (r"\bbq\s+(\S+\s+)*rm\b", "deleting BigQuery datasets/tables"),
    (r"\bDROP\s+(TABLE|SCHEMA|DATASET|VIEW)\b", "DROP statements"),
    (r"--full-refresh\b", "dbt full refresh (rebuilds tables; run it in CI or by hand)"),
    (r"\bdbt\s+\S+.*--target\s+prod\b", "dbt against the prod target"),
    (r"\bgit\s+push\b.*(\s-f\b|--force)", "force push"),
    (r"\bgit\s+push\b.*\bmain\b", "pushing to main directly (open a PR)"),
    (
        r"\b(cat|less|more|head|tail|grep|source|strings)\b[^|;&]*(^|[\s/])\.env($|[\s;|&])",
        "reading .env secrets",
    ),
    (r"\.config/gcloud", "reading gcloud credentials"),
]


def main() -> int:
    payload = json.load(sys.stdin)
    command = payload.get("tool_input", {}).get("command", "")
    for pattern, reason in RULES:
        if re.search(pattern, command, flags=re.IGNORECASE):
            print(
                f"Blocked by stack-pulse guard: {reason}. Ask the user to run it.", file=sys.stderr
            )
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
