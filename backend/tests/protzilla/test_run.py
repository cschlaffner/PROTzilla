import logging
import pytest

from backend.protzilla.constants.data_types import DataKey
from backend.protzilla.methods.data_preprocessing import (
    ImputationByKNN,
    FilterSamplesByProteinsMissing,
)
from backend.protzilla.methods.importing import MaxQuantImport, MetadataImport

from backend.protzilla.run import Run
from pathlib import Path
from backend.protzilla.stepfactory import StepFactory



class TestRun:
    def test_init_standard(self, run_standard: Run):
        assert run_standard.workflow_name == "standard"
        assert run_standard.steps is not None
        assert run_standard.current_step is not None
        assert run_standard.steps.current_selected_step_id == "s00001_MaxQuantImport"
        assert run_standard.steps.current_section == "importing"

    def test_init_empty(self, run_empty: Run):
        assert run_empty.workflow_name == ".test-run-empty"
        assert run_empty.steps is not None
        assert len(run_empty.steps.all_steps) == 0
        with pytest.raises(BaseException):
            _ = run_empty.steps.current_selected_step_id
        assert str(run_empty.steps) == "StepManager with 0 steps: []"

    def test_init_imported(self, run_imported: Run):
        assert run_imported.workflow_name == ".test-run-empty"
        assert run_imported.steps is not None and len(run_imported.steps.all_steps) == 1
        assert run_imported.current_step is not None
        assert (
            run_imported.current_step.output[DataKey.PROTEIN_DF] is not None
            and not run_imported.current_step.output[DataKey.PROTEIN_DF].empty
        )
        assert run_imported.steps.current_selected_step_id == "teststep01_MXQ"
        assert run_imported.steps.current_section == "importing"

    def test_step_add(self, run_imported: Run):
        step = ImputationByKNN()
        length_before = len(run_imported.steps.all_steps)
        run_imported.step_add(step)
        assert len(run_imported.steps.all_steps) == length_before + 1

    def test_step_add_creation(self, run_empty: Run):
        run_empty.step_add(StepFactory.create_step("MaxQuantImport", run_empty.steps))
        run_empty.step_add(
            StepFactory.create_step("FilterProteinsBySamplesMissing", run_empty.steps)
        )
        run_empty.step_add(StepFactory.create_step("ImputationByKNN", run_empty.steps))

        assert "s00001_MaxQuantImport" in run_empty.steps.all_step_ids
        assert "s00002_FilterProteinsBySamplesMissing" in run_empty.steps.all_step_ids
        assert "s00003_ImputationByKNN" in run_empty.steps.all_step_ids
        assert run_empty.steps._id_clock == 3

    def test_step_remove(self, run_imported: Run):
        step = ImputationByKNN("teststep01")
        run_imported.step_add(step)
        length_before = len(run_imported.steps.all_steps)
        run_imported.step_remove("teststep01")
        assert len(run_imported.steps.all_steps) == length_before - 1

    def test_step_calculate(self, run_empty: Run, maxquant_data_file: Path):
        step = MaxQuantImport("teststep01_MXQ")
        run_empty.step_add(step)
        run_empty.current_form(
            {
                "file_path": maxquant_data_file,
                "map_to_uniprot": False,
                "intensity_name": "Intensity",
                "aggregation_method": "Sum",
            }
        )
        run_empty.step_calculate()
        assert run_empty.current_step is not None
        assert run_empty.steps.current_location == (
            "importing",
            "Protein Data Import",
            "teststep01_MXQ",
        )
        assert run_empty.current_step.output[DataKey.PROTEIN_DF] is not None
        assert not run_empty.current_step.output[DataKey.PROTEIN_DF].empty

    def test_step_plot(self, run_imported: Run):
        step = ImputationByKNN("teststep02_kNN")
        run_imported.step_add(step)
        run_imported.steps.connect_steps(
            {
                "source": "teststep01_MXQ",
                "sourceHandle": DataKey.PROTEIN_DF,
                "target": "teststep02_kNN",
                "targetHandle": DataKey.PROTEIN_DF,
            }
        )
        run_imported.step_next()
        run_imported.current_form(
            {
                "number_of_neighbours": 5,
                "graph_type": "Boxplot",
                "group_by": "None",
                "visual_transformation": "log10",
                "graph_type_quantities": "Pie chart",
            }
        )
        run_imported.step_calculate()
        assert run_imported.current_step is not None
        assert run_imported.current_step == step
        print(run_imported.current_step.plots)
        assert not run_imported.current_step.plots.empty

    def test_step_next(self, run_imported: Run):
        step = ImputationByKNN("teststep02_kNN")
        run_imported.step_add(step)
        run_imported.steps.connect_steps(
            {
                "source": "teststep01_MXQ",
                "sourceHandle": DataKey.PROTEIN_DF,
                "target": "teststep02_kNN",
                "targetHandle": DataKey.PROTEIN_DF,
            }
        )
        assert run_imported.current_step != step
        run_imported.step_next()
        assert run_imported.current_step == step

    def test_step_previous(self, run_imported: Run):
        step = ImputationByKNN("teststep02_kNN")
        run_imported.step_add(step)
        run_imported.steps.connect_steps(
            {
                "source": "teststep01_MXQ",
                "sourceHandle": DataKey.PROTEIN_DF,
                "target": "teststep02_kNN",
                "targetHandle": DataKey.PROTEIN_DF,
            }
        )
        run_imported.step_next()
        assert run_imported.current_step == step
        run_imported.step_previous()
        assert run_imported.current_step != step

    def test_step_goto(self, run_import_and_imputation: Run):
        run_import_and_imputation.step_goto("definitelyAWrongStepID")
        assert any(
            message["level"] == logging.ERROR and "ValueError" in message["msg"]
            for message in run_import_and_imputation.current_messages
        ), "No error messages found in run.current_messages"
        assert (
            run_import_and_imputation.steps.current_selected_step_id != "teststep02_kNN"
        )
        run_import_and_imputation.step_next()
        assert (
            run_import_and_imputation.steps.current_selected_step_id == "teststep02_kNN"
        )
        run_import_and_imputation.step_goto("teststep01_MXQ")
        assert (
            run_import_and_imputation.steps.current_selected_step_id == "teststep01_MXQ"
        )

    def test_set_steps_outdated(self, run_import_and_imputation: Run):
        run_import_and_imputation.step_next()
        assert run_import_and_imputation.current_step is not None
        assert run_import_and_imputation.current_step.calculation_status == "incomplete"
        run_import_and_imputation.step_calculate()
        assert run_import_and_imputation.current_step.calculation_status == "complete"
        run_import_and_imputation.step_set_outdated()
        assert run_import_and_imputation.current_step.calculation_status == "outdated"

    def test_step_finished(
        self, run_standard: Run, maxquant_data_file: Path, metadata_file: Path
    ):
        assert run_standard.current_step is not None
        assert run_standard.current_step.calculation_status == "incomplete"

        parameters = {
            "file_path": maxquant_data_file,
            "intensity_name": "Intensity",
            "map_to_uniprot": False,
            "aggregation_method": "Sum",
        }
        run_standard.current_form(parameters)
        run_standard.step_calculate()

        assert run_standard.current_step.calculation_status == "complete"

        run_standard.step_goto("s00002_MetadataImport")

        assert run_standard.current_step.calculation_status == "incomplete"

        parameters = {
            "file_path": f"",
            "feature_orientation": "Columns (samples in rows, features in columns)",
        }
        run_standard.current_form(parameters)
        run_standard.step_calculate()

        assert run_standard.current_step.calculation_status == "failed"

        parameters = {
            "file_path": "nonexistent_file.txt",
            "feature_orientation": "Columns (samples in rows, features in columns)",
        }
        run_standard.current_form(parameters)
        run_standard.step_calculate()

        assert run_standard.current_step.calculation_status == "failed"

        parameters = {
            "file_path": metadata_file,
            "feature_orientation": "Columns (samples in rows, features in columns)",
        }
        run_standard.current_form(parameters)
        run_standard.step_calculate()

        assert run_standard.current_step.calculation_status == "complete"

    def test_multiple_steps_calculate(self, run_imported: Run):
        step1 = FilterSamplesByProteinsMissing("teststep02_filter")
        run_imported.step_add(step1)
        run_imported.steps.connect_steps(
            {
                "source": "teststep01_MXQ",
                "sourceHandle": DataKey.PROTEIN_DF,
                "target": "teststep02_filter",
                "targetHandle": DataKey.PROTEIN_DF,
            }
        )

        step2 = ImputationByKNN("teststep03_kNN")
        run_imported.step_add(step2)
        run_imported.steps.connect_steps(
            {
                "source": "teststep02_filter",
                "sourceHandle": DataKey.PROTEIN_DF,
                "target": "teststep03_kNN",
                "targetHandle": DataKey.PROTEIN_DF,
            }
        )

        run_imported.step_next()
        run_imported.step_calculate()
        assert run_imported.current_step is not None
        assert run_imported.current_step.calculation_status == "complete"
        step1_output = run_imported.current_step.output
        run_imported.step_next()
        run_imported.step_calculate()
        assert run_imported.current_step.calculation_status == "complete"
        step2_output = run_imported.current_step.output

        run_imported.step_goto("teststep02_filter")
        run_imported.step_set_outdated()
        assert run_imported.current_step.calculation_status == "outdated"
        run_imported.step_calculate()
        assert run_imported.current_step.calculation_status == "complete"

        run_imported.step_goto("teststep03_kNN")
        assert run_imported.current_step.calculation_status == "outdated"
        run_imported.step_calculate()
        assert run_imported.current_step.calculation_status == "complete"
        assert step2_output[DataKey.PROTEIN_DF].equals(
            run_imported.current_step.output[DataKey.PROTEIN_DF]
        )

        run_imported.step_goto("teststep02_filter")
        assert run_imported.current_step.calculation_status == "complete"
        assert step1_output[DataKey.PROTEIN_DF].equals(
            run_imported.current_step.output[DataKey.PROTEIN_DF]
        )
        assert (
            str(run_imported.steps)
            == "StepManager with 3 steps: ['teststep01_MXQ', 'teststep02_filter', 'teststep03_kNN']"
        )

        # Delete step in between and make sure back-navigation works and following step output is voided
        run_imported.step_remove("teststep02_filter")
        assert run_imported.steps.current_selected_step_id == "teststep01_MXQ"
        assert run_imported.current_step.calculation_status == "complete"

        # This cannot work on a terminal step
        assert run_imported.steps.recommended_next_step_id is None
        with pytest.raises(ValueError):
            run_imported.steps.next_step()

        run_imported.step_goto("teststep03_kNN")
        assert run_imported.current_step.output.is_empty

    def test_multiple_steps_connections(self, run_imported: Run):
        step1 = FilterSamplesByProteinsMissing("teststep02_filter")
        step2 = ImputationByKNN("teststep03_kNN")
        step3 = MetadataImport("teststep04_metaimp")

        run_imported.step_add(step1)
        run_imported.step_add(step2)
        run_imported.step_add(step3)

        # Circular connections
        with pytest.raises(ValueError):
            run_imported.steps.connect_steps(
                {
                    "source": "teststep03_kNN",
                    "sourceHandle": DataKey.PROTEIN_DF,
                    "target": "teststep03_kNN",
                    "targetHandle": DataKey.PROTEIN_DF,
                }
            )

        # Regular connection
        run_imported.steps.connect_steps(
            {
                "source": "teststep01_MXQ",
                "sourceHandle": DataKey.PROTEIN_DF,
                "target": "teststep02_filter",
                "targetHandle": DataKey.PROTEIN_DF,
            }
        )

        run_imported.steps.connect_steps(
            {
                "source": "teststep01_MXQ",
                "sourceHandle": DataKey.PROTEIN_DF,
                "target": "teststep04_metaimp",
                "targetHandle": DataKey.PROTEIN_DF,
            }
        )

        edges = run_imported.steps.get_edges()

        assert len(edges) == 2
        assert {
            "source": "teststep01_MXQ",
            "sourceHandle": DataKey.PROTEIN_DF,
            "target": "teststep04_metaimp",
            "targetHandle": DataKey.PROTEIN_DF,
            "key": "teststep01_MXQ:protein_df->teststep04_metaimp:protein_df",
            "id": "teststep01_MXQ:protein_df->teststep04_metaimp:protein_df",
        } in edges
        assert {
            "source": "teststep01_MXQ",
            "sourceHandle": DataKey.PROTEIN_DF,
            "target": "teststep02_filter",
            "targetHandle": DataKey.PROTEIN_DF,
            "key": "teststep01_MXQ:protein_df->teststep02_filter:protein_df",
            "id": "teststep01_MXQ:protein_df->teststep02_filter:protein_df",
        } in edges

        # Repeat same connection
        assert run_imported.steps.graph.has_edge("teststep01_MXQ", "teststep02_filter")
        run_imported.steps.connect_steps(
            {
                "source": "teststep01_MXQ",
                "sourceHandle": DataKey.PROTEIN_DF,
                "target": "teststep02_filter",
                "targetHandle": DataKey.PROTEIN_DF,
            }
        )
        assert run_imported.steps.graph.has_edge("teststep01_MXQ", "teststep02_filter")

        # Switch source for connected target
        run_imported.steps.connect_steps(
            {
                "source": "teststep03_kNN",
                "sourceHandle": DataKey.PROTEIN_DF,
                "target": "teststep02_filter",
                "targetHandle": DataKey.PROTEIN_DF,
            }
        )

        assert not run_imported.steps.graph.has_edge(
            "teststep01_MXQ", "teststep02_filter"
        )
        assert run_imported.steps.graph.has_edge("teststep03_kNN", "teststep02_filter")

        # Disconnect
        run_imported.steps.disconnect_steps(
            {
                "source": "teststep03_kNN",
                "sourceHandle": DataKey.PROTEIN_DF,
                "target": "teststep02_filter",
                "targetHandle": DataKey.PROTEIN_DF,
            }
        )

        assert not run_imported.steps.graph.has_edge(
            "teststep01_MXQ", "teststep02_filter"
        )
        assert not run_imported.steps.graph.has_edge(
            "teststep03_kNN", "teststep02_filter"
        )

        # Disconnect again
        with pytest.raises(ValueError):
            run_imported.steps.disconnect_steps(
                {
                    "source": "teststep03_kNN",
                    "sourceHandle": DataKey.PROTEIN_DF,
                    "target": "teststep02_filter",
                    "targetHandle": DataKey.PROTEIN_DF,
                }
            )
