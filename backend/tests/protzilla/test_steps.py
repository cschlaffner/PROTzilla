import pytest

from backend.protzilla.disk_operator import DiskOperator
from backend.protzilla.methods.data_preprocessing import ImputationByMinPerProtein
from backend.protzilla.methods.importing import MaxQuantImport
from backend.protzilla.steps import Section, Step
from backend.protzilla.step_manager import StepManager


class TestStepManager:
    @pytest.fixture
    def step_manager(self):
        disk_operator = DiskOperator("test_run", "test_workflow")
        return StepManager(disk_operator=disk_operator)

    def test_add_step(self, step_manager: StepManager):
        assert len(step_manager.sections[Section.IMPORTING]) == 0
        step = Step()
        step.section = Section.IMPORTING
        step_manager.add_step(step)
        assert len(step_manager.all_step_ids) == 1
        assert step_manager.current_step == step

    def test_remove_step(self, step_manager: StepManager):
        step1 = MaxQuantImport("teststep01_MXQ")
        step_manager.add_step(step1)
        step2 = MaxQuantImport("teststep02_MXQ")
        step_manager.add_step(step2)
        assert len(step_manager.all_step_ids) == 2
        step_manager.remove_step(step2.instance_identifier)
        assert len(step_manager.all_step_ids) == 1
        assert step_manager.current_selected_step_id != "teststep02_MXQ"

    def test_remove_last_step(self, step_manager: StepManager):
        step1 = MaxQuantImport("teststep01_MXQ")
        step_manager.add_step(step1)
        assert len(step_manager.all_step_ids) == 1
        with pytest.raises(ValueError):
            step_manager.remove_step(step1.instance_identifier)

    def test_first_step_becomes_current(self, step_manager: StepManager):
        assert step_manager._current_selected_step_id is None
        step = Step("teststep01_empty")
        step.section = Section.IMPORTING
        step_manager.add_step(step)
        assert step_manager.current_step == step

    def test_all_steps(self, step_manager: StepManager):
        assert len(step_manager.all_steps) == 0
        step1 = Step("teststep01_empty")
        step_manager.add_step(step1)
        step2 = Step("teststep02_empty")
        step_manager.add_step(step2)

        assert len(step_manager.all_steps) == 2
        assert step1 in step_manager.all_steps
        assert step2 in step_manager.all_steps

    def test_all_steps_in_section(self, step_manager: StepManager):
        step1 = Step("teststep01_empty")
        step_manager.add_step(step1)

        assert len(step_manager.all_steps_in_section(Section.IMPORTING)) == 0
        step = MaxQuantImport("teststep02_MXQ")
        step_manager.add_step(step)

        assert len(step_manager.all_steps_in_section(Section.IMPORTING)) == 1
        assert step_manager.all_steps_in_section(Section.IMPORTING)[0] == step
        step_manager.remove_step(step.instance_identifier)
        assert len(step_manager.all_steps_in_section(Section.IMPORTING)) == 0

    def test_goto_step(self, step_manager: StepManager):
        step1 = Step("teststep01_empty")
        step1.section = Section.IMPORTING
        step_manager.add_step(step1)

        step2 = Step("teststep02_empty")
        step2.section = Section.DATA_PREPROCESSING
        step_manager.add_step(step2)

        assert step_manager.current_selected_step_id == "teststep01_empty"
        step_manager.goto_step("teststep02_empty")
        assert step_manager.current_step == step2

    def test_invalid_goto_step(self, step_manager: StepManager):
        with pytest.raises(ValueError):
            step_manager.goto_step("nonexistingstep")

        step1 = Step("teststep01_empty")
        step1.section = Section.IMPORTING
        step_manager.add_step(step1)

        step2 = Step("teststep02_empty")
        step2.section = Section.DATA_PREPROCESSING
        step_manager.add_step(step2)

        step_manager.goto_step("teststep02_empty")

        step_manager.remove_step("teststep02_empty")
        with pytest.raises(ValueError):
            step_manager.goto_step("teststep02_empty")
