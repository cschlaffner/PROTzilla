import re
from pathlib import Path

import numpy as np

from backend.protzilla.constants.paths import SETTINGS_PATH
from backend.protzilla.disk_operator import YamlOperator
from backend.protzilla.steps import Step
from backend.protzilla.step_manager import StepManager
from backend.protzilla.utilities.utilities import name_to_title


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


# TODO: Rename this
def get_step(step: Step) -> dict:
    return {
        "id": step.instance_identifier,
        "name": step.display_name,
        "section": step.section,
        "input_keys": step.external_input_keys,
        "output_keys": step.output_keys,
        "visual_data": step.visual_data,
        "operation": step.operation,
        "status": step.calculation_status,
    }


def get_displayed_steps(steps: StepManager) -> list[dict]:
    """
    For front-end. Returns the necessary short info for all steps. Returned steps are ordered
    using toposort

    :param steps: A StepManager to get the steps from
    :return: A list of dictionaries with the necessary info for each step
    """
    displayed_steps = []

    for step_id in steps.all_step_ids_toposorted:
        step = steps.all_steps[step_id]
        displayed_steps.append(get_step(step))

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
