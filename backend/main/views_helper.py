import re
from pathlib import Path

import numpy as np
import pandas as pd

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


def _dataframe_as_datagrid_rows(_data: pd.DataFrame) -> list[dict] | None:
    """
    Converts dataframes from step outputs into a DataGrid-compatible row format for the frontend.
    Returns the output data of a step as a list of dicts in "records" orientaion, like this:
    [{'col1': 1, 'col2': 0.5}, {'col1': 2, 'col2': 0.75}]
    If the output could not be serialised, None is returned.
    An id column based on index will be added.

    :param _data: The data associated with the output
    """
    if isinstance(_data, pd.DataFrame):
        data = _data.copy()

        # Safer than just adding the new column. We assume __id_col is not
        # a column name anyone would use
        if "id" in data.columns:
            data.rename(columns={"id": "__id_col"}, inplace=True)

        data["id"] = data.index
        cleaned_data = data.replace(np.nan, None)
        return cleaned_data.to_dict(orient="records")
    else:
        return None


# ------------------------- helper for get_step_visualization: -------------------------


def create_visualization(
    cif_df: pd.DataFrame,
    structure_entry_id: str,
    crosslinking_df: pd.DataFrame | None = None,
) -> dict:
    """
    Create visualization data, by packaging a mmCIF string (converted from a CIF DataFrame) with its structure entry ID.
    Optionally include crosslinks.

    :param cif_df: DataFrame containing mmCIF atom_site information.
    :param structure_entry_id: Protein identifier to include in the mmCIF header.
    :param crosslinking_df: Optional DataFrame containing crosslink positions.
    :return: Dictionary containing:
             - "structureEntryId" (str)
             - "cifString" (str)
             - "crosslinks" (optional, list of dicts)
    """
    try:
        cif_string = convert_cif_df_to_mmcif_for_visualization(
            cif_df, structure_entry_id
        )
    except (ValueError, TypeError):
        cif_string = ""

    result = {"structureEntryId": structure_entry_id, "cifString": cif_string}

    if crosslinking_df is not None:
        result["crosslinks"] = extract_relevant_crosslink_information(crosslinking_df)

    return result


def convert_cif_df_to_mmcif_for_visualization(
    cif_df: pd.DataFrame, structure_entry_id: str
) -> str:
    """
    Convert a DataFrame containing mmCIF atom_site information back into a mmCIF string.

    :param cif_df: DataFrame with CIF columns
    :param structure_entry_id: Optional entry ID for the CIF block
    :return: A string representing the mmCIF file
    """
    if cif_df is None or cif_df.empty:
        raise ValueError("CIF-DataFrame is empty, cannot create mmCIF content.")

    lines = [
        f"data_{structure_entry_id}",
        "#",
        f"_entry.id {structure_entry_id}",
        "#",
        "loop_",
    ]

    for column in cif_df.columns:
        lines.append(column)

    for _, row in cif_df.iterrows():
        row_items = []
        for column in cif_df.columns:
            value = row[column]
            if value is None:
                value_str = "."
            else:
                value_str = str(value)
                if " " in value_str or any(char in value_str for char in "();,"):
                    value_str = f"'{value_str}'"
            row_items.append(value_str)
        lines.append(" ".join(row_items))

    cif_string = "\n".join(lines)
    return cif_string


def extract_relevant_crosslink_information(
    crosslinking_df: pd.DataFrame,
) -> list[dict[str, int]]:
    """
    For each crosslink extract its relevant information from a DataFrame.
    This includes information on where the crosslinker binds on both its ends,
    such as the chain and the absolute crosslinker position within the chain.
    As well as a boolean for its validity and wether it is an intra or inter crosslink.

    :param crosslinking_df: DataFrame with columns
        'crosslinker_position1',
        'crosslinker_position2',
        'Chain_id1',
        'Chain_id2',
        'reactive_atom1'
        'reactive_atom2'
        'valid_crosslink',
        'Is_intra_crosslink',
    :return: List of dicts with keys
        'crosslinkerPosition1',
        'crosslinkerPosition2',
        'chainId1',
        'chainId2',
        'reactiveAtom1'
        'reactiveAtom2'
        'isValid',
        'isIntraCrosslink',
    """
    crosslinks = []
    for _, row in crosslinking_df.iterrows():
        position1 = row.get("crosslinker_position1")
        position2 = row.get("crosslinker_position2")
        chain_id1 = row.get("Chain_id1")
        chain_id2 = row.get("Chain_id2")
        reactive_atom1 = row.get("reactive_atom1")
        reactive_atom2 = row.get("reactive_atom2")
        is_valid = row.get("valid_crosslink")
        is_intra_crosslink = row.get("Is_intra_crosslink")
        if pd.notnull(position1) and pd.notnull(position2) and pd.notnull(is_valid):
            crosslinks.append(
                {
                    "crosslinkerPosition1": int(position1),
                    "crosslinkerPosition2": int(position2),
                    "chainId1": str(chain_id1),
                    "chainId2": str(chain_id2),
                    "reactiveAtom1": str(reactive_atom1),
                    "reactiveAtom2": str(reactive_atom2),
                    "isValid": bool(is_valid),
                    "isIntraCrosslink": bool(is_intra_crosslink),
                }
            )
    return crosslinks
