from __future__ import annotations

import logging
import threading
import traceback

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from backend.protzilla.constants.data_types import Connection
import backend.protzilla.constants.paths as paths
from backend.protzilla.constants.date_format import metadata_date_format
from backend.protzilla.form import Form
from backend.protzilla.steps import Messages, Output, Plots, Step, StepManager, Section
from backend.protzilla.utilities import format_trace


def get_available_run_names() -> list[str]:
    if not paths.RUNS_PATH.exists():
        logging.warning(f"No runs have been found in {paths.RUNS_PATH}.")
        return []
    return [
        directory.name
        for directory in paths.RUNS_PATH.iterdir()
        if not directory.name.startswith(".")
    ]


def get_available_run_info() -> (
    str
    | tuple[
        list[dict[str, bool | list[Any] | str]],
        list[dict[str, bool | list[Any] | str | Any]],
        list[Any],
    ]
):
    """
    Get all available runs and their metadata.
    Each run is a dictionary with the following entries:
        - run_name: the name of the run
        - creation_date: the date of creation
        - modification_date: the date of last modification
        - memory_mode: the memory mode of the run (disk or memory)
        - run_steps: a list of all steps in the run
        - favourite_status: the favourite status of the run (True or False)
        - run_tags: a list of all tags of the run

    If an error occurs, a string is returned to be displayed in the frontend as an error message.

    :return: a list of all runs, a list of favourited runs and a list of all tags.
    """
    from backend.protzilla.disk_operator import (
        YamlOperator,
    )  # import here to avoid import error with runner

    if not paths.RUNS_PATH.exists():
        return f"No runs have been found in {paths.RUNS_PATH}."

    runs = []
    runs_favourited = []
    all_tags = set()
    for run_name in get_available_run_names():

        run_dir = os.path.join(paths.RUNS_PATH, run_name)
        metadata_yaml_path = os.path.join(run_dir, "metadata.yaml")
        if not os.path.isfile(metadata_yaml_path):
            Run(
                run_name
            )  # initialize run to create metadata.yaml (creation date set to now)
        yaml_operator = YamlOperator()
        metadata = yaml_operator.read(Path(metadata_yaml_path))
        if not metadata:
            metadata = {}
        tags = metadata.get("tags", set())

        run_name = {
            "run_name": run_name,
            "creation_date": metadata.get("creation_date", "date not available"),
            "modification_date": metadata.get(
                "modification_date", "date not available"
            ),
            "memory_mode": metadata.get("df_mode", "disk"),
            "run_steps": metadata.get("steps", []),
            "favourite_status": metadata.get("favourite", False),
            "run_tags": list(tags),
        }

        if run_name["favourite_status"]:
            runs_favourited.append(run_name)
        else:
            runs.append(run_name)

        for tag in tags:
            all_tags.add(tag)

    all_tags = list(all_tags)

    return runs, runs_favourited, all_tags


def delete_run_folder(run_name) -> None:
    path = os.path.join(paths.RUNS_PATH, run_name)

    if os.path.isdir(path):
        shutil.rmtree(path)


class Run:
    class ErrorHandlingContextManager:
        def __init__(self, run):
            self.run = run

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, tb):
            if exc_type:
                formatted_trace = format_trace(traceback.format_exception(exc_value))
                if (
                    hasattr(self.run, "current_step")
                    and self.run.current_step is not None
                ):
                    self.run.current_step.messages.append(
                        dict(
                            level=logging.ERROR,
                            msg=(
                                f"An error occurred: {exc_value.__class__.__name__}: {exc_value}."
                                f"Please check your parameters or report a potential programming issue if this is unexpected."
                            ),
                            trace=formatted_trace,
                        )
                    )
                else:
                    raise exc_value
                return True

    def error_handling(func):
        """
        Decorator to handle errors in the run, will log the errors.
        :return:
        """

        def wrapper(self, *args, **kwargs):
            with Run.ErrorHandlingContextManager(self):
                return func(self, *args, **kwargs)

        return wrapper

    def auto_save(func):
        """
        Decorator to automatically save the run in the background after the function is called.
        """

        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            thread = threading.Thread(target=self._run_write)
            thread.daemon = True
            thread.start()
            self.steps.df_mode = self.df_mode
            self.steps.disk_operator = self.disk_operator
            self.metadata_write(self._metadata)
            return result

        return wrapper

    _instances = {}

    def __new__(cls, run_name, *args, **kwargs):
        if run_name not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[run_name] = instance
            instance._initialized = False  # flag to control __init__

        return cls._instances[run_name]

    def __init__(
        self, run_name: str, workflow_name: str | None = None, df_mode: str = "disk"
    ):
        if getattr(self, "_initialized"):
            return  # skip init if already initialized

        from backend.protzilla.disk_operator import (
            DiskOperator,
        )  # to avoid a circular import

        self.run_name = run_name
        self.workflow_name = workflow_name
        self.disk_operator: DiskOperator = DiskOperator(run_name, workflow_name)
        self._metadata = {}

        if run_name in get_available_run_names():
            self._run_read()
        elif workflow_name:
            self.df_mode = df_mode
            self._workflow_read()
        else:
            raise ValueError(
                f"No run named {run_name} has been found and no workflow has been provided. Please reference an existing run or provide a workflow to create a new one."
            )

        self._initialized = True

    def __repr__(self):
        return f"Run({self.run_name}) with {len(self.steps.all_steps)} steps."

    @error_handling
    def _run_read(self) -> None:
        self.steps: StepManager = self.disk_operator.read_run()
        self.steps.disk_operator = self.disk_operator
        self.df_mode = self.steps.df_mode
        self._metadata = self.metadata_read()

    @error_handling
    def _run_write(self) -> None:
        self.disk_operator.write_run(self.steps)

    def delete_run(self) -> None:
        delete_run_folder(self.run_name)
        self._instances.pop(
            self.run_name, None
        )  # remove instance from the class dictionary

    @property
    def run_path(self) -> str:
        return self.disk_operator.run_dir

    @error_handling
    @auto_save
    def update_run_name(self, new_run_name: str) -> None:
        if self.run_name != new_run_name:
            self.disk_operator.update_run_name(new_run_name)
            self.update_modification_date()
            self._instances.pop(self.run_name, None)
            self._instances[new_run_name] = self
            self.run_name = new_run_name

    @error_handling
    def metadata_read(self) -> dict:
        return self.disk_operator.read_metadata()

    @error_handling
    def metadata_write(self, metadata: dict) -> None:
        return self.disk_operator.write_metadata(metadata)

    @error_handling
    @auto_save
    def update_metadata(self, metadata: dict) -> None:
        """
        Update the metadata field of the run. It will be written to the yaml with the next auto_save.
        :param metadata: dict with metadata to update
        :return:
        """
        self._metadata.update(metadata)

    @error_handling
    @auto_save
    def set_step_pos(self, step_id: str, x: float, y: float) -> None:
        step = self.steps.id_mapping.get(step_id)
        if step is None:
            raise ValueError(f"Unknown step id: {step_id}")
        step.visual_data["node_position"] = {"x": x, "y": y}

    def update_modification_date(self) -> None:
        self._metadata["modification_date"] = datetime.now().strftime(
            metadata_date_format
        )

    @error_handling
    @auto_save
    def _workflow_read(self) -> None:
        self.steps = self.disk_operator.read_workflow()
        self._metadata = self.metadata_read()
        self.update_metadata(
            {
                "df_mode": self.steps.df_mode,
                "steps": [step.display_name for step in self.steps.all_steps],
            }
        )

    @error_handling
    def _workflow_save(self, workflow_name: str | None = None) -> None:
        if workflow_name:
            self.workflow_name = workflow_name
        self.disk_operator.save_workflow(self.steps, self.workflow_name)

    @error_handling
    @auto_save
    def step_add(self, step: Step, step_index: int | None = None) -> None:
        self.steps.add_step(step)
        self.update_metadata(
            {
                "steps": [step.display_name for step in self.steps.all_steps],
            }
        )

    @error_handling
    @auto_save
    def step_remove(
        self,
        step: Step | None = None,
        step_index: int | None = None,
        section: Section | None = None,
    ) -> None:
        self.steps.remove_step(step=step, step_index=step_index, section=section)
        self.update_metadata(
            {
                "steps": [step.display_name for step in self.steps.all_steps],
            }
        )

    @auto_save
    def connect_steps(self, connection: Connection) -> None:
        """
        Currently not used. Applies the connection that is passed and reloads the target's form
        :param connection: The connection to apply to the steps
        """
        target = self.steps.connect_steps(connection)
        target.form.apply_modification(self)

    @auto_save
    def disconnect_steps(self, connection: Connection) -> None:
        """
        Currently not used. Removes the connection that is passed and reloads the target's form
        :param connection: The connection to remove from the steps
        """
        target = self.steps.disconnect_steps(connection)
        target.form.apply_modification(self)

    @error_handling
    @auto_save
    def step_calculate(self) -> None:
        self.steps.current_step.calculate(self.steps)
        self.update_modification_date()

    @error_handling
    @auto_save
    def step_plot(self, inputs: dict | None = None) -> None:
        self.steps.current_step.plot(inputs)

    @error_handling
    @auto_save
    def step_next(self) -> None:
        self.steps.next_step()

    @error_handling
    def step_previous(self) -> None:
        self.steps.previous_step()

    @error_handling
    @auto_save
    def step_goto(self, step_index: int, section: Section) -> None:
        self.steps.goto_step(step_index, section)

    @error_handling
    def step_set_outdated(self, offset: int = 0) -> int:
        return self.steps.set_steps_outdated(offset)

    @error_handling
    @auto_save
    def step_change_method(self, new_method: str) -> None:
        self.steps.change_method(new_method)

    @auto_save
    def step_upload_file(self, inputname: str, file) -> None:
        self.steps.current_step.upload_file(inputname, file)

    @auto_save
    def current_form(self, new_form_values={}) -> Form:
        self.steps.current_step.form.update_values(new_form_values)
        self.steps.current_step.form.apply_modification(self)
        return self.steps.current_step.form

    @property
    def current_messages(self) -> Messages:
        return self.steps.current_step.messages

    @property
    def current_plots(self) -> Plots | None:
        return self.steps.current_step.plots

    @property
    def current_outputs(self) -> Output:
        return self.steps.current_step.output

    @property
    def current_filtered_data(self) -> dict:
        return self.steps.current_step.filtered_datatable

    @property
    def current_step(self) -> Step | None:
        return self.steps.current_step
