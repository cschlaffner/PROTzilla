from __future__ import annotations

from enum import Enum
import logging
import traceback

from backend.protzilla.data_preprocessing import (
    filter_proteins,
    filter_samples,
    imputation,
    normalisation,
    outlier_detection,
    peptide_filter,
    transformation,
)
from backend.protzilla.steps import Plots, Step, StepManager
from backend.protzilla.utilities import format_trace
from backend.protzilla.form import *


class LogTransformationBaseType(Enum):
    log2 = "log2"
    log10 = "log10"


class SimpleImputerStrategyType(Enum):
    mean = "mean"
    median = "median"
    most_frequent = "most_frequent"


class ImputationByNormalDistributionSamplingStrategyType(Enum):
    per_protein = "perProtein"
    per_dataset = "perDataset"


class BarAndPieChart(Enum):
    bar_plot = "Bar chart"
    pie_chart = "Pie chart"


class BoxAndHistogramGraph(Enum):
    boxplot = "Boxplot"
    histogram = "Histogram"


class GroupBy(Enum):
    no_grouping = "None"
    sample = "Sample"
    protein_id = "Protein ID"


class VisualTrasformations(Enum):
    log10 = "log10"
    linear = "linear"


class VisulaTransformations(Enum):
    linear = "linear"
    log10 = "log10"


class DataPreprocessingStep(Step):
    section = "data_preprocessing"
    output_keys = ["protein_df"]

    plot_input_names = ["protein_df"]
    plot_output_names = ["plots"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plot_inputs: dict = {}

    def insert_dataframes(self, steps: StepManager, inputs: dict) -> dict:
        inputs["protein_df"] = steps.protein_df
        inputs["peptide_df"] = steps.get_step_output(Step, "peptide_df")
        return inputs

    def plot(self, inputs: dict = None):
        if inputs is None:
            inputs = self.plot_inputs
        else:
            self.plot_inputs = inputs.copy()
        inputs = self.insert_dataframes_for_plot(inputs)
        try:
            self.plots = Plots(self.plot_method(inputs))
        except Exception as e:
            self.messages.append(
                dict(
                    level=logging.ERROR,
                    msg=(
                        f"An error occurred while plotting this step: {e.__class__.__name__} {e} "
                        f"Please check your parameters or report a potential programming issue."
                    ),
                    trace=format_trace(traceback.format_exception(e)),
                )
            )

    def insert_dataframes_for_plot(self, inputs: dict) -> dict:
        inputs["method_inputs"] = self.inputs
        inputs["method_outputs"] = self.output
        return inputs

    def plot_method(self, inputs):
        raise NotImplementedError("Plot method not implemented for this step")


class FilterProteinsBySamplesMissing(DataPreprocessingStep):
    display_name = "By samples missing"
    operation = "filter_proteins"
    method_description = (
        "Filter proteins based on the amount of samples with nan values"
    )

    input_keys = ["protein_df", "peptide_df", "percentage"]

    def create_form(self):
        return Form(
            label="Filter Proteins by Samples Missing",
            fields=[
                NumberField(
                    name="percentage",
                    label="Percentage of minimum non-missing samples per protein",
                    value=0.5,
                    min=0,
                    max=1,
                    step=0.1,
                ),
                DropdownField(
                    name="graph_type",
                    value=BarAndPieChart.pie_chart,
                    label="Graph type",
                    options=BarAndPieChart,
                ),
            ],
        )

    def method(self, inputs):
        return filter_proteins.by_samples_missing(**inputs)

    def plot_method(self, inputs):
        return filter_proteins.by_samples_missing_plot(**inputs)


class FilterByProteinsCount(DataPreprocessingStep):
    display_name = "Protein Count"
    operation = "filter_samples"
    method_description = "Filter by protein count per sample"

    input_keys = ["protein_df", "peptide_df", "deviation_threshold"]

    def create_form(self):
        return Form(
            label="Filter Samples by Protein Count",
            fields=[
                NumberField(
                    name="deviation_threshold",
                    label="Number of standard deviations from the median",
                    value=2,
                    min=0,
                ),
                DropdownField(
                    name="graph_type",
                    value=BarAndPieChart.pie_chart,
                    label="Graph type",
                    options=BarAndPieChart,
                ),
            ],
        )

    def method(self, inputs):
        return filter_samples.by_protein_count(**inputs)

    def plot_method(self, inputs):
        return filter_samples.by_protein_count_plot(**inputs)


class FilterSamplesByProteinsMissing(DataPreprocessingStep):
    display_name = "By proteins missing"
    operation = "filter_samples"
    method_description = (
        "Filter samples based on the amount of proteins with nan values"
    )

    input_keys = ["protein_df", "peptide_df", "percentage"]

    def create_form(self):
        return Form(
            label="Filter Samples by Proteins Missing",
            fields=[
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
                    value=BarAndPieChart.pie_chart,
                    label="Graph type",
                    options=BarAndPieChart,
                ),
            ],
        )

    def method(self, inputs):
        return filter_samples.by_proteins_missing(**inputs)

    def plot_method(self, inputs):
        return filter_samples.by_proteins_missing_plot(**inputs)


class FilterSamplesByProteinIntensitiesSum(DataPreprocessingStep):
    display_name = "Sum of intensities"
    operation = "filter_samples"
    method_description = "Filter by sum of protein intensities per sample"

    input_keys = ["protein_df", "peptide_df", "deviation_threshold"]

    def create_form(self):
        return Form(
            label="Filter Samples by Protein Intensity Sum",
            fields=[
                FloatField(
                    name="deviation_threshold",
                    label="Number of standard deviations from the median",
                    value=2,
                    min=0,
                ),
                DropdownField(
                    name="graph_type",
                    value=BarAndPieChart.pie_chart,
                    label="Graph type",
                    options=BarAndPieChart,
                ),
            ],
        )

    def method(self, inputs):
        return filter_samples.by_protein_intensity_sum(**inputs)

    def plot_method(self, inputs):
        return filter_samples.by_protein_intensity_sum_plot(**inputs)


class OutlierDetectionByPCA(DataPreprocessingStep):
    display_name = "PCA"
    operation = "outlier_detection"
    method_description = "Detect outliers using PCA"

    input_keys = ["protein_df", "peptide_df", "number_of_components", "threshold"]

    def create_form(self):
        return Form(
            label="Outlier Detection by PCA",
            fields=[
                FloatField(
                    name="threshold",
                    label="Threshold for number of standard deviations from the median:",
                    value=2,
                    min=0,
                ),
                NumberField(
                    name="number_of_components",
                    label="Number of components",
                    value=3,
                    min=2,
                    max=3,
                    step=1,
                ),
            ],
        )

    def method(self, inputs):
        return outlier_detection.by_pca(**inputs)

    def plot_method(self, inputs):
        return outlier_detection.by_pca_plot(**inputs)


class OutlierDetectionByLocalOutlierFactor(DataPreprocessingStep):
    display_name = "Local outlier factor"
    operation = "outlier_detection"
    method_description = "Detect outliers using the local outlier factor"

    input_keys = ["protein_df", "peptide_df", "number_of_neighbors"]

    def create_form(self):
        return Form(
            label="Outlier Detection by Local Outlier Factor",
            fields=[
                NumberField(
                    name="number_of_neighbors",
                    label="Number of neighbors",
                    value=20,
                    min=1,
                    step=1,
                ),
            ],
        )

    def method(self, inputs):
        return outlier_detection.by_local_outlier_factor(**inputs)

    def plot_method(self, inputs):
        return outlier_detection.by_local_outlier_factor_plot(**inputs)


class OutlierDetectionByIsolationForest(DataPreprocessingStep):
    display_name = "Isolation Forest"
    operation = "outlier_detection"
    method_description = "Detect outliers using Isolation Forest"

    input_keys = ["protein_df", "peptide_df", "n_estimators"]

    def create_form(self):
        return Form(
            label="Outlier Detection by Isolation Forest",
            fields=[
                NumberField(
                    name="n_estimators",
                    label="Number of estimators",
                    value=100,
                    min=1,
                    step=1,
                ),
            ],
        )

    def method(self, inputs):
        return outlier_detection.by_isolation_forest(**inputs)

    def plot_method(self, inputs):
        return outlier_detection.by_isolation_forest_plot(**inputs)


class TransformationLog(DataPreprocessingStep):
    display_name = "Log"
    operation = "transformation"
    method_description = "Transform data by log"

    input_keys = [ "protein_df", "peptide_df", "log_base"]

    def create_form(self):
        return Form(
            label="Log Transformation",
            fields=[
                DropdownField(
                    name="log_base",
                    label="Log transformation base",
                    value=LogTransformationBaseType.log2,
                    options=LogTransformationBaseType,
                ),
                FormDivider("Plot settings"),
                DropdownField(
                    name="graph_type",
                    label="Graph type",
                    value=BarAndPieChart.pie_chart,
                    options=BarAndPieChart,
                ),
                DropdownField(
                    name="group_by",
                    label="Group by",
                    value=GroupBy.no_grouping,
                    options=GroupBy,
                ),
            ],
        )


    def method(self, inputs):
        return transformation.by_log(**inputs)

    def plot_method(self, inputs):
        return transformation.by_log_plot(**inputs)


class NormalisationByZScore(DataPreprocessingStep):
    display_name = "Z-Score"
    operation = "normalisation"
    method_description = "Normalise data by Z-Score"

    plot_input_names = ["protein_df"]

    def method(self, inputs):
        return normalisation.by_z_score(**inputs)

    def plot_method(self, inputs):
        return normalisation.by_z_score_plot(**inputs)


class NormalisationByTotalSum(DataPreprocessingStep):
    display_name = "Total sum"
    operation = "normalisation"
    method_description = "Normalise data by total sum"

    plot_input_names = ["protein_df"]

    def method(self, inputs):
        return normalisation.by_totalsum(**inputs)

    def plot_method(self, inputs):
        return normalisation.by_totalsum_plot(**inputs)


class NormalisationByMedian(DataPreprocessingStep):
    display_name = "Median"
    operation = "normalisation"
    method_description = "Normalise data by median"

    input_keys = ["protein_df", "percentile"]

    def create_form(self):
        return Form(
            label="Normalisation by Median",
            fields=[
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
                    value=BoxAndHistogramGraph.boxplot,
                    options=BoxAndHistogramGraph,
                ),
                DropdownField(
                    name="group_by",
                    label="Group by",
                    value=GroupBy.no_grouping,
                    options=GroupBy,
                ),
                DropdownField(
                    name="visual_transformation",
                    label="Visual transformation",
                    value=VisualTrasformations.log10,
                    options=VisualTrasformations,
                ),
            ],
        )

    def method(self, inputs):
        return normalisation.by_median(**inputs)

    def plot_method(self, inputs):
        return normalisation.by_median_plot(**inputs)


class NormalisationByReferenceProtein(DataPreprocessingStep):
    display_name = "Reference protein"
    operation = "normalisation"
    method_description = "Normalise data by reference protein"

    input_keys = ["protein_df", "reference_protein"]

    def method(self, inputs):
        return normalisation.by_reference_protein(**inputs)

    def plot_method(self, inputs):
        return normalisation.by_reference_protein_plot(**inputs)


class ImputationByMinPerDataset(DataPreprocessingStep):
    display_name = "Min per dataset"
    operation = "imputation"
    method_description = "Impute missing values by the minimum per dataset"

    input_keys = ["protein_df", "shrinking_value"]

    def method(self, inputs):
        return imputation.by_min_per_dataset(**inputs)

    def plot_method(self, inputs):
        return imputation.by_min_per_dataset_plot(**inputs)


class ImputationByMinPerProtein(DataPreprocessingStep):
    display_name = "Min per protein"
    operation = "imputation"
    method_description = "Impute missing values by the minimum per protein"

    input_keys = ["protein_df", "shrinking_value"]

    def method(self, inputs):
        return imputation.by_min_per_protein(**inputs)

    def plot_method(self, inputs):
        return imputation.by_min_per_protein_plot(**inputs)


class ImputationByMinPerSample(DataPreprocessingStep):
    display_name = "Min per sample"
    operation = "imputation"
    method_description = "Impute missing values by the minimum per sample"

    input_keys = ["protein_df", "shrinking_value"]

    def method(self, inputs):
        return imputation.by_min_per_protein(**inputs)

    def plot_method(self, inputs):
        return imputation.by_min_per_sample_plot(**inputs)


class SimpleImputationPerProtein(DataPreprocessingStep):
    display_name = "SimpleImputer"
    operation = "imputation"
    method_description = (
        "Imputation methods include imputation by mean, median and mode. Implements the "
        "sklearn.SimpleImputer class"
    )

    input_keys = ["protein_df", "strategy"]

    def method(self, inputs):
        return imputation.by_simple_imputer(**inputs)

    def plot_method(self, inputs):
        return imputation.by_simple_imputer_plot(**inputs)


class ImputationByKNN(DataPreprocessingStep):
    display_name = "kNN"
    operation = "imputation"
    method_description = (
        "A function to perform value imputation based on KNN (k-nearest neighbors). Imputes missing "
        "values for each sample based on intensity-wise similar samples. Two samples are close if "
        "the features that neither is missing are close."
    )

    input_keys = ["protein_df", "number_of_neighbours"]

    def create_form(self):
        return Form(
            label="Imputation by KNN",
            fields=[
                NumberField(
                    name="number_of_neighbours",
                    label="Number of neighbours",
                    value=5,
                    min=1,
                    step=1,
                ),
                FormDivider("Plot settings"),
                DropdownField(
                    name="group_by",
                    label="Group by",
                    value=GroupBy.no_grouping,
                    options=GroupBy,
                ),
                DropdownField(
                    name="visual_transformation",
                    label="Visual transformation",
                    value=VisualTrasformations.log10,
                    options=VisualTrasformations,
                ),
                DropdownField(
                    name="graph_type_quantities",
                    label="Graph type - quantity of imputed values",
                    value=BarAndPieChart.pie_chart,
                    options=BarAndPieChart,
                ),
            ],
        )

    def method(self, inputs):
        return imputation.by_knn(**inputs)

    def plot_method(self, inputs):
        return imputation.by_knn_plot(**inputs)


class ImputationByNormalDistributionSampling(DataPreprocessingStep):
    display_name = "Normal distribution sampling"
    operation = "imputation"
    method_description = "Imputation methods include normal distribution sampling per protein or per dataset"

    input_keys = ["protein_df", "strategy", "down_shift", "scaling_factor"]

    def method(self, inputs):
        return imputation.by_normal_distribution_sampling(**inputs)

    def plot_method(self, inputs):
        return imputation.by_normal_distribution_sampling_plot(**inputs)


class FilterPeptidesByPEPThreshold(DataPreprocessingStep):
    display_name = "PEP threshold"
    operation = "filter_peptides"
    method_description = "Filter by PEP-threshold"

    input_keys = ["protein_df", "peptide_df", "threshold"]
    output_keys = ["protein_df", "peptide_df", "filtered_peptides"]

    def method(self, inputs):
        return peptide_filter.by_pep_value(**inputs)

    def plot_method(self, inputs):
        return peptide_filter.by_pep_value_plot(**inputs)
