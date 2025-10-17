from pathlib import Path

PROJECT_PATH = Path(__file__).resolve().parent.parent.parent.parent  # path to the root of the project
BACKEND_PATH = Path(PROJECT_PATH, "backend")
FRONTEND_PATH = Path(PROJECT_PATH, "frontend")
USER_DATA_PATH = Path(BACKEND_PATH, "user_data")
RUNS_PATH = USER_DATA_PATH / "runs"
WORKFLOWS_PATH = USER_DATA_PATH / "workflows"
SETTINGS_PATH = USER_DATA_PATH / "settings"
EXTERNAL_DATA_PATH = USER_DATA_PATH / "external_data"
UPLOAD_PATH = BACKEND_PATH / "uploads"

CUSTOM_PLOT_SETTINGS_FILE_STEM = "plots"
DEFAULT_PLOT_SETTINGS_FILE_STEM = "plots_default"
CUSTOM_PTM_SETTINGS_FILE_STEM = "ptm_settings"
DEFAULT_PTM_SETTINGS_FILE_STEM = "ptm_settings_default"

EXAMPLE_DATASET_DIR = USER_DATA_PATH / "example_dataset"
EXAMPLE_DATASET_PROTEIN_FILE = EXAMPLE_DATASET_DIR / "proteinGroups.txt"
EXAMPLE_DATASET_METADATA_FILE = EXAMPLE_DATASET_DIR / "meta.csv"
EXAMPLE_DATASET_PEPTIDE_FILE = EXAMPLE_DATASET_DIR / "peptides.txt"
