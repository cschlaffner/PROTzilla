import json
import shutil
from pathlib import Path
from unittest import mock

import pytest

from backend.main import settings
from backend.protzilla.runner import _serialize_graphs
from backend.protzilla.utilities import random_string
from backend.tests.paths import (
    TEST_MSDATA_PATH,
    TEST_METADATA_PATH,
    TEST_WORKFLOWS_PATH,
)
from backend.protzilla import disk_operator
from backend.protzilla.runner import Runner
from runner_cli import args_parser


@pytest.fixture
def ms_data_file_path():
    return "MaxQuant/proteinGroups_medium_cut.txt"


@pytest.fixture
def metadata_file_path():
    return "metadata_full.csv"


@pytest.fixture()
def tmp_workflow_dir(tmp_path_factory):
    test_tmp_data_dir = Path("workflows/")
    tmp_path = tmp_path_factory.mktemp(str(test_tmp_data_dir))
    return tmp_path


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


def find_step_by_class_name(runner: Runner, class_name: str):
    return next(
        i
        for i, step in enumerate(runner.run.steps.all_steps)
        if step.__class__.__name__ == class_name
    )


def set_step_field_value(runner: Runner, step_idx: int, field_name: str, value):
    field = next(
        f
        for f in runner.run.steps.all_steps[step_idx].form.input_fields
        if f.name == field_name
    )
    field.value = value


def configure_step_fields(runner: Runner, class_name: str, field_values: dict):
    """Find a step by class name and set multiple field values."""
    step_idx = find_step_by_class_name(runner, class_name)
    for field_name, value in field_values.items():
        set_step_field_value(runner, step_idx, field_name, value)
    return step_idx


def prepare_standard_workflow_runner(runner: Runner):
    """
    The standard workflow does not specify out some of the configurable fields because it is a general purpose workflow
    that does not know the specifics of the data, e.g. group names for differential expression. In an interactive
    setting, these fields would be initialized automatically, but in this test setting we need to set them manually.
    One could argue that it would be better to have a mock workflow for MaxQuant data (just like for the other data
    types), but I kept it this way to also have a way to somewhat test the actual standard workflow that is used by
    the frontend.
    """
    prot_quant_idx = find_step_by_class_name(runner, "PlotProtQuant")
    configure_step_fields(
        runner,
        "PlotProtQuant",
        {
            "input_df": runner.run.steps.all_steps[
                prot_quant_idx - 1
            ].instance_identifier,
            "protein_group": "P10636",
        },
    )

    ttest_idx = configure_step_fields(
        runner,
        "DifferentialExpressionTTest",
        {"grouping": "Group", "group1": "AD", "group2": "CTR"},
    )

    # Configure volcano plot to use t-test results
    configure_step_fields(
        runner,
        "PlotVolcano",
        {"input_dict": runner.run.steps.all_steps[ttest_idx].instance_identifier},
    )

    # Configure GO enrichment analysis to use t-test results
    go_idx = configure_step_fields(
        runner,
        "EnrichmentAnalysisGOAnalysisWithString",
        {
            "proteins_df": runner.run.steps.all_steps[ttest_idx].instance_identifier,
        },
    )

    # Configure GO enrichment bar plot to use GO analysis results
    configure_step_fields(
        runner,
        "PlotGOEnrichmentBarPlot",
        {
            "input_df_step_instance": runner.run.steps.all_steps[
                go_idx
            ].instance_identifier
        },
    )


def assert_runner_finished_successfully(runner: Runner):
    assert all(
        step.calculation_status == "complete" for step in runner.run.steps.all_steps
    )
    assert runner.run.steps.all_steps[-1] == runner.run.current_step
    assert (
        all(step.finished for step in runner.run.steps.all_steps)
        and not runner.run.current_step.messages
        and "messages" not in runner.run.current_step.output
    )


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
            "ignore_only_identified_by_site": False,
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
            "protein_df_field": None,
            "protein_group": None,
            "similarity_measure": "euclidean distance",
            "similarity": 1,
        },
        {
            "ttest_type": "Welch's t-Test",
            "protein_df_field": None,
            "multiple_testing_correction_method": "Benjamini-Hochberg",
            "alpha": 0.05,
            "grouping": None,
            "group1": None,
            "group2": None,
            "fc_zscore_filter": False,
            "fc_zscore_alpha": 0.05,
        },
        {"input_dict": None, "fc_threshold": 1, "items_of_interest": []},
        {
            "protein_df_field": None,
            "differential_expression_threshold": 0,
            "gene_sets_restring": [],
            "organism": 9606,
            "direction": "both",
            "background_path": None,
        },
        {
            "input_df_field": None,
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
            "ignore_only_identified_by_site": False,
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
            "df_mode": "memory",
            "all_plots": True,
            "verbose": False,
        }
    )
    prepare_standard_workflow_runner(runner)

    mock_write = mock.MagicMock()
    monkeypatch.setattr(runner.run, "_run_write", mock_write)
    mock_plot_safe = mock.MagicMock()
    monkeypatch.setattr(runner, "_save_plots_html", mock_plot_safe)
    runner.compute_workflow()
    assert_runner_finished_successfully(runner)


@pytest.mark.parametrize(
    "mock_workflow,ms_data_file_path,metadata_file_path",
    [
        (
            "MSFragger_Standard",
            "MSFragger/combined_protein_runner_test.tsv",
            "MSFragger/metadata_runner_test.csv",
        ),
        (
            "DIA-NN_Standard",
            "DIANN/20230605_24h_prodi_DMSO_report.pg_matrix.tsv",
            "DIANN/meta.csv",
        ),
    ],
)
def test_integration_runner_non_maxquant(
    mock_workflow,
    metadata_file_path,
    ms_data_file_path,
    tmp_workflow_dir,
    tests_folder_name,
    monkeypatch,
):
    name = tests_folder_name + "/test_runner_integration_" + random_string()

    standard_workflow_file = TEST_WORKFLOWS_PATH / f"{mock_workflow}.yaml"
    shutil.copy(standard_workflow_file, tmp_workflow_dir)
    with mock.patch.object(
        disk_operator.paths, "WORKFLOWS_PATH", tmp_workflow_dir.resolve()
    ):
        runner = Runner(
            workflow=mock_workflow,
            ms_data_path=f"{TEST_MSDATA_PATH}/{ms_data_file_path}",
            meta_data_path=f"{TEST_METADATA_PATH}/{metadata_file_path}",
            peptides_path=None,
            run_name=f"{name}",
            df_mode="memory",
            all_plots=True,
            verbose=False,
        )

        mock_write = mock.MagicMock()
        monkeypatch.setattr(runner.run, "_run_write", mock_write)
        mock_plot_safe = mock.MagicMock()
        monkeypatch.setattr(runner, "_save_plots_html", mock_plot_safe)
        runner.compute_workflow()
        assert_runner_finished_successfully(runner)


def test_integration_runner_no_plots(
    metadata_file_path, ms_data_file_path, tests_folder_name, monkeypatch
):
    name = tests_folder_name + "/test_runner_integration" + random_string()
    runner = Runner(
        workflow="standard",
        ms_data_path=f"{TEST_MSDATA_PATH}/{ms_data_file_path}",
        meta_data_path=f"{TEST_METADATA_PATH}/{metadata_file_path}",
        peptides_path=None,
        run_name=f"{name}",
        df_mode="memory",
        all_plots=False,
        verbose=False,
    )
    prepare_standard_workflow_runner(runner)

    mock_write = mock.MagicMock()
    monkeypatch.setattr(runner.run, "_run_write", mock_write)
    runner.compute_workflow()
    assert_runner_finished_successfully(runner)
