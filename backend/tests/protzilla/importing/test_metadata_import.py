import pandas as pd

from backend.protzilla.constants.paths import BACKEND_PATH # TODO S change paths in whole file
from backend.protzilla.methods.importing import (
    DiannImport,
    MetadataColumnAssignment,
    MetadataImport,
    MetadataImportMethodDiann,
)
from backend.protzilla.steps import Step


def test_metadata_import(run_imported):
    run_imported.step_add(MetadataImport())
    run_imported.step_next()
    run_imported.current_form(
        {
            "file_path": f"{BACKEND_PATH}/tests/metadata_cut_columns.csv",
            "feature_orientation": "Columns (samples in rows, features in columns)",
        }
    )
    run_imported.step_calculate()
    test_metadata = pd.read_csv(f"{BACKEND_PATH}/tests/metadata_cut_columns.csv")
    pd.testing.assert_frame_equal(
        test_metadata, run_imported.current_outputs["metadata_df"]
    )

# TODO: This test is failing because there is no form for this import yet, uncomment as soon as the form is defined!!!

# def test_metadata_import_diann(run_empty):
#     run_empty.step_add(DiannImport())
#     run_empty.current_form(
#         {
#             "file_path": f"{BACKEND_PATH}/tests/test_data/DIANN_data/20230605 24h prodi DMSO report.pg_matrix.tsv",
#             "map_to_uniprot": "False",
#             "aggregation_method": "Sum",
#         }
#     )
#     run_empty.step_calculate()
#     assert (
#         run_empty.current_outputs["protein_df"] is not None
#     ), "DIA-NN MS data import failed."
#     assert not run_empty.current_outputs[
#         "protein_df"
#     ].empty, "DIA-NN MS data import failed."
#     run_empty.step_add(MetadataImportMethodDiann())
#     run_empty.step_next()
#     run_empty.current_form(
#         {
#             "file_path": f"{BACKEND_PATH}/tests/test_data/DIANN_data/sample run relationship.xlsx",
#             "groupby_sample": True,
#         }
#     )
#     run_empty.step_calculate()
#     test_metadata = pd.read_csv(
#         f"{BACKEND_PATH}/tests/test_data/DIANN_data/correct_metadata_table.csv"
#     )
#     test_protein_df = pd.read_csv(
#         f"{BACKEND_PATH}/tests/test_data/DIANN_data/correct_protein_df.csv"
#     )
#     pd.testing.assert_frame_equal(
#         test_metadata, run_empty.current_outputs["metadata_df"]
#     )
#     pd.testing.assert_frame_equal(
#         test_protein_df, run_empty.steps.get_step_output(DiannImport, "protein_df")
#     )


def test_metadata_orientation(run_empty):
    run_empty.step_add(MetadataImport())
    run_empty.step_next()
    run_empty.current_form(
        {
            "file_path": f"{BACKEND_PATH}/tests/metadata_cut_columns.csv",
            "feature_orientation": "Columns (samples in rows, features in columns)",
        }
    )
    run_empty.step_calculate()
    metadata_df_a = run_empty.current_outputs["metadata_df"]
    run_empty.current_form(
        {
            "file_path": f"{BACKEND_PATH}/tests/metadata_cut_rows.csv",
            "feature_orientation": "Rows (samples in columns, features in rows)",
        }
    )
    run_empty.step_calculate()
    metadata_df_b = run_empty.current_outputs["metadata_df"]
    assert metadata_df_a.shape == metadata_df_b.shape
    assert metadata_df_a.columns.tolist() == metadata_df_b.columns.tolist()
    assert metadata_df_a.equals(metadata_df_b)

# TODO: This test is failing because there is no form for this import yet, uncomment as soon as the form is defined!!!

# def test_metadata_column_assignment(run_empty):
#     run_empty.step_add(MetadataImport())
#     run_empty.step_next()
#     run_empty.current_form(
#         {
#             "file_path": f"{BACKEND_PATH}/tests/metadata_cut_columns.csv",
#             "feature_orientation": "Columns (samples in rows, features in columns)",
#         }
#     )
#     run_empty.step_calculate()
#     assert (
#         run_empty.current_outputs["metadata_df"] is not None
#         and not run_empty.current_outputs["metadata_df"].empty
#     )
#     assert "Sample" in run_empty.current_outputs["metadata_df"].columns
#     run_empty.step_add(MetadataColumnAssignment())
#     run_empty.step_next()
#     run_empty.current_form(
#         {
#             "metadata_required_column": "Sample_renamed",
#             "metadata_unknown_column": "Sample",
#         }
#     )
#     run_empty.step_calculate()
#     assert (
#         "Sample_renamed"
#         in run_empty.steps.get_step_output(
#             Step, "metadata_df", include_current_step=True
#         ).columns
#     )
#     run_empty.current_form(
#         {
#             "metadata_required_column": "Sample",
#             "metadata_unknown_column": "Sample_renamed",
#         }
#     )
#     run_empty.step_calculate()
#     assert (
#         "Sample"
#         in run_empty.steps.get_step_output(
#             Step, "metadata_df", include_current_step=True
#         ).columns
#     )
