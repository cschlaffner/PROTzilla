import sys
import shutil
import inspect
import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
import yaml

from django_adapter import post as django_post

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.protzilla.constants.paths import RUNS_PATH
from backend.protzilla.all_steps import get_all_methods, get_all_possible_steps
from backend.protzilla.workflow import get_available_workflow_names

mcp = FastMCP(
    "protzilla",
    host="0.0.0.0",
    port=5175,
    transport_security=TransportSecuritySettings(
        allowed_hosts=["127.0.0.1:5175", "localhost:5175"]
    ),
)


def _mcp_tool_log_file() -> Path:
    log_dir = PROJECT_ROOT / "mcp-server" / "ai"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "mcp_tool_calls.txt"


def _jsonable_log_value(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (list, tuple, set)):
        return [_jsonable_log_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable_log_value(item) for key, item in value.items()}
    if is_dataclass(value):
        return _jsonable_log_value(asdict(value))
    return str(value)


def _write_mcp_tool_log(tool_name: str, arguments: dict, status: str, **data) -> None:
    entry = {
        "time": datetime.now(timezone.utc).isoformat(),
        "tool": tool_name,
        "arguments": _jsonable_log_value(arguments),
        "status": status,
        **{key: _jsonable_log_value(value) for key, value in data.items()},
    }
    with _mcp_tool_log_file().open("a", encoding="utf-8") as file:
        file.write(json.dumps(entry, ensure_ascii=False) + "\n")


def mcp_tool():
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            try:
                bound_arguments = inspect.signature(function).bind_partial(
                    *args, **kwargs
                )
                bound_arguments.apply_defaults()
                arguments = dict(bound_arguments.arguments)
            except Exception:
                arguments = {"args": args, "kwargs": kwargs}

            try:
                result = function(*args, **kwargs)
            except Exception as error:
                _write_mcp_tool_log(
                    function.__name__,
                    arguments,
                    "error",
                    error=f"{type(error).__name__}: {error}",
                )
                raise

            _write_mcp_tool_log(function.__name__, arguments, "success", result=result)
            return result

        return mcp.tool()(wrapper)

    return decorator


def _read_yaml(path: Path, *, base_loader: bool = False) -> dict:
    with path.open("r", encoding="utf-8") as file:
        if base_loader:
            return yaml.load(file, Loader=yaml.BaseLoader) or {}
        return yaml.full_load(file) or {}


def _workflow_file(workflow_name: str) -> Path:
    return (
        PROJECT_ROOT / "backend" / "user_data" / "workflows" / f"{workflow_name}.yaml"
    )


def _run_dir(run_name: str) -> Path:
    return RUNS_PATH / run_name


def _imported_data_dir() -> Path:
    return PROJECT_ROOT / "mcp-server" / "imported-data"


def _add_step(run_name: str, step_type: str, step_name: str) -> dict:
    if not step_name.strip():
        raise ValueError("Step name must not be empty.")

    step = django_post(
        "add_step", run_name=run_name, method=step_type, step_name=step_name.strip()
    )
    return {"run_name": run_name, "step": step}


def _set_step_parameters(
    run_name: str, step_id: str, parameters: dict, *, custom_only: bool = False
) -> dict:
    return django_post(
        "set_step_parameters",
        run_name=run_name,
        step_id=step_id,
        parameters=parameters,
        custom_only=custom_only,
    )


@mcp_tool()
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


@mcp_tool()
def import_file(source_path: str) -> dict:
    """Copy one external file into PROTzilla's MCP staging directory.

    Input:
    - `source_path`: path to an existing file that the MCP server process can read

    Return format:
    - `source_path`: normalized absolute source path
    - `imported_path`: normalized absolute destination path inside
      `mcp-server/imported-data`
    - `file_name`: final stored file name inside the staging directory

    Error behaviour:
    - If `source_path` does not exist or is not a file, this tool raises
      `ValueError`.

    Important:
    - This tool is meant as a staging step before `set_step_input_file(...)`.
    - The returned `imported_path` is the path that should usually be passed to
      `set_step_input_file(...)`.
    - This operation copies the file. It does not move or delete the original.
    - If a file with the same name already exists in `mcp-server/imported-data`,
      a numeric suffix is added to avoid overwriting it.
    """
    source = Path(source_path).expanduser().resolve()
    if not source.is_file():
        raise ValueError(f"File '{source_path}' does not exist or is not a file.")

    target_dir = _imported_data_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    target = target_dir / source.name
    counter = 1
    while target.exists():
        target = target_dir / f"{source.stem}_{counter}{source.suffix}"
        counter += 1

    shutil.copy2(source, target)
    return {
        "source_path": str(source),
        "imported_path": str(target),
        "file_name": target.name,
    }


@mcp_tool()
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
    - If `workflow_name` does not exist.
    - It does not return an empty result for missing workflows.

    The `workflow` field contains the parsed YAML content of the saved workflow
    file and is kept close to the original file structure.

    Typical keys inside `workflow` are:
    - `steps`: list of workflow nodes / step definitions
    - `graph_edges`: connections between workflow nodes
    - `current_step_id`, `df_mode`, `id_clock`: workflow metadata if present

    Typical node structure inside `workflow["steps"]`:
    - `type`: PROTzilla step class, e.g. `MaxQuantImport`
    - `instance_identifier`: unique node / step id if present
    - `form_inputs`: the currently stored form values for the node, including
    default values for untouched fields and `null` for empty optional inputs
    - `visual_data`: optional editor layout metadata such as node position

    Important:
    - This tool is read-only. It does not save, modify, validate, or execute workflows.
    """
    workflow_file = _workflow_file(workflow_name)
    if not workflow_file.exists():
        raise ValueError(f"Unknown workflow '{workflow_name}'.")
    workflow = _read_yaml(workflow_file)

    return {
        "name": workflow_name,
        "step_count": len(workflow.get("steps", [])),
        "workflow": workflow,
    }


@mcp_tool()
def list_runs() -> dict:
    """List saved PROTzilla runs together with their basic metadata.

    Return format:
    - `runs`: list of non-favorited runs
    - `favorited_runs`: list of favorited runs
    - `tags`: list of all tags used across runs

    Each run entry may contain:
    - `run_name`: saved run name
    - `creation_date`: run creation timestamp if available
    - `modification_date`: last modification timestamp if available
    - `memory_mode`: run dataframe mode, usually `disk` or `memory`
    - `run_steps`: list of step display names stored in run metadata
    - `favorite_status`: whether the run is favorited
    - `run_tags`: list of tags attached to the run

    Error behaviour:
    - If no runs exist, this tool returns empty lists and a human-readable
      message in `message`.
    - It does not raise an error just because the run list is empty.

    Important:
    - This tool lists existing saved runs, not workflow templates.
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
        metadata = _read_yaml(metadata_file) if metadata_file.exists() else {}

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


@mcp_tool()
def list_available_steps() -> dict:
    """List the PROTzilla step types that users can add to workflows.

    Return format:
    - `step_count`: number of returned step definitions
    - `steps`: list of step definition dictionaries

    Each step entry comes from PROTzillas own step registry and typically
    contains:
    - `method_name`: internal step class name used to identify the step type
    - `section`: step category such as importing or data_analysis
    - `display_name`: name shown to users
    - `operation`: broader operation label for related steps
    - `method_description`: short explanation of what the step does
    - `calculation_status`: default status metadata from the step definition

    Important:
    - This tool only lists steps that are available to users in the current
      PROTzilla setup.
    - Hidden/internal steps are filtered out in the same way as in the
      frontend.
    - This tool is read-only. It does not add, remove, or execute steps.
    """
    steps = get_all_possible_steps(exclude_hidden=True)
    return {
        "step_count": len(steps),
        "steps": steps,
    }


@mcp_tool()
def get_step_definition(step_type: str) -> dict:
    """Load one available PROTzilla step definition.

    Input:
    - `step_type` must be a valid internal step name from
      `list_available_steps()`.

    Return format:
    - `step`: basic metadata for the selected step
    - `form`: the default form definition created by the step class
    - `io`: the generic input and output handles of this step type

    The `step` field contains PROTzilla's own step metadata such as:
    - `method_name`: internal step class name used to identify the step type
    - `section`: step category such as importing or data_analysis
    - `display_name`: name shown to users
    - `operation`: broader operation label for related steps
    - `operation_display_name`
    - `method_description`: short explanation of what the step does

    The `form` field contains the default parameter interface for that step:
    - `label`: displayed form title
    - `isAutoSubmit`: whether the form auto-submits in the UI
    - `input_fields`: ordered list of form fields with default values

    The `io` field contains the generic graph interface of that step type:
    - `inputs`: input handle names that can receive connections from other steps
    - `outputs`: output handle names that this step can expose to other steps

    Important:
    - The returned `input_fields` describe the default configurable parameters
      before any user-specific data or run-specific dynamic changes are applied.
    - `io["inputs"]` and `io["outputs"]` describe the generic step type, not
      the current state of a concrete run instance.
    - If this definition is still too imprecise, consult the PROTzilla wiki:
      https://github.com/cschlaffner/PROTzilla/wiki/Step-Documentation
    - For more detailed and more formal descriptions, use the section-specific
      wiki pages depending on the step's `section`:
      importing -> https://github.com/cschlaffner/PROTzilla/wiki/Importing
      data_preprocessing -> https://github.com/cschlaffner/PROTzilla/wiki/Data-Preprocessing
      data_analysis -> https://github.com/cschlaffner/PROTzilla/wiki/Data-Analysis
      data_integration -> https://github.com/cschlaffner/PROTzilla/wiki/Data-Integration
    - This tool is read-only. It does not add the step to a workflow or execute it.
    """
    for step_class in get_all_methods():
        if step_class.__name__ != step_type:
            continue

        step = step_class()
        return {
            "step": step_class.to_dict(),
            "form": {
                "label": step.form.label,
                "isAutoSubmit": step.form.isAutoSubmit,
                "input_fields": [
                    asdict(field) if is_dataclass(field) else str(field)
                    for field in step.form.input_fields
                ],
            },
            "io": {
                "inputs": [str(key) for key in step.external_input_keys],
                "outputs": [str(key) for key in step.output_keys],
            },
        }

    raise ValueError(f"Unknown step type '{step_type}'.")


@mcp_tool()
def get_run(run_name: str) -> dict:
    """Load one saved PROTzilla run from disk.

    Input:
    - `run_name` must be the name of an existing run returned by
    `list_runs()`

    Return format:
    - `name`: requested run name
    - `step_count`: number of entries in `run["steps"]`
    - `metadata`: parsed `metadata.yaml` content if present
    - `run`: parsed `run.yaml` content

    Typical keys inside `metadata` are:
    - `creation_date`
    - `modification_date`
    - `df_mode`: memory or disk
    - `steps`
    - `favourite`
    - `tags`

    Typical keys inside `run` are:
    - `current_step_index`
    - `df_mode`
    - `steps`

    Important:
    - `run["steps"]` contains the stored run state, not just a workflow template.
    - Step entries may include form inputs, outputs, messages, calculation
      status, plots, and instance identifiers, depending on what was saved.
    - This tool is read-only. It does not modify or execute the run.
    """
    run_dir = _run_dir(run_name)
    run_file = run_dir / "run.yaml"
    metadata_file = run_dir / "metadata.yaml"

    if not run_dir.exists() or not run_file.exists():
        raise ValueError(f"Unknown run '{run_name}'.")

    metadata = _read_yaml(metadata_file) if metadata_file.exists() else {}
    run = _read_yaml(run_file, base_loader=True)

    return {
        "name": run_name,
        "step_count": len(run.get("steps", [])),
        "metadata": metadata,
        "run": run,
    }


@mcp_tool()
def create_run(run_name: str, workflow_name: str, df_mode: str = "disk") -> dict:
    """Create a new PROTzilla run from an existing workflow.

    Input:
    - `run_name`: name for the new run
    - `workflow_name`: existing workflow name from `list_workflows()`
    - `df_mode`: dataframe mode for the run, usually `disk`

    Return format:
    - `name`: the created run name
    - `workflow_name`: the workflow used to create the run
    - `df_mode`: the run dataframe mode
    - `run_path`: filesystem path of the created run
    - `name_message`: optional note if the requested run name had to be changed

    Error behaviour:
    - If the workflow does not exist or the run cannot be created
    - If `run_name` contains spaces or unsupported filename characters, it is
      sanitized to match PROTzillas normal frontend behaviour.

    Important:
    - This tool creates a new saved run on disk.
    - It does not execute any workflow steps yet. It only creates the run from
      the selected workflow template.
    - If a run with the final sanitized name already exists, PROTzilla will load
      that existing run instead of silently creating a second one with the same name.
    """
    return django_post(
        "add_run",
        run_name=run_name,
        workflow_name=workflow_name,
        df_mode_name=df_mode,
    )


@mcp_tool()
def add_step_to_run(run_name: str, step_type: str, step_name: str) -> dict:
    """Add one new step node to an existing PROTzilla run.

    Input:
    - `run_name`: existing run name, for example from `list_runs()`
    - `step_type`: internal step type name from `list_available_steps()`
    - `step_name`: name shown for this concrete step node in the run

    Return format:
    - `run_name`: the run that was modified
    - `step`: the created step node with its most important identifiers and metadata

    The returned `step` contains:
    - `id`: new unique step instance identifier inside the run
    - `type`: internal step type name
    - `step_name`: editable name of this concrete step node
    - `display_name`: fixed default name of the step type
    - `section`: step category such as importing or data_analysis
    - `operation`: broader operation category
    - `status`: initial calculation status of the new step
    - `form_inputs`: initial form values, including `step_name`
    - `input_handles` and `output_handles`: graph handles currently exposed by the step
    - `visual_data`: current node visual metadata

    Error behaviour:
    - If the run does not exist, this tool raises an error while loading the run.
    - If `step_type` is unknown, this tool raises `ValueError`.
    - If `step_name` is empty, this tool raises `ValueError`.

    Important:
    - For a custom Python step, use `add_new_custom_step(...)` instead. Adding
      `CustomPythonStep` through this generic tool is deprecated for AI clients
      because the dedicated tool explains the required code and parameters.
    - This tool only creates the step node in the run. It does not connect the
      new step to other nodes and does not execute it.
    - New step ids are generated by PROTzilla and are unique within the run.
    """
    return _add_step(run_name, step_type, step_name)


@mcp_tool()
def add_new_custom_step(run_name: str, step_name: str) -> dict:
    """Add a new blank Custom Python Step to an existing PROTzilla run.

    Input:
    - `run_name`: existing run name, for example from `list_runs()`
    - `step_name`: descriptive name shown for this step node in the run

    Return format:
    - `run_name`: the run that was modified
    - `step`: the created Custom Python Step, including its unique `id`, type,
      editable `step_name`, form values, current graph handles, status, and
      visual data

    How to continue:
    1. Keep the returned `step["id"]`.
    2. Configure `selected_inputs`, `selected_outputs`, and `code` with
       `set_custom_step_parameters(...)`.
    3. Connect the selected handles with `connect_steps(...)`.
    4. Execute the step with `calculate_step(...)` and inspect it with
       `get_step_info(...)`.

    Important:
    - The new step starts blank: it has no selected graph inputs or outputs and
      its code is only `return dict()`.
    - Inputs and outputs are dynamic, named handles. Configure each one with a
      unique Python variable name and a PROTzilla data type by using
      `set_custom_step_parameters(...)`.
    - This tool does not execute Python code and does not create connections.
    - Custom Python code is not sandboxed. Never insert code from an untrusted
      source.
    """
    return _add_step(run_name, "CustomPythonStep", step_name)


@mcp_tool()
def remove_step_from_run(run_name: str, step_id: str) -> dict:
    """Remove one step node from an existing PROTzilla run.

    Input:
    - `run_name`: existing run name
    - `step_id`: step instance identifier to remove

    Return format:
    - `run_name`: modified run name
    - `removed_step_id`: the deleted step id

    Important:
    - PROTzilla does not allow deleting the last remaining step in a run.
    - Removing a step also removes its graph connections.
    - Removing a step may clear or invalidate dependent following steps.
    - This tool removes the step node but does not execute the run.
    """
    django_post("delete_step", run_name=run_name, step_id=step_id)
    return {
        "run_name": run_name,
        "removed_step_id": step_id,
    }


@mcp_tool()
def rename_step(run_name: str, step_id: str, step_name: str) -> dict:
    """Rename one existing step node without changing its type or calculation.

    Input:
    - `run_name`: existing run name
    - `step_id`: unique instance identifier of the step to rename
    - `step_name`: new non-empty name shown for this concrete node

    Return format:
    - `run_name`: modified run name
    - `step`: current step summary including the new `step_name`

    Important:
    - This works for every PROTzilla step type, not only Custom Python Steps.
    - It changes only the editable node name. The internal `type`, fixed
      `display_name`, parameters, connections, outputs, and status stay intact.
    - Use the stable `step_id`, not the editable name, in all other MCP tools.
    """
    if not step_name.strip():
        raise ValueError("Step name must not be empty.")

    return django_post(
        "rename_step",
        run_name=run_name,
        step_id=step_id,
        step_name=step_name.strip(),
    )


@mcp_tool()
def set_step_parameters(run_name: str, step_id: str, parameters: dict) -> dict:
    """Set form parameters for one step in an existing PROTzilla run.

    Input:
    - `run_name`: existing run name
    - `step_id`: step instance identifier to update
    - `parameters`: dictionary of form field names to new values

    Return format:
    - `run_name`: modified run name
    - `step_id`: updated step id
    - `parameters`: the values that were passed in
    - `stored_form_inputs`: the currently stored form values after the update

    Important:
    - Only fields that exist on the step form are updated directly. Unknown
      keys may be buffered by PROTzilla for dynamically added fields.
    - Updating parameters invalidates the selected step and all dependent
      following steps.
    - For a Custom Python Step, use `set_custom_step_parameters(...)` instead.
      It has the same update behavior but documents the custom code contract.
    - This tool updates configuration only. It does not execute the step.
    """
    return _set_step_parameters(run_name, step_id, parameters)


@mcp_tool()
def set_custom_step_parameters(run_name: str, step_id: str, parameters: dict) -> dict:
    """Configure the inputs, outputs, name, and Python code of a Custom Python Step.

    Input:
    - `run_name`: existing run name
    - `step_id`: id returned by `add_new_custom_step(...)`
    - `parameters`: dictionary containing one or more of:
      - `step_name`: editable display name
      - `selected_inputs`: list of named input handle dictionaries
      - `selected_outputs`: list of named output handle dictionaries
      - `code`: Python function body executed by the step

    Handle format:
    - Every input and output is `{"name": "<handle_name>", "type": "<data_key>"}`.
    - `name` must be a unique valid Python identifier such as `control_df`,
      `treated_df`, or `normalized_df`.
    - `type` must be a PROTzilla data key offered by
      `get_step_definition("CustomPythonStep")`, such as `protein_df`,
      `metadata_df`, or `custom_df`.
    - The same `type` may be used repeatedly under different names. For example:
      `selected_inputs=[{"name": "control_df", "type": "protein_df"},
      {"name": "treated_df", "type": "protein_df"}]`.

    Code contract:
    - Pass only the function body, without `def`, Markdown fences, or a call to
      the function.
    - Every selected input is available as a variable using its handle `name`.
      In the example above, the code receives `control_df` and `treated_df`.
    - `pandas` is available as `pd`, NumPy as `np`, and PROTzilla's
      `default_intensity_column(...)` helper is also available.
    - The code must return a dictionary, for example
      `return dict(protein_df=filtered_df, removed_samples=removed)`.
    - Every output handle `name` must occur as a key in the returned dictionary.
      For `{"name": "normalized_df", "type": "protein_df"}`, return for example
      `return {"normalized_df": result}`. Additional returned keys are stored as
      step results but are not graph output handles unless selected.
    - At least one output must currently be selected.

    Graph behavior:
    - The handle `name` is the exact `source_handle` or `target_handle` used by
      `connect_steps(...)`; the `type` controls its PROTzilla data semantics.
    - Configure these fields before calling `connect_steps(...)`.
    - Removing a selected input or output automatically removes connections
      attached to that handle so the run graph remains valid.

    Return format:
    - `run_name`: modified run name
    - `step_id`: updated step id
    - `parameters`: values supplied in this call
    - `stored_form_inputs`: complete stored form state after the update

    Important:
    - Partial updates are allowed; omitted fields keep their current values.
    - Updating the step invalidates it and all dependent following steps.
    - This tool configures the step but does not execute it. Use
      `calculate_step(...)` afterward and inspect errors/results with
      `get_step_info(...)`.
    - The code executes inside the PROTzilla backend and is not sandboxed.
      Never use code from an untrusted source.
    """
    return _set_step_parameters(run_name, step_id, parameters, custom_only=True)


@mcp_tool()
def set_step_input_file(
    run_name: str, step_id: str, input_name: str, file_path: str
) -> dict:
    """Set one file input field for a step in an existing PROTzilla run.

    Input:
    - `run_name`: existing run name
    - `step_id`: step instance identifier to update
    - `input_name`: name of a file input field on that step, for example `file_path`
    - `file_path`: path to a file that the PROTzilla process can read

    Return format:
    - `run_name`: modified run name
    - `step_id`: updated step id
    - `input_name`: updated file input field
    - `file_path`: normalized absolute file path that was stored
    - `stored_form_inputs`: the currently stored form values after the update

    Error behaviour:
    - If `step_id` does not exist in the run, this tool raises `ValueError`.
    - If `input_name` is not a field of the selected step, this tool raises
      `ValueError`.
    - If `input_name` exists but is not a file field, this tool raises
      `ValueError`.
    - If `file_path` does not point to an existing file, this tool raises
      `ValueError`.

    Important:
    - `file_path` must be readable from the environment where PROTzilla runs.
      In Docker setups this usually means a path inside a mounted volume or
      inside the container filesystem, not an arbitrary host-only path.
    - If the file currently only exists outside the PROTzilla/MCP environment,
      use `import_file(source_path)` first and then pass the returned
      `imported_path` into this tool.
    - Updating the file input invalidates the selected step and all dependent
      following steps.
    - This tool updates configuration only. It does not execute the step.
    """
    return django_post(
        "set_step_input_file",
        run_name=run_name,
        step_id=step_id,
        input_name=input_name,
        file_path=file_path,
    )


@mcp_tool()
def calculate_step(run_name: str, step_id: str) -> dict:
    """Calculate one step in an existing PROTzilla run.

    Input:
    - `run_name`: existing run name
    - `step_id`: step instance identifier to calculate

    Return format:
    - `run_name`: modified run name
    - `step_id`: calculated step id
    - `status`: stored calculation status after the attempt
    - `messages`: stored step messages after the attempt
    - `result_artifacts`: resolved output and plot artifact information

    Important:
    - This tool tries to calculate exactly the selected step, not the whole run.
    - Dependency checks are handled by PROTzilla itself. If required input
      steps are still missing, the step stores an error message instead of
      calculating successfully.
    - A successful calculation may create CSV, plot, or other output artifacts
      inside the run folder.
    """
    django_post(
        "calculate_step",
        allow_error_data=True,
        run_name=run_name,
        step_id=step_id,
        data={},
    )

    step_info = get_step_info(run_name, step_id)
    return {
        "run_name": run_name,
        "step_id": step_id,
        "status": step_info["step"].get("calculation_status"),
        "messages": step_info["step"].get("messages", []),
        "result_artifacts": step_info["result_artifacts"],
    }


@mcp_tool()
def calculate_run(run_name: str) -> dict:
    """Calculate all steps of an existing PROTzilla run in workflow order.

    Input:
    - `run_name`: existing run name

    Return format:
    - `run_name`: calculated run name
    - `status`: overall run status after the attempt
    - `completed_step_count`: number of steps with status `complete`
    - `failed_step_id`: first step that did not finish with status `complete`, if any
    - `steps`: per-step summary in workflow order

    Each entry in `steps` contains:
    - `step_id`: step instance identifier
    - `type`: PROTzilla step type
    - `status`: stored calculation status after the attempt
    - `messages`: stored step messages after the attempt

    Important:
    - This tool calculates the run step by step in topological workflow order.
    - It stops at the first step that does not finish with status `complete`.
      This can happen because of missing inputs, invalid parameters, missing
      files, or calculation errors.
    - This operation can take a long time for real datasets or larger runs.
      An AI client should wait for the tool call to finish and should not
      assume something is wrong just because the response is slow.
    - This tool writes outputs, plots, messages, and calculation states to the
      run on disk.
    """
    return django_post("calculate_run", run_name=run_name)


@mcp_tool()
def connect_steps(
    run_name: str,
    source_step_id: str,
    source_handle: str,
    target_step_id: str,
    target_handle: str,
) -> dict:
    """Connect one output handle of a step to one input handle of another step.

    Input:
    - `run_name`: existing run name
    - `source_step_id`: source node instance identifier
    - `source_handle`: output handle name on the source node
    - `target_step_id`: target node instance identifier
    - `target_handle`: input handle name on the target node

    Return format:
    - `run_name`: modified run name
    - `connection`: the created connection in PROTzilla's graph format

    Important:
    - This tool creates or replaces the connection for the given target handle.
    - PROTzilla prevents circular dependencies.
    - The target step and all dependent following steps may be invalidated by
      this change.
    - This tool connects steps but does not execute them.
    """
    connection = {
        "source": source_step_id,
        "sourceHandle": source_handle,
        "target": target_step_id,
        "targetHandle": target_handle,
        "key": f"{source_step_id}:{source_handle}->{target_step_id}:{target_handle}",
        "id": f"{source_step_id}:{source_handle}->{target_step_id}:{target_handle}",
    }
    django_post("connect_steps", run_name=run_name, connection=connection)
    return {
        "run_name": run_name,
        "connection": connection,
    }


@mcp_tool()
def delete_connection(
    run_name: str,
    source_step_id: str,
    source_handle: str,
    target_step_id: str,
    target_handle: str,
) -> dict:
    """Remove one connection between two step handles in an existing PROTzilla run.

    Input:
    - `run_name`: existing run name
    - `source_step_id`: source node instance identifier
    - `source_handle`: output handle name on the source node
    - `target_step_id`: target node instance identifier
    - `target_handle`: input handle name on the target node

    Return format:
    - `run_name`: modified run name
    - `connection`: the removed connection in PROTzilla's graph format

    Important:
    - The supplied connection must match an existing edge exactly.
    - Removing a connection may invalidate the target step and dependent
      following steps.
    - This tool only removes the graph connection. It does not delete steps and
      does not execute the run.
    """
    connection = {
        "source": source_step_id,
        "sourceHandle": source_handle,
        "target": target_step_id,
        "targetHandle": target_handle,
        "key": f"{source_step_id}:{source_handle}->{target_step_id}:{target_handle}",
        "id": f"{source_step_id}:{source_handle}->{target_step_id}:{target_handle}",
    }
    django_post("disconnect_steps", run_name=run_name, connection=connection)
    return {
        "run_name": run_name,
        "connection": connection,
    }


@mcp_tool()
def get_step_info(run_name: str, step_id: str) -> dict:
    """Load one step from a saved run together with connections and result artifacts.

    Input:
    - `run_name`: existing run name, for example from `list_runs()`
    - `step_id`: step instance identifier from `get_run(run_name)["run"]["steps"]`

    Return format:
    - `run_name`: the run that contains the step
    - `step_id`: requested step id
    - `is_current_step`: whether this is the currently selected step in the saved run
    - `step`: stored step data from the run
    - `incoming_connections`: edges targeting this step
    - `outgoing_connections`: edges starting from this step
    - `result_artifacts`: resolved output and plot artifact information

    Important:
    - `step` contains the stored run state for this node, including configured
      form values, messages, calculation status, outputs, plots, and visual data.
    - Output items of type `dataframe` usually point to CSV files in the run
      folder. Plot artifacts may include JSON, PNG, or HTML files.
    - This tool is read-only. It does not modify or execute the run.
    """
    run_info = get_run(run_name)
    run = run_info["run"]
    run_dir = _run_dir(run_name)

    step = next(
        (
            step
            for step in run.get("steps", [])
            if step.get("instance_identifier") == step_id
        ),
        None,
    )
    if step is None:
        raise ValueError(f"Unknown step id '{step_id}' in run '{run_name}'.")

    incoming_connections = []
    outgoing_connections = []
    for edge in run.get("graph_edges", []):
        if len(edge) < 3:
            continue
        connection = {
            "source_step_id": edge[0],
            "target_step_id": edge[1],
            "handles": edge[2],
        }
        if edge[1] == step_id:
            incoming_connections.append(connection)
        if edge[0] == step_id:
            outgoing_connections.append(connection)

    resolved_outputs = {}
    for output_name, output_item in step.get("output", {}).items():
        resolved_output = dict(output_item)
        output_value = output_item.get("value")
        if isinstance(output_value, str) and output_value not in ("", "null", "None"):
            output_path = run_dir / output_value
            resolved_output["resolved_path"] = str(output_path)
            resolved_output["path_exists"] = output_path.exists()
        resolved_outputs[output_name] = resolved_output

    plot_files = sorted(str(path) for path in (run_dir / "plots").glob(f"{step_id}*"))

    return {
        "run_name": run_name,
        "step_id": step_id,
        "is_current_step": run.get("current_step_id") == step_id,
        "step": step,
        "incoming_connections": incoming_connections,
        "outgoing_connections": outgoing_connections,
        "result_artifacts": {
            "outputs": resolved_outputs,
            "plot_files": plot_files,
        },
    }


def main():
    mcp.run(transport="streamable-http" if "--http" in sys.argv else "stdio")


if __name__ == "__main__":
    main()
