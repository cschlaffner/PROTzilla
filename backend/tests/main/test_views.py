from django.urls import reverse
from backend.tests.paths import TEST_WORKFLOWS_PATH, TEST_RUNS_PATH
import json

   
def test_get_all_steps(client):
    expected_step_names = [
        "MaxQuantImport", 
        "DiannImport", 
        "MsFraggerImport", 
        "MetadataImport", 
        "MetadataImportMethodDiann", 
        "MetadataColumnAssignment", 
        "PeptideImport", 
        "EvidenceImport", 
        "FilterProteinsBySamplesMissing", 
        "FilterByProteinsCount", 
        "FilterSamplesByProteinsMissing", 
        "FilterSamplesByProteinIntensitiesSum", 
        "OutlierDetectionByPCA", 
        "OutlierDetectionByLocalOutlierFactor", 
        "OutlierDetectionByIsolationForest", 
        "TransformationLog", 
        "NormalisationByZScore", 
        "NormalisationByTotalSum", 
        "NormalisationByMedian", 
        "NormalisationByReferenceProtein", 
        "ImputationByMinPerDataset", 
        "ImputationByMinPerProtein", 
        "SimpleImputationPerProtein", 
        "ImputationByKNN", 
        "ImputationByNormalDistributionSampling", 
        "FilterPeptidesByPEPThreshold", 
        "DifferentialExpressionANOVA", 
        "DifferentialExpressionTTest", 
        "DifferentialExpressionLinearModel", 
        "DifferentialExpressionMannWhitneyOnIntensity", 
        "DifferentialExpressionMannWhitneyOnPTM", 
        "DifferentialExpressionKruskalWallisOnIntensity", 
        "DifferentialExpressionKruskalWallisOnPTM", 
        "PlotVolcano", 
        "PlotScatterPlot", 
        "PlotClustergram", 
        "PlotProtQuant", 
        "PlotPrecisionRecallCurve", 
        "PlotROC", 
        "ClusteringKMeans", 
        "ClusteringExpectationMaximisation", 
        "ClusteringHierarchicalAgglomerative", 
        "ClassificationRandomForest", 
        "ClassificationSVM", 
        "ModelEvaluationClassificationModel", 
        "DimensionReductionTSNE", 
        "DimensionReductionUMAP", 
        "ProteinGraphPeptidesToIsoform", 
        "ProteinGraphVariationGraph", 
        "SelectPeptidesForProtein", 
        "FLEXIQuantLF", 
        "PTMsPerSample", 
        "PTMsProteinAndPerSample", 
        "ImputationByMinPerSample", 
        "EnrichmentAnalysisGOAnalysisWithString", 
        "EnrichmentAnalysisGOAnalysisWithEnrichr", 
        "EnrichmentAnalysisGOAnalysisOffline", 
        "EnrichmentAnalysisWithGSEA", 
        "EnrichmentAnalysisWithPrerankedGSEA", 
        "DatabaseIntegrationByGeneMapping", 
        "DatabaseIntegrationByUniprot", 
        "PlotGOEnrichmentBarPlot", 
        "PlotGOEnrichmentDotPlot", 
        "PlotGSEADotPlot", 
        "PlotGSEAEnrichmentPlot"
    ]

    response = client.get(reverse("step_list"))
    assert (list(step["method_name"] for step in response.json()) == expected_step_names)


def test_workflow_name_list(client):

    expected_workflows = ['standard', 'example_workflow', 'only_import', 'only_import_and_filter_proteins', 'test-run-empty', 'example_workflow_short']

    response = client.get(reverse("workflow_name_list"))
    assert(sorted(response.json()) == sorted(expected_workflows))


def test_add_run(client, static_run_name):
    parameters_valid = {
        "run_name": static_run_name,
        "workflow_name": "standard",
        "memory_mode": "standard"
    }
    parameters_faulty = {
        "run_name": f"not_existing_{static_run_name}",
        "workflow_name": "nonexistent",
        "memory_mode": "nonexistent"
    }
    response = client.post(
                reverse("add_run"),
                data=json.dumps(parameters_valid),
                content_type="application/json"
                )
    assert response.json()["success"]
    assert (TEST_RUNS_PATH / static_run_name).exists()

    response = client.post(
                reverse("add_run"),
                data=json.dumps(parameters_faulty),
                content_type="application/json"
                )
    assert not response.json()["success"]
    assert not (TEST_RUNS_PATH / f"not_existing_{static_run_name}").exists()


def test_run_information_list(client, static_run_name):
    expectedData = {'run_name': static_run_name, 'creation_date': '2025-06-12 14:37:59', 'modification_date': '2025-06-12 14:37:59', 'memory_mode': 'disk', 'run_steps': ['MaxQuant Protein Groups Import', 'Metadata Import', 'By samples missing', 'Sum of intensities', 'kNN', 'Local outlier factor', 'Log', 'Median', 'Protein Quantification Plot', 't-Test', 'Volcano Plot', 'GO analysis with STRING', 'Bar plot for GO enrichment analysis'], 'favourite_status': False, 'run_tags': []}
    
    response = client.get(reverse("run_information"))
    data = response.json()["data"]
    run_data = data[0][0]
    tag_data = data[1]

    assert response.json()["success"]
    assert tag_data == []

    for key, value in expectedData.items():
        if "date" in key:
            assert key in run_data and run_data[key] is not None
        else:
            assert value == run_data[key]

    
def test_add_tag(client, static_run_name):
    parameters = {
        "run_name": static_run_name,
        "tag_name": "random_tag"
    }
    response = client.post(
        reverse("add_tag"),
        data=json.dumps(parameters),
        content_type="application/json"
    )

    assert response.json()["success"]
    tag_data = client.get(reverse("run_information")).json()["data"][1]
    assert tag_data == ["random_tag"]


def test_delete_tag(client, static_run_name):
    parameters = {
        "run_name": static_run_name,
        "tag_name": "random_tag"
    }
    response = client.post(
        reverse("delete_tag"),
        data=json.dumps(parameters),
        content_type="application/json"
    )

    assert response.json()["success"]
    tag_data = client.get(reverse("run_information")).json()["data"][1]
    assert tag_data == []


def test_toggle_favourite(client, static_run_name):
    parameters = {
        "run_name": static_run_name
    }

    response = client.post(
        reverse("toggle_favourite"),
        data=json.dumps(parameters),
        content_type="application/json"
    )
    assert response.json()["success"]
    data = client.get(reverse("run_information")).json()["data"][0][0]
    assert data["favourite_status"]

    response = client.post(
        reverse("toggle_favourite"),
        data=json.dumps(parameters),
        content_type="application/json"
    )
    assert response.json()["success"]
    data = client.get(reverse("run_information")).json()["data"][0][0]
    assert not data["favourite_status"]


def test_continue_run(client, static_run_name):
    parameters = {
        "run_name": static_run_name
    }

    response = client.post(
        reverse("continue_run"),
        data=json.dumps(parameters),
        content_type="application/json"
    )
    assert response.json()["success"]


def test_update_run_name(client, static_run_name, run_name):
    parameters = {
        "run_name": static_run_name,
        "new_run_name": run_name
    }

    response = client.post(
        reverse("update_run_name"),
        data=json.dumps(parameters),
        content_type="application/json"
    )
    assert response.json()["success"]
    new_run_name = client.get(reverse("run_information")).json()["data"][0][0]["run_name"]
    assert new_run_name == run_name
    parameters = {
        "run_name": run_name,
        "new_run_name": static_run_name
    }

    response = client.post(
        reverse("update_run_name"),
        data=json.dumps(parameters),
        content_type="application/json"
    )
    assert response.json()["success"]
    new_run_name = client.get(reverse("run_information")).json()["data"][0][0]["run_name"]
    print(new_run_name)
    assert new_run_name == static_run_name


def test_delete_run(client, static_run_name):
    parameters = {
        "run_name": static_run_name
    }
    data = client.get(reverse("run_information")).json()["data"]
    response = client.post(
        reverse("delete_run"),
        data=json.dumps(parameters),
        content_type="application/json"
    )
    assert response.json()["success"]
    data = client.get(reverse("run_information")).json()["data"][0]
    assert data == []