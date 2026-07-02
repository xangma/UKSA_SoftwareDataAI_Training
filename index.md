# UKSA Software, Data and AI Training

This book collects the public course materials for the UK Space Agency Software, Data and AI CPD programme.

The rendered site is intended as the course navigation and reading layer. Learners should run notebooks on the CPD JupyterHub so they use the shared course image and mounted course data rather than setting up local environments.

## Run the notebooks

[Open the course in CPD JupyterHub][cpd-launch].

This link uses nbgitpuller to clone or update the repository in the learner's JupyterHub home directory and open it in JupyterLab.

The Hub image includes the course runtime, including the `python3`, `ml-env`, and `c` kernels. User home directories and the shared `/home/jovyan/data` and `/home/jovyan/shared` mounts are persistent.

## Build policy

The book is built as static HTML with notebook execution disabled. Notebook outputs that are already saved in the repository are rendered into the site. Full build-time execution is intentionally deferred until credentials, data paths, GPU assumptions, and long-running notebooks are made deterministic.

## Migration notes

The migration plan is tracked in [JUPYTERBOOK_MIGRATION_PLAN.md](JUPYTERBOOK_MIGRATION_PLAN.md).

[cpd-launch]: https://icg-cpd-cluster.port.ac.uk/jupyterhub/hub/user-redirect/git-pull?repo=https%3A%2F%2Fgithub.com%2Fxangma%2FUKSA_SoftwareDataAI_Training&branch=main&urlpath=lab%2Ftree%2FUKSA_SoftwareDataAI_Training%3Fautodecode
