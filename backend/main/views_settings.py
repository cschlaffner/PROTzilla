import json
import shutil
from datetime import date
from io import BytesIO

import pandas
import plotly.graph_objects as go
import plotly.io as pio
from PIL import Image
from django.contrib import messages
from django.http import JsonResponse, FileResponse

from backend.main import settings
from backend.main.views_helper import sanitize_name, load_plot_settings_from_file
from backend.protzilla.constants.paths import EXTERNAL_DATA_PATH, SETTINGS_PATH
from backend.protzilla.data_integration.database_query import uniprot_columns, uniprot_databases
from backend.protzilla.disk_operator import YamlOperator

database_metadata_path = EXTERNAL_DATA_PATH / "internal" / "metadata" / "uniprot.json"


# <--- Plot Export --->

def load_settings(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({"success": False, "message": "Invalid JSON response while loading the settings."}, status=400)
        templateName = data.get("templateName")

        plot_settings = load_plot_settings_from_file(templateName)
        return JsonResponse(plot_settings)
    return JsonResponse({"success": False, "message": "Only POST requests are allowed."}, status=405)


def save_settings(request):
    if request.method == "POST":
        settings = json.loads(request.body.decode("utf-8"))
        op = YamlOperator()
        path = SETTINGS_PATH / ("plots.yaml")
        try:
            op.write(path, settings)
        except:
            return JsonResponse({"success": False, "message": "Saving failed!"}, status=400)
        
        # TODO Update Plotly template that is used in run screen
        return JsonResponse({"success": True, "message": "Settings successfully saved."}, status=200)
    return JsonResponse({"success": False, "message": "Only POST requests are allowed."}, status=405)


def download_plot(request):
    if request.method == "POST":
        params = json.loads(request.body.decode("utf-8"))
        fig = go.Figure(json.loads(params["plot"]))
        file = get_plot_file(fig, params)
    return FileResponse(file)


def get_plot_file(fig: go.Figure, params: dict):
    file_format = params["fileFormat"]
    if file_format in ["eps", "tiff"]:
        fig_binary = pio.to_image(fig, format="png", scale=params["scale"])
        img = Image.open(BytesIO(fig_binary)).convert("RGB")
        binary = BytesIO()
        args = {"format": file_format}
        if file_format == "tiff":
            args["compression"] = "tiff_lzw"
        img.save(binary, **args)
    elif file_format == "pdf":
        img = pio.to_image(fig, format=file_format, scale=params["scale"])
        binary = BytesIO(img)
    binary.seek(0)
    return binary

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

        converted_name, message = sanitize_name(name)

        if converted_name is None or converted_name == "":
            msg = "Filename cannot be empty."
            messages.add_message(request, messages.ERROR, msg, "alert-danger")
            return JsonResponse({"success": False, "message": msg}, status=400)

        if database_path(converted_name).exists():
            msg = "Filename already taken."
            messages.add_message(request, messages.ERROR, msg, "alert-danger")
            return JsonResponse({"success": False, "message": msg}, status=400)

        if not (EXTERNAL_DATA_PATH / "uniprot").exists():
            (EXTERNAL_DATA_PATH / "uniprot").mkdir(parents=True)

        just_copy_string = data.get("just_copy", False)
        if just_copy_string == "True":
            shutil.copy(path, database_path(converted_name))
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

            dataframe.to_csv(database_path(converted_name), sep="\t", index=False)
            num_proteins = len(dataframe)

        if not database_metadata_path.parent.exists():
            database_metadata_path.parent.mkdir(parents=True)

        if database_metadata_path.exists():
            with open(database_metadata_path, "r") as f:
                database_metadata = json.load(f)
        else:
            database_metadata = {}
        database_metadata[converted_name] = dict(
            num_proteins=num_proteins, date=date.today().isoformat()
        )
        with open(database_metadata_path, "w") as f:
            json.dump(database_metadata, f)

        return JsonResponse({"success": True, "message": f"Database uploaded successfully. \n {message}" if len(message) > 0 else "Database uploaded successfully"}, status=200)
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
