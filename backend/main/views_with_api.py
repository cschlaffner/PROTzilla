import json
import os
import io
import tempfile
import traceback
import zipfile

from plotly.io import to_json
from pathlib import Path

import pandas as pd
from django.contrib import messages
from django.http import JsonResponse, FileResponse

import backend.protzilla.constants.paths as paths
from backend.protzilla.disk_operator import YamlOperator
from backend.protzilla.run import Run, delete_run_folder, get_available_runinfo
from backend.protzilla.workflow import get_available_workflow_names
from backend.protzilla.constants.paths import EXTERNAL_DATA_PATH
from backend.protzilla.data_integration.database_query import uniprot_columns, uniprot_databases
from backend.protzilla.utilities import format_trace, get_memory_usage
from backend.protzilla.stepfactory import StepFactory
from backend.protzilla.steps import Step
from backend.main.views_with_api_helper import get_displayed_steps, parameters_from_post, get_all_possible_step_names

database_metadata_path = EXTERNAL_DATA_PATH / "internal" / "metadata" / "uniprot.json"


active_runs: dict[str, Run] = {}

def run_information_list(request):
    run_info = get_available_runinfo()
    if not run_info:

        return JsonResponse(None, safe=False) #not clean, maybe use error message or smth
    runs, runs_favourite, all_tags = run_info
    all_available_runs = runs_favourite + runs
    available_runinfo = [all_available_runs, all_tags]

    return JsonResponse(available_runinfo, safe=False)

def step_name_list(request):
    step_names = get_all_possible_step_names()

    return JsonResponse(step_names, safe=False)

def workflow_name_list(request):
    workflow_names = get_available_workflow_names()

    return JsonResponse(workflow_names, safe=False)

def toggle_favourite(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")
    
        directory_path = os.path.join(paths.RUNS_PATH, run_name)
        metadata_yaml_path = os.path.join(directory_path, "metadata.yaml")

        yaml_operator = YamlOperator()
        metadata = {}
        if not os.path.exists(metadata_yaml_path):
           with open(metadata_yaml_path, 'w') as file:
               pass
        else:
            metadata = yaml_operator.read(metadata_yaml_path)

        metadata["favourite"]= not metadata.get("favourite", False)
        yaml_operator.write(Path(metadata_yaml_path), metadata)

        return JsonResponse({"success": True, "message": "Favourited run"})
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

def add_tag(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")
        run_tag = data.get("tag_name")

        tags = set()
        directory_path = os.path.join(paths.RUNS_PATH, run_name)
        metadata_yaml_path = os.path.join(directory_path, "metadata.yaml")

        yaml_operator = YamlOperator()
        metadata = {}
        if not os.path.exists(metadata_yaml_path):
            with open(metadata_yaml_path, 'w') as file:
                pass
        else:
            metadata = yaml_operator.read(metadata_yaml_path)
            tags_from_metadata = metadata.get("tags")
            if tags_from_metadata:
                tags.update(tags_from_metadata)
        tags.add(run_tag)
        metadata["tags"]= tags
        yaml_operator.write(Path(metadata_yaml_path), metadata)

        return JsonResponse({"success": True, "message": "Added tag"})
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

def delete_tag(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")
        run_tag = data.get("tag_name")
    
        directory_path = os.path.join(paths.RUNS_PATH, run_name)
        metadata_yaml_path = os.path.join(directory_path, "metadata.yaml")

        yaml_operator = YamlOperator()
        metadata = yaml_operator.read(metadata_yaml_path)
        tags = metadata.get("tags")
        tags.remove(run_tag)
        metadata["tags"] = tags
        yaml_operator.write(Path(metadata_yaml_path), metadata)

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

        active_runs[run_name] = Run(run_name)
        

        return JsonResponse({"success": True, "message": "Continued run"})
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
            run.step_calculate(parameters)
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

        return JsonResponse({"success": True, "message": "Deleted step"})
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

        run_data["displayed_steps"] = get_displayed_steps(run.steps)
        run_data["current_section"] = run.current_step.section
        run_data["current_step"] = run.current_step.instance_identifier
        run_data["memory_usage"] = get_memory_usage()

        return JsonResponse({"success": True, "message": "Got the data for the run", "data": run_data}, safe=False)
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
def get_step_parameters(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")

        run = active_runs[run_name]
        
        #get parameters for the step

        return JsonResponse({"success": True, "message": "Got the parameters for the step", "data": "placeholder"}, safe=False)
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
def get_step_plots(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")

        run = active_runs[run_name]
        plots = [to_json(plot) for plot in run.current_plots.plots]

        return JsonResponse({"success": True, "message": "Got the plot(s) for the step", "data": plots}, safe=False)
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

def get_step_table(request):
    if request.method == "POST":
        data = json.loads(request.body)
        run_name = data.get("run_name")

        run = active_runs[run_name]
        
        #get parameters for the step

        return JsonResponse({"success": True, "message": "Got the table for the step", "data": "placeholder"}, safe=False)
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

