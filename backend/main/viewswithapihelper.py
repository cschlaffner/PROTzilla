import re
from backend.protzilla.all_steps import get_all_methods
from backend.protzilla.steps import StepManager
from backend.protzilla.utilities.miscellaneous_utils import name_to_title

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

def get_all_possible_step_names() -> list[str]:
    """
    Returns a list of names of step classes. Not to be confused with class display names.

    :return: List of names.
    :rtype: String
    """
    step_classes = get_all_methods()
    step_names = []
    for step in step_classes:
        step_names.append(
            step.__name__
        )
    return step_names

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
        "data_analysis",
        "data_preprocessing",
        "data_integration",
        "importing"
    ]

    for section in sections:
        workflow_steps = []

        for index_in_section, step in enumerate(steps.all_steps_in_section(section)):
            workflow_steps.append(#maybe useless stuff wei z.b. index kram, weil besser wenn frontend kalkuliert? andererseits ist das auch teilweise input for step_remove
                {
                    "id": step.operation,
                    "name": name_to_title(step.operation),
                    "index": index_in_section,
                    "index_global": index_global,
                    "section": step.section,
                    "method_name": step.display_name,
                    "selected": step == steps.current_step,
                    "finished": index_global < steps.current_step_index,
                    "calculation_icon_path": "img/" + step.calculation_status + "_icon.svg"
                }
            )

            index_global += 1
        displayed_steps.append(
            {
                "id": section,
                "name": name_to_title(section),
                "steps": workflow_steps,
                "selected": steps.current_section == section,
                "finished": index_global - 1 < steps.current_step_index,
                "calculation_status": step.calculation_status,
            }
        )
    return displayed_steps