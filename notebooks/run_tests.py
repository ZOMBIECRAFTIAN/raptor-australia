"""
Run the automated pytest suite with Windows-safe temporary directories.

Some Windows environments lock or deny access to the default pytest temp
folder, and reusing a fixed --basetemp can fail when pytest tries to delete
it. This wrapper uses a unique basetemp per run and disables pytest's cache
plugin so the test command is stable for local demos and defence checks.
"""

from __future__ import annotations

import os
import subprocess
import sys
import uuid
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


def main() -> int:
    temp_root = BASE_DIR / "results" / "pytest-temp"
    temp_root.mkdir(parents=True, exist_ok=True)
    basetemp = temp_root / f"run-{os.getpid()}-{uuid.uuid4().hex[:8]}"

    env = os.environ.copy()
    env["RAPTOR_LIGHTWEIGHT"] = "1"
    env["TMP"] = str(temp_root)
    env["TEMP"] = str(temp_root)

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests",
        "-q",
        "-p",
        "no:cacheprovider",
        "--basetemp",
        str(basetemp),
    ]
    return subprocess.run(cmd, cwd=str(BASE_DIR), env=env).returncode


if __name__ == "__main__":
    raise SystemExit(main())
