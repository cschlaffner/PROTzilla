import json
import sys
from unittest import mock

import pytest

from backend.tests.paths import (
    TEST_MSDATA_PATH,
    TEST_METADATA_PATH,
    TEST_WORKFLOWS_PATH,
)
from backend.protzilla.utilities import random_string

from backend.protzilla.runner import Runner, _serialize_graphs
from runner_cli import args_parser
from backend.main import settings


@pytest.fixture
def ms_data_file_path():
    return "MaxQuant/proteinGroups_small_cut.txt"


@pytest.fixture
def metadata_file_path():
    return "metadata_cut_columns.csv"


def mock_perform_method(runner: Runner):
    mock_perform = mock.MagicMock()
    mock_perform.methods = []
    mock_perform.inputs = []

    def mock_current_parameters(*args, **kwargs):
        # saving parameters for later inspection
        mock_perform.methods.append(str(runner.run.current_step))
        mock_perform.inputs.append(runner.run.current_step.form_inputs)

        runner.run.current_step.calculation_status = "complete"

    mock_perform.side_effect = mock_current_parameters

    return mock_perform


def mock_perform_plot(runner: Runner):
    mock_plot = mock.MagicMock()
    mock_plot.inputs = []

    def mock_current_parameters(*args, **kwargs):
        # saving parameters for later inspection
        mock_plot.inputs.append(runner.run.current_step.plot_inputs)

    mock_plot.side_effect = mock_current_parameters

    return mock_plot


def test_runner_imports(
    monkeypatch, tests_folder_name, ms_data_file_path, metadata_file_path
):
    importing_args = [
        "standard",  # expects max-quant import, metadata import
        ms_data_file_path,
        f"--run_name={tests_folder_name}/test_runner_{random_string()}",
        f"--meta_data_path={metadata_file_path}",
    ]

    kwargs = args_parser().parse_args(importing_args).__dict__
    runner = Runner(**kwargs)

    mock_method = mock_perform_method(runner)
    monkeypatch.setattr(runner, "_perform_current_step", mock_method)
    mock_write = mock.MagicMock()
    monkeypatch.setattr(runner.run, "_run_write", mock_write)
    mock_plot_safe = mock.MagicMock()
    monkeypatch.setattr(runner, "_save_plots_html", mock_plot_safe)

    runner.compute_workflow()

    expected_methods = [
        "MaxQuantImport",
        "MetadataImport",
        "FilterProteinsBySamplesMissing",
        "FilterSamplesByProteinIntensitiesSum",
        "ImputationByKNN",
        "OutlierDetectionByLocalOutlierFactor",
        "TransformationLog",
        "NormalisationByMedian",
        "PlotProtQuant",
        "DifferentialExpressionTTest",
        "PlotVolcano",
        "EnrichmentAnalysisGOAnalysisWithString",
        "PlotGOEnrichmentBarPlot",
    ]
    expected_method_parameters = [
        {
            "file_path": (settings.FILE_UPLOAD_TEMP_DIR / ms_data_file_path),
            "intensity_name": "iBAQ",
            "map_to_uniprot": False,
            "aggregation_method": "Sum",
        },
        {
            "file_path": (settings.FILE_UPLOAD_TEMP_DIR / metadata_file_path),
            "feature_orientation": "Columns (samples in rows, features in columns)",
        },
        {"percentage": 0.5, "graph_type": "Pie chart"},
        {"deviation_threshold": 2.0, "graph_type": "Pie chart"},
        {
            "number_of_neighbours": 5,
            "graph_type": "Boxplot",
            "group_by": "None",
            "visual_transformation": "log10",
            "graph_type_quantities": "Pie chart",
        },
        {"number_of_neighbors": 20},
        {"log_base": "log2", "graph_type": "Boxplot", "group_by": "None"},
        {
            "percentile": 0.5,
            "graph_type": "Boxplot",
            "group_by": "None",
            "visual_transformation": "log10",
        },
        {
            "input_df": None,
            "protein_group": None,
            "similarity_measure": "euclidean distance",
            "similarity": 1,
        },
        {
            "ttest_type": "Welch's t-Test",
            "protein_df": None,
            "multiple_testing_correction_method": "Benjamini-Hochberg",
            "alpha": 0.05,
            "grouping": None,
            "group1": None,
            "group2": None,
        },
        {"input_dict": None, "fc_threshold": 1, "items_of_interest": []},
        {
            "proteins_df": None,
            "differential_expression_threshold": 0,
            "gene_sets_restring": [],
            "organism": 9606,
            "direction": "both",
            "background_path": None,
        },
        {
            "input_df_step_instance": None,
            "cutoff": 0.05,
            "gene_sets": ["Process", "Component", "Function", "KEGG"],
            "value": "p-value",
            "top_terms": 10,
            "title": "",
        },
    ]

    assert mock_method.call_count == 13
    assert mock_method.methods == expected_methods
    assert mock_method.inputs == expected_method_parameters


def test_runner_raises_error_for_missing_metadata_arg(
    monkeypatch, tests_folder_name, ms_data_file_path
):
    no_metadata_args = [
        "only_import",
        ms_data_file_path,
        f"--run_name={tests_folder_name}/test_runner_{random_string()}",
    ]
    kwargs = args_parser().parse_args(no_metadata_args).__dict__
    runner = Runner(**kwargs)
    mock_method = mock_perform_method(runner)

    monkeypatch.setattr(runner, "_perform_current_step", mock_method)

    with pytest.raises(ValueError) as e:
        runner.compute_workflow()


def test_runner_calculates(
    monkeypatch, tests_folder_name, ms_data_file_path, metadata_file_path
):
    calculating_args = [
        "only_import_and_filter_proteins",
        ms_data_file_path,
        f"--run_name={tests_folder_name}/test_runner_{random_string()}",
        f"--meta_data_path={metadata_file_path}",
    ]
    kwargs = args_parser().parse_args(calculating_args).__dict__
    runner = Runner(**kwargs)

    mock_method = mock_perform_method(runner)

    mock_plot = mock_perform_plot(runner)

    monkeypatch.setattr(runner, "_perform_current_step", mock_method)

    runner.compute_workflow()

    assert mock_method.call_count == 3
    assert mock_method.methods == [
        "MaxQuantImport",
        "MetadataImport",
        "FilterProteinsBySamplesMissing",
    ]
    assert mock_method.inputs == [
        {
            "file_path": (settings.FILE_UPLOAD_TEMP_DIR / ms_data_file_path),
            "intensity_name": "iBAQ",
            "map_to_uniprot": False,
            "aggregation_method": "Sum",
        },
        {
            "file_path": (settings.FILE_UPLOAD_TEMP_DIR / metadata_file_path),
            "feature_orientation": "Columns (samples in rows, features in columns)",
        },
        {"percentage": 0.5, "graph_type": "Pie chart"},
    ]
    mock_plot.assert_not_called()


def test_runner_calculates_logging(caplog, tests_folder_name):
    calculating_args = [
        "only_import_and_filter_proteins",
        "wrong_ms_data_file_path",
        f"--run_name={tests_folder_name}/test_runner_{random_string()}",
        f"--meta_data_path={metadata_file_path}",
    ]
    kwargs = args_parser().parse_args(calculating_args).__dict__
    runner = Runner(**kwargs)

    runner.compute_workflow()

    assert "ERROR" in caplog.text
    assert "FileNotFoundError" in caplog.text


def test_serialize_graphs():
    pre_graphs = [  # this is what the "graphs" section of a step should look like
        {"graph_type": "Bar chart", "group_by": "Sample"},
        {"graph_type_quantities": "Pie chart"},
    ]
    expected = {
        "graph_type": "Bar chart",
        "group_by": "Sample",
        "graph_type_quantities": "Pie chart",
    }
    assert _serialize_graphs(pre_graphs) == expected


def test_serialize_workflow_graphs():
    with open(TEST_WORKFLOWS_PATH / "example_workflow.json", "r") as f:
        workflow_config = json.load(f)

    serial_imputation_graphs = {
        "graph_type": "Bar chart",
        "group_by": "Sample",
        "graph_type_quantities": "Pie chart",
    }

    serial_filter_graphs = {"graph_type": "Pie chart"}

    steps = workflow_config["sections"]["data_preprocessing"]["steps"]
    for step in steps:
        if step["name"] == "imputation":
            assert _serialize_graphs(step["graphs"]) == serial_imputation_graphs
        elif step["name"] == "filter_proteins":
            assert _serialize_graphs(step["graphs"]) == serial_filter_graphs


def test_integration_runner(
    metadata_file_path, ms_data_file_path, tests_folder_name, monkeypatch
):
    name = tests_folder_name + "/test_runner_integration_" + random_string()
    print("ADBLHBSFHLB: ", f"{TEST_MSDATA_PATH}/{ms_data_file_path}")
    runner = Runner(
        **{
            "workflow": "standard",
            "ms_data_path": f"{TEST_MSDATA_PATH}/{ms_data_file_path}",
            "meta_data_path": f"{TEST_METADATA_PATH}/{metadata_file_path}",
            "peptides_path": None,
            "run_name": f"{name}",
            "df_mode": "disk",
            "all_plots": True,
            "verbose": False,
        }
    )
    mock_write = mock.MagicMock()
    monkeypatch.setattr(runner.run, "_run_write", mock_write)
    mock_plot_safe = mock.MagicMock()
    monkeypatch.setattr(runner, "_save_plots_html", mock_plot_safe)
    runner.compute_workflow()


def test_integration_runner_no_plots(
    metadata_file_path, ms_data_file_path, tests_folder_name, monkeypatch
):
    name = tests_folder_name + "/test_runner_integration" + random_string()
    runner = Runner(
        **{
            "workflow": "standard",
            "ms_data_path": f"{TEST_MSDATA_PATH}/{ms_data_file_path}",
            "meta_data_path": f"{TEST_METADATA_PATH}/{metadata_file_path}",
            "peptides_path": None,
            "run_name": f"{name}",
            "df_mode": "disk",
            "all_plots": False,
            "verbose": False,
        }
    )
    mock_write = mock.MagicMock()
    monkeypatch.setattr(runner.run, "_run_write", mock_write)
    runner.compute_workflow()
