#!/usr/bin/env python3
"""Check local image references in tracked notebooks."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


IMAGE_RE = re.compile(
    r"!\[[^\]]*\]\(([^)]+)\)|<img[^>]+src=[\"']([^\"']+)[\"']",
    re.IGNORECASE,
)


def tracked_notebooks() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files", "*.ipynb"], text=True)
    return [
        Path(line)
        for line in output.splitlines()
        if "/.ipynb_checkpoints/" not in line
    ]


def is_local_reference(reference: str) -> bool:
    return bool(reference) and not (
        "://" in reference
        or reference.startswith("#")
        or reference.startswith("data:")
        or reference.startswith("mailto:")
    )


def main() -> int:
    missing: list[tuple[Path, str]] = []
    for notebook_path in tracked_notebooks():
        notebook = json.loads(notebook_path.read_text())
        for cell in notebook.get("cells", []):
            if cell.get("cell_type") != "markdown":
                continue
            source = "".join(cell.get("source", []))
            for match in IMAGE_RE.finditer(source):
                reference = (match.group(1) or match.group(2) or "").strip()
                if not is_local_reference(reference):
                    continue
                clean_reference = reference.split("#", 1)[0].split("?", 1)[0]
                if not (notebook_path.parent / clean_reference).exists():
                    missing.append((notebook_path, reference))

    if missing:
        print("Missing local image references:")
        for notebook_path, reference in missing:
            print(f"- {notebook_path}: {reference}")
        return 1

    print("No missing local image references found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
