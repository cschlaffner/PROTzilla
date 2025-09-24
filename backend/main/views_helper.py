import re

from backend.protzilla.constants.paths import SETTINGS_PATH
from backend.protzilla.disk_operator import YamlOperator
from backend.protzilla.steps import StepManager, Step
from backend.protzilla.utilities import name_to_title
from protzilla.constants.paths import DEFAULT_PLOT_SETTINGS_FILE_STEM


def sanitize_name(name: str) -> [str, str]:
    """
    Converts a run name or database name to a valid filename by replacing spaces and special characters with underscores.
    """
    original_name = name
    name = re.sub(r"[^\w-]|[\s]", "_", name)  # replace special characters and spaces with underscores
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


def get_step(
        step: Step
) -> dict:
    return (
        {
            "id": step.instance_identifier,
            "name": step.display_name,
            "method_name": name_to_title(step.operation),
            "status": step.calculation_status,
        }
    )


def get_displayed_steps(
        steps: StepManager,
) -> list[
    dict]:  # TODO i think this broke with the new naming scheme, should be redone (old protzilla - jannes hat nur kopiert)
    displayed_steps = []
    index_global = 0

    sections = [
        "importing",
        "data_preprocessing",
        "data_analysis",
        "data_integration"
    ]

    for section in sections:
        workflow_steps = []

        for index_in_section, step in enumerate(steps.all_steps_in_section(section)):
            workflow_steps.append(
                get_step(step)
            )

            index_global += 1
        displayed_steps.append(
            {
                "id": section,
                "name": name_to_title(section),
                "steps": workflow_steps,
                #"selected": steps.current_section == section,
                #"finished": index_global - 1 < steps.current_step_index,
                #"calculation_status": step.calculation_status,
                #TODO merge changes from old Repos
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
        if key not in run.steps.previous_steps[index].datatable_filtered_output or reset:
            outputs = run.steps.previous_steps[index].output[key]
            filtered_data = outputs.copy()
            filtered_data = filtered_data.replace(np.nan, None)
            run.steps.previous_steps[index].datatable_filtered_output[key] = filtered_data
        else:
            filtered_data = run.steps.previous_steps[index].datatable_filtered_output[key]

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


def load_plot_settings_from_file(file_stem) -> dict:
    op = YamlOperator()
    path = SETTINGS_PATH / f"{file_stem}.yaml"

    if file_stem == DEFAULT_PLOT_SETTINGS_FILE_STEM or not path.exists():
        default_path = SETTINGS_PATH / f"{DEFAULT_PLOT_SETTINGS_FILE_STEM}.yaml"
        plot_settings = op.read(default_path)
    else:
        plot_settings = op.read(path)
    return plot_settings
