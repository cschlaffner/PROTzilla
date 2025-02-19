# THIS IS A WORKAROUND; NEEDS TO BE ADAPTED
"""
Wir hatten bisher eine form_mapping.py Datei, die definiert, was die Forms sind, die das backend erwartet, da drin auch ein dictionary was genau dokumentiert, was die methoden sind, die wir haben.
Das ist zu ändern, da wir sonst immer in dieser Liste die steps verwalten müssen - code smell...
Aber wo die Forms dann hinsollen bzw ihre Logik, sodass das frontend und backend darüber richtig kommunizieren können, ist wichtig zu klären!!

"""

import backend.protzilla.methods.data_analysis as data_analysis
import backend.protzilla.methods.data_integration as data_integration
import backend.protzilla.methods.data_preprocessing as data_preprocessing
import backend.protzilla.methods.importing as importing

_forward_mapping = [
    importing.MaxQuantImport,
    importing.DiannImport,
    importing.MsFraggerImport,
    importing.MetadataImport,
    importing.MetadataImportMethodDiann,
    importing.MetadataColumnAssignment,
    importing.PeptideImport,
    importing.EvidenceImport,
    data_preprocessing.FilterProteinsBySamplesMissing,
    data_preprocessing.FilterByProteinsCount,
    data_preprocessing.FilterSamplesByProteinsMissing,
    data_preprocessing.FilterSamplesByProteinIntensitiesSum,
    data_preprocessing.OutlierDetectionByPCA,
    data_preprocessing.OutlierDetectionByLocalOutlierFactor,
    data_preprocessing.OutlierDetectionByIsolationForest,
    data_preprocessing.TransformationLog,
    data_preprocessing.NormalisationByZScore,
    data_preprocessing.NormalisationByTotalSum,
    data_preprocessing.NormalisationByMedian,
    data_preprocessing.NormalisationByReferenceProtein,
    data_preprocessing.ImputationByMinPerDataset,
    data_preprocessing.ImputationByMinPerProtein,
    data_preprocessing.SimpleImputationPerProtein,
    data_preprocessing.ImputationByKNN,
    data_preprocessing.ImputationByNormalDistributionSampling,
    data_preprocessing.FilterPeptidesByPEPThreshold,
    data_analysis.DifferentialExpressionANOVA,
    data_analysis.DifferentialExpressionTTest,
    data_analysis.DifferentialExpressionLinearModel,
    data_analysis.DifferentialExpressionMannWhitneyOnIntensity,
    data_analysis.DifferentialExpressionMannWhitneyOnPTM,
    data_analysis.DifferentialExpressionKruskalWallisOnIntensity,
    data_analysis.DifferentialExpressionKruskalWallisOnPTM,
    data_analysis.PlotVolcano,
    data_analysis.PlotScatterPlot,
    data_analysis.PlotClustergram,
    data_analysis.PlotProtQuant,
    data_analysis.PlotPrecisionRecallCurve,
    data_analysis.PlotROC,
    data_analysis.ClusteringKMeans,
    data_analysis.ClusteringExpectationMaximisation,
    data_analysis.ClusteringHierarchicalAgglomerative,
    data_analysis.ClassificationRandomForest,
    data_analysis.ClassificationSVM,
    data_analysis.ModelEvaluationClassificationModel,
    data_analysis.DimensionReductionTSNE,
    data_analysis.DimensionReductionUMAP,
    data_analysis.ProteinGraphPeptidesToIsoform,
    data_analysis.ProteinGraphVariationGraph,
    data_analysis.SelectPeptidesForProtein,
    data_analysis.FLEXIQuantLF,
    data_analysis.PTMsPerSample,
    data_analysis.PTMsProteinAndPerSample,
    data_preprocessing.ImputationByMinPerSample,
    data_integration.EnrichmentAnalysisGOAnalysisWithString,
    data_integration.EnrichmentAnalysisGOAnalysisWithEnrichr,
    data_integration.EnrichmentAnalysisGOAnalysisOffline,
    data_integration.EnrichmentAnalysisWithGSEA,
    data_integration.EnrichmentAnalysisWithPrerankedGSEA,
    data_integration.DatabaseIntegrationByGeneMapping,
    data_integration.DatabaseIntegrationByUniprot,
    data_integration.PlotGOEnrichmentBarPlot,
    data_integration.PlotGOEnrichmentDotPlot,
    data_integration.PlotGSEADotPlot,
    data_integration.PlotGSEAEnrichmentPlot,
]

def get_all_methods():
    return _forward_mapping