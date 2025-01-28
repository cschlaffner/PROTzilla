import json
import shutil
from datetime import date

import pandas
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from backend.protzilla.constants.paths import EXTERNAL_DATA_PATH
from backend.protzilla.data_integration.database_query import uniprot_columns, uniprot_databases

#Most functions are not important right now, should be done when backend placement from protzilla2 is clear | by 10.02.

database_metadata_path = EXTERNAL_DATA_PATH / "internal" / "metadata" / "uniprot.json"

def available_runinfo(request):
    runs, runs_favourite, all_tags = get_available_runinfo()
    all_available_runs = runs_favourite + runs
    available_runinfo = [all_available_runs, all_tags]

    return JsonResponse(available_runinfo, safe=False)

def step_names(request):
    step_names = get_all_possible_step_names()

    return JsonResponse(step_names, safe=False)

def workflow_names(request):
    workflow_names = get_available_workflow_names()

    return JsonResponse(workflow_names, safe=False)

def make_favourite(request):
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
    
