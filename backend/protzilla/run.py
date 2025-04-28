from __future__ import annotations

import logging
import threading
import traceback

import os
import shutil
from pathlib import Path

import backend.protzilla.constants.paths as paths
from backend.protzilla.form import Form
from backend.protzilla.steps import Messages, Output, Plots, Step
from backend.protzilla.utilities import format_trace
from backend.protzilla.disk_operator import YamlOperator


def get_available_run_names() -> list[str]:
    if not paths.RUNS_PATH.exists():
        logging.warning(f"No runs have been found in {paths.RUNS_PATH}.")
        return []
    return [
        directory.name
        for directory in paths.RUNS_PATH.iterdir()
        if not directory.name.startswith(".")
    ]

def get_available_runinfo() -> tuple[list[dict[str, str | list[str]]], list[dict[str, str | list[str]]], set[str]]:
    if not paths.RUNS_PATH.exists():
        return []
    runs = []
    runs_favourited = []
    all_tags = set()
    for run in get_available_run_names():

        run_dir = os.path.join(paths.RUNS_PATH, run)
        metadata_yaml_path = os.path.join(run_dir, "metadata.yaml")
        if not os.path.isfile(metadata_yaml_path):
            logging.warning(f"No metadata.yaml file found for run {run}.")
            continue
        yaml_operator = YamlOperator()
        metadata = yaml_operator.read(Path(metadata_yaml_path))
        if not metadata:
            metadata = {}
        tags = metadata.get("tags", set())

        run = {
            "run_name": run,
            "creation_date": metadata.get("creation_date", "date not available"),
            "modification_date": metadata.get("modification_date", "date not available"),
            "memory_mode": metadata.get("df_mode", "disk"),
            "run_steps": metadata.get("steps", []),
            "favourite_status": metadata.get("favourite", False),
            "run_tags": list(tags)
        }

        if run["favourite_status"]:
            runs_favourited.append(run)
        else:
            runs.append(run)

        for tag in tags:
            all_tags.add(tag)

    all_tags = list(all_tags)


    #     #----
    #     disk_operator = DiskOperator(name, "dummy_workflow_name")
    #     directory_path = os.path.join(paths.RUNS_PATH, name)
    #     run_yaml_path = os.path.join(directory_path, "run.yaml")
    #     step_manager = disk_operator.read_run(run_yaml_path)
    #     steps = step_manager.all_steps
    #     step_names = []
    #     for step in steps:
    #         step_names.append(step.display_name)
    #
    #     # empty initialization to ensure backwardscompatibility for runs without metadata.yaml
    #     favourite = False
    #     tags = set()
    #     creation_date = "date not available"
    #     modification_date = "date not available"
    #
    #     metadata_yaml_path = os.path.join(directory_path, "metadata.yaml")
    #     if os.path.isfile(metadata_yaml_path):
    #         yaml_operator = YamlOperator()
    #         metadata = yaml_operator.read(metadata_yaml_path)
    #         #TODO handle empty tags
    #         tags = metadata.get("tags", set())
    #         favourite = metadata.get("favourite", False)
    #         creation_date = metadata.get("creation_date", "date not available")
    #         modification_date = metadata.get("modification_date", "date not available")
    #
    #     for tag in tags:
    #         all_tags.add(tag)
    #
    #     tags = list(tags) #sets are not json serializable
    #     run = {
    #         "run_name": name,
    #         "creation_date": creation_date,
    #         "modification_date": modification_date,
    #         "memory_mode": step_manager.df_mode,
    #         "run_steps" : step_names,
    #         "favourite_status" : favourite,
    #         "run_tags": tags
    #         }
    #
    #     if favourite:
    #         runs_favourited.append(run)
    #     else:
    #         runs.append(run)
    #
    # all_tags = list(all_tags)

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
            return result

        return wrapper

    def __init__(
        self, run_name: str, workflow_name: str | None = None, df_mode: str = "disk"
    ):
        from backend.protzilla.disk_operator import DiskOperator  # to avoid a circular import

        self.run_name = run_name
        self.workflow_name = workflow_name
        self.disk_operator: DiskOperator = DiskOperator(run_name, workflow_name)

        if run_name in get_available_run_names():
            self._run_read()
        elif workflow_name:
            self.df_mode = df_mode
            self._workflow_read()
        else:
            raise ValueError(
                f"No run named {run_name} has been found and no workflow has been provided. Please reference an existing run or provide a workflow to create a new one."
            )

    def __repr__(self):
        return f"Run({self.run_name}) with {len(self.steps.all_steps)} steps."

    @error_handling
    def _run_read(self) -> None:
        self.steps = self.disk_operator.read_run()
        self.steps.disk_operator = self.disk_operator
        self.df_mode = self.steps.df_mode

    @error_handling
    def _run_write(self) -> None:
        self.disk_operator.write_run(self.steps)

    @property
    def run_path(self) -> str:
        return self.disk_operator.run_dir

    @error_handling
    def metadata_read(self) -> dict:
        return self.disk_operator.read_metadata()

    @error_handling
    def metadata_write(self, metadata: dict) -> None:
        return self.disk_operator.write_metadata(metadata)

    @error_handling
    @auto_save
    def _workflow_read(self) -> None:
        self.steps = self.disk_operator.read_workflow()

    @error_handling
    def _workflow_export(self, workflow_name: str | None = None) -> None:
        if workflow_name:
            self.workflow_name = workflow_name
        self.disk_operator.export_workflow(self.steps, self.workflow_name)

    @error_handling
    @auto_save
    def step_add(self, step: Step, step_index: int | None = None) -> None:
        self.steps.add_step(step)

    @error_handling
    @auto_save
    def step_remove(
        self,
        step: Step | None = None,
        step_index: int | None = None,
        section: str | None = None,
    ) -> None:
        self.steps.remove_step(step=step, step_index=step_index, section=section)

    @error_handling
    @auto_save
    def step_calculate(self, inputs: dict | None = None) -> None:
        self.steps.current_step.calculate(self.steps, inputs)

    @error_handling
    @auto_save
    def update_inputs(self, inputs: dict) -> None:
        self.steps.current_step.updateInputs(inputs)

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
    def step_goto(self, step_index: int, section: str) -> None:
        self.steps.goto_step(step_index, section)

    @error_handling
    def step_set_outdated(self, offset: int = 0) -> int:
        return self.steps.set_steps_outdated(offset)

    @error_handling
    @auto_save
    def step_change_method(self, new_method: str) -> None:
        self.steps.change_method(new_method)

    
    @auto_save
    def current_form(self, new_form_values = {}) -> Form:
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
    
