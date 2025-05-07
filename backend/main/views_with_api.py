import json
import io
import tempfile
import traceback
import zipfile

import numpy as np
from plotly.io import to_json

import pandas as pd
from django.http import JsonResponse, FileResponse

from backend.protzilla.form import Form
from backend.protzilla.run import Run, delete_run_folder, get_available_run_info, get_available_run_names
from backend.protzilla.workflow import get_available_workflow_names
from backend.protzilla.constants.paths import EXTERNAL_DATA_PATH
from backend.protzilla.utilities import format_trace, get_memory_usage
from backend.protzilla.stepfactory import StepFactory
from backend.protzilla.steps import Step
from backend.main.views_with_api_helper import get_step, get_displayed_steps, parameters_from_post, get_all_possible_steps

database_metadata_path = EXTERNAL_DATA_PATH / "internal" / "metadata" / "uniprot.json"


active_runs: dict[str, Run] = {}

def get_run(run_name: str) -> Run:
    """
    Get the run object for the given run name to minimize the creation of new run objects. If the run is not in active runs, it will be created.

    :param run_name: The name of the run.
    """
    if run_name not in active_runs:
        run = Run(run_name)
        active_runs[run_name] = run
    else:
        run = active_runs[run_name]
    return run

def run_information_list(request):
    run_info = get_available_run_info()
    if type(run_info) == str:
        return JsonResponse(success=False, data=None, messages=run_info, safe=False)
    if not run_info or len(run_info) == 0:
        return JsonResponse(success=False, data=None, messages="An unkown error occured when creating run table.",safe=False)
    runs, runs_favourite, all_tags = run_info
    all_available_runs = runs_favourite + runs
    available_run_info = [all_available_runs, all_tags]

    return JsonResponse(success=True, data=available_run_info, safe=False)

def all_steps(request):
    steps = get_all_possible_steps()
    return JsonResponse(steps, safe=False)

def workflow_name_list(request):
    workflow_names = get_available_workflow_names()

    return JsonResponse(workflow_names, safe=False)

def toggle_favourite(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")

        run = get_run(run_name)
        metadata = run.metadata_read()
        metadata["favourite"] = not metadata.get("favourite", False)
        run.metadata_write(metadata)

        return JsonResponse({"success": True, "message": "Favourited run"})
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

def add_tag(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")
        run_tag = data.get("tag_name")

        run = get_run(run_name)
        metadata = run.metadata_read()
        tags = metadata.get("tags", set())
        tags.add(run_tag)
        metadata["tags"] = tags
        run.metadata_write(metadata)

        return JsonResponse({"success": True, "message": "Added tag"})
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

def delete_tag(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")
        run_tag = data.get("tag_name")

        run = get_run(run_name)
        metadata = run.metadata_read()
        tags = metadata.get("tags", set())
        tags.remove(run_tag)
        metadata["tags"] = tags
        run.metadata_write(metadata)

        return JsonResponse({"success": True, "message": "Deleted tag"})
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

def add_run(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")
        workflow_name = data.get("workflow_name")
        df_mode_name = data.get("df_mode_name")

        try:
            run = Run(run_name, workflow_name, df_mode_name,)
            active_runs[run_name] = run

            return JsonResponse({"success": True, "message": "Created run"})
        except Exception as e:
            traceback.print_exc() #not sure if it still needs to be here 
            return JsonResponse({"success": False, "message": format_trace(traceback.format_exception(e))}, status=404)
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

def delete_run(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")

        try:
            if run_name in active_runs:
               del active_runs[run_name]
            delete_run_folder(run_name)

            return JsonResponse({"success": True, "message": "Deleted run"})
        except Exception as e:
            traceback.print_exc() #not sure if it still needs to be here 
            return JsonResponse({"success": False, "message": format_trace(traceback.format_exception(e))}, status=404)
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

def continue_run(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")

        get_run(run_name)
        

        return JsonResponse({"success": True, "message": "Continued run"})
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
def update_run_name(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")
        new_run_name = data.get("new_run_name")

        try:
            if new_run_name in get_available_run_names():
                return JsonResponse({"success": False, "message": "Run name already exists."})

            run = get_run(run_name)
            run.update_run_name(new_run_name)

            active_runs[new_run_name] = run
            if run_name in active_runs:
                del active_runs[run_name]

            return JsonResponse({"success": True, "message": "Renamed run"})
        except Exception as e:
            if isinstance(e, OSError):
                return JsonResponse({"success": False, "message": "Run name already exists."})
            return JsonResponse({"success": False, "message": "Error when renaming run: " + str(e)}, status=404)
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

def add_plot(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")

        parameters = parameters_from_post(request.POST)
        run = active_runs[run_name]
        if run.current_step.display_name == "plot":
            del parameters["chosen_method"]
            run.current_form(parameters)
            run.step_calculate()
        else:
            run.current_step.plot(parameters)

        return JsonResponse({"success": True, "message": "Created plot"})
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
def add_step(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")
        method = data.get("method")

        run = active_runs[run_name]
        step = StepFactory.create_step(method, run.steps)
        run.step_add(step)

        return JsonResponse({"success": True, "message": "Added step: " + method, "data": get_step(step)}, safe=False)
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

def delete_step(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")
        section = data.get("section") #this is a bit different to the original, but frontend prob has to deal with it :)
        index = data.get("index")

        index = int(index)
        run = active_runs[run_name]
        run.step_remove(step_index=index, section=section)

        return JsonResponse({"success": True, "message": "Deleted step"})
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

def update_step(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")
        method = data.get("method")

        run = active_runs[run_name]

        run.step_change_method(method)

        return JsonResponse({"success": True, "message": "Updated step method"})
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

def navigate_to_step(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")
        section = data.get("section") #this is a bit different to the original, but frontend prob has to deal with it :)
        index = data.get("index")

        index = int(index) 
        run = active_runs[run_name]
        run.step_goto(index, section)

        return JsonResponse({"success": True, "message": "Navigated successfully"})
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)


def export_workflow(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")
        workflow_name = data.get("workflow_name")

        run = active_runs[run_name]
        run._workflow_export(workflow_name)

        return JsonResponse({"success": True, "message": "Exported workflow"})
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
def download_plots(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")
        format = data.get("format")

        run = active_runs[run_name]

        index = run.steps.current_step_index
        section = run.current_step.section
        operation = run.current_step.operation
        exported = run.current_plots.export(format_=format)
        if len(exported) == 1:
            filename = f"{index}-{section}-{operation}.{format}"
            return FileResponse(exported[0], filename=filename, as_attachment=True)

        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_filename = f.name
        with zipfile.ZipFile(temp_filename, "w") as zf:
            for i, plot in enumerate(exported):
                filename = f"{index}-{section}-{operation}-{i}.{format}"
                zf.writestr(filename, plot.getvalue())
        return FileResponse(
            open(temp_filename, "rb"),
            filename=f"{index}-{section}-{operation}.zip",
            as_attachment=True,
        )
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

    
def download_table(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")
        index = data.get("index")
        key = data.get("key")

        run = active_runs[run_name]

        instance_id = run.steps.all_steps[index].instance_identifier
        buffer = io.StringIO()
        df: pd.DataFrame = run.steps.get_step_output(
            Step, key, instance_id, include_current_step=True
        )
        df.to_csv(buffer)

        buffer.seek(0)
        csv_bytes = buffer.getvalue()

        return FileResponse(csv_bytes, content_type="text/csv")
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
def get_run_data(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")

        run = active_runs[run_name]
        run_data = {}

        if run.current_step is not None:
            run_data["displayed_steps"] = get_displayed_steps(run.steps)
            run_data["current_section"] = run.current_step.section
            run_data["current_step_index"] = run.steps.current_step_index
            run_data["memory_usage"] = get_memory_usage()
        else:
            run_data["displayed_steps"] = []
            run_data["current_section"] = None
            run_data["current_step"] = None
            run_data["memory_usage"] = get_memory_usage()

        return JsonResponse({"success": True, "message": "Got the data for the run", "data": run_data}, safe=False)
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
def get_step_form(request):
    if request.method == "POST":
        data:dict = json.loads(request.body)
        run_name = data.get("run_name")
        new_form_values = data.get("data")
        
        if (run_name not in active_runs):
            return JsonResponse({"success": False, "message": "Run not in active runs"})

        run = active_runs[run_name]

        if new_form_values!={}:
            run.steps.set_steps_outdated()

        form = run.current_form(new_form_values)

        return JsonResponse({"success": True, "message": "Received input parameters", "data": form}, safe=False, encoder=Form.CustomEncoder)
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

def get_step_plots(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")

        run = active_runs[run_name]
        if run.current_step is not None:
            plots = [to_json(plot) for plot in run.current_plots.plots]
        else:
            plots = []

        return JsonResponse({"success": True, "message": "Got the plot(s) for the step", "data": plots}, safe=False)
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

def get_step_table(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")

        run = active_runs[run_name]
        
        if run.current_step is not None:
            if "protein_df" in run.current_outputs:
                data = run.current_outputs["protein_df"]
                data["id"] = data.index
                cleaned_data = data.replace(np.nan, None)
                json_data = cleaned_data.to_dict(orient="records")
            else:
                json_data = [{}]

        return JsonResponse({"success": True, "message": "Got the table for the step", "data": json_data}, safe=False)
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

def calculate_step(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")
        user_input = data.get("data")

        run = active_runs[run_name]
        run.current_form(user_input)
        run.step_calculate()

        calculation_data = {}
        calculation_data["section"] = run.current_step.section
        calculation_data["index"] = run.steps.current_step_index_in_section
        calculation_data["status"] = run.current_step.calculation_status
        calculation_data["messages"] = [str(message) for message in run.current_messages.messages]

        if calculation_data["status"] != "complete":
            return JsonResponse({"success": False, "message": calculation_data["messages"]
                                , "data": calculation_data}, status=500)
        return JsonResponse({"success": True, "message": "Calculated step", "data": calculation_data})
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        return JsonResponse({"success": True, "message": "File uploaded successfully!"})
    else:
        return JsonResponse({"success": False, "message": "Invalid request method or no file provided"}, status=400)