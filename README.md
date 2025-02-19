# PROTzilla

This is a work-in-progress version. 
Please refer to the current PROTzilla at https://github.com/cschlaffner/PROTzilla2

### Install scripts
Available for Linux-based (run_protzilla.sh) & Windows (run_protzilla.bat)
- installs all dependencies 
- installs pnpm & node.js (if errors occur, please inform others!)
- opens frontend index.html built by pnpm via backend-configured port http://127.0.0.1:8000/

## Starting PROTzilla
Run `protzilla_dev` for your OS (Windows not tested yet).
It starts the frontend server in development mode (`pnpm dev`) and the backend server (as usual in PROTzilla2, but with a dynamic link to the frontend).

The port `http://localhost:5174/` is a dynamic version of the frontend (changes directly) which can communicate with the backend since it was started as well.

Port `http://127.0.0.1:8000/` is static and does not change without running `pnpm build` - as seen by a user. (Not really helpful in this configuration but needed because the backend needs to be active for API-calls etc.)

### Code Status PROTzilla
NOT up to date! As soon as PROTzilla2 has all features merged, backend will be updated.

There might be open new TODOs, these will be addressed, nothing crucial for now.

### Frontend Status
- Contains README from Pauls workshop (might not be entirely up to date, but kept for now as a reference)
- Contains many components that will be changed/deleted -> **WIP for Feb/March 2025**

### Testing 
For local testing execute `pytest`.
For specific tests execute `pytest path/to/test`


### GitHub Workflows
- Frontend CI & Backend CI separated -> only executed if changes in each folder

### Dependencies
(Automatically done by run_protzilla script but if needed:)
- **backend**: managed via python in requirements.txt
  - `pip install -q -r requirements.txt` 
- **frontend**: managed via pnpm _(performant node package manager)_ in frontend/package.json (bzw. pnpm-lock to save explicit versions)
  - `cd frontend && pnpm install`



_Ready for development. :D_