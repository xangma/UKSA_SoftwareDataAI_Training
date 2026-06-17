#!/usr/bin/env python3
"""Generate CPD JupyterHub nbgitpuller launch URLs for this course."""

from __future__ import annotations

import argparse
from pathlib import PurePosixPath
from urllib.parse import urlencode, urlparse


DEFAULT_BRANCH = "main"
DEFAULT_HUB_URL = "https://icg-cpd-cluster.port.ac.uk/jupyterhub"
DEFAULT_REPO_URL = "https://github.com/reac2/UKSA_SoftwareDataAI_Training"


def repo_directory(repo_url: str) -> str:
    path = urlparse(repo_url).path.rstrip("/")
    name = PurePosixPath(path).name
    if name.endswith(".git"):
        name = name[:-4]
    if not name:
        raise ValueError(f"Could not infer repository directory from {repo_url!r}")
    return name


def build_url(hub_url: str, repo_url: str, branch: str, open_path: str) -> str:
    hub_base = hub_url.rstrip("/")
    repo_dir = repo_directory(repo_url)
    clean_path = open_path.strip("/")
    target = repo_dir if clean_path in {"", "."} else f"{repo_dir}/{clean_path}"
    query = urlencode(
        {
            "repo": repo_url,
            "branch": branch,
            "urlpath": f"lab/tree/{target}?autodecode",
        }
    )
    return f"{hub_base}/hub/user-redirect/git-pull?{query}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Repo-relative notebook, file, or directory to open.",
    )
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    parser.add_argument("--hub-url", default=DEFAULT_HUB_URL)
    parser.add_argument("--repo-url", default=DEFAULT_REPO_URL)
    args = parser.parse_args()
    print(build_url(args.hub_url, args.repo_url, args.branch, args.path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
