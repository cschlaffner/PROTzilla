# PROTzilla

> [!NOTE]
> This repository is still a work-in-progress version.<br> Please refer to the previous PROTzilla at https://github.com/cschlaffner/PROTzilla2.

[![backend](https://github.com/cschlaffner/PROTzilla/actions/workflows/backend_ci.yml/badge.svg)](https://github.com/cschlaffner/PROTzilla/actions/workflows/backend_ci.yml)
[![frontend](https://github.com/cschlaffner/PROTzilla/actions/workflows/frontend_ci.yml/badge.svg)](https://github.com/cschlaffner/PROTzilla/actions/workflows/frontend_ci.yml)
[![coverage badge](https://github.com/cschlaffner/PROTzilla/blob/python-coverage-comment-action-data/badge.svg)](https://github.com/cschlaffner/PROTzilla/tree/python-coverage-comment-action-data) 

PROTzilla is an open-source and browser-based tool for downstream proteomics MS analysis, enabling non-programmers to preprocess data, perform analyses, and generate publication-ready plots. The shareable, reproducible workflows and the integration of knowledge databases support automated analysis and transparent reporting in proteomics research.

## :gear: Deploy PROTzilla

### Regular setup (production deployment)

We have prepared user guides for [Windows](./docs/Windows.md), [macOS](./docs/MacOS.md) and [Linux](./docs/Linux.md).
We have also prepared a guide for [Windows Server 2012](./docs/WindowsServer2012.md).

### Development (Docker)

1. Clone the PROTzilla repository <br> `git clone https://github.com/cschlaffner/PROTzilla.git`
2. Enter repository folder <br> `cd PROTzilla`

Before running, make sure you have [Docker](https://www.docker.com/) and Docker Compose installed. 

1. Run `docker compose up --build vite` (or `docker-compose up --build vite` on old versions) <br> You can optionally add `-d` to detatch protzilla from your shell
2. (optional) If you want persistent user data storage, uncomment the volume specification in the `docker-compose.yml` and adjust for your system. Make sure to copy the repo contents in `/backend/user_data` over to your desired persistent directory first.
3. Go to [the web UI](http://localhost:5173)
4. Hack away and see the changes reflected instantly!
5. (optional) In VS Code, go to the debugging tab and select Python Debugger: Remote Attach to enable listening for easy debugging in your IDE!
    For other setups, `debugpy` is listening on its default port 5678

### Linux/macOS native
> [!NOTE]
> This deployment script is kept for legacy reasons and might not work well on every kind of system. We strongly encourage you to use docker instead.

1. Execute `./install_protzilla.sh` to install dependencies and set up the environment. Might take up to 15 minutes. 
2. Execute `./run_protzilla.sh` to run PROTzilla. <br>

If this script does not work, you can try to use the docker scripts natively:
1. Execute `./install_scripts/install_dependencies.sh` once <br>
2. Execute `./install_scripts/build_frontend.sh` for every frontend change <br>
3. Execute `./run_protzilla.sh` to run. <br>

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
To open PROTzilla in development mode, see [the docker steps](#development)

Additionally, you can launch the storybook by `docker compose up --build storybook` to inspect UI components independently.
