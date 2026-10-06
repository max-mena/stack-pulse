#!/usr/bin/env python3
"""PostToolUse hook: format and lint-fix any Python file Claude just edited."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    payload = json.load(sys.stdin)
    path = payload.get("tool_input", {}).get("file_path", "")
    project = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
    if not path.endswith(".py") or shutil.which("uv") is None:
        return 0
    if not Path(path).resolve().is_relative_to(project):
        return 0

    subprocess.run(["uv", "run", "--quiet", "ruff", "format", path], check=False)
    result = subprocess.run(
        ["uv", "run", "--quiet", "ruff", "check", "--fix", path],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        # Surface remaining lint errors to Claude so it fixes them.
        print(result.stdout, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
