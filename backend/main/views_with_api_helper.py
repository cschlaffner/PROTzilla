import re
from backend.protzilla.all_steps import get_all_methods
from backend.protzilla.steps import StepManager
from backend.protzilla.utilities import name_to_title

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

def get_all_possible_steps() -> list[dict]:
    """
        Returns a list of dictionaries of all step classes and their fields. Allows spreading of information about these steps.

        :return: List of step dictionaries via the steps to_dict function.
        :rtype: List[dict]
        """
    steps = get_all_methods()
    step_list = []
    for step in steps:
        step_list.append(step.to_dict(step))
    return step_list

def get_displayed_steps(
    steps: StepManager,
) -> list[dict]:  # TODO i think this broke with the new naming scheme, should be redone (old protzilla - jannes hat nur kopiert)
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
                {
                    "id": step.instance_identifier,
                    "name": step.display_name,
                    "method_name": name_to_title(step.operation),
                    "status": step.calculation_status,
                }
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