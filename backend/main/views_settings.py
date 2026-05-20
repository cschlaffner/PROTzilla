import json
import os
import shutil
import re
from datetime import date, datetime, timezone
from io import BytesIO


import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from PIL import Image
from django.contrib import messages
from django.http import JsonResponse, FileResponse

from backend.main import settings
from backend.main.views_helper import (
    sanitize_name,
    load_settings_from_file,
)
from backend.protzilla.utilities.utilities import copy_file_to_directory
from backend.protzilla.constants.paths import (
    EXTERNAL_DATA_PATH,
    SETTINGS_PATH,
    AF_MONOMER_METADATA_CSV_PATH,
    AF_MULTIMER_METADATA_CSV_PATH,
    ALPHAFOLD_MONOMER_PATH,
    ALPHAFOLD_MULTIMER_PATH,
)
from backend.protzilla.data_integration.database_query import (
    uniprot_columns,
    uniprot_databases,
)
from backend.protzilla.disk_operator import YamlOperator
from backend.protzilla.disk_operator import DefaultsOperator
from backend.main.views_helper import load_yaml_from_file
from backend.protzilla.constants.paths import (
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


# <--- helper functions for monomer and multimer structure prediction --->
def check_and_copy_files_to_directory(file_names: list, target_dir: str):
    if target_dir.exists():
        return (
            False,
            'Entry ID is not unique. Entry IDs are compared case insensitively, so "ABC" and "abc" are treated as the same ID.',
        )
    else:
        target_dir.mkdir(parents=True, exist_ok=True)

    for file_name in file_names:
        source_file = settings.FILE_UPLOAD_TEMP_DIR / file_name
        success, message = copy_file_to_directory(source_file, target_dir)
        if not success:
            shutil.rmtree(target_dir, ignore_errors=True)
            return False, message
    return True, "All files successfully uploaded"


def get_metadata_df(csv_file_path: str, expected_columns: list[str]) -> pd.DataFrame:
    if csv_file_path.exists():
        df = pd.read_csv(csv_file_path, usecols=lambda c: c in expected_columns)
    else:
        df = pd.DataFrame(columns=expected_columns)
    return df


def delete_structure(dir_path: str, csv_file_path: str, request):
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )

    data = json.loads(request.body)
    entry_id = (str(data.get("entry_id") or "")).strip()
    if not entry_id:
        return JsonResponse(
            {"success": False, "message": "Missing entry_id"}, status=400
        )

    # delete folder with files for the monomer structure
    target_dir = dir_path / entry_id.upper()
    metadata_csv = csv_file_path

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
            df = pd.read_csv(metadata_csv, dtype=str)
            df = df[
                (df["entry_id"].fillna("").str.strip().str).upper() != entry_id.upper()
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


def extend_metadata_csv(
    entry_id: str,
    metadata_csv: str,
    existing_metadata_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
) -> None:
    try:
        combined = pd.concat([existing_metadata_df, metadata_df], ignore_index=True)
        combined.to_csv(metadata_csv, index=False)
        return True, f'"{metadata_csv}" updated successfully.'

    except Exception:
        msg = f'Failed to write AlphaFold metadata CSV to "{metadata_csv}".'
        return False, msg


# <--- Monomer Structure Predictions --->


def get_monomer_structure(request):
    metadata_csv = AF_MONOMER_METADATA_CSV_PATH
    expected_columns = [
        "entry_id",
        "uniprot_accession",
        "model_created_date",
        "gene",
        "model_used",
    ]

    df = get_metadata_df(csv_file_path=metadata_csv, expected_columns=expected_columns)
    df = df.fillna("")

    df_infos = df.rename(
        columns={
            "entry_id": "entry_id",
            "uniprot_accession": "uniprot_id",
            "model_created_date": "date_modified",
            "gene": "gene",
            "model_used": "model_used",
        }
    ).to_dict(orient="records")

    return JsonResponse(df_infos, safe=False)


def upload_monomer_structure(request):
    if request.method == "POST":
        data = json.loads(request.body)
        uniprot_id = data.get("uniprot_id")
        entry_id = data.get("entry_id")
        model_used = data.get("model_used")
        gene = data.get("gene")
        cif_file = data.get("cif_file")
        confidence = data.get("confidence")
        pae = data.get("pae")
        fasta_file = data.get("fasta_file")

        if not entry_id:
            return JsonResponse(
                data={
                    "success": False,
                    "message": "The entry Id cannot be empty or None.",
                },
                status=500,
            )

        if not uniprot_id:
            return JsonResponse(
                data={
                    "success": False,
                    "message": "Uniprot Id cannot be empty or None.",
                },
                status=500,
            )

        ALPHAFOLD_MONOMER_PATH.mkdir(parents=True, exist_ok=True)
        metadata_csv = AF_MONOMER_METADATA_CSV_PATH

        expected_columns = [
            "entry_id",
            "uniprot_accession",
            "model_created_date",
            "gene",
            "model_used",
        ]

        existing_metadata_df = get_metadata_df(
            csv_file_path=metadata_csv, expected_columns=expected_columns
        )

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        new_row = {
            "entry_id": entry_id,
            "uniprot_accession": uniprot_id,
            "model_created_date": timestamp,
            "gene": "" if gene is None else gene,
            "model_used": "" if model_used is None else model_used,
        }

        metadata_df = pd.DataFrame([new_row])

        mask = (
            existing_metadata_df["entry_id"].astype(str).str.upper() == entry_id.upper()
        )
        if mask.any():
            msg = f'Entry ID "{entry_id}" not unique. Entry IDs are compared case insensitively, so "ABC" and "abc" are treated as the same ID.'
            return False, msg

        #  Copy files to source directory out of temp directory

        target_dir = ALPHAFOLD_MONOMER_PATH / entry_id.upper()
        file_names = [cif_file, confidence, pae, fasta_file]
        success, message = check_and_copy_files_to_directory(
            file_names=file_names, target_dir=target_dir
        )

        if not success:
            return JsonResponse(
                {"success": False, "message": message},
                status=500,
            )

        # add row to metadata csv
        success, message = extend_metadata_csv(
            entry_id=entry_id,
            metadata_csv=metadata_csv,
            existing_metadata_df=existing_metadata_df,
            metadata_df=metadata_df,
        )
        if not success:
            shutil.rmtree(target_dir, ignore_errors=True)
            return JsonResponse(
                {"success": False, "message": message},
                status=500,
            )

        return JsonResponse(
            {
                "success": True,
                "message": (
                    f"Predicted monomer structure uploaded successfully. \n {message}"
                    if len(message) > 0
                    else "Predicted monomer structure uploaded successfully."
                ),
            },
            status=200,
        )
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def delete_monomer_structure(request):
    return delete_structure(
        dir_path=ALPHAFOLD_MONOMER_PATH,
        csv_file_path=AF_MONOMER_METADATA_CSV_PATH,
        request=request,
    )


# <--- Multimer Structure Predictions --->


def get_multimer_structure(request):
    metadata_csv = AF_MULTIMER_METADATA_CSV_PATH
    expected_columns = [
        "entry_id",
        "uniprot_ids",
        "model_created_date",
        "model_used",
    ]
    df = get_metadata_df(csv_file_path=metadata_csv, expected_columns=expected_columns)
    df = df.fillna("")

    df_infos = df.rename(
        columns={
            "entry_id": "entry_id",
            "uniprot_ids": "uniprot_ids",
            "model_created_date": "date_modified",
            "model_used": "model_used",
        }
    ).to_dict(orient="records")

    return JsonResponse(df_infos, safe=False)


def upload_multimer_structure(request):
    if request.method == "POST":
        data = json.loads(request.body)
        entry_id = data.get("entry_id")
        uniprot_ids = data.get("uniprot_ids")
        model_used = data.get("model_used")
        fasta_file = data.get("fasta_file")
        cif_file = data.get("cif_file")
        confidence_file = data.get("confidence_file")
        full_data_file = data.get("full_data_file")
        job_request_file = data.get("job_request_file")

        ALPHAFOLD_MULTIMER_PATH.mkdir(parents=True, exist_ok=True)

        if not entry_id:
            return JsonResponse(
                data={
                    "success": False,
                    "message": "The entry Id cannot be empty or None.",
                },
                status=500,
            )

        if not uniprot_ids:
            return JsonResponse(
                data={
                    "success": False,
                    "message": "Uniprot Ids cannot be empty or None.",
                },
                status=500,
            )

        metadata_csv = AF_MULTIMER_METADATA_CSV_PATH
        expected_columns = [
            "entry_id",
            "uniprot_ids",
            "model_created_date",
            "model_used",
        ]

        existing_metadata_df = get_metadata_df(
            csv_file_path=metadata_csv, expected_columns=expected_columns
        )

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        uniprot_ids_as_list = re.split(r"\s*,\s*", uniprot_ids.strip())

        new_row = {
            "entry_id": entry_id,
            "uniprot_ids": uniprot_ids_as_list,
            "model_created_date": timestamp,
            "model_used": "" if model_used is None else model_used,
        }

        metadata_df = pd.DataFrame([new_row])

        mask = (
            existing_metadata_df["entry_id"].astype(str).str.upper() == entry_id.upper()
        )
        if mask.any():
            msg = f'Entry ID "{entry_id}" not unique. Entry IDs are compared case insensitively, so "ABC" and "abc" are treated as the same ID.'
            return False, msg

        #  Copy files to source directory out of temp directory

        target_dir = ALPHAFOLD_MULTIMER_PATH / entry_id.upper()
        file_names = [
            fasta_file,
            cif_file,
            confidence_file,
            full_data_file,
            job_request_file,
        ]
        success, message = check_and_copy_files_to_directory(
            file_names=file_names, target_dir=target_dir
        )
        if not success:
            return JsonResponse(
                data={"success": False, "message": message},
                status=500,
            )

        # add row to metadata csv
        success, message = extend_metadata_csv(
            entry_id=entry_id,
            metadata_csv=metadata_csv,
            existing_metadata_df=existing_metadata_df,
            metadata_df=metadata_df,
        )
        if not success:
            shutil.rmtree(target_dir, ignore_errors=True)
            return JsonResponse(
                {"success": False, "message": message},
                status=500,
            )

        return JsonResponse(
            {
                "success": True,
                "message": (
                    f"Predicted multimer structure uploaded successfully. \n {message}"
                    if len(message) > 0
                    else "Predicted multimer structure uploaded successfully."
                ),
            },
            status=200,
        )
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def delete_multimer_structure(request):
    return delete_structure(
        dir_path=ALPHAFOLD_MULTIMER_PATH,
        csv_file_path=AF_MULTIMER_METADATA_CSV_PATH,
        request=request,
    )


# <--- Crosslink defaults --->


def get_cl_defaults(request):
    default_operator = DefaultsOperator()
    defaults = default_operator.read_default(name="crosslinker_lengths")
    return JsonResponse(defaults, safe=False)


def update_cl_default(request):
    if request.method == "POST":
        data = json.loads(request.body)
        cl_name = data.get("cl_name")
        cl_length = data.get("cl_length") if data.get("cl_length") != "" else 0
        cl_upper_deviation = (
            data.get("cl_upper_deviation")
            if data.get("cl_upper_deviation") != ""
            else 0
        )
        cl_lower_deviation = (
            data.get("cl_lower_deviation")
            if data.get("cl_lower_deviation") != ""
            else 0
        )

        try:
            defaults_operator = DefaultsOperator()
            all_cl_defaults = defaults_operator.read_default(name="crosslinker_lengths")
            all_cl_defaults[cl_name] = {
                "cl_length": cl_length,
                "cl_upper_deviation": cl_upper_deviation,
                "cl_lower_deviation": cl_lower_deviation,
            }
            defaults_operator.write_default(
                name="crosslinker_lengths", value=all_cl_defaults
            )
            return JsonResponse(
                {
                    "success": True,
                    "message": (f"Default values updated successfully. "),
                },
                status=200,
            )
        except Exception:
            return JsonResponse(
                {"success": False, "message": "Default values could not be updated."},
                status=405,
            )
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )


def delete_cl_default(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            cl_name = data.get("cl_name")
            defaults_operator = DefaultsOperator()
            cl_defaults = defaults_operator.read_default(name="crosslinker_lengths")
            del cl_defaults[cl_name]
            defaults_operator.write_default(
                name="crosslinker_lengths", value=cl_defaults
            )
            return JsonResponse(
                {
                    "success": True,
                    "message": "Default values deleted successfully.",
                },
                status=200,
            )
        except Exception:
            return JsonResponse(
                {"success": False, "message": "Error occured while deleting."},
                status=405,
            )
    return JsonResponse(
        {"success": False, "message": "Invalid request method"}, status=405
    )


# <--- Crosslink colors --->


def get_cl_colors(request):
    operator = DefaultsOperator()
    colors = operator.read_default(name="crosslinker_colors")
    return JsonResponse(colors or {}, safe=False)


def update_cl_colors(request):
    if request.method == "POST":
        data = json.loads(request.body)

        try:
            operator = DefaultsOperator()
            operator.write_default(name="crosslinker_colors", value=data)

            return JsonResponse(
                {"success": True, "message": "Colours updated successfully."},
                status=200,
            )
        except Exception:
            return JsonResponse(
                {"success": False, "message": "Could not update colours."},
                status=405,
            )

    return JsonResponse({"success": False, "message": "Invalid method"}, status=405)


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
                dataframe = pd.read_csv(path, sep="\t")
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
