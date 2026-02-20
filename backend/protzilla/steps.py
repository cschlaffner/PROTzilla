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

from matplotlib.pyplot import locator_params
import pandas as pd

from backend.main import settings
from backend.protzilla.constants.data_types import DataKeys, OutputLocator, StepID
from backend.protzilla.form import FormInputType, Form, InputField
from backend.protzilla.utilities import format_trace, name_to_title

# to avoid circular imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.protzilla.run import Run
    from backend.protzilla.step_manager import StepManager

# To avoid race conditions when dumping to disk
from threading import Lock

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
    input_sources: dict[DataKeys, OutputLocator]
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
        instance_identifier: StepID | None = None,
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
            instance_identifier = StepID(self.__class__.__name__)
        self.instance_identifier: StepID = instance_identifier

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
        for key, locator in self.input_sources.items():
            output = steps.get_step_output(
                output_key=locator["key"], instance_identifier=locator["step_id"]
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

    def clear_generated_artifacts(self) -> None:
        """
        Voids all artifacts the step has generated
        """
        self.output = Output()
        self.messages = Messages()
        self.plots = Plots()

    def invalidate(self) -> None:
        self.calculation_status = "outdated"


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
