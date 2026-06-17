# Jupyter Book Migration Plan

Date: 2026-06-17

## Goal

Move this course repository to a modern Jupyter Book / MyST site that acts as the public navigation and reading layer, while CPD JupyterHub remains the execution environment for learners.

The first production target is a static rendered book with notebook execution disabled. Full build-time execution can be added later for selected notebooks once credentials, data paths, long-running computations, and hardware assumptions are deterministic.

## Current Position

The CPD cluster side is ready for this migration:

- JupyterHub is deployed with the new course runtime image.
- The image is pinned in GitOps by immutable digest.
- The image is pre-pulled on all six cluster nodes.
- Kernels available in the deployed image include `python3`, `ml-env`, and `c`.
- `jupyter-book`, `jupytext`, `nbgitpuller`, Node.js, geospatial packages, Earth Engine/geemap, Sentinel Hub, TensorFlow, Torch, HDBSCAN, OSMnx, Rasterio, and Ultralytics were smoke-tested in the cluster runtime.
- Existing user and shared PVC data was verified as still mounted and readable.

Initial repo findings before this migration branch:

- The current docs setup is Sphinx/ReadTheDocs based.
- Only a small subset of the teaching content is in the existing docs TOC.
- There are 40 real tracked notebooks plus 10 tracked checkpoint notebooks.
- Tracked generated/noise files include `.ipynb_checkpoints`, `.DS_Store`, and `docs/build`.
- Notebook kernels include `python3`, `ml-env`, and `c` in the real tracked notebooks, with unsupported kernels appearing only in generated/noise files.
- Most notebooks already contain outputs, which supports static rendering.
- Five missing local image references were found:
  - `UKSA_SoftwareDataAI_Training/Bridging_Course/Anatomy_of_a_NN_BC.ipynb`: `AI_ML_NN_DL.png`
  - `UKSA_SoftwareDataAI_Training/Bridging_Course/EarthEngineAPI.ipynb`: `MODIS_data_cat_snapshot.png`
  - `UKSA_SoftwareDataAI_Training/Resources/Navigating_the_notebooks.ipynb`: `git_clone.png`
  - `UKSA_SoftwareDataAI_Training/Resources/Navigating_the_notebooks.ipynb`: `Pull_request.png`
  - `UKSA_SoftwareDataAI_Training/Resources/Navigating_the_notebooks.ipynb`: `Github_pic.png`

## Current Jupyter Book Guidance

Use the modern Jupyter Book 2 / MyST workflow:

- New projects should use `myst.yml`.
- The table of contents should be defined under `project.toc`, or in a separate file included with `extends`.
- Build static HTML with `myst build --html`.
- Keep `_build/` out of git.
- Notebook execution is disabled by default and should only be enabled explicitly with `--execute`.
- Build-time execution requires Jupyter Server and matching kernels.
- MyST launch buttons exist via `project.jupyter: true`, but the UX is still experimental. For this course, explicit JupyterHub/nbgitpuller links should be treated as the reliable launch path.

Useful references:

- https://jupyterbook.org/stable/authoring/table-of-contents/
- https://mystmd.org/guide/execute-notebooks
- https://mystmd.org/guide/deployment
- https://mystmd.org/guide/website-launch-buttons
- https://nbgitpuller.readthedocs.io/en/latest/

## Action Plan

### 1. Repo Hygiene

- [x] Add or repair `.gitignore` entries for `.DS_Store`, `.ipynb_checkpoints/`, `docs/build/`, `_build/`, `node_modules/`, and MyST execution caches.
- [x] Remove tracked generated files with `git rm` where appropriate.
- [x] Finish final review of checkpoint-only source deltas before committing checkpoint deletions. The C colab checkpoint-only cells already exist in the real Colab notebook and equivalent C-kernel notebook; the Python introduction checkpoint-only text is stale Computational Physics source text and should not be carried forward.
- [x] Keep real notebooks and intentional static assets only.

### 2. Jupyter Book Scaffold

- [x] Add `myst.yml` at the repository root.
- [x] Use `site.template: book-theme`.
- [x] Add project metadata: title, description, repository, and Jupyter launch support. Authors/maintainers and license still need confirming if they should appear in public metadata.
- [x] Define a curated `project.toc`.
- [x] Stop using the old Sphinx docs path in ReadTheDocs.
- [ ] Decide whether to delete or archive legacy `docs/source` files after the MyST site is accepted. The logo is still reused from that path.

### 3. Course Structure

- [x] Add a clear `index.md` landing page.
- [x] Organize the book around the learner journey: resources, bridging course, programming foundations, and cohort-specific materials.
- [x] Keep notebook files in their current locations initially to avoid breaking relative paths and launch links.
- [ ] Add or normalize notebook titles/frontmatter where needed.

### 4. Content Fixes

- [x] Restore or replace the five missing images.
- [x] Validate kernelspecs against cluster-supported names: `python3`, `ml-env`, and `c`.
- [x] Confirm unsupported kernels only appeared in generated/noise files, not in the real tracked notebooks.
- [x] Add a CI guard so future notebooks fail if they use unsupported kernels.
- [ ] Audit hard-coded paths so notebooks intentionally use repo-relative paths, `/home/jovyan/data`, or `/home/jovyan/shared`.
- [ ] Clean notebook warning sources: duplicate cell/output identifiers, missing heading-depth structure, and the oversized GIF warning.

### 5. Static Build and CI

- [x] Build first with execution disabled: `myst build --html`.
- [x] Add docs build dependencies separate from the teaching runtime.
- [x] Add CI for the static MyST/Jupyter Book build.
- [x] Add CI for missing local asset checks.
- [x] Add CI for tracked generated-file checks.
- [x] Add CI for notebook kernelspec checks.

### 6. JupyterHub Integration

- [x] Add an explicit course-level launch link using CPD JupyterHub and nbgitpuller.
- [x] Generate launch URLs from a script so repo paths, branch names, and URL encoding stay correct.
- [x] Prefer JupyterLab as the opened interface.
- [x] Enable `project.jupyter: true` as a secondary convenience, not the primary course launch mechanism.
- [x] Verify the rendered site exposes the expected CPD JupyterHub launch links.
- [ ] Add page-specific launch links for key notebooks if instructors want one-click notebook-level entry points beyond the course-level launch.
- [ ] Test an authenticated launch against `https://icg-cpd-cluster.port.ac.uk/jupyterhub/`.

### 7. Later: Controlled Execution

- [x] Do not make full build-time execution a first release blocker.
- [ ] Add a small smoke-execution subset once the static book is stable.
- [ ] Only consider full `myst build --execute --html` after credentials, data availability, GPU assumptions, and long-running notebooks are made deterministic.

## First Implementation PRs

1. [x] Hygiene and ignore rules.
2. [x] MyST scaffold and initial TOC.
3. [x] Missing assets and kernelspec validation.
4. [x] Static build CI.
5. [x] Course-level JupyterHub launch link.
6. [ ] Remaining content polish and optional notebook-level launch links.

## Progress in `codex/jupyterbook-migration`

- Added MyST/Jupyter Book 2 scaffold at the repo root.
- Added a curated static-book TOC covering resources, bridging content, programming foundations, and cohort material.
- Added a course landing page with a CPD JupyterHub nbgitpuller launch link.
- Replaced the old Sphinx ReadTheDocs build with a MyST static HTML build.
- Added GitHub Actions docs build checks.
- Added repository hygiene, missing local image, and CPD-supported kernelspec checks.
- Restored the missing local image assets referenced by notebooks.
- Removed tracked `.DS_Store`, `.ipynb_checkpoints`, and `docs/build` artifacts.
- Reviewed checkpoint-only source deltas and confirmed there is no course content that needs to be rescued before deleting checkpoints.
