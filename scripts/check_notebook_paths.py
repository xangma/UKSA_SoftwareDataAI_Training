#!/usr/bin/env python3
"""Check course sources for local paths that will not work on CPD JupyterHub."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

PATH_RE = re.compile(
    r"(?<![\w:])/(?:Users|home|content|mnt|Volumes|opt|tmp)/[^\s'\"),`\]]+"
)
WINDOWS_DRIVE_RE = re.compile(r"\b[A-Za-z]:\\[^\s'\")]+")
COLAB_RE = re.compile(r"\bdrive\.mount\s*\(|Google Drive|MyDrive|gdrive", re.I)
CHDIR_RE = re.compile(r"\b(?:os\.)?chdir\s*\(")

ALLOWED_PATHS = (
    re.compile(r"^/home/jovyan/(?:data|shared)(?:/|$)"),
)

EXCLUDED_PARTS = {
    ".ipynb_checkpoints",
    "_build",
    "node_modules",
    "docs/build",
}


def tracked_sources() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files"], text=True)
    paths: list[Path] = []
    for line in output.splitlines():
        if any(part in line for part in EXCLUDED_PARTS):
            continue
        if line in {"package-lock.json", "JUPYTERBOOK_MIGRATION_PLAN.md"}:
            continue
        if line.endswith((".ipynb", ".md")):
            paths.append(Path(line))
    return paths


def source_from_cell(cell: dict) -> str:
    source = cell.get("source", "")
    if isinstance(source, list):
        return "".join(source)
    return source


def is_allowed_path(value: str) -> bool:
    normalized = value.rstrip(".,;:")
    return any(pattern.match(normalized) for pattern in ALLOWED_PATHS)


def scan_text(path: Path, text: str, *, cell_index: int | None = None) -> list[str]:
    findings: list[str] = []

    for regex, label in (
        (PATH_RE, "absolute path"),
        (WINDOWS_DRIVE_RE, "Windows path"),
        (COLAB_RE, "Google Drive/Colab storage"),
        (CHDIR_RE, "working-directory change"),
    ):
        for match in regex.finditer(text):
            value = match.group(0)
            if label == "absolute path" and is_allowed_path(value):
                continue
            line = text.count("\n", 0, match.start()) + 1
            location = f"{path}:"
            if cell_index is not None:
                location += f" cell {cell_index},"
            location += f" line {line}"
            findings.append(f"{location}: {label}: {value}")

    return findings


def main() -> int:
    findings: list[str] = []
    for path in tracked_sources():
        if path.suffix == ".ipynb":
            notebook = json.loads(path.read_text())
            for index, cell in enumerate(notebook.get("cells", [])):
                findings.extend(scan_text(path, source_from_cell(cell), cell_index=index))
        else:
            findings.extend(scan_text(path, path.read_text(errors="replace")))

    if findings:
        print("Hard-coded path or Colab storage references found:")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print("No unsupported hard-coded paths found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
