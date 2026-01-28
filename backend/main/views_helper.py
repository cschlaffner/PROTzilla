import re
import shutil
from pathlib import Path

import numpy as np

from backend.protzilla.constants.paths import SETTINGS_PATH
from backend.protzilla.constants.protzilla_logging import logger
from backend.protzilla.disk_operator import YamlOperator
from backend.protzilla.steps import StepManager, Step
from backend.protzilla.utilities import name_to_title


def sanitize_name(name: str) -> [str, str]:
    """
    Converts a run name or database name to a valid filename by replacing spaces and special characters with underscores.
    """
    original_name = name
    name = re.sub(
        r"[^\w-]|[\s]", "_", name
    )  # replace special characters and spaces with underscores
    message = ""
    if original_name != name:
        message = f" \n Provided name '{original_name}' has been converted to '{name}' to ensure it is a valid filename."
    return name, message


def parameters_from_post(post):
    d = dict(post)
    if "csrfmiddlewaretoken" in d:
        del d["csrfmiddlewaretoken"]
    parameters = {}
    for k, v in d.items():
        if len(v) > 1:
            # only used for named_output parameters and multiselect fields
            parameters[k] = v
        else:
            parameters[k] = convert_str_if_possible(v[0])
    return parameters


def convert_str_if_possible(s):
    try:
        f = float(s)
        return int(f) if int(f) == f else f
    except ValueError:
        if s == "checked":
            # s is a checkbox
            return True
        if re.fullmatch(r"\d+(\.\d+)?(\|\d+(\.\d+)?)*", s):
            # s is a multi-numeric input e.g. 1-0.12-5
            numbers_str = re.findall(r"\d+(?:\.\d+)?", s)
            numbers = []
            for num in numbers_str:
                num = float(num)
                num = int(num) if int(num) == num else num
                numbers.append(num)
            return numbers
        return s


def get_step(step: Step) -> dict:
    return {
        "id": step.instance_identifier,
        "name": step.display_name,
        "method_name": name_to_title(step.operation),
        "status": step.calculation_status,
    }


def get_displayed_steps(
    steps: StepManager,
) -> list[
    dict
]:  # TODO i think this broke with the new naming scheme, should be redone (old protzilla - jannes hat nur kopiert)
    displayed_steps = []
    index_global = 0

    sections = ["importing", "data_preprocessing", "data_analysis", "data_integration"]

    for section in sections:
        workflow_steps = []

        for index_in_section, step in enumerate(steps.all_steps_in_section(section)):
            workflow_steps.append(get_step(step))

            index_global += 1
        displayed_steps.append(
            {
                "id": section,
                "name": name_to_title(section),
                "steps": workflow_steps,
                # "selected": steps.current_section == section,
                # "finished": index_global - 1 < steps.current_step_index,
                # "calculation_status": step.calculation_status,
                # TODO merge changes from old Repos
            }
        )
    return displayed_steps


# TODO display_message, display_messages, clear_messages


# TODO @Lennard, please check if suitable/needed in new repo as well
def get_filtered_data(run, index, key, reset=False):
    """
    Retrieves the corresponding output data and creates a copy for the filtered data in the data table

    :param run: the corresponding run
    :param index: the index of the current step
    :param key: the key of the datatable
    :param reset: the option to reload the real output data

    :return: a dict with the filtered data for the table
    """
    if index < len(run.steps.previous_steps):
        if (
            key not in run.steps.previous_steps[index].datatable_filtered_output
            or reset
        ):
            outputs = run.steps.previous_steps[index].output[key]
            filtered_data = outputs.copy()
            filtered_data = filtered_data.replace(np.nan, None)
            run.steps.previous_steps[index].datatable_filtered_output[
                key
            ] = filtered_data
        else:
            filtered_data = run.steps.previous_steps[index].datatable_filtered_output[
                key
            ]

    else:
        if key not in run.current_filtered_data or reset:
            outputs = run.current_outputs[key]
            filtered_data = outputs.copy()
            filtered_data = filtered_data.replace(np.nan, None)
            run.current_filtered_data[key] = filtered_data
        else:
            filtered_data = run.current_filtered_data[key]

    return filtered_data


def set_filtered_data(run, index, key, filtered_data):
    """
    Saves the filtered data from the table

    :param run: the corresponding run
    :param index: the index of the current step
    :param key: the key of the datatable
    :param filtered_data: the filtered data from the table
    """
    if index < len(run.steps.previous_steps):
        run.steps.previous_steps[index].datatable_filtered_output[key] = filtered_data
    else:
        run.current_filtered_data[key] = filtered_data


def get_display_name(dataframe: str):
    name = dataframe.replace("_df", "")
    return name


def load_settings_from_file(
    file_stem: str,
    default_file_stem: str | None = None,
    settings_path: Path = SETTINGS_PATH,
) -> dict:
    op = YamlOperator()
    path = settings_path / f"{file_stem}.yaml"

    if not path.exists():
        if default_file_stem is not None:
            default_path = SETTINGS_PATH / f"{default_file_stem}.yaml"
            plot_settings = op.read(default_path)
        else:
            raise FileNotFoundError(f"Settings file {path} does not exist.")
    else:
        plot_settings = op.read(path)
    return plot_settings


def load_yaml_from_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"File {path} does not exist.")
    with path.open("r") as f:
        return f.read()


def copy_file_to_directory(source_file: Path, dest_dir: Path) -> tuple[bool, str]:
    """
    Copy a single file to a destination directory.
    Creates the destination directory if it doesn't exist.

    :param source_file: Path to the source file
    :param dest_dir: Path to the destination directory
    :return: Tuple of (success: bool, message: str)
    """

    if not source_file.exists():
        msg = f"Source file does not exist: {source_file}"
        logger.error(msg)
        return False, msg

    if not source_file.is_file():
        msg = f"Source path is not a file: {source_file}"
        logger.error(msg)
        return False, msg

    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / source_file.name

        shutil.copy2(source_file, dest_file)

        msg = f"Successfully copied file {source_file} to {dest_dir}"
        logger.info(msg)
        return True, msg

    except OSError as e:
        msg = f"Failed to copy file: {str(e)}"
        logger.error(msg)
        return False, msg


def validate_uploaded_files(
    upload_dir: Path, file_mapping: dict[str, list[str]]
) -> tuple[bool, str]:
    """
    Validate that expected files exist in the upload directory with correct formats.

    :param upload_dir: Path to the upload directory
    :param file_mapping: Dictionary mapping file names to list of valid extensions
                        e.g., {"cif_file": [".cif"], "fasta_file": [".fasta", ".fa"]}
    :return: Tuple of (success: bool, message: str)
    """
    if not upload_dir.exists():
        msg = f"Upload directory does not exist: {upload_dir}"
        logger.error(msg)
        return False, msg

    missing_files = []
    invalid_files = []

    for file_name, valid_extensions in file_mapping.items():
        file_path = upload_dir / file_name
        if not file_path.exists():
            missing_files.append(file_name)
        else:
            # Check file extension
            if not any(file_name.lower().endswith(ext) for ext in valid_extensions):
                invalid_files.append(
                    f"{file_name} (expected: {', '.join(valid_extensions)})"
                )

    # Build error message
    error_messages = []
    if missing_files:
        error_messages.append(f"Missing files: {', '.join(missing_files)}")
    if invalid_files:
        error_messages.append(f"Invalid file format: {', '.join(invalid_files)}")

    if error_messages:
        msg = " | ".join(error_messages)
        logger.warning(msg)
        return False, msg

    msg = f"All {len(file_mapping)} files validated successfully"
    logger.info(msg)
    return True, msg

