import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.protzilla.constants.paths import RUNS_PATH
from backend.protzilla.workflow import get_available_workflow_names

mcp = FastMCP("protzilla")


@mcp.tool()
def list_workflows() -> list[str]:
    """List the names of all saved PROTzilla workflows.

    Returns a plain list of workflow names without the `.yaml` suffix.
    These names are the valid inputs for `get_workflow(workflow_name=...)`.

    The result only contains real workflows. Helper files such as
    `.file_input_map.yaml` are filtered out.

    Example result:
    ["standard", "only_import", "all_steps"]

    This tool is read-only. It does not create, modify, validate, or execute
    workflows.
    """
    return get_available_workflow_names()


@mcp.tool()
def get_workflow(workflow_name: str) -> dict:
    """Load one saved PROTzilla workflow and return its stored structure.

    Input:
    `workflow_name` must be one of the names returned by `list_workflows()`.
    Pass the bare name without `.yaml`.

    Return format:
    - `name`: the requested workflow name
    - `step_count`: number of entries in `workflow["steps"]`
    - `workflow`: the parsed YAML content as a Python dictionary

    Error behaviour:
    - If `workflow_name` does not exist, this tool raises
    `ValueError("Unknown workflow '<name>'.")`.
    - It does not return an empty result for missing workflows.

    The `workflow` field contains the parsed YAML content of the saved workflow
    file and is kept close to the original file structure.

    Typical keys inside `workflow` are:
    - `steps`: list of workflow nodes / step definitions
    - `graph_edges`: explicit connections between workflow nodes
    - `current_step_id`, `df_mode`, `id_clock`: workflow metadata if present

    Typical node structure inside `workflow["steps"]`:
    - `type`: PROTzilla step class, e.g. `MaxQuantImport`
    - `instance_identifier`: unique node / step id if present
    - `form_inputs`: user-configured parameters for the node
    - `visual_data`: optional editor layout metadata such as node position

    Important:
    - In graph-based workflows, connectivity is defined by `graph_edges`.
    - Do not assume that the order of `workflow["steps"]` alone fully defines the workflow.
    - This tool is read-only. It does not save, modify, validate, or execute workflows.
    """
    workflow_file = PROJECT_ROOT / "backend" / "user_data" / "workflows" / f"{workflow_name}.yaml"
    if not workflow_file.exists():
        raise ValueError(f"Unknown workflow '{workflow_name}'.")

    with workflow_file.open("r", encoding="utf-8") as file:
        workflow = yaml.full_load(file) or {}

    return {
        "name": workflow_name,
        "step_count": len(workflow.get("steps", [])),
        "workflow": workflow,
    }


@mcp.tool()
def list_runs() -> dict:
    """List saved PROTzilla runs together with their basic metadata.

    Return format:
    - `runs`: list of non-favourited runs
    - `favourited_runs`: list of favourited runs
    - `tags`: list of all tags used across runs

    Each run entry may contain:
    - `run_name`: saved run name
    - `creation_date`: run creation timestamp if available
    - `modification_date`: last modification timestamp if available
    - `memory_mode`: run dataframe mode, usually `disk` or `memory`
    - `run_steps`: list of step display names stored in run metadata
    - `favourite_status`: whether the run is favourited
    - `run_tags`: list of tags attached to the run

    Error behaviour:
    - If no runs exist, this tool returns empty lists and a human-readable
      message in `message`.
    - It does not raise an error just because the run list is empty.

    Important:
    - This tool lists existing saved runs, not workflow templates.
    - `run_steps` comes from stored metadata and is useful for quick inspection,
      but it is not a full run export.
    - This tool is read-only. It does not create, modify, delete, or execute runs.
    """
    if not RUNS_PATH.exists():
        return {
            "runs": [],
            "favourited_runs": [],
            "tags": [],
            "message": f"No runs have been found in {RUNS_PATH}.",
        }

    runs = []
    favourited_runs = []
    tags = set()

    for run_dir in RUNS_PATH.iterdir():
        if run_dir.name.startswith(".") or not run_dir.is_dir():
            continue

        metadata_file = run_dir / "metadata.yaml"
        metadata = {}
        if metadata_file.exists():
            with metadata_file.open("r", encoding="utf-8") as file:
                metadata = yaml.full_load(file) or {}

        run_info = {
            "run_name": run_dir.name,
            "creation_date": metadata.get("creation_date", "date not available"),
            "modification_date": metadata.get(
                "modification_date", "date not available"
            ),
            "memory_mode": metadata.get("df_mode", "disk"),
            "run_steps": metadata.get("steps", []),
            "favourite_status": metadata.get("favourite", False),
            "run_tags": list(metadata.get("tags", [])),
        }

        tags.update(run_info["run_tags"])
        if run_info["favourite_status"]:
            favourited_runs.append(run_info)
        else:
            runs.append(run_info)

    return {
        "runs": runs,
        "favourited_runs": favourited_runs,
        "tags": list(tags),
    }




def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
