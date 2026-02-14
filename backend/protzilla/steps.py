from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict
import inspect
import logging
from multiprocessing.sharedctypes import Value
import traceback
from enum import Enum
from pathlib import Path
from types import MethodType
from typing import Any, Literal

import pandas as pd

from backend.main import settings
from backend.protzilla.constants.data_types import Connection, DataKeys
from backend.protzilla.form import FormInputType, Form, InputField
from backend.protzilla.utilities import format_trace, name_to_title

# to avoid circular imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.protzilla.run import Run
    from backend.protzilla.disk_operator import DiskOperator

# To avoid race conditions when dumping to disk
from threading import Lock

import networkx as nx

class Section(str, Enum):
    """
    Supported sections for steps
    """
    IMPORTING = "importing"
    DATA_PREPROCESSING = "data_preprocessing"
    DATA_ANALYSIS = "data_analysis"
    DATA_INTEGRATION = "data_integration"


class Step(ABC):
    """
    Abstract base class for concrete step implementations
    """

    section: Section
    display_name: str = None
    operation: str = None
    method_description: str = None
    input_sources: dict[DataKeys, str]  # maps to instance identifier
    visual_data: dict
    internal_inputs: set[str] = set[str]()
    output_keys: list[DataKeys] = (
        []
    )  # keys collections like this should probably be sets
    calculation_status: Literal["complete", "outdated", "incomplete", "failed", "ongoing"] = (
        "incomplete"
    )

    def __init__(
        self,
        instance_identifier: str | None = None,
    ):
        self.inputs: dict = {}
        self.output: Output = Output()
        self.input_sources = {}
        self.visual_data = {"node_position": {"x": 0, "y": 0}}
        self.filtered_datatable: dict = {}
        self.plots: Plots = Plots()
        self.messages: Messages = Messages([])
        self.disk_write_mutex = Lock()

        self.form: Form = self.create_form()
        self.form.modify_form = MethodType(self.modify_form, self.form)

        # Keeps track of calculations to avoid repetitive dumping
        self.artifact_versions = {
            "output": {
                "generated": 0,
                "dumped": 0,
            },
            "plots": {
                "generated": 0,
                "dumped": 0,
            },
        }

        if instance_identifier is None:
            logging.warning(
                f"No instance identifier provided for step {self.__class__.__name__}, defaulting to class name."
            )
            instance_identifier = self.__class__.__name__
        self.instance_identifier = instance_identifier

    def __repr__(self):
        return self.__class__.__name__

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__
            and self.instance_identifier == other.instance_identifier
            and self.output == other.output
        )

    def get_form_values(self) -> None:
        self.inputs = self.form_inputs.copy()

    @classmethod
    def to_dict(cls):
        """
        Returns a dictionary representation of the step object with some meta information about the step.
        :return: dict
        """
        return {
            "method_name": cls.__name__,
            "section": cls.section,
            "display_name": cls.display_name,
            "operation": name_to_title(cls.operation),
            "method_description": cls.method_description,
        }

    @abstractmethod
    def calc_method(self):
        raise NotImplementedError("This method must be implemented in a subclass.")

    def calculate(self, steps: StepManager) -> bool:
        """
        Core calculation method for all steps, receives the inputs from the front-end and calculates the output.

        :param steps: The StepManager object that contains all steps
        :return: bool: True if the calculation was successful, False otherwise
        """
        if not steps.calc_dependencies_met_for_step(self.instance_identifier):
            self.messages.append(
                dict(
                    level=logging.ERROR,
                    msg=f"At least one dependent step has not been calculated yet",
                )
            )
            return False

        self.get_form_values()
        self.messages.clear()
        self.calculation_status = "ongoing"

        try:
            self.insert_dataframes(steps)
            if self.calc_method:
                calc_output = self.calc_method(**self.calculation_input)
                self.handle_calc_outputs(calc_output)
                self.validate_outputs()
                self.artifact_versions["output"]["generated"] += 1

            if self.plot_method:
                plot_output = self.plot_method(**self.plot_input)
                self.handle_plot_outputs(plot_output)
                self.artifact_versions["plots"]["generated"] += 1

            self.calculation_status = "complete"

            # delete tempfiles
            for file in settings.FILE_UPLOAD_TEMP_DIR.iterdir():
                if file.is_file():
                    file.unlink()

        except NotImplementedError as e:
            self.messages.append(
                dict(
                    level=logging.ERROR,
                    msg=f"Method not implemented: {e}. Please contact the developer.",
                    trace=format_trace(traceback.format_exception(e)),
                )
            )
        except ValueError as e:
            self.messages.append(
                dict(
                    level=logging.ERROR,
                    msg=f"An error occured while validating inputs or outputs: {e} Please check your parameters.",
                    trace=format_trace(traceback.format_exception(e)),
                )
            )
        except TypeError as e:
            self.messages.append(
                dict(
                    level=logging.ERROR,
                    msg=f"Please check the implementation of this step's method class (especially the input_keys): {e}.",
                    trace=format_trace(traceback.format_exception(e)),
                )
            )
        except Exception as e:
            self.messages.append(
                dict(
                    level=logging.ERROR,
                    msg=(
                        f"An error occurred while calculating this step: {e.__class__.__name__} {e} "
                        f"Please check your parameters or report a potential programming issue."
                    ),
                    trace=format_trace(traceback.format_exception(e)),
                )
            )

        if self.calculation_status != "complete":
            self.calculation_status = "failed"

        return self.calculation_status == "complete"

    def insert_dataframes(self, steps: StepManager) -> None:
        """
        Adds the necessary entries to self.inputs. Needs to be overridden in concrete classes.

        :param steps: The relevant StepManager instance
        """
        for key, instance_identifier in self.input_sources.items():
            output = steps.get_step_output(
                output_key=key, instance_identifier=instance_identifier
            ).copy()
            if output is None:
                raise ValueError(
                    f"Step {instance_identifier} has no output with key {key}, but was set to be this key's input in {self.instance_identifier}"
                )
            self.inputs[key] = output.copy()

    @property
    def external_input_keys(self) -> list[DataKeys]:
        keys: set[DataKeys] = set[DataKeys]()
        form_keys = {
            field.name
            for field in self.form.input_fields
            if isinstance(field, InputField)
        }
        if self.calc_method:
            calc_params = inspect.signature(self.calc_method).parameters.values()
            keys |= {
                param.name
                for param in calc_params
                if (
                    param.name.endswith("_df")
                    or param.annotation == pd.DataFrame
                    or not param.name in form_keys
                )
                and not param.name in self.internal_inputs
            }
        if self.plot_method:
            plot_params = inspect.signature(self.plot_method).parameters.values()
            keys |= {
                param.name
                for param in plot_params
                if not param.name.startswith("output_")
                and not param.name in form_keys
                and not param.name in self.internal_inputs
            }
        return list(keys)

    def handle_calc_outputs(self, outputs: dict) -> None:
        """
        Handles the dictionary from the calculation method and creates an Output object from it.
        Responsible for checking that the output is a dictionary and not empty, and setting the output attribute of the instance.

        :param outputs: A dictionary received after the calculation
        :return: None
        """
        if not isinstance(outputs, dict):
            raise TypeError("Output of calculation is not a dictionary.")
        outputs = {key: value for key, value in outputs.items() if value is not None}
        if not outputs:
            raise ValueError("Output of calculation is empty.")
        self.output = Output(outputs)

        self.handle_messages(outputs)

    def handle_plot_outputs(self, outputs: dict | list) -> None:
        """
        Handles the dictionary from the plot method and creates a Plots object from it.
        Responsible for clearing and setting the plots attribute of the class.
        :param outputs: A dictionary or a list received after the plot method
        :return: None
        """

        if not isinstance(outputs, dict) and not isinstance(outputs, list):
            raise TypeError("Output of plot method is not a dictionary or a list.")

        if isinstance(outputs, dict):
            plots = outputs.pop("plots", [])
            self.output.output.update(outputs)
            self.handle_messages(outputs)
        else:
            plots = outputs

        self.plots = Plots(plots)

    def handle_messages(self, outputs: dict) -> None:
        """
        Handles the messages from the calculation method and creates a Messages object from it.
        Responsible for clearing and setting the messages attribute of the class.
        :param outputs: A dictionary received after the calculation
        :return: None
        """
        messages = outputs.get("messages", [])
        self.messages.extend(messages)

    calc_method = None
    plot_method = None  # if the plot method uses the output of the calculation method, it should be prefixed with "output_"

    @property
    def calculation_input(self) -> dict:
        input_parameters = inspect.signature(self.calc_method).parameters
        required_keys = [
            key
            for key, param in input_parameters.items()
            if param.default == inspect.Parameter.empty
        ]
        for key in required_keys:
            if key not in self.inputs:
                raise ValueError(
                    f"Missing required input '{key}' for the calculation method"
                )

        return {
            key: self.inputs[key]
            for key in input_parameters.keys()
            if key in self.inputs
        }

    @property
    def plot_input(self) -> dict:
        # if the plot method uses the output of the calculation method, it should be prefixed with "output_"
        prefixed_output = {
            "output_" + key: value for key, value in self.output.output.items()
        }
        plot_input = self.inputs | prefixed_output

        input_parameters = inspect.signature(self.plot_method).parameters
        required_keys = [
            key
            for key, param in input_parameters.items()
            if param.default == inspect.Parameter.empty
        ]
        for key in required_keys:
            if key not in plot_input:
                raise ValueError(f"Missing required input '{key}' for the plot method")

        return {
            key: plot_input[key] for key in input_parameters.keys() if key in plot_input
        }

    def validate_outputs(self, soft_check: bool = False) -> bool:
        """
        Validates the outputs of the step. Uses the output_keys attribute to check if all required keys are present in
        the output dictionary.
        :param soft_check: Whether to raise errors or just return False if the output is invalid
        :return: True if the outputs are valid, False otherwise
        :raises ValueError: If a required key is missing in the outputs
        """
        if list(self.output.output.keys()) == ["messages"]:
            message_string = ""
            for message in self.messages.messages:
                message_string += f"{message['msg']}\n"
            raise ValueError(
                f"Output validation failed: Output only contains messages: {message_string}."
            )
        for key in self.output_keys:
            if key not in self.output or self.output[key] is None:
                if not soft_check:
                    raise ValueError(
                        f"Output validation failed: missing output {key} in outputs."
                    )
                else:
                    return False
        return True

    def create_form(self) -> Form:
        """
        This method must be overridden in Step classes to define a form for the step.
        example:

        return Form(
            label="Filter Proteins by Samples Missing",
            fields=[
                NumberField(
                    name="percentage",
                    label="Percentage of minimum non-missing samples per protein",
                    value=0.5,
                    min=0,
                    max=1,
                    step=0.1,
                ),
                DropdownField(
                    name="graph_type",
                    value=BarAndPieChart.PIE_CHART,
                    label="Graph type",
                    options=BarAndPieChart,
                ),
            ],
        )
        """
        return Form("No form defined.", [])

    def modify_form(self, form: Form, run: Run) -> None:
        """
        This method can be overridden in Step classes to modify the form based on the current state of the run.
        examples:
        - disable a field based on the current state of the run
            form["field_name"].disabled = True
        - change the options of a dropdown based on the current state of the run
            form["field_name"].options = {"option1": "Option 1", "option2": "Option 2"}
        - change the value of a field based on the current state of the run
            form["field_name"].value = "new_value"

        run can be used to access the current state of the run, e.g. the previous steps, the current section, etc.
        """
        pass

    @property
    def finished(self) -> bool:
        """
        Return whether the step has valid outputs and is therefore considered finished.
        Plot steps without required outputs are considered finished if they have plots.
        :return: True if the step is finished, False otherwise
        """
        if len(self.output_keys) == 0:
            return not self.plots.empty
        return self.validate_outputs(soft_check=True)

    @property
    def form_inputs(self) -> dict[str, FormInputType]:
        return self.form.values


class Output:
    def __init__(self, output: dict = {}):
        if output is None:
            output = {}

        self.output = output

    def __iter__(self):
        return iter(self.output.items())

    def __getitem__(self, key):
        return self.output[key]

    def __repr__(self):
        return f"Output: {self.output}"

    def __contains__(self, key):
        return key in self.output

    @property
    def is_empty(self) -> bool:
        return len(self.output) == 0 or all(
            value is None for value in self.output.values()
        )


class Messages:
    def __init__(self, messages: list[dict] = None):
        if messages is None:
            messages = []
        self.messages = messages

    def __iter__(self):
        return iter(self.messages)

    def __getitem__(self, key):
        return self.messages[key]

    def __repr__(self):
        return f"Messages: {[message['msg'] for message in self.messages]}"

    def __len__(self):
        return len(self.messages)

    def append(self, param):
        self.messages.append(param)

    def extend(self, messages):
        self.messages.extend(messages)

    def clear(self):
        self.messages = []


class Plots:
    def __init__(self, plots: list | None = None):
        if plots is None:
            plots: list = []
        self.plots = plots

    def __iter__(self):
        return iter(self.plots)

    def __repr__(self):
        return f"Plots: {len(self.plots)}"

    @property
    def empty(self) -> bool:
        return len(self.plots) == 0


class StepManager:
    def __repr__(self):
        return f"IMP: {self.sections[Section.IMPORTING]} PRE: {self.sections[Section.DATA_PREPROCESSING]} ANA: {self.sections[Section.DATA_PREPROCESSING]} INT: {self.sections[Section.DATA_INTEGRATION]}"

    def __init__(
        self,
        steps: list[Step] | None = None,
        df_mode: str = "disk",
        disk_operator: DiskOperator | None = None,
    ):
        self.df_mode: str = df_mode
        self.disk_operator: DiskOperator | None = disk_operator

        # Saves all steps, accessible by their instance identifiers
        self.all_steps: dict[str, Step] = {}

        # Graph saving connections between steps.
        # All steps are represented by their instance_identifiers as nodes.
        # If an output of step X is connected to an input of step Y,
        # an edge with weight "n_connections" 1 is added. If multiple such links exist,
        # the edge's weight is incremented by 1 with every additional link
        self.graph: nx.DiGraph[str] = nx.DiGraph()

        # Instance identifier of the currently selected step
        self.current_selected_step_iid: str | None = None

        # Logical clock for instance identifier creation.
        # Incremented by StepFactory after every created step, may never be decremented
        self.iid_clock: int = 0

        if steps is not None:
            for step in steps:
                self.add_step(step)

    def next_iid_clock_value(self) -> int:
        """
        Logical clock implementation for step instance identifier generation
        :return: The next instance identifier clock value
        """
        self.iid_clock += 1
        return self.iid_clock

    @property
    def sections(self) -> dict[Section, list[Step]]:
        """
        For front-end compatibility. Please deprecate eventually

        :return: Dict mapping section titles to lists of step objects
        """
        return {section: [step for step in self.all_steps.values() if step.section == section] for section in Section}

    @property
    def all_step_iids_toposorted(self) -> list[str]:
        """
        :return: A list of all step instance identifiers in topological order according to the current
            connections in self.graph
        """
        return list(nx.topological_sort(self.graph))

    def preceding_steps(self, step_iid: str) -> list[Step]:
        """
        :param step_iid: Step of interest
        :return: List of all predecessors of the given step
        """
        ancestor_iids = list(nx.ancestors(self.graph, step_iid))
        return [self.all_steps[iid] for iid in ancestor_iids]

    def succeeding_steps(self, step_iid: str) -> list[Step]:
        """
        :param step_iid: Step of interest
        :return: List of all successors of the given step
        """
        descendant_iids = list(nx.descendants(self.graph, step_iid))
        return [self.all_steps[iid] for iid in descendant_iids]

    def calc_dependencies_met_for_step(self, step_iid: str) -> bool:
        """
        Checks calculation status of all preceding steps in the graph.
        :return: True iff all preceding steps have been calculated
        """
        return all([step.calculation_status == "complete" for step in self.preceding_steps(step_iid)])

    # TODO B179: make obsolete and delete
    def get_instance_identifiers(
        self, step_type: type[Step], output_key: str | list[str] | None = None
    ) -> list[str]:
        if isinstance(output_key, str):
            output_key = [output_key]

        instance_identifiers = [
            step.instance_identifier
            for step in self.all_steps.values()
            if isinstance(step, step_type)
            and (output_key is None or all(k in step.output for k in output_key))
        ]
        if not instance_identifiers:
            logging.warning(
                f"No instance identifiers found with step type {step_type} and output_key{'s' if len(output_key) > 1 else ''} {output_key}"
            )
        return instance_identifiers

    # TODO WTAF is this?
    # It only makes sense in the context in which it is used,
    # which is a stupid context that will be deprecated with B179.
    # Looking forward to it @Tarek
    @staticmethod
    def check_instance_identifier(step: Step, instance_identifier: str | None):
        return (
            step.instance_identifier == instance_identifier
            or instance_identifier is None
        )

    def get_step_output(
        self,
        step_type: Step | None = None,
        output_key: str = "",  # TODO remove step_type and default empty string
        instance_identifier: str | None = None,
        include_current_step: bool = False,
    ) -> pd.DataFrame | Any | None:
        """
        Get the specific output of the outputs of a specific step type. The step type can also a parent class of the
        step type, in which case the output of the most recent step of the specific type is returned.

        :param step_type: The type of the step as a class object
        :param output_key: The key of the desired output in the output dictionary of the step
        :param instance_identifier: The instance identifier of the step to get the output from
        :param include_current_step: Whether to include the current step in the search
        :return: The value of the output of the step or None
        """

        if step_type is not None:
            raise NotImplementedError("Passing the step type is deprecated")

        if include_current_step:
            steps_to_search = self.all_steps.values()
        else:
            steps_to_search = self.previous_calculated_steps

        # TODO: this is stupid. iterating over all steps should now only be necessary if for whatever reason the instance identifier is unknown
        # if an instance identifier is present, self.all_steps should be used
        for step in reversed(steps_to_search):
            if (
                StepManager.check_instance_identifier(step, instance_identifier)
                and output_key in step.output
            ):
                val = step.output[output_key]
                if val is None:
                    continue
                if isinstance(val, str) and Path(val).exists():
                    if Path(val).suffix == ".csv":
                        from backend.protzilla.disk_operator import DataFrameOperator

                        df_operator = DataFrameOperator()
                        df = df_operator.read(Path(val))
                        if df.empty:
                            logging.warning(
                                f"Could not read DataFrame from {val}, continuing"
                            )
                            continue
                        return df
                    else:
                        raise ValueError(f"Unsupported file format {Path(str).suffix}")
                return val
        return None

    def get_step_input(
        self,
        step_type: Step | None = None,
        input_key: str = "",  # TODO same as get_step_output
        instance_identifier: str | None = None,
        default: Any = None,
    ):
        """
        Get the specific input of the inputs of a specific step type. The step type can also a parent class of the
        step type, in which case the input of the most recent step of the specific type is returned.
        :param step_type: The type of the step as a class object
        :param input_key: The key of the desired input in the input dictionary of the step
        :param instance_identifier: The instance identifier of the step to get the input from
        :param default: The default value to return if the input is not found
        :return: The value of the input of the step or None
        """

        if step_type is not None:
            raise NotImplementedError("Passing the step type is deprecated")

        for step in reversed(self.previous_calculated_steps):
            if (
                StepManager.check_instance_identifier(step, instance_identifier)
                and input_key in step.inputs
            ):
                return step.inputs[input_key]
        return default

    def get_step_operation(self, step_iid: str) -> str:
        try:
            return self.all_steps[step_iid].operation
        except KeyError: # TODO: Should really not happen and should be caught in a different way
            raise ValueError(f"No step associated with ID {step_iid}")

    def all_steps_in_section(self, section: Section) -> list[Step]:
        """
        Get all steps in a specific section via the section name
        :param section: The section name
        :return: A list of steps in the section
        """
        if section in self.sections:
            return self.sections[section]
        else:
            raise ValueError(f"Unknown section {section}")

    def invalidate_succeeding_steps(self) -> int:
        if self.current_selected_step_iid is None:
            return 0
        steps_to_remove = self.succeeding_steps(self.current_selected_step_iid)
        steps_to_remove.append(self.current_step)
        for step in steps_to_remove:
            step.calculation_status = "outdated"
        return len(steps_to_remove)

    @property
    def previous_steps(self) -> list[Step]:
        return self.preceding_steps(self.current_selected_step_iid)

    @property
    def following_steps(self) -> list[Step]:
        return self.succeeding_steps(self.current_selected_step_iid)

    @property
    def previous_calculated_steps(self) -> list[Step]:
        return list(
            filter(
                lambda step: step.calculation_status == "complete", self.previous_steps
            )
        )

    @property
    def current_step(self) -> Step | None:
        return self.all_steps.get(self.current_selected_step_iid)

    @property
    def current_operation(self) -> str:
        return self.current_step.operation

    @property
    def current_section(self) -> Section:
        return self.current_step.section

    @property
    def current_location(self) -> tuple[str, str, str]:
        return (
            self.current_section,
            self.current_operation,
            self.current_selected_step_iid,
        )

    # TODO B179
    @property
    def protein_df(self) -> pd.DataFrame:
        return self.get_step_output(output_key="protein_df")

    # TODO B179
    @property
    def metadata_df(self) -> pd.DataFrame | None:
        return self.get_step_output(output_key="metadata_df")

    def step_is_terminal(self, step_iid: str) -> bool:
        return int(self.graph.out_degree(step_iid)) == 0
    
    def step_is_source(self, step_iid: str) -> bool:
        return int(self.graph.in_degree(step_iid)) == 0

    @property
    def fallback_step_iid(self) -> str:
        return list(self.all_steps.keys())[0]

    @property
    def is_at_terminal_step(self) -> bool:
        return self.step_is_terminal(self.current_selected_step_iid)

    @property
    def is_at_source_step(self) -> bool:
        return self.step_is_source(self.current_selected_step_iid)

    def add_step(self, step: Step) -> None:
        if not step.section in self.sections:
            raise ValueError(f"Unknown section {step.section}")

        self.all_steps[step.instance_identifier] = step

        if len(self.all_steps) == 1:
            self.current_selected_step_iid = step.instance_identifier
        
        self.graph.add_node(step.instance_identifier)

    def remove_step(self, step_iid: str | None) -> None:
        """
        Removes a step.
        :param step_iid: instance identifier of the step to delete
        """
        if step_iid is None:
            raise ValueError("")
        if step_iid not in self.all_steps.keys():
            raise ValueError(f"No step with iid {str(step_iid)} found")
        if len(self.all_steps) == 1:
            raise ValueError("At least one step must exist")

        self._clear_succeeding_steps(step_iid)
        
        # Navigate to a predecessor if step was selected
        mustNavigateToFallback = False
        if self.current_selected_step_iid == step_iid:
            try:
                self.previous_step()
            except ValueError: # No previous step
                mustNavigateToFallback = True
    
        # Remove all dangling references
        for step in self.all_steps.values():
            step.input_sources = {
                data_key: mapped_step_iid 
                for data_key, mapped_step_iid 
                in step.input_sources.items() 
                if mapped_step_iid != step_iid
            }

        self.graph.remove_node(step_iid)
        del self.all_steps[step_iid]

        if mustNavigateToFallback:
            self.goto_step(self.fallback_step_iid)
    
    @property
    def recommended_next_step_iid(self) -> str | None:
        """
        Mainly for front-end. Instance identifier of the next step to naviagte to when pressing the "Next" button.

        :return: The recommended next step identifier or None if we are at a terminal step
        """
        if self.is_at_terminal_step:
            return None
        return list(self.graph.successors(self.current_selected_step_iid))[0]

    def next_step(self) -> None:
        """
        Go to the next step in the workflow. Depending on the df_mode, the dataframes of the previous output are
        replaced with the respective paths on the disk where they are saved to save memory.

        :return: None
        """
        if not self.is_at_terminal_step:
            self.disk_operator.clear_upload_dir()  # TODO this could be a problem when using protzilla for multiple users
            if self.df_mode == "disk":
                # TODO maybe this doesnt really need to be written to disk anymore,
                # as it is preceeded by a calculation, after which everything is written to
                # disk anyway. Better would be if it would just replace the dfs with their respective paths
                self.current_step.output = Output(
                    self.disk_operator._write_output(self.current_step)
                )
            next_step_iid = self.recommended_next_step_iid
            self.current_selected_step_iid = next_step_iid
        else:
            raise ValueError("Cannot go to the next step from a terminal step")

    def previous_step(self) -> None:
        """
        Go to the previous step in the workflow. If the previous step is in disk mode, the respective dataframes are
        loaded from disk and replaced in the output dictionary of the step.

        :return: None
        """
        if not self.is_at_source_step:
            prev_step_iid = list(self.graph.predecessors(self.current_selected_step_iid))[0]
            self.current_selected_step_iid = prev_step_iid
        else:
            raise ValueError("Cannot go back from a step with no predecessors")

    def goto_step(self, step_iid: str) -> None:
        """
        Go to a specific step in the workflow.
        :param step_iid: The step to navigate to
        """
        if step_iid not in self.all_steps.keys():
            raise ValueError(f"Step {step_iid} not found")

        if self.df_mode == "disk":
            self.disk_operator._write_output(self.current_step)

        self.current_selected_step_iid = step_iid
            
    def connect_steps(self, connection: Connection) -> Step:
        try:
            source = connection["source"]
            sourceHandle = connection["sourceHandle"]
            target = connection["target"]
            targetHandle = connection["targetHandle"]
            # do we allow these keys to differ?
            # TODO: yes, we need a compatibility matrix. ~ Joris
            if sourceHandle != targetHandle:
                raise ValueError(
                    f"The output key {sourceHandle} does not match the input key {targetHandle}"
                )
            target_instance = self.all_steps[target]

            # Skip connection if already connected
            if target_instance.input_sources.get(targetHandle) == source:
                return target_instance

            # Delete old connection in graph if input source changes from existing connection
            old_source = target_instance.input_sources.get(targetHandle) 
            if old_source is not None:
                self.remove_graph_connection(old_source, target)

            target_instance.input_sources[targetHandle] = source
            if not self.graph.has_edge(source, target):
                self.graph.add_edge(source, target, n_connections=1)
            else:
                self.graph[source][target]["n_connections"] += 1

            return target_instance
        except KeyError as e:
            raise KeyError(
                "The supplied connection parameter does not adhere to the specification. Expected keys are source, sourceHandle, target and targetHandle" + str(e)
            ) from e

    def remove_graph_connection(self, source_iid: str, target_iid: str) -> None:
        """
        Removes a connection between two steps. If multiple connections between these
        steps existed (i.e. 2+ outputs of source mapping to inputs on target), 
        the connetion counter is decremented. If no more such connections exist,
        the edge is deleted from the graph.

        :param source_iid: instance identifier of source step
        :param target_iid: instance identifier of target step
        """
        self.graph[source_iid][target_iid]["n_connections"] -= 1

        # Remove edge if no more connections exist
        if self.graph[source_iid][target_iid]["n_connections"] == 0:
            self.graph.remove_edge(source_iid, target_iid)

    def disconnect_steps(self, connection: Connection) -> Step:
        try:
            source = connection["source"]
            target = connection["target"]
            targetHandle = connection["targetHandle"]
        except KeyError as e:
            raise KeyError(
                "The supplied connection parameter does not adhere to the specification. Expected keys are source, sourceHandle, target and targetHandle"
            ) from e

        target_instance = self.all_steps.get(target)
        if target_instance is None:
            raise ValueError(f"No step with id {target} found")
        existing_source = target_instance.input_sources.get(targetHandle)
        if existing_source == source:
            self.remove_graph_connection(source, target)
            del target_instance.input_sources[targetHandle]
        return target_instance

    def get_edges(self) -> list[Connection]:
        """
        For front-end
        :return: List of connections between steps as interpretable by front-end
        """
        return [
            {
                "source": source,
                "sourceHandle": key,
                "target": step.instance_identifier,
                "targetHandle": key,
                "key": f"{source}->{step.instance_identifier}: {key}",
                "id": f"{source}->{step.instance_identifier}: {key}",
            }
            for step in self.all_steps.values()
            for key, source in step.input_sources.items()
        ]

    def _clear_succeeding_steps(self, step_iid: str) -> None:
        """
        Voids outputs, messages and plots of all steps succeeding a given step
        :param step_iid: instance identifier of step of interest
        """
        for step in self.succeeding_steps(step_iid):
            step.output = Output()
            step.messages = Messages()
            step.plots = Plots()
