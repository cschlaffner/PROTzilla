from __future__ import annotations
from abc import ABC
from collections.abc import Sequence

from backend.protzilla.constants.data_types import DataKey
from backend.protzilla.data_preprocessing import (
    filter_proteins,
    filter_samples,
    imputation,
    normalisation,
    outlier_detection,
    peptide_filter,
    transformation,
    simplification,
)
from backend.protzilla.form import *
from backend.protzilla.steps import Step, Section
from backend.protzilla.constants.option_types import *
from backend.protzilla import form_helper
from backend.protzilla.run import Run
from protzilla.data_preprocessing.simplification import AggregationMethod


class DataPreprocessingStep(Step, ABC):
    section = Section.DATA_PREPROCESSING
    # default output_keys for most preprocessing steps. adapt where necessary!
    output_keys = [DataKey.PROTEIN_DF, DataKey.PEPTIDE_DF]

    plot_input_names = [DataKey.PROTEIN_DF]
    plot_output_names = ["plots"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plot_inputs: dict = {}


class FilteringStepBasedOnProteins(DataPreprocessingStep, ABC):
    output_keys = [DataKey.PROTEIN_DF]


class OutlierDetectionStep(DataPreprocessingStep, ABC):
    operation = "outlier_detection"
    output_keys = [DataKey.PROTEIN_DF]


class FilterProteinsBySamplesMissing(FilteringStepBasedOnProteins):
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


class FilterProteinsByNumberOfValuesPerGroup(FilteringStepBasedOnProteins):
    display_name = "By number of values per group"
    operation = "filter_proteins"
    method_description = "Filter proteins based on the minimum amount of samples with different values in each group"

    def create_form(self):
        return Form(
            label="Filter Proteins by number of values per group",
            input_fields=[
                NumberField(
                    name="min_amount",
                    label="Amount of minimum present samples per group with different values",
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

    calc_method = staticmethod(filter_proteins.by_number_of_values_per_group)
    plot_method = staticmethod(filter_proteins.by_number_of_values_per_group_plot)


class FilterProteinsByProteinIDs(FilteringStepBasedOnProteins):
    display_name = "By protein ids"
    operation = "filter_proteins"
    method_description = "Filter by protein ids entered by user"

    def create_form(self):
        return Form(
            label="Filter proteins by protein ids",
            input_fields=[
                MultiSelectField(
                    name="protein_ids",
                    label="Protein IDs",
                ),
            ],
        )

    calc_method = staticmethod(filter_proteins.by_protein_ids)

    def modify_form(self, run: Run) -> None:
        protein_ids_field: MultiSelectField = self.form["protein_ids"]
        protein_df = self.get_input(run.steps, DataKey.PROTEIN_DF)
        if protein_df is not None:
            protein_ids_field.set_options(
                form_helper.to_choices(
                    protein_df["Protein ID"].dropna().sort_values().unique()
                )
            )
        else:
            protein_ids_field.set_options([])


class FilterByProteinsCount(FilteringStepBasedOnProteins):
    display_name = "By protein count"
    operation = "filter_samples"
    method_description = "Filter by protein count per sample"

    def create_form(self):
        return Form(
            label="Filter samples by protein count",
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
    output_keys = [DataKey.PEPTIDE_DF]

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
                    name="graph_type",
                    label="Graph type",
                    value=BarAndPieChart.PIE_CHART.value,
                    options=BarAndPieChart,
                ),
            ],
        )

    calc_method = staticmethod(peptide_filter.by_pep_value)
    plot_method = staticmethod(peptide_filter.by_pep_value_plot)


class FilterPeptidesByExistingProteins(DataPreprocessingStep):
    display_name = "By existing proteins"
    operation = "filter_peptides"
    method_description = "Filter by existing proteins"
    output_keys = [DataKey.PEPTIDE_DF]

    def create_form(self):
        return Form(
            label="Filter peptides by existing proteins",
            input_fields=[],
        )

    calc_method = staticmethod(peptide_filter.by_existing_proteins)
    plot_method = staticmethod(peptide_filter.peptide_filtering_pie_plot)


class FilterPeptidesByExistingSamples(DataPreprocessingStep):
    display_name = "By existing samples"
    operation = "filter_peptides"
    method_description = "Filter by existing samples"
    output_keys = [DataKey.PEPTIDE_DF]

    def create_form(self):
        return Form(
            label="Filter peptides by existing samples",
            input_fields=[],
        )

    calc_method = staticmethod(peptide_filter.by_existing_samples)
    plot_method = staticmethod(peptide_filter.peptide_filtering_pie_plot)


class FilterSamplesByProteinsMissing(FilteringStepBasedOnProteins):
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


class FilterSamplesByProteinIntensitiesSum(FilteringStepBasedOnProteins):
    display_name = "By sum of intensities"
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


class OutlierDetectionByPCA(OutlierDetectionStep):
    display_name = "PCA"
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


class OutlierDetectionByLocalOutlierFactor(OutlierDetectionStep):
    display_name = "Local outlier factor"
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


class OutlierDetectionByIsolationForest(OutlierDetectionStep):
    display_name = "Isolation Forest"
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


class NormalisationStep(DataPreprocessingStep, ABC):
    operation = "normalisation"
    output_keys = [DataKey.PROTEIN_DF]


class NormalisationByZScore(NormalisationStep):
    display_name = "Z-Score"
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


class NormalisationByTotalSum(NormalisationStep):
    display_name = "Total sum"
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


class NormalisationByMedian(NormalisationStep):
    display_name = "Median"
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


class NormalisationByWidthAdjustment(NormalisationStep):
    display_name = "Width adjustment"
    method_description = "Normalise data by asymmetric quartile width adjustment"

    output_keys = [DataKey.PROTEIN_DF]

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


class NormalisationByReferenceProtein(NormalisationStep):
    display_name = "Reference protein"
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


class ImputationStep(DataPreprocessingStep, ABC):
    operation = "imputation"
    output_keys = [DataKey.PROTEIN_DF]

    plot_input_fields: Sequence[FormField] = [
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
    ]


class ImputationByMinPerDataset(ImputationStep):
    display_name = "Min per dataset"
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
                # pyright says + is not supported between Sequences
                # but lists are not covariant
                *self.plot_input_fields,
            ],
        )

    calc_method = staticmethod(imputation.by_min_per_dataset)
    plot_method = staticmethod(imputation.by_min_per_dataset_plot)


class ImputationByMinPerProtein(ImputationStep):
    display_name = "Min per protein"
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
                # pyright says + is not supported between Sequences
                # but lists are not covariant
                *self.plot_input_fields,
            ],
        )

    calc_method = staticmethod(imputation.by_min_per_protein)
    plot_method = staticmethod(imputation.by_min_per_protein_plot)


class ImputationByMinPerSample(ImputationStep):
    display_name = "Min per sample"
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
                # pyright says + is not supported between Sequences
                # but lists are not covariant
                *self.plot_input_fields,
            ],
        )

    calc_method = staticmethod(imputation.by_min_per_protein)
    plot_method = staticmethod(imputation.by_min_per_sample_plot)


class SimpleImputationPerProtein(ImputationStep):
    display_name = "Protein"
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
                # pyright says + is not supported between Sequences
                # but lists are not covariant
                *self.plot_input_fields,
            ],
        )

    calc_method = staticmethod(imputation.by_simple_imputer)
    plot_method = staticmethod(imputation.by_simple_imputer_plot)


class ImputationByKNN(ImputationStep):
    display_name = "kNN"
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
                # pyright says + is not supported between Sequences
                # but lists are not covariant
                *self.plot_input_fields,
            ],
        )

    calc_method = staticmethod(imputation.by_knn)
    plot_method = staticmethod(imputation.by_knn_plot)


class ImputationByNormalDistributionSampling(ImputationStep):
    display_name = "Normal distribution sampling"
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
                # pyright says + is not supported between Sequences
                # but lists are not covariant
                *self.plot_input_fields,
            ],
        )

    calc_method = staticmethod(imputation.by_normal_distribution_sampling)
    plot_method = staticmethod(imputation.by_normal_distribution_sampling_plot)


class GroupReplicates(Step):
    section = Section.DATA_PREPROCESSING
    display_name = "Group Replicates"
    operation = "simplification"
    method_description = "Aggregate intensities of proteins from replicate runs."
    output_keys = [DataKey.PROTEIN_DF]

    def create_form(self):
        return Form(
            label="Group Replicates",
            input_fields=[
                DropdownField(
                    name="aggregation_column",
                    label="Column based on which replicates should be aggregated on",
                ),
                DropdownField(
                    name="aggregation_method",
                    label="Aggregation method used to aggregate replicate values",
                    options=AggregationMethod,
                ),
            ],
        )

    calc_method = staticmethod(simplification.group_replicates)

    def modify_form(self, run: Run) -> None:
        aggregation_column_field: DropdownField = self.form["aggregation_column"]
        metadata_df = self.get_input(run.steps, DataKey.METADATA_DF)
        if metadata_df is not None:
            aggregation_column_field.set_options(
                form_helper.to_choices(list(metadata_df.columns))
            )
        else:
            aggregation_column_field.set_options([])
