#!/usr/bin/env python3
"""Check tracked notebooks use kernels available on the CPD JupyterHub."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ALLOWED_KERNELS = {
    "python3": "python",
    "ml-env": "python",
    "c": "c",
}


def tracked_notebooks() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files", "*.ipynb"], text=True)
    return [
        Path(line)
        for line in output.splitlines()
        if "/.ipynb_checkpoints/" not in line
    ]


def main() -> int:
    invalid: list[str] = []
    for notebook_path in tracked_notebooks():
        notebook = json.loads(notebook_path.read_text())
        kernelspec = notebook.get("metadata", {}).get("kernelspec", {})
        kernel_name = kernelspec.get("name")
        if kernel_name not in ALLOWED_KERNELS:
            invalid.append(f"{notebook_path}: unsupported kernel {kernel_name!r}")
            continue

        expected_language = ALLOWED_KERNELS[kernel_name]
        kernel_language = kernelspec.get("language")
        if kernel_language and kernel_language != expected_language:
            invalid.append(
                f"{notebook_path}: kernel {kernel_name!r} has language "
                f"{kernel_language!r}, expected {expected_language!r}"
            )

    if invalid:
        print("Unsupported notebook kernels:")
        for issue in invalid:
            print(f"- {issue}")
        return 1

    print("All tracked notebooks use CPD-supported kernels.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
