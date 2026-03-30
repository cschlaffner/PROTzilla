import json
from shutil import copy2, make_archive
import traceback
from zipfile import ZipFile
import re
import logging
from typing import Any

import numpy as np
from plotly.io import to_json

import pandas as pd
from django.http import JsonResponse, FileResponse
from django.http.request import HttpRequest
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie

from backend.main import settings
from backend.protzilla.constants.envs import DEBUGMODE
from backend.protzilla.constants.data_types import Connection
from backend.protzilla.form import Form
from backend.protzilla.run import (
    Run,
    delete_run_folder,
    get_available_run_info,
    get_available_run_names,
)
from backend.protzilla.workflow import (
    delete_workflow_file,
    get_available_workflow_names,
)
from backend.protzilla.constants.paths import (
    EXTERNAL_DATA_PATH,
    RUNS_PATH,
    WORKFLOWS_PATH,
)
from backend.protzilla.utilities.utilities import format_trace, get_memory_usage
from backend.protzilla.stepfactory import StepFactory
from backend.main.views_helper import (
    get_display_name,
    get_step,
    get_displayed_steps,
    parameters_from_post,
    sanitize_name,
)
from backend.protzilla.all_steps import get_all_possible_steps

database_metadata_path = EXTERNAL_DATA_PATH / "internal" / "metadata" / "uniprot.json"

# Labels of outputs not sent via the output tables API
hidden_outputs = ["messages"]


@ensure_csrf_cookie
def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({"csrfToken": csrf_token, "message": "CSRF cookie set."})


def run_information_list(request):
    run_info = get_available_run_info()
    if type(run_info) == str:
        return JsonResponse({"success": False, "message": run_info}, safe=False)
    if not run_info or len(run_info) == 0:
        return JsonResponse(
            {
                "success": False,
                "message": "An unknown error occurred when creating run table.",
            },
            safe=False,
        )
    runs, runs_favourite, all_tags = run_info
    all_available_runs = runs_favourite + runs
    available_run_info = [all_available_runs, all_tags]

    return JsonResponse({"success": True, "data": available_run_info}, safe=False)


def all_steps(request):
    steps = get_all_possible_steps(exclude_hidden=not DEBUGMODE)
    return JsonResponse(steps, safe=False)


def workflow_name_list(request):
    workflow_names = get_available_workflow_names()

    return JsonResponse(workflow_names, safe=False)


def toggle_favourite(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")

        run = Run(run_name)
        metadata = run.metadata_read()
        metadata["favourite"] = not metadata.get("favourite", False)
        run.update_metadata(metadata)

        return JsonResponse({"success": True, "message": "Favourited run"})
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def add_tag(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")
        run_tag = data.get("tag_name")

        run = Run(run_name)
        metadata = run.metadata_read()
        tags = metadata.get("tags", set())
        tags.add(run_tag)
        metadata["tags"] = tags
        run.update_metadata(metadata)

        return JsonResponse({"success": True, "message": "Added tag"})
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def delete_tag(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")
        run_tag = data.get("tag_name")

        run = Run(run_name)
        metadata = run.metadata_read()
        tags = metadata.get("tags", set())
        tags.remove(run_tag)
        metadata["tags"] = tags
        run.update_metadata(metadata)

        return JsonResponse({"success": True, "message": "Deleted tag"})
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def add_run(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")
        workflow_name = data.get("workflow_name")
        df_mode_name = data.get("df_mode_name")

        converted_run_name, additional_message = sanitize_name(run_name)

        try:
            Run(
                converted_run_name,
                workflow_name,
                df_mode_name,
            )
            message = (
                f"Created run {converted_run_name}. \n{additional_message}"
                if len(additional_message) > 0
                else f"Created run {converted_run_name}."
            )
            return JsonResponse(
                {
                    "success": True,
                    "message": message,
                    "data": {"run_name": converted_run_name},
                }
            )
        except Exception as e:
            msg = "Error when creating run: " + str(e)
            return JsonResponse(
                {
                    "success": False,
                    "message": msg,
                    "traceback": format_trace(traceback.format_exception(e)),
                },
                status=404,
            )
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def delete_run(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")

        try:
            if run_name not in Run._instances:
                delete_run_folder(run_name)
            else:
                run = Run(run_name)
                run.delete_run()

            return JsonResponse({"success": True, "message": "Deleted run"})
        except Exception as e:
            traceback.print_exc()  # not sure if it still needs to be here
            return JsonResponse(
                {
                    "success": False,
                    "message": format_trace(traceback.format_exception(e)),
                },
                status=404,
            )
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def continue_run(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")

        Run(run_name)

        return JsonResponse({"success": True, "message": "Continued run"})
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def update_run_name(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")
        new_run_name = data.get("new_run_name")
        converted_run_name, additional_message = sanitize_name(new_run_name)

        try:
            if converted_run_name in get_available_run_names():
                return JsonResponse(
                    {
                        "success": False,
                        "message": f"Run name {converted_run_name} already exists.",
                    }
                )

            run = Run(run_name)
            run.update_run_name(converted_run_name)

            message = (
                f"Run name updated from {run_name} to {converted_run_name}. \n{additional_message}"
                if len(additional_message) > 0
                else f"Run name updated from {run_name} to {converted_run_name}."
            )
            return JsonResponse(
                {
                    "success": True,
                    "message": message,
                    "data": {"run_name": converted_run_name},
                }
            )
        except Exception as e:
            if isinstance(e, OSError):
                return JsonResponse(
                    {"success": False, "message": "Run name already exists."}
                )
            return JsonResponse(
                {"success": False, "message": "Error when renaming run: " + str(e)},
                status=404,
            )
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def export_run(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")

        run_directory = RUNS_PATH / run_name
        run_zip_path = settings.FILE_UPLOAD_TEMP_DIR / run_name
        run_zip_path_absolute = settings.FILE_UPLOAD_TEMP_DIR / f"{run_name}.zip"

        make_archive(run_zip_path, "zip", run_directory)

        return FileResponse(open(run_zip_path_absolute, "rb"), as_attachment=True)
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def import_run(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_file = data.get("run_file")

        run_name = run_file.removesuffix(".zip")

        run_zip = ZipFile(settings.FILE_UPLOAD_TEMP_DIR / run_file)

        run_zip.extractall(path=RUNS_PATH / run_name)

        return JsonResponse({"success": True, "message": "Imported the workflow"})
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def add_plot(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")

        parameters = parameters_from_post(request.POST)
        run = Run(run_name)
        if run.current_step.display_name == "plot":
            del parameters["chosen_method"]
            run.current_form(parameters)
            run.step_calculate()
        else:
            run.current_step.plot(parameters)

        return JsonResponse({"success": True, "message": "Created plot"})
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def add_step(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")
        method = data.get("method")

        run = Run(run_name)
        step = StepFactory.create_step(method, run.steps)
        run.step_add(step)

        return JsonResponse(
            {
                "success": True,
                "message": "Added step: " + method,
                "data": get_step(step),
            },
            safe=False,
        )
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def delete_step(request):
    """
    API call. Deletes the step with the given instance identifier
    """
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )

    data = json.loads(request.body)
    run_name = data.get("run_name")
    step_id = data.get("step_id")

    run = Run(run_name)

    try:
        run.step_remove(step_id)
    except ValueError as e:
        return JsonResponse(
            {"success": False, "message": "Cannot delete step: " + str(e)}
        )

    return JsonResponse({"success": True, "message": "Deleted step"})


def navigate_to_step(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")
        step_id = data.get("step_id")

        run = Run(run_name)
        run.step_goto(step_id)

        return JsonResponse({"success": True, "message": "Navigated successfully"})
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def set_step_pos(request) -> JsonResponse:
    if request.method == "POST":
        data = json.loads(request.body)
        run_name: str = data.get("run_name")
        step_id = data.get("step_id")
        x = data.get("x")
        y = data.get("y")

        if run_name is None or step_id is None or x is None or y is None:
            return JsonResponse(
                {"success": False, "message": "Missing parameters"}, status=400
            )

        run = Run(run_name)
        run.set_step_pos(step_id, float(x), float(y))

        return JsonResponse({"success": True, "message": "Updated step position"})
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def connect_steps(request) -> JsonResponse:
    if request.method == "POST":
        data = json.loads(request.body)
        run_name: str = data.get("run_name")
        connection: Connection = data.get("connection")
        run = Run(run_name)
        try:
            run.steps.connect_steps(connection, run)
            return JsonResponse(
                {
                    "success": True,
                    # we really need a general message type outside of step calculation
                    "message": {
                        "title": "Connected steps successfully",
                        # very verbose, could be condensed in the future
                        "msg": f"Step {connection['target']} now uses the output with key {connection['sourceHandle']} of step {connection['source']} as its input with key {connection['targetHandle']}.",
                    },
                }
            )
        except Exception as e:
            return JsonResponse(
                {
                    "success": False,
                    "message": dict(
                        title="Error connecting steps",
                        msg=str(e),
                        # TODO: trace is never shown atm, but should be part of a message system refactor
                        trace=format_trace(traceback.format_exception(e)),
                    ),
                }
            )

    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def disconnect_steps(request) -> JsonResponse:
    if request.method == "POST":
        data = json.loads(request.body)
        run_name: str = data.get("run_name")
        connection = data.get("connection")
        run = Run(run_name)
        try:
            run.steps.disconnect_steps(connection)
            return JsonResponse(
                {
                    "success": True,
                    # we really need a general message type outside of step calculation
                    "message": {
                        "title": "Disconnected steps successfully",
                        # very verbose, could be condensed in the future
                        "msg": f"Removed {connection['source']} as the input for {connection['targetHandle']} of step {connection['target']}.",
                    },
                }
            )
        except Exception as e:
            return JsonResponse(
                {
                    "success": False,
                    "message": dict(
                        title="Error disconnecting steps",
                        msg=str(e),
                        # TODO: trace is never shown atm, but should be part of a message system refactor
                        trace=format_trace(traceback.format_exception(e)),
                    ),
                }
            )

    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def get_edges(request) -> JsonResponse:
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")
        run = Run(run_name)
        edges = run.steps.get_edges()
        return JsonResponse({"success": True, "data": edges})
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def save_workflow(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")
        workflow_name = data.get("workflow_name")

        run = Run(run_name)
        new_workflow_name = re.sub(r"[^\w\.-]", "-", workflow_name)
        run._workflow_save(new_workflow_name)

        return JsonResponse({"success": True, "message": "Saved workflow"})
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def export_workflow(request):
    if request.method == "POST":
        data = json.loads(request.body)
        workflow_name = data.get("workflow_name")

        workflow_file = WORKFLOWS_PATH / f"{workflow_name}.yaml"

        return FileResponse(open(workflow_file, "rb"), as_attachment=True)
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def import_workflow(request):
    if request.method == "POST":
        data = json.loads(request.body)
        workflow = data.get("workflow_file")
        new_name = data.get("new_name")

        workflow_file = settings.FILE_UPLOAD_TEMP_DIR / workflow

        if new_name == "":
            copy2(
                str(workflow_file),
                str((WORKFLOWS_PATH / workflow).with_suffix(".yaml")),
            )
        else:
            try:
                copy2(str(workflow_file), str(WORKFLOWS_PATH / f"{new_name}.yaml"))
            except Exception as exception:
                return JsonResponse(
                    {"success": False, "message": "That is not a valid name"},
                    status=405,
                )

        return JsonResponse({"success": True, "message": "Imported the workflow"})
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def delete_workflow(request):
    if request.method == "POST":
        data = json.loads(request.body)
        workflow_name = data.get("workflow_name")

        try:
            success, filename = delete_workflow_file(workflow_name)
            if not success:
                return JsonResponse(
                    {
                        "success": False,
                        "message": f"Workflow {filename} does not exist.",
                    },
                    status=404,
                )
            return JsonResponse({"success": True, "message": "Deleted run"})
        except Exception as e:
            traceback.print_exc()
            return JsonResponse(
                {
                    "success": False,
                    "message": format_trace(traceback.format_exception(e)),
                },
                status=404,
            )
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def get_run_data(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")

        run = Run(run_name)
        run_data = {}

        if run.current_step is not None:
            run_data["displayed_steps"] = get_displayed_steps(run.steps)
            run_data["current_section"] = run.current_step.section
            run_data["current_step_id"] = run.steps.current_selected_step_id
            run_data["recommended_next_step_id"] = run.steps.recommended_next_step_id
            run_data["memory_usage"] = get_memory_usage()
            run_data["current_step_has_plot"] = (
                True if run.current_step.plot_method is not None else False
            )
            run_data["__dbg_graph_nodes"] = list(run.steps.graph.nodes())
            run_data["graph_edges"] = run.steps.get_edges()
        else:
            run_data["displayed_steps"] = []
            run_data["current_section"] = None
            run_data["current_step"] = None
            run_data["current_step_id"] = None
            run_data["memory_usage"] = get_memory_usage()
            run_data["current_step_has_plot"] = False

        return JsonResponse(
            {"success": True, "message": "Got the data for the run", "data": run_data},
            safe=False,
        )
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def get_step_form(request):
    if request.method == "POST":
        data: dict = json.loads(request.body)
        run_name = data.get("run_name")
        new_form_values = data.get("data")

        run = Run(run_name)

        if new_form_values != {}:
            run.steps.invalidate_current_and_following_steps()

        form = run.current_form(new_form_values)

        return JsonResponse(
            {"success": True, "message": "Received input parameters", "data": form},
            safe=False,
            encoder=Form.CustomEncoder,
        )
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def get_step_plots(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")

        run = Run(run_name)
        if run.current_step is not None:
            plots = [to_json(plot) for plot in run.current_plots.plots]
        else:
            plots = []

        return JsonResponse(
            {"success": True, "message": "Got the plot(s) for the step", "data": plots},
            safe=False,
        )
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def get_downloads_from_step(request: HttpRequest):
    """
    API call. Returns a base64-encoded PNG of a step output to the front-end
    """
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )

    data = json.loads(request.body)
    run_name = data.get("run_name")
    step_id = data.get("step_id")
    output_key = data.get("output_key")

    run = Run(run_name)
    step = run.steps.get_step_by_id(step_id)
    #output = step.output.get(output_key)

    if run.current_step is not None:
        downloads = step.output["downloads"]
    else:
        downloads = {}

    return JsonResponse({"success": True, "message": "Got the available download(s) for the step", "data": downloads})


# TODO: Move somewhere else
def _step_output_as_serialised_table(
    label: str, _data: pd.DataFrame | Any, index_delims: tuple[int, int] = (None, None)
) -> list[dict]:
    """
    Returns the output data of a step as a list of dicts in "records" orientaion, like this:
    [{'col1': 1, 'col2': 0.5}, {'col1': 2, 'col2': 0.75}]
    Also delimits the return according to index_delims.
    If the output could not be serialised, None is returned

    :param label: The label of the step output to serialise
    :param _data: The data associated with the output
    :param index_delims: tuple used as slice begin and end indices to delimit the output
    """
    start_index = index_delims[0]
    end_index = index_delims[1]

    # Note: using [None:None] as a slice returns the entire collection
    if isinstance(_data, pd.DataFrame):
        data = _data.iloc[start_index:end_index].copy()

        # Safer than just adding the new column. We assume __id_col is not
        # a column name anyone would use
        if "id" in data.columns:
            data.rename(columns={"id": "__id_col"}, inplace=True)

        data["id"] = data.index
        cleaned_data = data.replace(np.nan, None)
        return cleaned_data.to_dict(orient="records")

    # Serialise compatible lists
    # TODO #49 this should be refactored to be stored somewhere and not be calculated on every call (can take a few seconds)
    # Potential fix: Just do not use lists bro???
    elif (
        ("_df" not in label) and (label not in hidden_outputs) and (type(_data) == list)
    ):
        data = pd.DataFrame({label: _data[start_index:end_index]})
        data["id"] = data.index
        cleaned_data = data.replace(np.nan, None)
        return cleaned_data.to_dict(orient="records")

    else:
        return None


def get_png_from_step(request: HttpRequest):
    """
    API call. Returns a base64-encoded PNG of a step output to the front-end
    """
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )

    data = json.loads(request.body)
    run_name = data.get("run_name")
    step_id = data.get("step_id")
    output_key = data.get("output_key")

    run = Run(run_name)
    step = run.steps.get_step_by_id(step_id)
    output = step.output.get(output_key)
    if not isinstance(output, bytes):
        return JsonResponse(
            {
                "success": False,
                "message": f"Requested output must be bytes object, is {str(type(output))}",
            },
            status=405,
        )

    content = output.decode("utf-8")
    return JsonResponse({"success": True, "message": "OK", "data": content})


def get_current_step_table_data(request):
    """
    API call. Returns a specific delimited slice of data from a specified table
    of the current step's outputs.
    """
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )

    data = json.loads(request.body)

    run_name = data.get("run_name")
    table_label = data.get("table_label")
    start_index = data.get("start_index")
    end_index = data.get("end_index")
    index_delims = (start_index, end_index)

    response = {"success": False, "message": None, "rows": None, "total_row_count": 0}

    run = Run(run_name)

    if run.current_step is None:
        response["message"] = "No step selected"
        return JsonResponse(response, status=500)

    step_output = run.current_outputs[table_label]
    if step_output is None:
        response["message"] = "Requested step output not found"
        return JsonResponse(response, status=404)

    serialised_output = _step_output_as_serialised_table(
        table_label, step_output, index_delims
    )

    if serialised_output is None:
        response["rows"] = [
            {
                "Info": f"This step output of type {str(type(step_output))} cannot be displayed as a table"
            }
        ]
    else:
        response["success"] = True
        response["rows"] = serialised_output

    response["total_row_count"] = len(step_output)

    return JsonResponse(response)


def get_current_step_output_labels(request):
    """
    API call. Returns all output labels of the current step and their respective visual labels
    """

    if request.method != "POST":
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )

    data = json.loads(request.body)

    run_name = data.get("run_name")
    run = Run(run_name)

    response = {
        "success": False,
        "message": None,
        "outputs": [],
    }

    if run.current_step is None:
        response["message"] = "No step selected"
        return JsonResponse(response, status=500)

    for label, data in run.current_outputs:
        if label not in hidden_outputs:
            response["outputs"].append(
                {
                    "label": label,
                    "display_name": get_display_name(label),
                    "output_type": data.output_type,
                }
            )

    response["success"] = True
    return JsonResponse(response)


def calculate_step(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")
        user_input = data.get("data")

        run = Run(run_name)

        if not run.current_step_ready_for_calculation:
            return JsonResponse(
                {
                    "success": False,
                    "message": dict(
                        level=logging.ERROR,
                        msg="At least one dependent step has not been calculated yet",
                    ),
                }
            )

        run.current_form(user_input)
        run.step_calculate()

        calculation_data = {}
        calculation_data["step_id"] = run.current_step.instance_identifier
        calculation_data["status"] = run.current_step.calculation_status
        calculation_data["messages"] = [
            message for message in run.current_messages.messages
        ]

        if calculation_data["status"] != "complete":
            return JsonResponse(
                {
                    "success": False,
                    "message": calculation_data["messages"],
                    "data": calculation_data,
                },
                status=500,
            )
        return JsonResponse(
            {
                "success": True,
                "message": calculation_data["messages"],
                "data": calculation_data,
            },
            safe=False,
        )
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def upload_file(request):
    if request.method == "POST" and request.FILES.get("file"):
        return JsonResponse({"success": True, "message": "File uploaded successfully!"})
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method or no file provided"},
            status=400,
        )
