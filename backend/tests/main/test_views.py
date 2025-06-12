from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from backend.tests.paths import TEST_WORKFLOWS_PATH, TEST_RUNS_PATH

class RunViewsTests(TestCase):
    
    def test_get_all_steps(self):
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
    
        response = self.client.get(reverse("step_list"))
        self.assertEqual(list(step["method_name"] for step in response.json()),expected_step_names)
    
    def test_workflow_name_list(self):

        expected_workflows = ['standard', 'example_workflow', 'only_import', 'only_import_and_filter_proteins', 'test-run-empty', 'example_workflow_short']

        response = self.client.get(reverse("workflow_name_list"))
        print(response.json())
        self.assertEqual(sorted(response.json()),sorted(expected_workflows))

    def test_add_run(self):
        parameters = {
            "run_name": "test_run",
            "workflow_name": "standard",
            "memory_mode": "standard"
        }
        response = self.client.get(reverse("add_run"),data=parameters)
    # def test_run_information_list(self):
    #     with patch("backend.protzilla.constants.paths.RUNS_PATH", TEST_RUNS_PATH):
    #         response = self.client.get(reverse("run_information"))
    #     print(response.json())
    #     self.assertTrue(response.json()["success"])
    #     assert False