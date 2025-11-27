from pathlib import Path

PROJECT_PATH = Path(__file__).resolve().parent.parent.parent.parent # path to the root of the project
BACKEND_PATH = Path(PROJECT_PATH, "backend")
FRONTEND_PATH = Path(PROJECT_PATH, "frontend")
USER_DATA_PATH = Path(BACKEND_PATH, "user_data")
RUNS_PATH = USER_DATA_PATH / "runs"
WORKFLOWS_PATH = USER_DATA_PATH / "workflows"
SETTINGS_PATH = USER_DATA_PATH / "settings"
EXTERNAL_DATA_PATH = USER_DATA_PATH / "external_data"
UPLOAD_PATH = BACKEND_PATH / "uploads"