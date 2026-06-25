#!/usr/bin/env python3
"""Check notebook metadata that can create unstable MyST anchors."""

from __future__ import annotations

import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


def tracked_notebooks() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files", "*.ipynb"], text=True)
    return [
        Path(line)
        for line in output.splitlines()
        if "/.ipynb_checkpoints/" not in line
    ]


def main() -> int:
    values: dict[str, dict[str, list[str]]] = {
        "metadata.id": defaultdict(list),
        "metadata.outputId": defaultdict(list),
    }
    for notebook_path in tracked_notebooks():
        notebook = json.loads(notebook_path.read_text())
        for index, cell in enumerate(notebook.get("cells", [])):
            metadata = cell.get("metadata", {})
            if not isinstance(metadata, dict):
                continue
            for field, label in (("id", "metadata.id"), ("outputId", "metadata.outputId")):
                value = metadata.get(field)
                if value:
                    values[label][value].append(f"{notebook_path}: cell {index}")

    duplicates: list[str] = []
    for label, seen in values.items():
        for value, locations in sorted(seen.items()):
            if len(locations) > 1:
                duplicates.append(f"{label} {value!r}: {', '.join(locations)}")

    if duplicates:
        print("Duplicate notebook metadata identifiers:")
        for duplicate in duplicates:
            print(f"- {duplicate}")
        return 1

    print("No duplicate notebook metadata identifiers found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
