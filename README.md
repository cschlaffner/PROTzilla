# PROTzilla

> [!NOTE]
> This repository is still a work-in-progress version.<br> Please refer to the previous PROTzilla at https://github.com/cschlaffner/PROTzilla2.

[TODO: Add general information on PROTzilla and documentation]

## :gear: Set Up & Install PROTzilla
Available for Unix-based systems (`run_protzilla.sh`) & Windows (`run_protzilla.bat`).

- Installs all software dependencies and creates the environment
- Opens frontend built by `pnpm` via port http://127.0.0.1:8000/
- The initial set-up might take up to 15 minutes

## &#x1F996; Start & Use PROTzilla
Simply run the `run_protzilla` script for your OS and start using PROTzilla for your research! &#x1F996;

## :bulb: Quick Introduction on How To Use PROTzilla

[TODO: Summarize PROTzilla's functionalities, add link to detailed documentation]

## :mag: Further information: Development

> [!NOTE]
> For further information on how to contribute to PROTzilla, please read our dev-guide. [TODO: Add dev-guide to wiki]

To open PROTzilla in development mode (`pnpm dev`), run the `protzilla_dev` script for your OS. (In this mode, the frontend and backend servers are started, but code changes are dynamically included.)

- The port `http://localhost:5174/` is a dynamic version of the frontend.
- The port `http://127.0.0.1:8000/` is static and does not change without running `pnpm build` - as seen by a user.

### Testing

- For local testing, execute `pytest`.
- For specific tests, execute `pytest path/to/test`.
- [TODO: Testing in frontend?]
- The CI Pipeline for the frontend and backend is separated and is only executed if there are changes in the respective folder.

### Dependencies
(Automatically done by the `run_protzilla` script.)

- **Backend**: Managed via Python in `requirements.txt`: `pip install -q -r requirements.txt` 
- **Frontend**: Managed via pnpm in `frontend/package.json`: `cd frontend && pnpm install`
