import logging
import os
from pathlib import Path

from backend.protzilla.constants.paths import RUNS_PATH
from backend.protzilla.run import Run, delete_run_folder
from backend.protzilla.run_helper import log_messages
from backend.protzilla.steps import Step, Section
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
    :ivar run_name: str, name of run to be created
    :ivar df_mode: str, keep DFs in memory or write on disk, default: disk
    :ivar all_plots: bool, if set all plots will be generated and save in the
    :ivar verbose: bool, logs this input dict (args), default: false
    """

    def __init__(
        self,
        workflow: str,
        ms_data_path: str,
        meta_data_path: str | None,
        peptides_path: str | None,
        run_name: str | None,
        df_mode: str | None = "disk",
        all_plots: bool = False,
        verbose: bool = False,
        msfragger_path: str | None = None,
        diann_path: str | None = None,
        diann_meta_data_path: str | None = None,
        evidence_path: str | None = None,
        fasta_path: str | None = None,
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
            if self.run.steps._current_selected_step_id is None:
                self.run.steps._current_selected_step_id = step_id
            else:
                self.run.steps.goto_step(step_id)
            step = self.run.current_step
            logging.info(f"performing step: {*self.run.steps.current_location,}")
            if step.section == Section.IMPORTING:
                self._insert_commandline_inputs(step)
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

    def _insert_commandline_inputs(self, step: Step):
        step_type = step.__class__.__name__
        if step_type == "MaxQuantImport":
            step.form["file_path"].value = self.ms_data_path
            return
        if step_type == "MsFraggerImport":
            if self.msfragger_path is None:
                raise ValueError(
                    "msfragger_path (--msfragger_path=<path/to/combined_proteins.tsv>) "
                    f"is not specified, but is required for {step.operation} with {step.display_name}"
                )
            step.form["file_path"].value = self.msfragger_path
            return
        if step_type == "DiannImport":
            if self.diann_path is None:
                raise ValueError(
                    "diann_path (--diann_path=<path/to/pg_matrix.tsv>) "
                    f"is not specified, but is required for {step.operation} with {step.display_name}"
                )
            step.form["file_path"].value = self.diann_path
            return

        if step_type == "MetadataImport":
            if self.meta_data_path is None:
                raise ValueError(
                    f"meta_data_path (--meta_data_path=<path/to/data) is not specified,"
                    f" but is required for {step.operation} with {step.display_name}"
                )
            step.form["file_path"].value = self.meta_data_path
            return
        if step_type == "MetadataImportMethodDiann":
            if self.diann_meta_data_path is None:
                raise ValueError(
                    "diann_meta_data_path (--diann_meta_data_path=<path/to/data>) "
                    f"is not specified, but is required for {step.operation} with {step.display_name}"
                )
            step.form["file_path"].value = self.diann_meta_data_path
            return

        if step_type == "PeptideImport":
            if self.peptides_path is None:
                raise ValueError(
                    f"peptides_path (--peptides_path=<path/to/data>) is not specified, "
                    f"but is required for {step.operation} with {step.display_name}"
                )
            step.form["file_path"].value = self.peptides_path
            return
        if step_type == "EvidenceImport":
            if self.evidence_path is None:
                raise ValueError(
                    "evidence_path (--evidence_path=<path/to/evidence.txt>) "
                    f"is not specified, but is required for {step.operation} with {step.display_name}"
                )
            step.form["file_path"].value = self.evidence_path
            return
        if step_type == "FastaImport":
            if self.fasta_path is None:
                raise ValueError(
                    "fasta_path (--fasta_path=<path/to/file.fasta>) "
                    f"is not specified, but is required for {step.operation} with {step.display_name}"
                )
            step.form["file_path"].value = self.fasta_path
            return
        if step_type == "ExampleDatasetImport":
            return
        if step_type == "MetadataColumnAssignment":
            return
        else:
            raise ValueError(
                f"Cannot find step with name {step.operation} with {step.display_name} in importing"
            )

    def _perform_current_step(self):
        self.run.current_step.calculate(self.run.steps)

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
