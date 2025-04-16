import json
import shutil
from datetime import date

import pandas
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from backend.main import settings
from backend.protzilla.constants.paths import EXTERNAL_DATA_PATH, SETTINGS_PATH
from backend.protzilla.data_integration.database_query import uniprot_columns, uniprot_databases
from backend.protzilla.disk_operator import YamlOperator

database_metadata_path = EXTERNAL_DATA_PATH / "internal" / "metadata" / "uniprot.json"

# <--- Plot Export --->

def load_settings(request):
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({"error": "Invalid JSON response while loading the settings."}, status=400)
    templateName = data.get("templateName")

    op = YamlOperator()
    path = SETTINGS_PATH / (templateName + ".yaml")
    default_path = SETTINGS_PATH / ("plots_default.yaml")

    if (templateName == "plots_default" or not path.exists()):
        settings = op.read(default_path)
    else:
        settings = op.read(path)
    return JsonResponse(settings)

def save_settings(request):
    if request.method == "POST":
        settings = json.loads(request.body.decode("utf-8"))

        op = YamlOperator()
        path = SETTINGS_PATH / ("plots.yaml")
        op.write(path, settings)

        # TODO Update Plotly template that is used in run screen
        return JsonResponse({"success": True, "message": "Settings successfully saved."}, status=200)
    return JsonResponse({"error": "Only POST requests are allowed."}, status=405)
    
# TODO Include the following methods and functionalities from PROTzilla2

# SCALED_WIDTH = 600
# PT_TO_INCH = 1 / 72
# INCH_TO_MM = 25.4
# DPI = 300
# template = None

# def determine_font(params: dict) -> str:
#     """
#     Returns the selected or a given custom font.
#     :param params: Dict with parameter and values from this settings section.
#     :return: Selected font.
#     """
#     if(params["font"] == "Custom"):
#         font = params["custom_font"]
#     else:
#         font = params["font"]
#     return font

# def resize_for_display(params: dict) -> dict:
#     """
#     Scales the input sizes to sizes that can be easily displayed in a webbrowser.
#     :param params: Dict containing the plot settings.
#     :return: Dict containing plot settings with scaled sizes.
#     """
#     # Figure size
#     ratio = params["width"] / params["height"]
#     display_height = int(SCALED_WIDTH / ratio)
#     # Font size
#     ratio = SCALED_WIDTH / params["width"]
#     display_heading = int(params["heading_size"] * PT_TO_INCH * INCH_TO_MM * ratio)
#     display_text = int(params["text_size"] * PT_TO_INCH * INCH_TO_MM * ratio)
#     params["display_width"] = SCALED_WIDTH
#     params["display_height"] = display_height
#     params["display_heading_size"] = display_heading
#     params["display_text_size"] = display_text
#     return params

# def get_scale_factor(
#         fig: go.Figure,
#         params: dict
#     ) -> float:
#     """
#     Calculates the scale factor for downloading the plot in desired size and resolution.
#     :param fig: Plotly figure to be scaled.
#     :param params: Dict containing the plot settings.
#     :return: Scale factor to scale the whole plot to desired size.
#     """
#     current_width = fig.layout.width or SCALED_WIDTH
#     scale_factor = (params["width"] / INCH_TO_MM * DPI) / current_width
#     return scale_factor

# <--- Databases --->

def get_databases(request):
    databases = uniprot_databases()
    df_infos = []
    if database_metadata_path.exists():
        with open(database_metadata_path, "r") as f:
            database_metadata = json.load(f)
    else:
        database_metadata = {}

    for db in databases:
        database = dict(
            name=db,
            cols=uniprot_columns(db),
            filesize=database_path(db).stat().st_size,
            date=database_metadata.get(db, {}).get("date", ""),
            num_proteins=database_metadata.get(db, {}).get("num_proteins", 0),
        )
        df_infos.append(database)
    return JsonResponse(df_infos, safe=False)


def database_upload(request):
    if request.method == "POST":
        data = json.loads(request.body)
        name = data.get("name")
        file_name = data.get("file")
        path = settings.FILE_UPLOAD_TEMP_DIR / file_name

        if database_path(name).exists():
            msg = "Filename already taken."
            messages.add_message(request, messages.ERROR, msg, "alert-danger")
            return JsonResponse({"success": False, "message": msg}, status=400)

        if not (EXTERNAL_DATA_PATH / "uniprot").exists():
            (EXTERNAL_DATA_PATH / "uniprot").mkdir(parents=True)

        just_copy_string = data.get("just_copy", False)
        if just_copy_string == "True":
            shutil.copy(path, database_path(name))
            num_proteins = 0
        else:
            if path.suffix != ".tsv":
                msg = "File must be a tab-separated file with the extension .tsv"
                messages.add_message(request, messages.ERROR, msg, "alert-danger")
                return JsonResponse({"success": False, "message": msg}, status=400)

            try:
                dataframe = pandas.read_csv(path, sep="\t")
            except UnicodeDecodeError:
                msg = "File could not be decoded."
                messages.add_message(request, messages.ERROR, msg, "alert-danger")
                return JsonResponse({"success": False, "message": msg}, status=400)

            if "Entry" not in dataframe.columns:
                msg = "Required 'Entry' column not found."
                messages.add_message(request, messages.ERROR, msg, "alert-danger")
                return JsonResponse({"success": False, "message": msg}, status=400)

            dataframe.to_csv(database_path(name), sep="\t", index=False)
            num_proteins = len(dataframe)

        if not database_metadata_path.parent.exists():
            database_metadata_path.parent.mkdir(parents=True)

        if database_metadata_path.exists():
            with open(database_metadata_path, "r") as f:
                database_metadata = json.load(f)
        else:
            database_metadata = {}
        database_metadata[name] = dict(
            num_proteins=num_proteins, date=date.today().isoformat()
        )
        with open(database_metadata_path, "w") as f:
            json.dump(database_metadata, f)

        return JsonResponse({"success": True, "message": "Database uploaded successfully"}, status=200)
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)


def database_delete(request):
    if request.method == "POST":
        data = json.loads(request.body)
        database_name = data.get("name")
        path = database_path(database_name)
        path.unlink()

        if database_metadata_path.exists():
            with open(database_metadata_path, "r") as f:
                database_metadata = json.load(f)

            if database_name in database_metadata:
                del database_metadata[database_name]
                with open(database_metadata_path, "w") as f:
                    json.dump(database_metadata, f)


        return JsonResponse({"success": True, "message": "Database deleted successfully"}, status=200)
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

def database_path(name):
    return EXTERNAL_DATA_PATH / "uniprot" / f"{name}.tsv"