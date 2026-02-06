from __future__ import annotations
from abc import ABC

from backend.protzilla.data_preprocessing import (
    filter_proteins,
    filter_samples,
    imputation,
    normalisation,
    outlier_detection,
    peptide_filter,
    transformation,
)
from backend.protzilla import form_helper
from backend.protzilla.form import *
from backend.protzilla.steps import Step, StepManager, Section
from backend.protzilla.constants.option_types import *


class DataPreprocessingStep(Step, ABC):
    section = Section.DATA_PREPROCESSING
    output_keys = ["protein_df"]

    plot_input_names = ["protein_df"]
    plot_output_names = ["plots"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plot_inputs: dict = {}

    # def insert_dataframes(self, steps: StepManager) -> None:
    #     self.inputs["protein_df"] = steps.protein_df
    #     self.inputs["peptide_df"] = steps.get_step_output(output_key="peptide_df")


class FilterProteinsBySamplesMissing(DataPreprocessingStep):
    display_name = "By samples missing"
    operation = "filter_proteins"
    method_description = (
        "Filter proteins based on the amount of samples with nan values"
    )

    def create_form(self):
        return Form(
            label="Filter Proteins by Samples Missing",
            input_fields=[
                FloatField(
                    name="percentage",
                    label="Percentage of minimum non-missing samples per protein",
                    value=0.5,
                    min=0,
                    max=1,
                    step=0.1,
                ),
                DropdownField(
                    name="graph_type",
                    label="Graph type",
                    value=BarAndPieChart.PIE_CHART.value,
                    options=BarAndPieChart,
                ),
            ],
        )

    calc_method = staticmethod(filter_proteins.by_samples_missing)
    plot_method = staticmethod(filter_proteins.by_samples_missing_plot)


class FilterProteinsBySilacRatios(DataPreprocessingStep):
    display_name = "By SILAC ratios"
    operation = "filter_proteins"
    method_description = "Filter proteins based on the minimum amount of samples with different SILAC ratios in each group"

    def create_form(self):
        return Form(
            label="Filter Proteins by SILAC ratios",
            input_fields=[
                NumberField(
                    name="min_amount",
                    label="Amount of minimum present samples per group with different SILAC ratios",
                    value=1,
                    min=0,
                    step=1,
                ),
                DropdownField(
                    name="graph_type",
                    label="Graph type",
                    value=BarAndPieChart.PIE_CHART.value,
                    options=BarAndPieChart,
                ),
            ],
        )

    # def insert_dataframes(self, steps: StepManager, inputs: dict) -> dict:
    #     inputs["protein_df"] = steps.protein_df
    #     inputs["peptide_df"] = steps.get_step_output(Step, "peptide_df")
    #     inputs["metadata_df"] = steps.get_step_output(Step, "metadata_df")
    #     return inputs

    calc_method = staticmethod(filter_proteins.by_silac_ratios)
    plot_method = staticmethod(filter_proteins.by_silac_ratios_plot)


class FilterByProteinsCount(DataPreprocessingStep):
    display_name = "Protein Count"
    operation = "filter_samples"
    method_description = "Filter by protein count per sample"

    def create_form(self):
        return Form(
            label="Filter Samples by Protein Count",
            input_fields=[
                FloatField(
                    name="deviation_threshold",
                    label="Number of standard deviations from the median",
                    value=2,
                    min=0,
                    step=0.5,
                    hasStepButtons=True,
                    separatePrefix="\u03c3",
                ),
                DropdownField(
                    name="graph_type",
                    label="Graph type",
                    value=BarAndPieChart.PIE_CHART.value,
                    options=BarAndPieChart,
                ),
            ],
        )

    calc_method = staticmethod(filter_samples.by_protein_count)
    plot_method = staticmethod(filter_samples.by_protein_count_plot)


class FilterPeptidesByPEPThreshold(DataPreprocessingStep):
    display_name = "PEP threshold"
    operation = "filter_peptides"
    method_description = "Filter by PEP-threshold"
    output_keys = ["peptide_df", "filtered_peptides"]

    def create_form(self):
        return Form(
            label="Filter peptides by PEP threshold",
            input_fields=[
                FloatField(
                    name="threshold",
                    label="Threshold value for PEP",
                    value=0,
                    min=0,
                    max=1,
                    step=0.1,
                    hasStepButtons=True,
                ),
                DropdownField(
                    name="peptide_df",
                    label="peptide_df",
                    options=EmptyEnum,
                ),
                DropdownField(
                    name="graph_type",
                    label="Graph type",
                    value=BarAndPieChart.PIE_CHART.value,
                    options=BarAndPieChart,
                ),
            ],
        )

    calc_method = staticmethod(peptide_filter.by_pep_value)
    plot_method = staticmethod(peptide_filter.by_pep_value_plot)

    def modify_form(self, form, run):
        peptide_df_field = form["peptide_df"]
        peptide_df_field.set_options(form_helper.get_choices(run, "peptide_df"))


class FilterSamplesByProteinsMissing(DataPreprocessingStep):
    display_name = "By proteins missing"
    operation = "filter_samples"
    method_description = (
        "Filter samples based on the amount of proteins with nan values"
    )

    def create_form(self):
        return Form(
            label="Filter Samples by Proteins Missing",
            input_fields=[
                FloatField(
                    name="percentage",
                    label="Percentage of minimum non-missing proteins per sample",
                    value=0.5,
                    min=0,
                    max=1,
                    step=0.1,
                ),
                DropdownField(
                    name="graph_type",
                    label="Graph type",
                    value=BarAndPieChart.PIE_CHART.value,
                    options=BarAndPieChart,
                ),
            ],
        )

    calc_method = staticmethod(filter_samples.by_proteins_missing)
    plot_method = staticmethod(filter_samples.by_proteins_missing_plot)


class FilterSamplesByProteinIntensitiesSum(DataPreprocessingStep):
    display_name = "Sum of intensities"
    operation = "filter_samples"
    method_description = "Filter by sum of protein intensities per sample"

    def create_form(self):
        return Form(
            label="Filter Samples by Protein Intensity Sum",
            input_fields=[
                FloatField(
                    name="deviation_threshold",
                    label="Number of standard deviations from the median",
                    value=2,
                    min=0,
                    step=0.5,
                    hasStepButtons=True,
                    separatePrefix="\u03c3",
                ),
                DropdownField(
                    name="graph_type",
                    label="Graph type",
                    value=BarAndPieChart.PIE_CHART.value,
                    options=BarAndPieChart,
                ),
            ],
        )

    calc_method = staticmethod(filter_samples.by_protein_intensity_sum)
    plot_method = staticmethod(filter_samples.by_protein_intensity_sum_plot)


class OutlierDetectionByPCA(DataPreprocessingStep):
    display_name = "PCA"
    operation = "outlier_detection"
    method_description = "Detect outliers using PCA"

    def create_form(self):
        return Form(
            label="Outlier Detection by PCA",
            input_fields=[
                FloatField(
                    name="threshold",
                    label="Threshold for number of standard deviations from the median:",
                    value=2,
                    min=0,
                    step=0.5,
                    hasStepButtons=True,
                ),
                NumberField(
                    name="number_of_components",
                    label="Number of components",
                    value=3,
                    min=2,
                    max=3,
                    step=1,
                    hasStepButtons=True,
                ),
            ],
        )

    calc_method = staticmethod(outlier_detection.by_pca)
    plot_method = staticmethod(outlier_detection.by_pca_plot)


class OutlierDetectionByLocalOutlierFactor(DataPreprocessingStep):
    display_name = "Local outlier factor"
    operation = "outlier_detection"
    method_description = "Detect outliers using the local outlier factor"

    def create_form(self):
        return Form(
            label="Outlier Detection by Local Outlier Factor",
            input_fields=[
                NumberField(
                    name="number_of_neighbors",
                    label="Number of neighbors",
                    value=20,
                    min=1,
                    step=1,
                    hasStepButtons=True,
                ),
            ],
        )

    calc_method = staticmethod(outlier_detection.by_local_outlier_factor)
    plot_method = staticmethod(outlier_detection.by_local_outlier_factor_plot)


class OutlierDetectionByIsolationForest(DataPreprocessingStep):
    display_name = "Isolation Forest"
    operation = "outlier_detection"
    method_description = "Detect outliers using Isolation Forest"

    def create_form(self):
        return Form(
            label="Outlier Detection by Isolation Forest",
            input_fields=[
                NumberField(
                    name="n_estimators",
                    label="Number of estimators",
                    value=100,
                    min=1,
                    step=1,
                    hasStepButtons=True,
                ),
            ],
        )

    calc_method = staticmethod(outlier_detection.by_isolation_forest)
    plot_method = staticmethod(outlier_detection.by_isolation_forest_plot)


class TransformationLog(DataPreprocessingStep):
    display_name = "Log"
    operation = "transformation"
    method_description = "Transform data by log"

    def create_form(self):
        return Form(
            label="Log Transformation",
            input_fields=[
                DropdownField(
                    name="log_base",
                    label="Log transformation base",
                    value=LogTransformationBaseType.LOG2.value,
                    options=LogTransformationBaseType,
                ),
                FormDivider("Plot settings"),
                DropdownField(
                    name="graph_type",
                    label="Graph type",
                    value=BoxAndHistogramGraph.BOXPLOT.value,
                    options=BoxAndHistogramGraph,
                ),
                DropdownField(
                    name="group_by",
                    label="Group by",
                    value=GroupBy.NO_GROUPING.value,
                    options=GroupBy,
                ),
            ],
        )

    calc_method = staticmethod(transformation.by_log)
    plot_method = staticmethod(transformation.by_log_plot)


class TransformationInversion(DataPreprocessingStep):
    display_name = "Inversion"
    operation = "transformation"
    method_description = "Transform data by inversion"

    def create_form(self):
        return Form(
            label="Data Inversion Transformation",
            input_fields=[],
        )

    calc_method = staticmethod(transformation.by_inversion)


class NormalisationByZScore(DataPreprocessingStep):
    display_name = "Z-Score"
    operation = "normalisation"
    method_description = "Normalise data by Z-Score"

    def create_form(self):
        return Form(
            label="Normalisation by Z-Score",
            input_fields=[
                DropdownField(
                    name="graph_type",
                    label="Graph type",
                    value=BoxAndHistogramGraph.BOXPLOT.value,
                    options=BoxAndHistogramGraph,
                ),
                DropdownField(
                    name="group_by",
                    label="Group by",
                    value=GroupBy.NO_GROUPING.value,
                    options=GroupBy,
                ),
                DropdownField(
                    name="visual_transformation",
                    label="Visual transformation",
                    value=VisualTransformations.LOG10.value,
                    options=VisualTransformations,
                ),
            ],
        )

    calc_method = staticmethod(normalisation.by_z_score)
    plot_method = staticmethod(normalisation.by_z_score_plot)


class NormalisationByTotalSum(DataPreprocessingStep):
    display_name = "Total sum"
    operation = "normalisation"
    method_description = "Normalise data by total sum"

    def create_form(self):
        return Form(
            label="Normalisation by total sum",
            input_fields=[
                DropdownField(
                    name="graph_type",
                    label="Graph type",
                    value=BoxAndHistogramGraph.BOXPLOT.value,
                    options=BoxAndHistogramGraph,
                ),
                DropdownField(
                    name="group_by",
                    label="Group by",
                    value=GroupBy.NO_GROUPING.value,
                    options=GroupBy,
                ),
                DropdownField(
                    name="visual_transformation",
                    label="Visual transformation",
                    value=VisualTransformations.LOG10.value,
                    options=VisualTransformations,
                ),
            ],
        )

    calc_method = staticmethod(normalisation.by_totalsum)
    plot_method = staticmethod(normalisation.by_totalsum_plot)


class NormalisationByMedian(DataPreprocessingStep):
    display_name = "Median"
    operation = "normalisation"
    method_description = "Normalise data by median"

    def create_form(self):
        return Form(
            label="Normalisation by Median",
            input_fields=[
                FloatField(
                    name="percentile",
                    label="Percentile for normalisation",
                    value=0.5,
                    min=0,
                    max=1,
                    step=0.1,
                ),
                FormDivider("Plot settings"),
                DropdownField(
                    name="graph_type",
                    label="Graph type",
                    value=BoxAndHistogramGraph.BOXPLOT.value,
                    options=BoxAndHistogramGraph,
                ),
                DropdownField(
                    name="group_by",
                    label="Group by",
                    value=GroupBy.NO_GROUPING.value,
                    options=GroupBy,
                ),
                DropdownField(
                    name="visual_transformation",
                    label="Visual transformation",
                    value=VisualTransformations.LOG10.value,
                    options=VisualTransformations,
                ),
            ],
        )

    calc_method = staticmethod(normalisation.by_median)
    plot_method = staticmethod(normalisation.by_median_plot)


class NormalisationByWidthAdjustment(DataPreprocessingStep):
    display_name = "Width adjustment"
    operation = "normalisation"
    method_description = "Normalise data by asymmetric quartile width adjustment"

    def create_form(self):
        return Form(
            label="Normalisation by width adjustment",
            input_fields=[
                DropdownField(
                    name="graph_type",
                    label="Graph type",
                    value=BoxAndHistogramGraph.BOXPLOT.value,
                    options=BoxAndHistogramGraph,
                ),
                DropdownField(
                    name="group_by",
                    label="Group by",
                    value=GroupBy.NO_GROUPING.value,
                    options=GroupBy,
                ),
                DropdownField(
                    name="visual_transformation",
                    label="Visual transformation",
                    value=VisualTransformations.LOG10.value,
                    options=VisualTransformations,
                ),
            ],
        )

    calc_method = staticmethod(normalisation.by_width_adjustment)
    plot_method = staticmethod(normalisation.by_width_adjustment_plot)


class NormalisationByReferenceProtein(DataPreprocessingStep):
    display_name = "Reference protein"
    operation = "normalisation"
    method_description = "Normalise data by reference protein"

    def create_form(self):
        return Form(
            label="Normalisation by reference protein",
            input_fields=[
                InfoField(
                    label="A function to perform protein-intensity normalisation in reference to a selected protein "
                    "on your dataframe. Normalises the data on the level of each sample. Divides each intensity "
                    "by the intensity of the chosen reference protein in each sample. Samples where this value "
                    "is zero will be removed and returned separately."
                ),
                TextField(
                    name="reference_protein",
                    label="Reference protein",
                ),
                DropdownField(
                    name="graph_type",
                    label="Graph type",
                    value=BoxAndHistogramGraph.BOXPLOT.value,
                    options=BoxAndHistogramGraph,
                ),
                DropdownField(
                    name="group_by",
                    label="Group by",
                    value=GroupBy.NO_GROUPING.value,
                    options=GroupBy,
                ),
                DropdownField(
                    name="visual_transformation",
                    label="Visual transformation",
                    value=VisualTransformations.LOG10.value,
                    options=VisualTransformations,
                ),
            ],
        )

    calc_method = staticmethod(normalisation.by_reference_protein)
    plot_method = staticmethod(normalisation.by_reference_protein_plot)


class ImputationByMinPerDataset(DataPreprocessingStep):
    display_name = "Min per dataset"
    operation = "imputation"
    method_description = "Impute missing values by the minimum per dataset"

    def create_form(self):
        return Form(
            label="Imputation by minimum per dataset",
            input_fields=[
                InfoField(
                    label="A function to impute missing values for each protein by taking into account data from the "
                    "entire dataframe. Sets missing value to the smallest measured value in the dataframe. The "
                    "user can also assign a shrinking factor to take a fraction of that minimum value for "
                    "imputation."
                ),
                FloatField(
                    name="shrinking_value",
                    label="Shrinking value",
                    value=0.5,
                    min=0,
                    max=1,
                    step=0.1,
                ),
                DropdownField(
                    name="graph_type",
                    label="Graph type",
                    value=BoxAndHistogramGraph.BOXPLOT.value,
                    options=BoxAndHistogramGraph,
                ),
                DropdownField(
                    name="group_by",
                    label="Group by",
                    value=GroupBy.NO_GROUPING.value,
                    options=GroupBy,
                ),
                DropdownField(
                    name="visual_transformation",
                    label="Visual transformation",
                    value=VisualTransformations.LOG10.value,
                    options=VisualTransformations,
                ),
                DropdownField(
                    name="graph_type_quantities",
                    label="Graph type - quantity of imputed values",
                    value=BarAndPieChart.PIE_CHART.value,
                    options=BarAndPieChart,
                ),
            ],
        )

    calc_method = staticmethod(imputation.by_min_per_dataset)
    plot_method = staticmethod(imputation.by_min_per_dataset_plot)


class ImputationByMinPerProtein(DataPreprocessingStep):
    display_name = "Min per protein"
    operation = "imputation"
    method_description = "Impute missing values by the minimum per protein"

    def create_form(self):
        return Form(
            label="Imputation by minimum per protein",
            input_fields=[
                InfoField(
                    label="A function to impute missing values for each protein by taking into account data from each "
                    "protein. Sets missing value to the smallest measured value for each protein column. The "
                    "user can also assign a shrinking factor to take a fraction of that minimum value for "
                    "imputation. CAVE: All proteins without any values will be filtered out."
                ),
                FloatField(
                    name="shrinking_value",
                    label="Shrinking value",
                    value=0.5,
                    min=0,
                    max=1,
                    step=0.1,
                ),
                DropdownField(
                    name="graph_type",
                    label="Graph type",
                    value=BoxAndHistogramGraph.BOXPLOT.value,
                    options=BoxAndHistogramGraph,
                ),
                DropdownField(
                    name="group_by",
                    label="Group by",
                    value=GroupBy.NO_GROUPING.value,
                    options=GroupBy,
                ),
                DropdownField(
                    name="visual_transformation",
                    label="Visual transformation",
                    value=VisualTransformations.LOG10.value,
                    options=VisualTransformations,
                ),
                DropdownField(
                    name="graph_type_quantities",
                    label="Graph type - quantity of imputed values",
                    value=BarAndPieChart.PIE_CHART.value,
                    options=BarAndPieChart,
                ),
            ],
        )

    calc_method = staticmethod(imputation.by_min_per_protein)
    plot_method = staticmethod(imputation.by_min_per_protein_plot)


class ImputationByMinPerSample(DataPreprocessingStep):
    display_name = "Min per sample"
    operation = "imputation"
    method_description = "Impute missing values by the minimum per sample"

    def create_form(self):
        return Form(
            label="Imputation by minimum per sample",
            input_fields=[
                InfoField(
                    label="Sets missing intensity values to the smallest measured value for each sample"
                ),
                FloatField(
                    name="shrinking_value",
                    label="Shrinking value",
                    value=0.5,
                    min=0,
                    max=1,
                    step=0.1,
                ),
                DropdownField(
                    name="graph_type",
                    label="Graph type",
                    value=BoxAndHistogramGraph.BOXPLOT.value,
                    options=BoxAndHistogramGraph,
                ),
                DropdownField(
                    name="group_by",
                    label="Group by",
                    value=GroupBy.NO_GROUPING.value,
                    options=GroupBy,
                ),
                DropdownField(
                    name="visual_transformation",
                    label="Visual transformation",
                    value=VisualTransformations.LOG10.value,
                    options=VisualTransformations,
                ),
                DropdownField(
                    name="graph_type_quantities",
                    label="Graph type - quantity of imputed values",
                    value=BarAndPieChart.PIE_CHART.value,
                    options=BarAndPieChart,
                ),
            ],
        )

    calc_method = staticmethod(imputation.by_min_per_protein)
    plot_method = staticmethod(imputation.by_min_per_sample_plot)


class SimpleImputationPerProtein(DataPreprocessingStep):
    display_name = "Protein"
    operation = "imputation"
    method_description = (
        "Imputation methods include imputation by mean, median and mode. Implements the "
        "sklearn.SimpleImputer class"
    )

    def create_form(self):
        return Form(
            label="Imputation per Protein",
            input_fields=[
                DropdownField(
                    name="strategy",
                    label="Strategy",
                    value=SimpleImputerStrategyType.MEAN.value,
                    options=SimpleImputerStrategyType,
                ),
                DropdownField(
                    name="graph_type",
                    label="Graph type",
                    value=BoxAndHistogramGraph.BOXPLOT.value,
                    options=BoxAndHistogramGraph,
                ),
                DropdownField(
                    name="group_by",
                    label="Group by",
                    value=GroupBy.NO_GROUPING.value,
                    options=GroupBy,
                ),
                DropdownField(
                    name="visual_transformation",
                    label="Visual transformation",
                    value=VisualTransformations.LOG10.value,
                    options=VisualTransformations,
                ),
                DropdownField(
                    name="graph_type_quantities",
                    label="Graph type - quantity of imputed values",
                    value=BarAndPieChart.PIE_CHART.value,
                    options=BarAndPieChart,
                ),
            ],
        )

    calc_method = staticmethod(imputation.by_simple_imputer)
    plot_method = staticmethod(imputation.by_simple_imputer_plot)


class ImputationByKNN(DataPreprocessingStep):
    display_name = "kNN"
    operation = "imputation"
    method_description = (
        "A function to perform value imputation based on KNN (k-nearest neighbors). Imputes missing "
        "values for each sample based on intensity-wise similar samples. Two samples are close if "
        "the features that neither is missing are close."
    )

    def create_form(self):
        return Form(
            label="Imputation by KNN",
            input_fields=[
                NumberField(
                    name="number_of_neighbours",
                    label="Number of neighbours",
                    value=5,
                    min=1,
                    step=1,
                    hasStepButtons=True,
                ),
                FormDivider("Plot settings"),
                DropdownField(
                    name="graph_type",
                    label="Graph type",
                    value=BoxAndHistogramGraph.BOXPLOT.value,
                    options=BoxAndHistogramGraph,
                ),
                DropdownField(
                    name="group_by",
                    label="Group by",
                    value=GroupBy.NO_GROUPING.value,
                    options=GroupBy,
                ),
                DropdownField(
                    name="visual_transformation",
                    label="Visual transformation",
                    value=VisualTransformations.LOG10.value,
                    options=VisualTransformations,
                ),
                DropdownField(
                    name="graph_type_quantities",
                    label="Graph type - quantity of imputed values",
                    value=BarAndPieChart.PIE_CHART.value,
                    options=BarAndPieChart,
                ),
            ],
        )

    calc_method = staticmethod(imputation.by_knn)
    plot_method = staticmethod(imputation.by_knn_plot)


class ImputationByNormalDistributionSampling(DataPreprocessingStep):
    display_name = "Normal distribution sampling"
    operation = "imputation"
    method_description = "Imputation methods include normal distribution sampling per protein or per dataset"

    def create_form(self):
        return Form(
            label="Imputation by normal distribution sampling",
            input_fields=[
                DropdownField(
                    name="strategy",
                    label="Strategy",
                    value=ImputationByNormalDistributionSamplingStrategyType.PER_PROTEIN.value,
                    options=ImputationByNormalDistributionSamplingStrategyType,
                ),
                NumberField(
                    name="down_shift",
                    label="Downshift",
                    value=-1,
                    min=-10,
                    max=10,
                    step=1,
                    hasStepButtons=True,
                ),
                FloatField(
                    name="scaling_factor",
                    label="Scaling factor",
                    value=0.5,
                    min=0,
                    max=1,
                    step=0.1,
                ),
                DropdownField(
                    name="graph_type",
                    label="Graph type",
                    value=BoxAndHistogramGraph.BOXPLOT.value,
                    options=BoxAndHistogramGraph,
                ),
                DropdownField(
                    name="group_by",
                    label="Group by",
                    value=GroupBy.NO_GROUPING.value,
                    options=GroupBy,
                ),
                DropdownField(
                    name="visual_transformation",
                    label="Visual transformation",
                    value=VisualTransformations.LOG10.value,
                    options=VisualTransformations,
                ),
                DropdownField(
                    name="graph_type_quantities",
                    label="Graph type - quantity of imputed values",
                    value=BarAndPieChart.PIE_CHART.value,
                    options=BarAndPieChart,
                ),
            ],
        )

    calc_method = staticmethod(imputation.by_normal_distribution_sampling)
    plot_method = staticmethod(imputation.by_normal_distribution_sampling_plot)
