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

def get_all_possible_step_names() -> list[str]:
    """
    Returns a list of names of step classes. Not to be confused with class display names.

    :return: List of names.
    :rtype: String
    """
    return [step.__name__ for step in get_all_methods()]

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
            workflow_steps.append(#maybe useless stuff wei z.b. index kram, weil besser wenn frontend kalkuliert? andererseits ist das auch teilweise input for step_remove
                {
                    "id": step.instance_identifier,
                    "name": step.display_name,
                    # "index": index_in_section,
                    # "index_global": index_global,
                    # "section": step.section,
                    "method_name": name_to_title(step.operation),
                    # "selected": step == steps.current_step,
                    "finished": index_global < steps.current_step_index,
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