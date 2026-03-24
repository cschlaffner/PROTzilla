from __future__ import annotations

import base64
import datetime
import os
import shutil
import traceback
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yaml
import joblib
from plotly.io import read_json, write_json

from backend.protzilla.constants.data_types import DataKey
import backend.protzilla.utilities.utilities as utilities
from backend.protzilla.constants import paths
from backend.protzilla.constants.date_format import metadata_date_format
from backend.protzilla.constants.protzilla_logging import logger
from backend.protzilla.steps import (
    Messages,
    Output,
    OutputItem,
    OutputType,
    Plots,
    Step,
)
from backend.protzilla.step_manager import StepManager

try:
    from django.conf import settings

    DEBUG_MODE = settings.DEBUG if settings.configured else False
except ImportError:
    DEBUG_MODE = False


class ErrorHandler:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            if issubclass(exc_type, FileNotFoundError):
                logger.error(f"File not found: {exc_val}")
            elif issubclass(exc_type, PermissionError):
                logger.error(f"Permission denied: {exc_val}")
            if DEBUG_MODE:
                traceback.print_exception(exc_type, exc_val, exc_tb)
            return False
        return True


##
## Custom PyYAML representers/constructors
##


def output_type_representer(dumper, data):
    return dumper.represent_scalar("!OutputType", str(data.value))


def output_type_constructor(loader, node):
    value = loader.construct_scalar(node)
    return OutputType(value)


yaml.add_representer(OutputType, output_type_representer)
yaml.add_constructor("!OutputType", output_type_constructor)


class YamlOperator:
    @staticmethod
    def read(file_path: Path):
        with ErrorHandler():
            with open(file_path, "r") as file:
                logger.info(f"Reading yaml from {file_path}")
                return yaml.full_load(file)

    @staticmethod
    def write(file_path: Path, data: dict):
        with ErrorHandler():
            if not file_path.exists():
                if not file_path.parent.exists():
                    logger.info(
                        f"Parent directory {file_path.parent} did not exist and was created"
                    )
                    file_path.parent.mkdir(parents=True)
            with open(file_path, "w") as file:
                yaml.dump(data, file)


class DataFrameOperator:
    @staticmethod
    def read(file_path: Path):
        with ErrorHandler():
            logger.info(f"Reading dataframe from {file_path}")
            return pd.read_csv(file_path)

    @staticmethod
    def write(file_path: Path, dataframe: pd.DataFrame):
        with ErrorHandler():
            logger.info(f"Writing dataframe to {file_path}")
            dataframe.to_csv(file_path, index=False)


# for all non serializable data types
class ArtifactOperator:
    @staticmethod
    def read(file_path: Path):
        with ErrorHandler():
            logger.info(f"Reading artifact from {file_path}")
            return joblib.load(file_path)

    @staticmethod
    def write(file_path: Path, artifact):
        with ErrorHandler():
            logger.info(f"Writing artifact to {file_path}")
            file_path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(artifact, file_path, compress=("gzip", 3))


class Base64Operator:
    """
    Handles dumping and loading of files encoded in base64, e.g. PNG images.
    Files are dumped in binary format and loaded as base64 strings for
    easier front-end handling
    """

    @staticmethod
    def read(file_path: Path) -> bytes:
        with ErrorHandler():
            logger.info(f"Reading {file_path} into base64")
            with open(file_path, "rb") as file:
                file_content = file.read()
                encoded = base64.b64encode(file_content)
                return encoded

    @staticmethod
    def write(file_path: Path, base64_string: bytes):
        with ErrorHandler():
            logger.info(f"Writing base64 to {file_path}")
            file_path.parent.mkdir(parents=True, exist_ok=True)
            data = base64.b64decode(base64_string)
            with open(file_path, "wb") as file:
                file.write(data)


RUN_FILE = "run.yaml"


@dataclass
class KEYS:
    # We add this here to avoid typos and signal to the developer that accessing the keys should be done through this class only
    STEPS: str = "steps"
    STEP_OUTPUTS: str = "output"
    STEP_FORM_INPUTS: str = "form_inputs"
    STEP_INPUTS: str = "inputs"
    STEP_MESSAGES: str = "messages"
    STEP_PLOTS: str = "plots"
    STEP_INSTANCE_IDENTIFIER: str = "instance_identifier"
    STEP_TYPE: str = "type"
    STEP_CALCULATION_STATUS: str = "calculation_status"
    DF_MODE: str = "df_mode"
    VISUAL_DATA: str = "visual_data"
    CURRENT_STEP_ID: str = "current_step_id"
    GRAPH_EDGES: str = "graph_edges"
    ID_CLOCK: str = "id_clock"


class DiskOperator:
    def __init__(self, run_name: str, workflow_name: str):
        self.run_name = run_name
        self.workflow_name = workflow_name
        self.yaml_operator = YamlOperator()
        self.dataframe_operator = DataFrameOperator()
        self.artifact_operator = ArtifactOperator()
        self.base64_operator = Base64Operator()

    def read_run(self, file: Path | None = None) -> StepManager:
        with ErrorHandler():
            run = self.yaml_operator.read(file or self.run_file)
            step_manager = StepManager(disk_operator=self)
            step_manager.df_mode = run.get(KEYS.DF_MODE, "disk")
            for step_data in run[KEYS.STEPS]:
                try:
                    step = self._read_step(step_data, step_manager)
                except Exception as e:
                    logger.error(f"Error reading step: {e}")
                    continue
                step_manager.add_step(step)

            edges = run.get(KEYS.GRAPH_EDGES)
            if edges is not None:
                step_manager.graph.add_edges_from(run[KEYS.GRAPH_EDGES])

            id_clock = run.get(KEYS.ID_CLOCK)
            if id_clock is not None:
                step_manager._id_clock = id_clock

            current_step_id = run.get(KEYS.CURRENT_STEP_ID)
            step_manager._current_selected_step_id = current_step_id

            return step_manager

    def write_run(self, step_manager: StepManager) -> None:
        with ErrorHandler():
            if not self.run_dir.exists():
                self.run_dir.mkdir(parents=True, exist_ok=True)
            if not self.dataframe_dir.exists():
                self.dataframe_dir.mkdir(parents=True, exist_ok=True)
            self.clean_dataframes_dir(step_manager)
            run = {}
            run[KEYS.CURRENT_STEP_ID] = step_manager._current_selected_step_id
            run[KEYS.DF_MODE] = step_manager.df_mode
            run[KEYS.STEPS] = []
            run[KEYS.GRAPH_EDGES] = list(step_manager.graph.edges(data=True))
            run[KEYS.ID_CLOCK] = step_manager._id_clock
            for step in step_manager.all_step_instances:
                run[KEYS.STEPS].append(self._write_step(step))
            self.yaml_operator.write(self.run_file, run)

    def read_metadata(self) -> dict:
        with ErrorHandler():
            if not self.metadata_path.exists():
                self._create_metadata()
            metadata = self.yaml_operator.read(self.metadata_path)
            return metadata

    def write_metadata(self, metadata: dict = None) -> None:
        with ErrorHandler():
            if not self.metadata_path.exists():
                self._create_metadata()
            existing_metadata = self.read_metadata()
            if existing_metadata:
                metadata = {**existing_metadata, **metadata}
            else:
                metadata = metadata or {}

            self.yaml_operator.write(self.metadata_path, metadata)

    def _create_metadata(self) -> None:
        with ErrorHandler():
            if not self.run_dir.exists():
                self.run_dir.mkdir(parents=True, exist_ok=True)
            self.metadata_path.touch()
            logger.info(
                f"Metadata file {self.metadata_path} did not exist and was created"
            )
            date = datetime.datetime.now().strftime(metadata_date_format)
            metadata = {"creation_date": date, "modification_date": date}
            self.yaml_operator.write(self.metadata_path, metadata)

    def update_modification_date(self):
        with ErrorHandler():
            metadata = self.read_metadata()
            metadata["modification_date"] = datetime.datetime.now().strftime(
                metadata_date_format
            )
            self.write_metadata(metadata)

    def update_run_name(self, new_run_name: str) -> None:
        with ErrorHandler():
            new_run_dir = paths.RUNS_PATH / new_run_name
            if new_run_dir.exists():
                logger.warning(
                    f"Run directory {new_run_dir} for run {self.run_name} already exists."
                )
                return
            os.rename(self.run_dir, new_run_dir)
            self.run_name = new_run_name

    def read_workflow(self) -> StepManager:
        return self.read_run(self.workflow_file)

    def save_workflow(self, step_manager: StepManager, workflow_name: str) -> None:
        self.workflow_name = workflow_name
        workflow = {}
        workflow[KEYS.STEPS] = []
        workflow[KEYS.DF_MODE] = step_manager.df_mode
        workflow[KEYS.GRAPH_EDGES] = list(step_manager.graph.edges(data=True))
        workflow[KEYS.ID_CLOCK] = step_manager._id_clock
        workflow[KEYS.CURRENT_STEP_ID] = step_manager._current_selected_step_id
        with ErrorHandler():
            for step in step_manager.all_step_instances:
                step_data = self._write_step(
                    step, workflow_mode=True
                ).copy()  # unsure if copying is needed
                workflow[KEYS.STEPS].append(step_data)
            self.yaml_operator.write(self.workflow_file, workflow)

    def check_file_validity(self, file: Path, steps: StepManager) -> bool:
        """
        Check if the file is still valid, i.e. if it is still needed or if it can be deleted.
        :param file: The file to check
        :param steps: the current StepManager object
        :return: whether the file is valid
        """
        # if we are writing the run, chances are the outputs of the current step
        # have recently been (re)calculcated, therefore invalidating the existing file

        return any(
            step.instance_identifier in file.name
            and step.calculation_status != "incomplete"
            for step in steps.all_step_instances
        )

    def clean_dataframes_dir(self, steps: StepManager) -> None:
        with ErrorHandler():
            for file in self.dataframe_dir.iterdir():
                if not self.check_file_validity(file, steps):
                    logger.warning(f"Deleting dataframe {file}")
                    file.unlink()

    def clean_artifact_dir(self, steps: StepManager) -> None:
        with ErrorHandler():
            if not self.artifact_dir.exists():
                return
            for file in self.artifact_dir.iterdir():
                if file.is_dir():
                    continue
                if not self.check_file_validity(file, steps):
                    logger.warning(f"Deleting artifact {file}")
                    file.unlink()

    def clear_upload_dir(self) -> None:
        # TODO in general our way of handling file uploads is kind of non-straightforward, maybe we should switch
        # to directly using the FileUpload provided by Django instead of the work-around with the path of the upload as a str
        if not paths.UPLOAD_PATH.exists():
            return
        with ErrorHandler():
            upload_dir = paths.UPLOAD_PATH
            for element in upload_dir.iterdir():
                # using rmtree is more powerful than Path.unlink, as it can also delete non-empty directories
                shutil.rmtree(element)

    def _read_step(self, step_data: dict, steps: StepManager) -> Step:
        from backend.protzilla.stepfactory import StepFactory

        with ErrorHandler():
            step = StepFactory.create_step(
                step_type=step_data.get(KEYS.STEP_TYPE),
                steps=steps,
                instance_identifier=step_data.get(KEYS.STEP_INSTANCE_IDENTIFIER),
            )
            step.messages = Messages(step_data.get(KEYS.STEP_MESSAGES, []))
            step.output = self._read_outputs(step_data.get(KEYS.STEP_OUTPUTS, {}))
            step.visual_data = step_data.get(
                KEYS.VISUAL_DATA, {"node_position": {"x": 0, "y": 0}}
            )
            step.plots = self._read_plots(step_data.get(KEYS.STEP_PLOTS, []))
            step.form.update_values(step_data.get(KEYS.STEP_FORM_INPUTS, {}))
            step.calculation_status = step_data.get(
                KEYS.STEP_CALCULATION_STATUS, "incomplete"
            )
            return step

    def _dump_is_outdated(self, step: Step, key: str) -> bool:
        return (
            step.artifact_versions[key]["generated"]
            > step.artifact_versions[key]["dumped"]
        )

    def _update_dump_state(self, step: Step, key: str) -> None:
        step.artifact_versions[key]["dumped"] = step.artifact_versions[key]["generated"]

    def _write_step(self, step: Step, workflow_mode: bool = False) -> dict:
        """
        Serializes a step to a dictionary for the YamlOperator to dump

        :param step: the step to serialize
        :param workflow_mode: whether or not to save all data or only metadata
            (e.g. when dumping workflows)

        :return: Serializable dictionary
        """
        with ErrorHandler():
            step_data = {}
            step_data[KEYS.STEP_TYPE] = step.__class__.__name__
            step_data[KEYS.STEP_INSTANCE_IDENTIFIER] = step.instance_identifier
            step_data[KEYS.STEP_FORM_INPUTS] = step.form_inputs
            step_data[KEYS.VISUAL_DATA] = step.visual_data
            if not workflow_mode:
                step_data[KEYS.STEP_PLOTS] = self._write_plots(step)
                step_data[KEYS.STEP_OUTPUTS] = self._write_output(step)
                step_data[KEYS.STEP_MESSAGES] = step.messages.messages
                step_data[KEYS.STEP_CALCULATION_STATUS] = step.calculation_status
            return step_data

    def _read_outputs(self, _output: dict[str, OutputItem]) -> Output:
        step_output = {}
        with ErrorHandler():
            for key, item in _output.items():
                match item.output_type:
                    # Load Dataframes from disk
                    case OutputType.DATAFRAME:
                        path = Path(str(item.value))
                        step_output[key] = OutputItem(
                            output_type=OutputType.DATAFRAME,
                            value=self.dataframe_operator.read(self.run_dir / path),
                        )
                    case OutputType.JOBLIB_ARTIFACT:
                        path = Path(str(item.value))
                        step_output[key] = OutputItem(
                            output_type=OutputType.JOBLIB_ARTIFACT,
                            value=self.artifact_operator.read(self.run_dir / path),
                        )
                    case OutputType.PNG_BASE64:
                        path = Path(str(item.value))
                        step_output[key] = OutputItem(
                            output_type=OutputType.PNG_BASE64,
                            value=self.base64_operator.read(self.run_dir / path),
                        )
                    case _:
                        step_output[key] = item

            return Output(step_output)

    def _write_output(self, step: Step) -> dict:
        """
        Writes the outputs of a step to disk and returns a dictionary describing the outputs
        to then be serialized.

        :param step: the step whose outputs to dump
        :return: serialized output
        """
        with ErrorHandler(), step.disk_write_mutex:
            output_data: dict[str, OutputItem] = {}
            for key, item in step.output:
                match item.output_type:
                    case OutputType.DATAFRAME:
                        assert isinstance(item.value, pd.DataFrame)
                        file_path = (
                            self.dataframe_dir / f"{step.instance_identifier}_{key}.csv"
                        )
                        # Only dump if outdated version
                        if self._dump_is_outdated(step, "output"):
                            self.dataframe_operator.write(file_path, item.value)
                        output_data[key] = OutputItem(
                            output_type=OutputType.DATAFRAME,
                            value=str(file_path.relative_to(self.run_dir)),
                        )
                    case OutputType.JOBLIB_ARTIFACT:
                        file_path = (
                            self.artifact_dir
                            / f"{step.instance_identifier}_{key}.joblib.gz"
                        )
                        # Only dump if outdated version
                        if self._dump_is_outdated(step, "output"):
                            self.artifact_operator.write(file_path, item.value)
                        output_data[key] = OutputItem(
                            output_type=OutputType.JOBLIB_ARTIFACT,
                            value=str(file_path.relative_to(self.run_dir)),
                        )
                    case OutputType.PNG_BASE64:
                        file_path = (
                            self.plot_dir
                            / f"{step.instance_identifier}_{key}_image.png"
                        )
                        if self._dump_is_outdated(step, "output"):
                            self.base64_operator.write(file_path, item.value)
                        output_data[key] = OutputItem(
                            output_type=OutputType.PNG_BASE64,
                            value=str(file_path.relative_to(self.run_dir)),
                        )
                    case _:
                        output_data[key] = item

            self._update_dump_state(step, "output")
            return output_data

    def _read_plots(self, plots: dict) -> Plots:
        if plots:
            figures = []
            for plot in plots.values():
                # Make sure this works for old run saves which use absolute directories
                base_path = self.run_dir
                if Path(plot).is_absolute():
                    base_path = Path()
                figures.append(read_json(base_path / Path(plot)))
            return Plots(figures)
        return Plots([])

    def _write_plots(self, step: Step) -> dict:
        with ErrorHandler(), step.disk_write_mutex:
            plots_data = {}
            for i, plot in enumerate(step.plots):
                file_path = self.plot_dir / f"{step.instance_identifier}_plot{i}.json"

                self.plot_dir.mkdir(parents=True, exist_ok=True)
                if not isinstance(
                    plot, bytes
                ):  # TODO the data integration plots are of type byte, and therefore cannot be written using this methodology

                    # Only dump if disk state is outdated
                    if self._dump_is_outdated(step, "plots"):
                        write_json(plot, file_path)
                        plot.write_image(str(file_path).replace(".json", ".png"))

                    plots_data[i] = str(file_path.relative_to(self.run_dir))

            self._update_dump_state(step, "plots")

            return plots_data

    @property
    def run_dir(self):
        return paths.RUNS_PATH / self.run_name

    @property
    def metadata_path(self):
        return paths.RUNS_PATH / self.run_name / "metadata.yaml"

    @property
    def run_file(self) -> Path:
        return self.run_dir / RUN_FILE

    @property
    def workflow_file(self) -> Path:
        return paths.WORKFLOWS_PATH / f"{self.workflow_name}.yaml"

    @property
    def dataframe_dir(self) -> Path:
        return self.run_dir / "dataframes"

    @property
    def artifact_dir(self) -> Path:
        return self.run_dir / "artifacts"

    @property
    def plot_dir(self) -> Path:
        return self.run_dir / "plots"
