from __future__ import annotations

from abc import ABC, abstractmethod
import inspect
import logging
import traceback
from enum import Enum, StrEnum
from pathlib import Path
from types import MethodType
from typing import Any, Literal, Callable

import pandas as pd
import yaml

from backend.main import settings
from backend.protzilla.constants.data_types import DataKey, StepID
from backend.protzilla.form import FormInputType, Form, InputField
from backend.protzilla.utilities.utilities import format_trace, name_to_title

# to avoid circular imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.protzilla.run import Run
    from backend.protzilla.step_manager import StepManager

# To avoid race conditions when dumping to disk
from threading import Lock


class Section(StrEnum):
    """
    Supported sections for steps
    """

    IMPORTING = "importing"
    DATA_PREPROCESSING = "data_preprocessing"
    DATA_ANALYSIS = "data_analysis"
    DATA_INTEGRATION = "data_integration"
    NOT_CATEGORIZED = "others"


class Step(ABC):
    """
    Abstract base class for concrete step implementations
    """

    section: Section = Section.NOT_CATEGORIZED
    form: Form
    display_name: str = None
    operation: str = None
    method_description: str = None
    visual_data: dict
    internal_inputs: set[str] = set[str]()
    output_keys: list[DataKey] = (
        []
    )  # keys collections like this should probably be sets
    calculation_status: Literal[
        "complete", "outdated", "incomplete", "failed", "ongoing"
    ] = "incomplete"

    def __init__(
        self,
        instance_identifier: StepID | None = None,
    ):
        self.inputs: dict[DataKey | str, pd.DataFrame | FormInputType] = {}
        self.output: Output = Output()
        self.visual_data = {"node_position": {"x": 0, "y": 0}}
        self.plots: Plots = Plots()
        self.visualizations: Visualizations = Visualizations()
        self.messages: Messages = Messages([])
        self.disk_write_mutex = Lock()

        self.form = self.create_form()

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
            "visualization": {
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
        self.inputs |= self.form_inputs.copy()

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

            if self.visualization_method:
                visualization_output = self.visualization_method(
                    **self.visualization_input
                )
                self.handle_visualization_outputs(visualization_output)
                self.artifact_versions["visualization"]["generated"] += 1

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
        Retrieves the dataframes that are connected in the graph editor and inserts them into self.inputs

        :param steps: The relevant StepManager instance
        """
        for source, target, data in steps.graph.in_edges(
            self.instance_identifier, data=True
        ):
            source_handle: DataKey = data["source_handle"]
            target_handle: DataKey = data["target_handle"]
            source_output = steps.get_step_output(
                output_key=source_handle, instance_identifier=source
            )
            if source_output is None:
                raise ValueError(
                    f"Step {source} has no output with key {source_handle}, but was set to be the input in {target} for key {target_handle}"
                )
            # TODO: temporary measure while support for model outputs isn't properly finished
            # the model instances don't implement a .copy() method
            self.inputs[target_handle] = (
                source_output.copy()
                if isinstance(source_output, (pd.DataFrame, list))
                else source_output
            )

    def input_source(
        self, steps: StepManager, input_key: DataKey
    ) -> tuple[StepID | None, DataKey | None]:
        """
        Retrieves the step ID and source handle that serve as the source for a specific input

        :param steps: the StepManager object
        :param input_key: the key for which to get the data
        :returns: the output of the step which is currently specified as the input for this key
        """

        edges = steps.incoming_edges_for_handle(
            None, None, self.instance_identifier, input_key
        )
        if not edges:
            return (None, None)
        if len(edges) > 1:
            raise ValueError(
                f"Multiple inputs for key {input_key} of step {self.instance_identifier} found: {[edge[0] for edge in edges]}"
            )
        source, _, _, data = edges[0]
        return source, DataKey(data["source_handle"])

    def get_input(self, steps: StepManager, input_key: DataKey):
        source_step, source_handle = self.input_source(steps, input_key)
        if source_step is None or source_handle is None:
            return None
        return steps.get_step_output(
            output_key=source_handle, instance_identifier=source_step
        )

    @property
    def external_input_keys(self) -> list[DataKey]:
        keys: set[DataKey] = set[DataKey]()
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
        self.output = Output()
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
            self.output.update(outputs)
            self.handle_messages(outputs)
        else:
            plots = outputs

        self.plots = Plots(plots)

    def handle_visualization_outputs(self, outputs: dict | list) -> None:
        """
        Handles the output of the visualization method and creates a Visualizations object from it.
        :param outputs: Must be a dict or a list of dicts
        """
        if not isinstance(outputs, dict) and not isinstance(outputs, list):
            raise TypeError(
                f"Visualization outputs must be a dict or list, got {type(outputs)}."
            )
        elif isinstance(outputs, dict):
            self.visualizations = Visualizations([outputs])
        elif isinstance(outputs, list):
            for entry in outputs:
                if not isinstance(entry, dict):
                    raise TypeError(f"All entries must be dicts, got {type(entry)}")
            self.visualizations = Visualizations(outputs)

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
    visualization_method = None

    def _get_input_parameters(
        self, function: Callable[..., Any], relevant_inputs: dict | None = None
    ) -> dict:
        if relevant_inputs is None:
            relevant_inputs = self.inputs
        input_parameters = inspect.signature(function).parameters
        required_keys = [
            key
            for key, param in input_parameters.items()
            if param.default == inspect.Parameter.empty
        ]
        for key in required_keys:
            if key not in relevant_inputs:
                raise ValueError(
                    f"Missing required input '{key}' for the '{function.__name__}' method"
                )

        return {
            # if there is a default value, we want to use it
            key: (
                relevant_inputs.get(key, param.default)
                if param.default != inspect.Parameter.empty
                else relevant_inputs.get(key)
            )
            for key, param in input_parameters.items()
            if key in relevant_inputs
        }

    @property
    def calculation_input(self) -> dict:
        return self._get_input_parameters(self.calc_method)

    @property
    def plot_input(self) -> dict:
        # if the plot method uses the output of the calculation method, it should be prefixed with "output_"
        prefixed_output = {"output_" + key: item.value for key, item in self.output}
        plot_input = self.inputs | prefixed_output
        return self._get_input_parameters(
            function=self.plot_method, relevant_inputs=plot_input
        )

    @property
    def visualization_input(self) -> dict:
        input_parameters = inspect.signature(self.visualization_method).parameters

        prefixed_output = {
            "output_" + key: value for key, value in self.output.output.items()
        }

        visualization_input = self.inputs | prefixed_output

        required_keys = [
            key
            for key, param in input_parameters.items()
            if param.default == inspect.Parameter.empty
        ]
        for key in required_keys:
            if key not in visualization_input:
                raise ValueError(
                    f"Missing required input '{key}' for the visualization method"
                )

        return {
            key: visualization_input[key]
            for key in input_parameters.keys()
            if key in visualization_input
        }

    def validate_outputs(self, soft_check: bool = False) -> bool:
        """
        Validates the outputs of the step. Uses the output_keys attribute to check if all required keys are present in
        the output dictionary.
        :param soft_check: Whether to raise errors or just return False if the output is invalid
        :return: True if the outputs are valid, False otherwise
        :raises ValueError: If a required key is missing in the outputs
        """
        # TODO: find a way of handling optional outputs
        # or remove this method

        # this is stupid - the steps should just raise the ValueError themselves.
        if list(self.output.output.keys()) == ["messages"]:
            raise ValueError(f"Output validation failed: Output does not contain data.")

        # for key in self.output_keys:
        #     if key not in self.output or self.output[key] is None:
        #         if not soft_check:
        #             raise ValueError(
        #                 f"Output validation failed: missing output {key} in outputs."
        #             )
        #         else:
        #             return False
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

    def modify_form(self, run: Run) -> None:
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
        # step should not show as outdated if it's never been calculated
        if self.calculation_status != "incomplete":
            self.calculation_status = "outdated"


class OutputType(StrEnum):
    DATAFRAME = "dataframe"
    LIST = "list"
    MESSAGES = "messages"
    FLOAT = "float"
    INT = "int"
    PNG_BASE64 = "png_base64"
    DOWNLOAD = "download"  # right now only JSONs are supported, value should be dict(filename, json content)
    # for every data type that is not yaml serializable
    JOBLIB_ARTIFACT = "joblib_artifact"


class OutputItem(yaml.YAMLObject):
    """
    Describes one output of a step.

    :ivar output_type: type of output, required for proper serialization
        and front-end display.
    :ivar value: data associated with the output
    """

    yaml_tag: str = "!OutputItem"

    def __init__(self, output_type: OutputType, value: Any) -> None:
        self.output_type: OutputType = output_type
        self.value: Any = value


class Output:
    def __init__(
        self,
        _output: dict[str, Any] | None = None,
    ):
        if _output is None:
            _output = {}

        self.output: dict[str, OutputItem] = {}

        self.update(_output)

    def __iter__(self):
        return iter(self.output.items())

    def __getitem__(self, key: str) -> Any:
        return self.output[key].value

    def __repr__(self):
        return f"Output: {self.output}"

    def __contains__(self, key: str):
        return key in self.output

    def get(self, key: str) -> Any | None:
        try:
            return self.output[key].value
        except KeyError:
            return None

    def update(self, source_dict: dict[str, Any]):
        for key, value in source_dict.items():
            if isinstance(value, OutputItem):
                self.output[key] = value

            elif key == "messages":
                if isinstance(value, list):
                    self.output[key] = OutputItem(
                        output_type=OutputType.MESSAGES, value=value
                    )
                elif isinstance(value, dict) and len(value) == 0:
                    self.output[key] = OutputItem(
                        output_type=OutputType.MESSAGES, value=[]
                    )
                elif isinstance(value, dict) and len(value) > 0:
                    self.output[key] = OutputItem(
                        output_type=OutputType.MESSAGES, value=[value]
                    )
                else:
                    raise ValueError("Messages should be lists or dicts.")

            # These checks are for backwards compatibility with existing
            # calculation methods.
            # We automatically convert the most common data types
            # to reasonable OutputItem representations

            elif isinstance(value, pd.DataFrame):
                self.output[key] = OutputItem(
                    output_type=OutputType.DATAFRAME, value=value
                )

            elif isinstance(value, list):
                self.output[key] = OutputItem(output_type=OutputType.LIST, value=value)

            elif isinstance(value, float):
                self.output[key] = OutputItem(output_type=OutputType.FLOAT, value=value)

            elif isinstance(value, int):
                self.output[key] = OutputItem(output_type=OutputType.INT, value=value)

            else:
                raise ValueError(
                    "Outputs must be passed as messages, dataframes, lists, scalars or OutputItems"
                )

    @property
    def is_empty(self) -> bool:
        return len(self.output) == 0 or all(
            item.value is None for item in self.output.values()
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


class Visualizations:
    def __init__(self, visualizations: list | None = None):
        if visualizations is None:
            visualizations: list = []
        self.visualizations = visualizations

    def __iter__(self):
        return iter(self.visualizations)

    def __repr__(self):
        return f"Visualizations: {len(self.visualizations)}"

    @property
    def empty(self) -> bool:
        return len(self.visualizations) == 0