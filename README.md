# PROTzilla

> [!NOTE]
> This repository is still a work-in-progress version.<br> Please refer to the previous PROTzilla at https://github.com/cschlaffner/PROTzilla2.

[![backend](https://github.com/cschlaffner/PROTzilla/actions/workflows/backend_ci.yml/badge.svg)](https://github.com/cschlaffner/PROTzilla/actions/workflows/backend_ci.yml)
[![frontend](https://github.com/cschlaffner/PROTzilla/actions/workflows/frontend_ci.yml/badge.svg)](https://github.com/cschlaffner/PROTzilla/actions/workflows/frontend_ci.yml)
[![coverage badge](https://github.com/cschlaffner/PROTzilla/blob/python-coverage-comment-action-data/badge.svg)](https://github.com/cschlaffner/PROTzilla/tree/python-coverage-comment-action-data) 

PROTzilla is an open-source and browser-based tool for downstream proteomics MS analysis, enabling non-programmers to preprocess data, perform analyses, and generate publication-ready plots. The shareable, reproducible workflows and the integration of knowledge databases support automated analysis and transparent reporting in proteomics research.

## :gear: Deploy PROTzilla
1. Clone the PROTzilla repository <br> `git clone https://github.com/cschlaffner/PROTzilla.git`
2. Enter repository folder <br> `cd PROTzilla`

### :whale: Using Docker (recommended)
1. Make sure you have [Docker](https://www.docker.com/) and Docker Compose installed
2. Run `docker compose up --build` (or `docker-compose up --build` on old versions) <br> You can optionally add `-d` to detatch protzilla from your shell (useful for production environments)
3. (optional) If you want persistent user data storage, uncomment the volume specification in the `docker-compose.yml` and adjust for your system. Make sure to copy the repo contents in `/backend/user_data` over to your desired persistent directory first.

### Windows native 
> [!NOTE]
> We ensure native compatibility with Windows Server 2012. If you can run Docker on your system, please use Docker.

1. Double-click `run_protzilla.bat` or execute `.\run_protzilla.bat` in terminal <br>

### Linux/macOS native
> [!NOTE]
> This deployment script is kept for legacy reasons and might not work well on every kind of system.

1. Execute `./install_protzilla.sh` to install dependencies and set up the environment. Might take up to 15 minutes
2. Execute `./run_protzilla.sh` to run PROTzilla.

## &#x1F996; Start & use PROTzilla
If your deployment was successful, open the application on http://127.0.0.1:8000/. After that, you can start using PROTzilla for your research! &#x1F996;

## :bulb: Quick Introduction on how to use PROTzilla in the browser
**Workflows** in PROTzilla are blank templates that define a predefined sequence of parameterized steps, each **step** being a computation that takes data as input and produces according results. Steps are organized into Importing, Preprocessing, Analysis, and Integration sections. For your analysis, you can select a workflow to create a **run**, import your real data (and add extra steps if needed), then execute it. You can execute a run step by step or in one go with a single click on `Calculate` in the last step. PROTzilla also lets you generate and download **custom plots** and seamlessly integrate **UniProt databases** into your analysis.
> [!TIP]
> For more details, please see the [user guide in our wiki](https://github.com/cschlaffner/PROTzilla/wiki/User-Guide).

## :bulb: How to use PROTzilla via the command line
A command line based runner for PROTzilla workflows is available via `runner_cli.py`. It allows you to run PROTzilla workflows from the command line, which can be useful for batch processing or automation tasks. The runner calculates a given dataset on a given workflow without the need for a graphical user interface.

A guide on how to use the Runner is available in our [wiki](https://github.com/cschlaffner/PROTzilla/wiki/User-Guide#protzilla-as-a-command-line-tool).

## :mag: Further information: Development
The PROTzilla backend is built with Python/Django and Node.js (managed via pnpm) is used for the frontend. <br>
To open PROTzilla in development mode, run the `protzilla_dev` script for your OS. (In this mode, the frontend and backend servers are started, but code changes are dynamically included.)

- `http://localhost:5174/` is a dynamic version of the frontend.
- `http://127.0.0.1:8000/` is static and does not change without running `pnpm build` - as seen by a user.

Additionally, you can launch the storybook by `pnpm storybook` to inspect UI components independently.
