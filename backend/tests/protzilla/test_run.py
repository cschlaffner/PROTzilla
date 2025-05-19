import logging

from backend.protzilla.methods.data_preprocessing import ImputationByKNN, FilterSamplesByProteinsMissing
from backend.protzilla.methods.importing import MaxQuantImport


class TestRun:
    def test_init_standard(self, run_standard):
        assert run_standard.workflow_name == "standard"
        assert run_standard.steps is not None
        assert run_standard.current_step is not None
        assert run_standard.steps.current_step_index == 0
        assert run_standard.steps.current_section == "importing"

    def test_init_empty(self, run_empty):
        assert run_empty.workflow_name == "test-run-empty"
        assert run_empty.steps is not None
        assert len(run_empty.steps.all_steps) == 0
        assert run_empty.current_step is None
        assert run_empty.steps.current_step_index == 0

    def test_init_imported(self, run_imported):
        assert run_imported.workflow_name == "test-run-empty"
        assert run_imported.steps is not None and len(run_imported.steps.all_steps) == 1
        assert (
            run_imported.current_step.output["protein_df"] is not None
            and not run_imported.current_step.output["protein_df"].empty
        )
        assert run_imported.steps.current_step_index == 0
        assert run_imported.steps.current_section == "importing"

    def test_step_add(self, run_imported):
        step = ImputationByKNN()
        length_before = len(run_imported.steps.all_steps)
        run_imported.step_add(step)
        assert len(run_imported.steps.all_steps) == length_before + 1

    def test_step_remove(self, run_imported):
        step = ImputationByKNN()
        run_imported.step_add(step)
        length_before = len(run_imported.steps.all_steps)
        run_imported.step_remove(step)
        assert len(run_imported.steps.all_steps) == length_before - 1

    def test_step_calculate(self, run_empty, maxquant_data_file):
        step = MaxQuantImport()
        run_empty.step_add(step)
        run_empty.current_form(
             {
                "file_path": maxquant_data_file,
                "map_to_uniprot": False,
                "intensity_name": "Intensity",
                "aggregation_method": "Sum"
             }
        )
        run_empty.step_calculate()
        assert run_empty.current_step.output["protein_df"] is not None
        assert not run_empty.current_step.output["protein_df"].empty

    def test_step_plot(self, run_imported):
        step = ImputationByKNN()
        run_imported.step_add(step)
        run_imported.step_next()
        run_imported.current_form(
            {
                "number_of_neighbours": 5,
                "graph_type": "Boxplot",
                "group_by": "None",
                "visual_transformation": "log10",
                "graph_type_quantities": "Pie chart"
            }
        )
        run_imported.step_calculate()
        assert run_imported.current_step == step
        print(run_imported.current_step.plots)
        assert not run_imported.current_step.plots.empty

    def test_step_next(self, run_imported):
        step = ImputationByKNN()
        run_imported.step_add(step)
        assert run_imported.current_step != step
        run_imported.step_next()
        assert run_imported.current_step == step

    def test_step_previous(self, run_imported):
        step = ImputationByKNN()
        run_imported.step_add(step)
        run_imported.step_next()
        assert run_imported.current_step == step
        run_imported.step_previous()
        assert run_imported.current_step != step

    def test_step_goto(self, caplog, run_imported):
        step = ImputationByKNN()
        run_imported.step_add(step)
        run_imported.step_goto(0, "data_preprocessing_wrong")
        assert any(
            message["level"] == logging.ERROR and "ValueError" in message["msg"]
            for message in run_imported.current_messages
        ), "No error messages found in run.current_messages"
        assert run_imported.current_step != step
        run_imported.step_next()
        assert run_imported.current_step == step
        run_imported.step_goto(0, "importing")
        assert run_imported.current_step == run_imported.steps.all_steps[0]

    def test_step_change_method(self, run_imported):
        run_imported.step_change_method("DiannImport")
        assert run_imported.current_step.__class__.__name__ == "DiannImport"

    def test_set_steps_outdated(self,run_imported):
        step = ImputationByKNN()
        run_imported.step_add(step)
        run_imported.step_next()
        assert run_imported.current_step.calculation_status == "incomplete"
        run_imported.step_calculate()
        assert run_imported.current_step.calculation_status == "complete"
        run_imported.step_set_outdated()
        assert run_imported.current_step.calculation_status == "outdated"

    def test_multiple_steps_calculate(self, run_imported):
        step1 = FilterSamplesByProteinsMissing()
        step2 = ImputationByKNN()
        run_imported.step_add(step1)
        run_imported.step_add(step2)
        run_imported.step_next()
        run_imported.step_calculate()
        assert run_imported.current_step.calculation_status == "complete"
        step1_output = run_imported.current_step.output
        run_imported.step_next()
        run_imported.step_calculate()
        assert run_imported.current_step.calculation_status == "complete"
        step2_output = run_imported.current_step.output
        run_imported.step_goto(0, "data_preprocessing")
        run_imported.step_set_outdated()
        assert run_imported.current_step.calculation_status == "outdated"
        run_imported.step_goto(1, "data_preprocessing")
        assert run_imported.current_step.calculation_status == "outdated"
        run_imported.step_calculate()
        assert run_imported.current_step.calculation_status == "complete"
        assert step2_output["protein_df"].equals(run_imported.current_step.output["protein_df"])
        run_imported.step_goto(0, "data_preprocessing")
        assert run_imported.current_step.calculation_status == "complete"
        assert step1_output["protein_df"].equals(run_imported.current_step.output["protein_df"])

