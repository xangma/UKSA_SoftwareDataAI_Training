#!/usr/bin/env python3
"""Fail if generated local artifacts are tracked by git."""

from __future__ import annotations

import subprocess
import sys


NOISE_PATTERNS = (
    "/.ipynb_checkpoints/",
    "docs/build/",
)


def is_noise(path: str) -> bool:
    return (
        path == ".DS_Store"
        or path.endswith("/.DS_Store")
        or any(pattern in path for pattern in NOISE_PATTERNS)
        or path.startswith("docs/build/")
        or path.startswith("_build/")
    )


def main() -> int:
    output = subprocess.check_output(["git", "ls-files"], text=True)
    noise = sorted(path for path in output.splitlines() if is_noise(path))
    if noise:
        print("Tracked generated/noise files:")
        for path in noise:
            print(f"- {path}")
        return 1

    print("No tracked generated/noise files found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
