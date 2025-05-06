# PROTzilla

> [!NOTE]
> This repository is still a work-in-progress version.<br> Please refer to the previous PROTzilla at https://github.com/cschlaffner/PROTzilla2.

PROTzilla is an open-source and browser-based tool for downstream proteomics MS analysis, enabling non-programmers to preprocess data, perform analyses, and generate publication-ready plots. Its shareable, reproducible workflows and integration with knowledge bases support automated analysis and transparent reporting in proteomics research.

## :gear: Set up & install PROTzilla

1. Clone the PROTzilla repository <br> `git clone https://github.com/cschlaffner/PROTzilla.git`
2. Enter repository folder <br> `cd PROTzilla`
3. Run install script <br>
    **For Windows:** Double-click `run_protzilla.bat` or execute `.\run_protzilla.bat` in terminal <br>
    **For macOS & Linux:** Execute `.\run_protzilla.sh` <br>

The script automatically installs all software dependencies and creates the environment. The initial set-up might take up to 15 minutes.

## &#x1F996; Start & use PROTzilla
Simply run the `run_protzilla` script for your OS and open the application on http://127.0.0.1:8000/. After that, you can start using PROTzilla for your research! &#x1F996;

## :bulb: Quick Introduction on how to use PROTzilla
**Workflows** in PROTzilla are blank templates that define a predefined sequence of parameterized steps, each **step** being a computation that takes data as input and produces according results. Steps are organized into Importing, Preprocessing, Analysis, and Integration sections. For your analysis, you can select a workflow to create a **run**, import your real data (and add extra steps if needed), then execute it. You can execute a run step by step or in one go with a single click. PROTzilla also lets you generate and download **custom plots** and seamlessly integrate **UniProt databases** into your analysis.
> [!TIP]
> For more details, please see the [user guide in our wiki](https://github.com/cschlaffner/PROTzilla/wiki/User-Guide).

## :mag: Further information: Development
PROTzilla is built with Python/Django on the backend and Node.js (managed via pnpm) for the frontend. <br>
To open PROTzilla in development mode, run the `protzilla_dev` script for your OS. (In this mode, the frontend and backend servers are started, but code changes are dynamically included.)

- `http://localhost:5174/` is a dynamic version of the frontend.
- `http://127.0.0.1:8000/` is static and does not change without running `pnpm build` - as seen by a user.

Additionally, you can launch the storybook by `pnpm storybook` to inspect UI components independently.

For more technical details and further information on how to contribute to PROTzilla, please see the [developer guide in our wiki](https://github.com/cschlaffner/PROTzilla/wiki/Developer-Guide).
