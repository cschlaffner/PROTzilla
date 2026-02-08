from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict
import inspect
import logging
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


class Section(str, Enum):
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
    additional_inputs: list[str] = []
    output_keys: list[DataKeys] = []
    calculation_status: Literal["complete", "outdated", "incomplete", "failed"] = (
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

    def calculate(self, steps: StepManager) -> bool:
        """
        Core calculation method for all steps, receives the inputs from the front-end and calculates the output.

        :param steps: The StepManager object that contains all steps
        :return: bool: True if the calculation was successful, False otherwise
        """
        stepIndex = steps.all_steps.index(self)
        previousStep = steps.all_steps[stepIndex - 1]

        if stepIndex != 0 and previousStep.calculation_status == "outdated":
            if not previousStep.calculate(steps):
                return False

        self.get_form_values()
        self.messages.clear()

        try:
            self.insert_dataframes(steps)
            if self.calc_method:
                calc_output = self.calc_method(**self.calculation_input)
                self.handle_calc_outputs(calc_output)
                self.validate_outputs()
                self.artifact_versions["output"]["generated"] += 1

            self.calculation_status = "complete"
            if steps.failed_step_index == stepIndex:
                steps.failed_step_index = -1

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
            steps.failed_step_index = stepIndex

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
        keys: list[DataKeys] = []
        form_keys = [
            field.name
            for field in self.form.input_fields
            if isinstance(field, InputField)
        ]
        if self.calc_method:
            calc_params = inspect.signature(self.calc_method).parameters.values()
            keys += [
                param.name
                for param in calc_params
                if (
                    param.name.endswith("_df")
                    or param.annotation == pd.DataFrame
                    or not param.name in form_keys
                )
                and not param.name in self.additional_inputs
            ]
        if self.plot_method:
            plot_params = inspect.signature(self.plot_method).parameters.values()
            keys += [
                param.name
                for param in plot_params
                if not param.name.startswith("output_")
                and not param.name in form_keys
                and not param.name in self.additional_inputs
            ]
        return keys

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
    id_mapping: dict[str, Step]

    def __repr__(self):
        return f"IMP: {self.sections[Section.IMPORTING]} PRE: {self.sections[Section.DATA_PREPROCESSING]} ANA: {self.sections[Section.DATA_PREPROCESSING]} INT: {self.sections[Section.DATA_INTEGRATION]}"

    def __init__(
        self,
        steps: list[Step] | None = None,
        df_mode: str = "disk",
        disk_operator: DiskOperator | None = None,
    ):
        self.df_mode = df_mode
        self.disk_operator = disk_operator
        self.current_step_index = 0
        self.failed_step_index = -1
        self.sections: dict[Section, list[Step]] = {section: [] for section in Section}
        self.id_mapping = {}

        if steps is not None:
            for step in steps:
                self.add_step(step)

    @property
    def all_steps(self) -> list[Step]:
        """
        This is read-only, meaning the changes made to this list will not persist.
        :return: a list of all the steps in the current StepManager
        """
        return sum(self.sections.values(), [])

    @property
    def current_step_index_in_section(self) -> int:
        """
        Returns the index of the current step in the current section.
        :return: an integer for the index of the current step in the current section
        """

        return self.current_step_index - sum(
            len(self.sections[section])
            for section in self.sections
            if section != self.current_section
            and section not in [step.section for step in self.future_steps]
        )

    def get_instance_identifiers(
        self, step_type: type[Step], output_key: str | list[str] | None = None
    ) -> list[str]:
        if isinstance(output_key, str):
            output_key = [output_key]

        instance_identifiers = [
            step.instance_identifier
            for step in self.all_steps
            if isinstance(step, step_type)
            and (output_key is None or all(k in step.output for k in output_key))
        ]
        if not instance_identifiers:
            logging.warning(
                f"No instance identifiers found with step type {step_type} and output_key{'s' if len(output_key) > 1 else ''} {output_key}"
            )
        return instance_identifiers

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
            steps_to_search = self.all_steps
        else:
            steps_to_search = self.previous_calculated_steps

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

    def get_step_operation(self, instance_identifier: str) -> str:
        for step in reversed(self.all_steps):
            if step.instance_identifier == instance_identifier:
                return step.operation
        raise ValueError(f"No step associated with ID {instance_identifier}")

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

    def set_steps_outdated(self, offset: int = 0) -> None:
        count = 0
        for step in self.following_steps[offset:]:
            if step.calculation_status == "complete":
                step.calculation_status = "outdated"
                count += 1
        return count

    @property
    def previous_steps(self) -> list[Step]:
        return self.all_steps[: self.current_step_index]

    @property
    def previous_calculated_steps(self) -> list[Step]:
        return list(
            filter(
                lambda step: step.calculation_status == "complete", self.previous_steps
            )
        )

    @property
    def following_steps(self) -> list[Step]:
        return self.all_steps[self.current_step_index :]

    @property
    def current_step(self) -> Step:
        if self.current_step_index >= len(self.all_steps):
            return None
        return self.all_steps[self.current_step_index]

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
            self.current_step.instance_identifier,
        )

    @property
    def protein_df(self) -> pd.DataFrame:

        return self.get_step_output(output_key="protein_df")

    @property
    def metadata_df(self) -> pd.DataFrame | None:

        return self.get_step_output(output_key="metadata_df")

    @property
    def preprocessed_output(self) -> Output | None:
        if self.current_section == Section.IMPORTING:
            return None
        if self.current_section == Section.DATA_PREPROCESSING:
            return (
                self.current_step.output
                if self.current_step.calculation_status != "incomplete"
                else self.previous_steps[-1].output
            )
        return self.sections[Section.DATA_PREPROCESSING][-1].output

    @property
    def is_at_last_step(self) -> bool:
        return self.current_step_index == len(self.all_steps) - 1

    def add_step(self, step: Step) -> None:
        if step.section in self.sections:
            self.sections[step.section].append(step)
            self.id_mapping[step.instance_identifier] = step
        else:
            raise ValueError(f"Unknown section {step.section}")

    def remove_step(
        self,
        step: Step | None,
        step_index: int | None = None,
        section: Section | None = None,
    ) -> None:
        """
        Removes a step. Either the step must be passed or both section and step_index in the specific section.
        :param step: the step instance object
        :param step_index: the step index in the section
        :param section: the section as a string
        """
        if step is None and (step_index is None or section is None):
            raise ValueError("Either step or step_index and section must be provided")
        if step is None:
            if section is None or section not in self.sections:
                raise ValueError(f"Unknown section {section}")
            if step_index is None or step_index >= len(self.sections[section]):
                raise ValueError(
                    f"Step index {step_index} out of bounds for section {section}"
                )

            step = self.all_steps_in_section(section)[step_index]

        global_step_index = self.all_steps.index(step)
        self._clear_future_steps(global_step_index)
        if global_step_index < self.current_step_index:
            self.current_step_index -= 1
        self.sections[step.section].remove(step)
        del self.id_mapping[step.instance_identifier]

    def next_step(self) -> None:
        """
        Go to the next step in the workflow. Depending on the df_mode, the dataframes of the previous output are
        replaced with the respective paths on the disk where they are saved to save memory.

        :return: None
        """
        if not self.is_at_last_step:
            self.disk_operator.clear_upload_dir()  # TODO this could be a problem when using protzilla for multiple users
            if self.df_mode == "disk":
                # TODO maybe this doesnt really need to be written to disk anymore,
                # as it is preceeded by a calculation, after which everything is written to
                # disk anyway. Better would be if it would just replace the dfs with their respective paths
                self.current_step.output = Output(
                    self.disk_operator._write_output(self.current_step)
                )
            self.current_step_index += 1
        else:
            raise ValueError("Cannot go to the next step from the last step")

    def previous_step(self) -> None:
        """
        Go to the previous step in the workflow. If the previous step is in disk mode, the respective dataframes are
        loaded from disk and replaced in the output dictionary of the step.

        :return: None
        """
        if self.current_step_index > 0:
            self.current_step_index -= 1
        else:
            raise ValueError("Cannot go back from the first step")

    @property
    def future_steps(self) -> list[Step]:
        """
        Get all steps that are after the current step in the workflow.
        :return: A list of steps that are after the current step
        """
        if self.is_at_last_step:
            return []
        return self.all_steps[self.current_step_index + 1 :]

    def goto_step(self, step_index: int, section: Section) -> None:
        """
        Go to a specific step in the workflow.
        :param step_index: The index of the step in the respective section
        :param section: The section of the step to go to
        :return:
        """
        if section not in self.sections:
            raise ValueError(f"Unknown section {section}")
        if step_index < 0 or step_index >= len(self.sections[section]):
            raise ValueError(
                f"Step index {step_index} out of bounds for section {section}"
            )

        if self.df_mode == "disk":
            self.disk_operator._write_output(self.current_step)

        step = self.all_steps_in_section(section)[step_index]
        new_step_index = self.all_steps.index(step)
        self.current_step_index = new_step_index

    def connect_steps(self, connection: Connection):
        try:
            source = connection["source"]
            sourceHandle = connection["sourceHandle"]
            target = connection["target"]
            targetHandle = connection["targetHandle"]
            self.id_mapping[target].input_sources[targetHandle] = source
        except KeyError as e:
            raise ValueError(
                "The supplied connection parameter does not adhere to the specification. Expected keys are source, sourceHandle, target and targetHandle"
            ) from e

    def disconnect_steps(self, connection: Connection):
        try:
            source = connection["source"]
            target = connection["target"]
            targetHandle = connection["targetHandle"]
        except KeyError as e:
            raise ValueError(
                "The supplied connection parameter does not adhere to the specification. Expected keys are source, sourceHandle, target and targetHandle"
            ) from e

        step = self.id_mapping.get(target)
        if step is None:
            return
        existing_source = step.input_sources.get(targetHandle)
        if existing_source == source:
            del step.input_sources[targetHandle]

    def get_edges(self) -> list[Connection]:
        return [
            {
                "source": source,
                "sourceHandle": key,
                "target": step.instance_identifier,
                "targetHandle": key,
                "key": f"{source}->{step.instance_identifier}: {key}",
                "id": f"{source}->{step.instance_identifier}: {key}",
            }
            for step in self.all_steps
            for key, source in step.input_sources.items()
        ]

    def name_current_step_instance(self, new_instance_identifier: str) -> None:
        """
        Change the instance identifier of the current step
        :return: None
        :param new_instance_identifier: the new instance identifier
        """
        self.current_step.instance_identifier = new_instance_identifier

    def change_method(self, new_method: str) -> None:
        """
        Change the method of the current step,
        :param new_method: the new method, the name of the method class (accessible via __class__.__name__)
        :return: None
        :raises ValueError: if the section of the current step is unknown
        """
        from backend.protzilla.stepfactory import StepFactory

        new_step = StepFactory.create_step(new_method, self)

        try:
            current_index = self.all_steps_in_section(self.current_section).index(
                self.current_step
            )
            self.all_steps_in_section(self.current_section)[current_index] = new_step
            self._clear_future_steps()
        except ValueError:
            raise ValueError(f"Unknown section {self.current_section}")
        except Exception as e:
            logging.error(f"Error while changing method: {e}")

    def _clear_future_steps(self, index: int | None = None) -> None:
        if index == None:
            index = self.current_step_index
        if index == len(self.all_steps) - 1:
            return
        for step in self.all_steps[index + 1 :]:
            step.output = Output()
            step.messages = Messages()
            step.plots = Plots()
