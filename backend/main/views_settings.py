import json
import os
import shutil
from datetime import date, datetime, timezone
from io import BytesIO
from pathlib import Path


import pandas
import plotly.graph_objects as go
import plotly.io as pio
from PIL import Image
from django.contrib import messages
from django.http import JsonResponse, FileResponse

from backend.main import settings
from backend.main.views_helper import (
    sanitize_name,
    load_settings_from_file,
    validate_uploaded_files,
    copy_file_to_directory,
)
from backend.protzilla.constants.paths import EXTERNAL_DATA_PATH, SETTINGS_PATH
from backend.protzilla.data_integration.database_query import (
    uniprot_columns,
    uniprot_databases,
)
from backend.protzilla.disk_operator import YamlOperator
from main.views_helper import load_yaml_from_file
from protzilla.constants.paths import (
    CUSTOM_PLOT_SETTINGS_FILE_STEM,
    DEFAULT_PLOT_SETTINGS_FILE_STEM,
    DEFAULT_PTM_SETTINGS_FILE_STEM,
    CUSTOM_PTM_SETTINGS_FILE_STEM,
)

DATABASE_METADATA_PATH = EXTERNAL_DATA_PATH / "internal" / "metadata" / "uniprot.json"


def load_settings(request, default_file_stem: str):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid JSON response while loading the settings.",
                },
                status=400,
            )
        template_name = data.get("templateName")

        settings = load_settings_from_file(template_name, default_file_stem)
        return JsonResponse(settings)
    return JsonResponse(
        {"success": False, "message": "Only POST requests are allowed."}, status=405
    )


# <--- Plot Export --->


def load_plot_settings(
    request, default_file_stem: str = DEFAULT_PLOT_SETTINGS_FILE_STEM
):
    return load_settings(request, default_file_stem)


def save_plot_settings(request):
    if request.method == "POST":
        settings = json.loads(request.body.decode("utf-8"))
        op = YamlOperator()
        path = SETTINGS_PATH / f"{CUSTOM_PLOT_SETTINGS_FILE_STEM}.yaml"
        try:
            op.write(path, settings)
        except:
            return JsonResponse(
                {"success": False, "message": "Saving failed!"}, status=400
            )

        # TODO Update Plotly template that is used in run screen
        return JsonResponse(
            {"success": True, "message": "Settings successfully saved."}, status=200
        )
    return JsonResponse(
        {"success": False, "message": "Only POST requests are allowed."}, status=405
    )


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


# <--- PTM Settings --->


def load_ptm_settings(request, default_file_stem: str = DEFAULT_PTM_SETTINGS_FILE_STEM):
    return load_settings(request, default_file_stem)


def load_default_ptm_settings_as_yaml(request):
    try:
        example_settings = load_yaml_from_file(
            SETTINGS_PATH / f"{DEFAULT_PTM_SETTINGS_FILE_STEM}.yaml"
        )
    except:
        return JsonResponse(
            {"success": False, "message": "Couldn't load default settings from file."},
            status=400,
        )

    return JsonResponse({"example_settings": example_settings})


def _load_dict_from_yaml_file(request, filename: str) -> tuple[dict | None, str]:
    path = settings.FILE_UPLOAD_TEMP_DIR / filename
    if path.suffix != ".yaml":
        msg = "File must be a YAML file with the extension .yaml"
        messages.add_message(request, messages.ERROR, msg, "alert-danger")
        return None, msg
    try:
        data = YamlOperator().read(path)
    except UnicodeDecodeError:
        msg = "File could not be decoded."
        messages.add_message(request, messages.ERROR, msg, "alert-danger")
        return None, msg
    return data, ""


def load_modification_settings_from_upload(
    request, old_settings, ptm_settings_filename: str
) -> tuple[dict | None, str]:
    modification_settings, msg = _load_dict_from_yaml_file(
        request, ptm_settings_filename
    )
    if modification_settings is None:
        return None, msg

    # Modifications should be overwritten, so that user can also remove modifications. Other stuff should retain the
    # same keys and thus also old values for unchanged keys.
    merged = old_settings
    if "modifications" in modification_settings:
        merged["modifications"] = modification_settings["modifications"]
    if "color_settings" in modification_settings:
        merged["color_settings"] = dict(
            old_settings["color_settings"], **modification_settings["color_settings"]
        )
    if "other_settings" in modification_settings:
        merged["other_settings"] = dict(
            old_settings["other_settings"], **modification_settings["other_settings"]
        )
    return merged, ""


def save_ptm_settings(request, default_file_stem: str = DEFAULT_PTM_SETTINGS_FILE_STEM):
    if not request.method == "POST":
        return JsonResponse(
            {"success": False, "message": "Only POST requests are allowed."}, status=405
        )

    ptm_settings_yaml_path = SETTINGS_PATH / f"{CUSTOM_PTM_SETTINGS_FILE_STEM}.yaml"
    op = YamlOperator()
    if not ptm_settings_yaml_path.exists():
        default_settings_yaml_path = SETTINGS_PATH / f"{default_file_stem}.yaml"
        old_settings = op.read(default_settings_yaml_path)
    else:
        old_settings = op.read(ptm_settings_yaml_path)

    request_args = json.loads(request.body.decode("utf-8"))
    if (ptm_settings_filename := request_args.get("ptm_settings_file", "")) != "":
        modification_settings, msg = load_modification_settings_from_upload(
            request, old_settings, ptm_settings_filename
        )
        if modification_settings is None:
            return JsonResponse({"success": False, "message": msg}, status=400)

    for _, mod_settings in modification_settings["modifications"].items():
        if not (
            "above_below" in mod_settings
            and isinstance(mod_settings["above_below"], str)
            and "color" in mod_settings
            and isinstance(mod_settings["color"], str)
            and "name" in mod_settings
            and isinstance(mod_settings["name"], str)
            and "sites" in mod_settings
            and isinstance(mod_settings["sites"], list)
        ):

            return JsonResponse(
                {
                    "success": False,
                    "message": "Provided modifications need to specify 'above_below' ('A'/'B'), 'color' (as hex "
                    "string), 'name' (string) and 'sites' (list of amino acids). Refer to the default "
                    "settings for an example.",
                },
                status=400,
            )

    try:
        op.write(ptm_settings_yaml_path, modification_settings)
    except:
        return JsonResponse({"success": False, "message": "Saving failed!"}, status=400)

    return JsonResponse(
        {"success": True, "message": "Settings successfully saved."}, status=200
    )


# <--- Protein Structure Predictions --->

AF_DICT_PATH = EXTERNAL_DATA_PATH / "alphafold"


def get_prot_structure(request):
    metadata_csv = AF_DICT_PATH / "alphafold_metadata.csv"
    df = pandas.read_csv(metadata_csv)

    df_infos = df.rename(
        columns={
            "entryID": "entry_id",
            "uniprotAccession": "uniprot_id",
            "modelCreatedDate": "date_modified",
            "gene": "gene",
            "alphafold_version": "af_version",
        }
    ).to_dict(orient="records")

    return JsonResponse(df_infos, safe=False)


def upload_prot_structure(request):
    if request.method == "POST":
        data = json.loads(request.body)
        uniprot_id = data.get("uniprot_id")
        entry_id = data.get("entry_id")
        af_version = data.get("af_version")
        gene = data.get("gene")
        cif_file = data.get("cif_file")
        confidence = data.get("confidence")
        pae = data.get("pae")
        fasta_file = data.get("fasta_file")

        # Validate uploaded files and copy them to source directory out of temp directory
        file_mapping = {
            cif_file: [".cif"],
            confidence: [".json"],
            pae: [".json"],
            fasta_file: [".fasta", ".fa"],
        }

        is_valid, validation_message = validate_uploaded_files(
            settings.FILE_UPLOAD_TEMP_DIR, file_mapping
        )
        if not is_valid:
            messages.add_message(
                request, messages.ERROR, validation_message, "alert-danger"
            )
            return JsonResponse(
                {"success": False, "message": validation_message}, status=400
            )

        af_path = AF_DICT_PATH / entry_id.upper()
        if af_path.exists():
            return JsonResponse(
                {"success": False, "message": "Entry ID is not unique."}, status=405
            )
        else:
            af_path.mkdir(parents=True, exist_ok=True)

        for file_name in [cif_file, confidence, pae, fasta_file]:
            source_dir = settings.FILE_UPLOAD_TEMP_DIR / file_name
            success, message = copy_file_to_directory(source_dir, af_path)

        # add row to metadata csv
        AF_DICT_PATH.mkdir(parents=True, exist_ok=True)
        metadata_csv = AF_DICT_PATH / "alphafold_metadata.csv"
        df = pandas.read_csv(metadata_csv)

        now_utc = datetime.now(timezone.utc)
        formatted = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

        new_row = {
            "entryID": entry_id,
            "uniprotAccession": uniprot_id,
            "modelCreatedDate": formatted,
            "gene": gene,
            "alphafold_version": af_version,
        }

        df = pandas.concat([df, pandas.DataFrame([new_row])], ignore_index=True)
        df.to_csv(metadata_csv, index=False)

        return JsonResponse(
            {
                "success": True,
                "message": (
                    f"Predicted Protein Structure uploaded successfully. \n {message}"
                    if len(message) > 0
                    else "Predicted Protein Structure uploaded successfully."
                ),
            },
            status=200,
        )
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def prot_structure_delete(request):
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )

    data = json.loads(request.body)
    entry_id = (data.get("entry_id") or "").strip()
    if not entry_id:
        return JsonResponse(
            {"success": False, "message": "Missing entry_id"}, status=400
        )

    # delete folder with files for the protein structure
    target_dir = AF_DICT_PATH / entry_id.upper()
    metadata_csv = AF_DICT_PATH / "alphafold_metadata.csv"

    if not target_dir.exists() or not target_dir.is_dir():
        return JsonResponse(
            {"success": False, "message": f"Entry folder not found: {target_dir.name}"},
            status=404,
        )

    try:
        shutil.rmtree(target_dir)
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"Failed to delete folder: {str(e)}"},
            status=500,
        )

    # remove entry out of metadata csv
    if (
        metadata_csv.exists()
        and metadata_csv.is_file()
        and metadata_csv.stat().st_size > 0
    ):
        try:
            df = pandas.read_csv(metadata_csv, dtype=str)
            df = df[
                df["entryID"].fillna("").str.strip().str.upper() != entry_id.upper()
            ]
            df.to_csv(metadata_csv, index=False)

        except Exception as e:
            return JsonResponse(
                {
                    "success": True,
                    "message": f"Folder deleted. Failed to update CSV: {str(e)}",
                },
                status=200,
            )

    return JsonResponse(
        {"success": True, "message": "Entry deleted successfully"}, status=200
    )


# <--- Databases --->


def get_databases(request):
    databases = uniprot_databases()
    df_infos = []
    # second check avoids errors if the metadata is somehow empty and thus prevents the database listing from displaying
    if DATABASE_METADATA_PATH.exists() and os.path.getsize(DATABASE_METADATA_PATH) > 0:
        with open(DATABASE_METADATA_PATH, "r") as f:
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

        if not DATABASE_METADATA_PATH.parent.exists():
            DATABASE_METADATA_PATH.parent.mkdir(parents=True)

        if DATABASE_METADATA_PATH.exists():
            with open(DATABASE_METADATA_PATH, "r") as f:
                database_metadata = json.load(f)
        else:
            database_metadata = {}
        database_metadata[converted_name] = dict(
            num_proteins=num_proteins, date=date.today().isoformat()
        )
        with open(DATABASE_METADATA_PATH, "w") as f:
            json.dump(database_metadata, f)

        return JsonResponse(
            {
                "success": True,
                "message": (
                    f"Database uploaded successfully. \n {message}"
                    if len(message) > 0
                    else "Database uploaded successfully"
                ),
            },
            status=200,
        )
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def database_delete(request):
    if request.method == "POST":
        data = json.loads(request.body)
        database_name = data.get("name")
        path = database_path(database_name)
        path.unlink()

        if DATABASE_METADATA_PATH.exists():
            with open(DATABASE_METADATA_PATH, "r") as f:
                database_metadata = json.load(f)

            if database_name in database_metadata:
                del database_metadata[database_name]
                with open(DATABASE_METADATA_PATH, "w") as f:
                    json.dump(database_metadata, f)

        return JsonResponse(
            {"success": True, "message": "Database deleted successfully"}, status=200
        )
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def database_path(name):
    return EXTERNAL_DATA_PATH / "uniprot" / f"{name}.tsv"
