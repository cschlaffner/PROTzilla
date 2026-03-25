import logging
import os
from copy import deepcopy
from pathlib import Path
import yaml

from backend.protzilla.constants.paths import RUNS_PATH
from backend.protzilla.form import FileInput
from backend.protzilla.run import Run, delete_run_folder
from backend.protzilla.run_helper import log_messages
from backend.protzilla.steps import Step
from backend.protzilla.utilities.utilities import random_string


class Runner:
    """
    Intended for use with runner_cli.py-Script (at PROTzilla2/runner_cli.py).
    Then .compute_workflow() is called, the workflow, with all it's steps will be
    executed. If specified, the Plots will be saved to <run_name>/plots.
    Results can be viewed after completion in the PROTzilla UI via `Continue Run`.

    :ivar workflow: str, name of workflow in user_data/workflows
    :ivar ms_data_path: str, path to MS-Data
    :ivar meta_data_path: str, path to Meta-Data
    :ivar msfragger_path: str, path to MSFragger combined_proteins.tsv
    :ivar diann_path: str, path to DIA-NN intensities file (*.pg_matrix.tsv)
    :ivar diann_meta_data_path: str, path to DIA-NN run-relationship metadata
    :ivar file_input_map: str, path to YAML file with step-specific file inputs
    :ivar run_name: str, name of run to be created
    :ivar df_mode: str, keep DFs in memory or write on disk, default: disk
    :ivar all_plots: bool, if set all plots will be generated and save in the
    :ivar verbose: bool, logs this input dict (args), default: false
    """

    def __init__(
        self,
        workflow: str,
        ms_data_path: str | None = None,
        meta_data_path: str | None = None,
        peptides_path: str | None = None,
        run_name: str | None = None,
        df_mode: str | None = "disk",
        all_plots: bool = False,
        verbose: bool = False,
        msfragger_path: str | None = None,
        diann_path: str | None = None,
        diann_meta_data_path: str | None = None,
        evidence_path: str | None = None,
        fasta_path: str | None = None,
        file_input_map: str | None = None,
    ):
        logging.basicConfig(level=logging.INFO)

        self.verbose = verbose
        if self.verbose:
            logging.info(f"Parsed arguments: {locals()}")

        self.ms_data_path = ms_data_path
        self.meta_data_path = meta_data_path
        self.peptides_path = peptides_path
        self.msfragger_path = msfragger_path
        self.diann_path = diann_path
        self.diann_meta_data_path = diann_meta_data_path
        self.evidence_path = evidence_path
        self.fasta_path = fasta_path
        self.file_input_map = self._load_file_input_map(file_input_map)
        self.df_mode = df_mode if df_mode is not None else "disk"
        self.workflow = workflow

        self.run_name = (
            run_name.strip()
            if run_name is not None and run_name.strip() is not None
            else f"runner_{random_string()}"
        )

        if os.path.exists(Path(f"{RUNS_PATH}/{self.run_name}")):
            self._overwrite_run_prompt()
            print("\n\n")

        self.run = Run(
            run_name=self.run_name,
            workflow_name=self.workflow,
            df_mode=self.df_mode,
        )
        self._validate_file_input_map()
        logging.info(f"Run {self.run_name} created at {self.run.run_path}")

        if (
            self.run.steps._current_selected_step_id is None
            and self.run.steps.all_steps
        ):
            self.run.steps._current_selected_step_id = (
                self.run.steps.all_step_ids_toposorted[0]
            )

        self.all_plots = all_plots
        self.plots_path = Path(f"{self.run.run_path}/plots")
        self.plots_path.mkdir(parents=True, exist_ok=True)
        logging.info(f"Saving plots at {self.plots_path}")

        log_messages(self.run.current_messages)
        self.run.current_messages.clear()

        self.run._run_write()

    def compute_workflow(self):
        logging.info("------ computing workflow\n")
        ordered_ids = self.run.steps.all_step_ids_toposorted
        for step_id in ordered_ids:
            self.run.steps.goto_step(step_id)
            step = self.run.current_step
            logging.info(f"performing step: {*self.run.steps.current_location,}")
            self._insert_file_inputs(step)
            self._perform_current_step()

            if step.plots and not step.plots.empty:
                self._save_plots_html(step)

            log_messages(self.run.current_messages)
            self.run.current_messages.clear()

            if step.calculation_status != "complete":
                break
        logging.info("\n Saving run...\n")
        self.run._run_write()
        logging.info(f"Run {self.run_name} saved at {self.run.run_path}")

    def _insert_file_inputs(self, step: Step):
        file_fields = {
            field.name: field
            for field in step.form.input_fields
            if isinstance(field, FileInput)
        }
        if not file_fields:
            return

        combined_inputs = self._legacy_file_inputs_for_step(step)
        combined_inputs.update(
            self.file_input_map.get(step.instance_identifier, {})
        )  # input map has priority over legacy inputs

        for field_name, file_path in combined_inputs.items():
            if field_name in file_fields:
                file_fields[field_name].value = file_path

    def _legacy_file_inputs_for_step(self, step: Step) -> dict[str, str]:
        specs = {
            "MaxQuantImport": {
                "file_path": ("ms_data_path", "the positional ms-data-path argument"),
            },
            "MsFraggerImport": {
                "file_path": ("msfragger_path", "--msfragger-path"),
            },
            "DiannImport": {
                "file_path": ("diann_path", "--diann-path"),
            },
            "MetadataImport": {
                "file_path": ("meta_data_path", "--meta-data-path"),
            },
            "MetadataImportMethodDiann": {
                "file_path": ("diann_meta_data_path", "--diann-meta-data-path"),
            },
            "PeptideImport": {
                "file_path": ("peptides_path", "--peptides-path"),
            },
            "EvidenceImport": {
                "file_path": ("evidence_path", "--evidence-path"),
            },
            "FastaImport": {
                "file_path": ("fasta_path", "--fasta-path"),
            },
        }.get(step.__class__.__name__, {})

        configured_inputs = {}  # ^._.^ ~ MEOW
        step_overrides = self.file_input_map.get(step.instance_identifier, {})

        for field_name, (attribute_name, legacy_argument) in specs.items():
            file_path = getattr(self, attribute_name)
            if file_path is not None:
                configured_inputs[field_name] = file_path
                continue
            if field_name in step_overrides:
                continue
            raise ValueError(
                f"Missing required file input '{field_name}' for {step.operation} with "
                f"{step.display_name}. Provide it via the file-input-map."
            )

        return configured_inputs

    def _load_file_input_map(
        self, file_input_map_path: str | None
    ) -> dict[str, dict[str, str]]:
        if not file_input_map_path:
            return {}

        with open(file_input_map_path, "r", encoding="utf-8") as handle:
            file_input_config = yaml.safe_load(handle)

        if file_input_config is None:
            return {}

        if not isinstance(file_input_config, dict):
            raise ValueError("file-input-map must be a YAML mapping.")

        parsed_inputs = {}
        for step_id, field_map in file_input_config.items():
            if not isinstance(field_map, dict):
                raise ValueError(
                    "file-input-map must use the format: step_id -> {field_name: path}."
                )
            parsed_field_map = {}
            for field_name, path in field_map.items():
                if path is None or str(path) == "None":
                    continue
                parsed_field_map[str(field_name)] = str(path)
            if parsed_field_map:
                parsed_inputs[str(step_id)] = parsed_field_map
        return parsed_inputs

    def _validate_file_input_map(self):
        for step_id, field_paths in self.file_input_map.items():
            if step_id not in self.run.steps.all_steps:
                raise ValueError(f"file-input-map references unknown step '{step_id}'.")

            step = self.run.steps.get_step_by_id(step_id)

            for field_name in field_paths:
                if field_name not in step.form:
                    raise ValueError(
                        f"file-input-map references unknown field '{field_name}' for step '{step_id}'."
                    )
                if not isinstance(step.form[field_name], FileInput):
                    raise ValueError(
                        f"file-input-map field '{field_name}' for step '{step_id}' is not a file input."
                    )

    def _perform_current_step(self):
        step = self.run.current_step
        explicit_form_values = {}
        for field in step.form.input_fields:
            if not hasattr(field, "name") or not hasattr(field, "value"):
                continue
            if field.value in (None, "", []):
                continue
            explicit_form_values[field.name] = deepcopy(field.value)
        step.modify_form(self.run)
        step.form.update_values(explicit_form_values)
        step.calculate(self.run.steps)
        self.run._run_write()

    def _save_plots_html(self, step):
        for i, plot in enumerate(step.plots):
            plot_path = f"{self.plots_path}/{step.instance_identifier}-{step.section}-{step.operation}-{step.display_name}-{i}.html"
            plot.write_html(plot_path)

    def _overwrite_run_prompt(self):
        answer = input(
            "A run with the this name already exists. "
            "Do you want to overwrite it? [y/n]: "
        )
        if answer in ["n", "no"]:
            print("exiting")
            exit(0)
        elif answer in ["y", "yes"]:
            delete_run_folder(run_name=self.run_name)
            return
        else:
            print("\n\n----- Please answer with one of the given options")
            self._overwrite_run_prompt()


def _serialize_graphs(graphs):
    return {k: v for graph in graphs for k, v in graph.items()}
