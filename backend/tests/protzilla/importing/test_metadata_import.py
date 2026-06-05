import pandas as pd
import pytest

from backend.protzilla.constants.data_types import DataKey
from backend.protzilla.constants.option_types import Separators
from backend.protzilla.run import Run
from backend.tests.paths import TEST_METADATA_PATH
from backend.protzilla.methods.importing import (
    DiannImport,
    MetadataColumnAssignment,
    MetadataImport,
)
from backend.protzilla.steps import Step


def test_metadata_import(run_imported):
    run_imported.step_add(MetadataImport("teststep02_Meta"))
    run_imported.steps.connect_steps(
        {
            "source": "teststep01_MXQ",
            "sourceHandle": DataKey.PROTEIN_DF,
            "target": "teststep02_Meta",
            "targetHandle": DataKey.PROTEIN_DF,
        }
    )
    run_imported.step_next()
    run_imported.current_form(
        {
            "file_path": TEST_METADATA_PATH / "metadata_cut_columns.csv",
            "feature_orientation": "Columns (samples in rows, features in columns)",
            "separator": Separators.comma.value,
        }
    )
    run_imported.step_calculate()
    test_metadata = pd.read_csv(TEST_METADATA_PATH / "metadata_cut_columns.csv")
    pd.testing.assert_frame_equal(
        test_metadata, run_imported.current_outputs[DataKey.METADATA_DF]
    )


def test_metadata_import_faulty_file(run_imported):
    run_imported.step_add(MetadataImport("teststep02_Meta"))
    run_imported.steps.connect_steps(
        {
            "source": "teststep01_MXQ",
            "sourceHandle": DataKey.PROTEIN_DF,
            "target": "teststep02_Meta",
            "targetHandle": DataKey.PROTEIN_DF,
        }
    )
    run_imported.step_next()
    run_imported.current_form(
        {
            "file_path": TEST_METADATA_PATH / "metadata_sample_column_missing.csv",
            "feature_orientation": "Columns (samples in rows, features in columns)",
            "separator": Separators.comma.value,
        }
    )
    run_imported.step_calculate()
    assert "messages" in run_imported.current_outputs.output
    messages = run_imported.current_outputs["messages"][0]
    assert (
        messages["level"] == 40
        and "The metadata file must contain a column named 'Sample'" in messages["msg"]
    )


@pytest.mark.skip(reason="Formerly commented out, needs reevaluation")
def test_metadata_import_diann(run_empty):
    run_empty.step_add(DiannImport())
    run_empty.current_form(
        {
            "file_path": f"{TEST_METADATA_PATH}/DIANN/20230605_24h_prodi_DMSO_report.pg_matrix.tsv",
            "map_to_uniprot": "False",
            "aggregation_method": "Sum",
        }
    )
    run_empty.step_calculate()
    assert (
        run_empty.current_outputs[DataKey.PROTEIN_DF] is not None
    ), "DIA-NN MS data import failed."
    assert not run_empty.current_outputs[
        DataKey.PROTEIN_DF
    ].empty, "DIA-NN MS data import failed."
    run_empty.step_add(MetadataImportMethodDiann())
    run_empty.step_next()
    run_empty.current_form(
        {
            "file_path": f"{TEST_METADATA_PATH}/DIANN/sample run relationship.xlsx",
            "groupby_sample": True,
        }
    )
    run_empty.step_calculate()
    test_metadata = pd.read_csv(f"{TEST_METADATA_PATH}/DIANN/meta.csv")
    test_protein_df = pd.read_csv(f"{TEST_METADATA_PATH}/DIANN/correct_protein_df.csv")
    pd.testing.assert_frame_equal(
        test_metadata, run_empty.current_outputs[DataKey.METADATA_DF]
    )
    pd.testing.assert_frame_equal(
        test_protein_df,
        run_empty.steps.get_step_output(DiannImport, DataKey.PROTEIN_DF),
    )


def test_metadata_orientation(run_imported: Run):
    run_imported.step_add(MetadataImport("teststep02_Meta"))
    run_imported.steps.connect_steps(
        {
            "source": "teststep01_MXQ",
            "sourceHandle": DataKey.PROTEIN_DF,
            "target": "teststep02_Meta",
            "targetHandle": DataKey.PROTEIN_DF,
        }
    )
    run_imported.step_next()
    run_imported.current_form(
        {
            "file_path": f"{TEST_METADATA_PATH}/metadata_cut_columns.csv",
            "feature_orientation": "Columns (samples in rows, features in columns)",
            "separator": Separators.comma.value,
        }
    )
    run_imported.step_calculate()
    metadata_df_a = run_imported.current_outputs[DataKey.METADATA_DF]
    run_imported.current_form(
        {
            "file_path": f"{TEST_METADATA_PATH}/metadata_cut_rows.csv",
            "feature_orientation": "Rows (samples in columns, features in rows)",
            "separator": Separators.comma.value,
        }
    )
    run_imported.step_calculate()
    metadata_df_b = run_imported.current_outputs[DataKey.METADATA_DF]
    assert metadata_df_a.shape == metadata_df_b.shape
    assert metadata_df_a.columns.tolist() == metadata_df_b.columns.tolist()
    assert metadata_df_a.equals(metadata_df_b)


@pytest.mark.skip(reason="Formerly commented out, needs reevaluation")
def test_metadata_column_assignment(run_empty):
    run_empty.step_add(MetadataImport())
    run_empty.step_next()
    run_empty.current_form(
        {
            "file_path": f"{TEST_METADATA_PATH}/metadata_cut_columns.csv",
            "feature_orientation": "Columns (samples in rows, features in columns)",
            "separator": Separators.comma.value,
        }
    )
    run_empty.step_calculate()
    assert (
        run_empty.current_outputs[DataKey.METADATA_DF] is not None
        and not run_empty.current_outputs[DataKey.METADATA_DF].empty
    )
    assert "Sample" in run_empty.current_outputs[DataKey.METADATA_DF].columns
    run_empty.step_add(MetadataColumnAssignment())
    run_empty.step_next()
    run_empty.current_form(
        {
            "metadata_required_column": "Sample_renamed",
            "metadata_unknown_column": "Sample",
        }
    )
    run_empty.step_calculate()
    assert (
        "Sample_renamed"
        in run_empty.steps.get_step_output(
            Step, DataKey.METADATA_DF, include_current_step=True
        ).columns
    )
    run_empty.current_form(
        {
            "metadata_required_column": "Sample",
            "metadata_unknown_column": "Sample_renamed",
        }
    )
    run_empty.step_calculate()
    assert (
        "Sample"
        in run_empty.steps.get_step_output(
            Step, DataKey.METADATA_DF, include_current_step=True
        ).columns
    )
