import json
import shutil
from datetime import date

import pandas
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from backend.main import settings
from backend.protzilla.constants.paths import EXTERNAL_DATA_PATH
from backend.protzilla.data_integration.database_query import uniprot_columns, uniprot_databases

database_metadata_path = EXTERNAL_DATA_PATH / "internal" / "metadata" / "uniprot.json"


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