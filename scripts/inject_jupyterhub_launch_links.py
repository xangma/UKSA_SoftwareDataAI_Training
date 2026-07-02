#!/usr/bin/env python3
"""Inject per-notebook CPD JupyterHub launch links into built MyST HTML."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import quote, urlencode


BUILD_DIR = Path("_build/html")
HTML_ENTRYPOINT = "index.html"
HUB_URL = "https://icg-cpd-cluster.port.ac.uk/jupyterhub"
REPO_URL = "https://github.com/xangma/UKSA_SoftwareDataAI_Training"
REPO_DIR = "UKSA_SoftwareDataAI_Training"
BRANCH = "main"
ROOT_PATH = "/jupyterbook"
THEBE_BOOTSTRAP_URL = f"{HUB_URL}/services/uksa-thebe/bootstrap"
MARKER_START = "<!-- cpd-jupyterhub-launch-links:start -->"
MARKER_END = "<!-- cpd-jupyterhub-launch-links:end -->"


def launch_url(source_path: str | None = None) -> str:
    target = REPO_DIR
    if source_path:
        target = f"{REPO_DIR}/{source_path.strip('/')}"
    query = urlencode(
        {
            "repo": REPO_URL,
            "branch": BRANCH,
            "urlpath": f"lab/tree/{target}?autodecode",
        },
        quote_via=quote,
    )
    return f"{HUB_URL.rstrip('/')}/hub/user-redirect/git-pull?{query}"


def extract_project(html_text: str) -> dict:
    marker = '"project":'
    start = html_text.find(marker)
    if start == -1:
        raise ValueError("Could not find MyST project metadata in built HTML")
    project, _ = json.JSONDecoder().raw_decode(html_text[start + len(marker) :])
    if not isinstance(project, dict):
        raise ValueError("MyST project metadata was not a JSON object")
    return project


def iter_visible_files(items: list[dict]) -> list[str]:
    files: list[str] = []
    for item in items:
        if item.get("hidden"):
            continue
        if "file" in item:
            files.append(item["file"])
        files.extend(iter_visible_files(item.get("children", [])))
    return files


def notebook_routes(project: dict) -> dict[str, str]:
    files = [
        file
        for file in iter_visible_files(project.get("toc", []))
        if file != "index.md"
    ]
    pages = [page for page in project.get("pages", []) if "slug" in page]
    if len(files) != len(pages):
        raise ValueError(
            f"Could not align MyST TOC files ({len(files)}) with pages ({len(pages)})"
        )

    routes: dict[str, str] = {}
    for file, page in zip(files, pages):
        if file.endswith(".ipynb"):
            routes[page["slug"]] = launch_url(file)
    return routes


def injected_script(routes: dict[str, str]) -> str:
    routes_json = json.dumps(routes, sort_keys=True, separators=(",", ":"))
    default_url = json.dumps(launch_url())
    root_path = json.dumps(ROOT_PATH.rstrip("/"))
    thebe_bootstrap_url = json.dumps(THEBE_BOOTSTRAP_URL)
    return f"""{MARKER_START}
<script id="cpd-jupyterhub-launch-links">
(() => {{
  const rootPath = {root_path};
  const defaultUrl = {default_url};
  const thebeBootstrapUrl = {thebe_bootstrap_url};
  const notebookUrls = {routes_json};

  function currentSlug() {{
    let path = window.location.pathname.replace(/\\/$/, "");
    if (path === rootPath || path === "") return "";
    if (path.startsWith(rootPath + "/")) path = path.slice(rootPath.length + 1);
    return decodeURIComponent(path.replace(/^\\/+/, "").replace(/\\/$/, ""));
  }}

  function currentNotebookUrl() {{
    return notebookUrls[currentSlug()] || "";
  }}

  function authReturnUrl() {{
    const url = new URL(window.location.href);
    url.searchParams.set("thebe", "1");
    return url.toString();
  }}

  function bootstrapUrl() {{
    const url = new URL(thebeBootstrapUrl);
    url.searchParams.set("return", authReturnUrl());
    return url.toString();
  }}

  function findLaunchLink() {{
    for (const link of document.querySelectorAll("a")) {{
      if (link.textContent.trim() !== "Open in JupyterHub") continue;
      if (link.href.includes("/hub/user-redirect/git-pull")) return link;
    }}
    return null;
  }}

  function removeLiveCodeLink() {{
    document.querySelectorAll("[data-cpd-thebe-bootstrap]").forEach((node) => node.remove());
  }}

  function updateLiveCodeLink() {{
    const notebookUrl = currentNotebookUrl();
    if (!notebookUrl) {{
      removeLiveCodeLink();
      return;
    }}

    const launchLink = findLaunchLink();
    if (!launchLink) return;

    let link = launchLink.parentElement?.querySelector("[data-cpd-thebe-bootstrap]");
    if (!link) {{
      link = launchLink.cloneNode(false);
      link.dataset.cpdThebeBootstrap = "true";
      link.textContent = "Connect JupyterHub";
      launchLink.insertAdjacentElement("afterend", link);
    }}
    link.setAttribute("href", bootstrapUrl());
    link.removeAttribute("target");
    link.removeAttribute("rel");
    link.title = "Authenticate with CPD JupyterHub for in-page code execution";
    link.setAttribute("aria-label", "Connect CPD JupyterHub for live code");
  }}

  function updateLaunchLinks() {{
    const href = currentNotebookUrl() || defaultUrl;
    for (const link of document.querySelectorAll("a")) {{
      if (link.textContent.trim() !== "Open in JupyterHub") continue;
      if (!link.href.includes("/hub/user-redirect/git-pull")) continue;
      if (link.getAttribute("href") !== href) link.setAttribute("href", href);
      link.title = notebookUrls[currentSlug()]
        ? "Open this notebook in CPD JupyterHub"
        : "Open the course in CPD JupyterHub";
    }}
    updateLiveCodeLink();
  }}

  let pending = false;
  function scheduleUpdate() {{
    if (pending) return;
    pending = true;
    requestAnimationFrame(() => {{
      pending = false;
      updateLaunchLinks();
    }});
  }}

  for (const method of ["pushState", "replaceState"]) {{
    const original = history[method];
    history[method] = function (...args) {{
      const result = original.apply(this, args);
      scheduleUpdate();
      return result;
    }};
  }}

  window.addEventListener("popstate", scheduleUpdate);
  document.addEventListener("DOMContentLoaded", updateLaunchLinks);
  new MutationObserver(scheduleUpdate).observe(document.documentElement, {{
    childList: true,
    subtree: true,
  }});
  updateLaunchLinks();
}})();
</script>
{MARKER_END}"""


def inject(html_path: Path, script: str) -> bool:
    original = html_path.read_text(encoding="utf-8")
    html = re.sub(
        rf"{re.escape(MARKER_START)}.*?{re.escape(MARKER_END)}\n?",
        "",
        original,
        flags=re.DOTALL,
    )
    if "</body>" not in html:
        raise ValueError(f"{html_path} does not contain </body>")
    updated = html.replace("</body>", f"{script}\n</body>", 1)
    changed = updated != original
    if changed:
        html_path.write_text(updated, encoding="utf-8")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", type=Path, default=BUILD_DIR)
    args = parser.parse_args()

    entrypoint = args.build_dir / HTML_ENTRYPOINT
    project = extract_project(entrypoint.read_text(encoding="utf-8"))
    routes = notebook_routes(project)
    script = injected_script(routes)

    changed = 0
    for html_path in args.build_dir.rglob("*.html"):
        changed += int(inject(html_path, script))
    print(f"Injected {len(routes)} CPD notebook launch routes into {changed} HTML file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
