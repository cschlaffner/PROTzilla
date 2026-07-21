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
    filter_peptides_or_psm,
    transformation,
    simplification,
)
from backend.protzilla.form import *
from backend.protzilla.steps import Step, Section, StepOperation
from backend.protzilla.constants.option_types import *
from backend.protzilla import form_helper
from backend.protzilla.run import Run
from backend.protzilla.data_preprocessing.simplification import AggregationMethod
from backend.protzilla.data_preprocessing.debug_transform_to_wide import (
    transform_to_wide,
)

info_field_show_outliers = InfoField(
    name="show_outliers_info",
    label="Hiding outliers changes how the chart is calculated. It "
    "will extend the whiskers to the absolute minimum and maximum "
    "values of your data instead of the standard 1.5 interquartile "
    "range (IQR).",
    isVisible=True,
)


class DataPreprocessingStep(Step, ABC):
    section = Section.DATA_PREPROCESSING
    # default output_keys for most preprocessing steps. adapt where necessary!
    output_keys = [DataKey.PROTEIN_DF, DataKey.PEPTIDE_DF]

    plot_input_names = [DataKey.PROTEIN_DF]
    plot_output_names = ["plots"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plot_inputs: dict = {}


class FilterSamplesStep(DataPreprocessingStep, ABC):
    output_keys = [DataKey.PROTEIN_DF]
    operation: StepOperation = StepOperation.FILTER_SAMPLES


class FilterProteinsStep(DataPreprocessingStep, ABC):
    output_keys = [DataKey.PROTEIN_DF]
    operation: StepOperation = StepOperation.FILTER_PROTEINS


class FilterPeptidesStep(DataPreprocessingStep, ABC):
    operation: StepOperation = StepOperation.FILTER_PEPTIDES


class OutlierDetectionStep(DataPreprocessingStep, ABC):
    output_keys = [DataKey.PROTEIN_DF]
    operation: StepOperation = StepOperation.OUTLIER_DETECTION


class FilterPsmStep(DataPreprocessingStep, ABC):
    output_keys = [DataKey.PSM_DF]
    operation: StepOperation = StepOperation.FILTER_PSMS


class FilterProteinsBySamplesMissing(FilterProteinsStep):
    display_name = "Filter Proteins: Missing Samples"
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


class FilterProteinsByNumberOfValuesPerGroup(FilterProteinsStep):
    display_name = "Filter Proteins: #Values / Group"
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


class FilterProteinsByProteinIDs(FilterProteinsStep):
    display_name = "Filter Proteins: Specific IDs"
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


class FilterProteinsKeepNmostSignificantProteins(FilterProteinsStep):
    display_name = "Filter Proteins: Keep n Most Significant"
    method_description = (
        "Filter to keep the n most significant proteins (with the lowest p-values)"
    )
    output_keys = [DataKey.DIFFERENTIALLY_EXPRESSED_PROTEINS_DF]

    def create_form(self):
        return Form(
            label="Filter proteins to keep the n most significant proteins",
            input_fields=[
                NumberField(
                    name="number_of_proteins_to_keep",
                    label="Number of proteins to keep",
                    value=1,
                    min=1,
                )
            ],
        )

    calc_method = staticmethod(filter_proteins.keep_n_most_significant_proteins)


class FilterByProteinsCount(FilterSamplesStep):
    display_name = "Filter Samples: #Proteins / Sample"
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


class FilterPeptidesByPEPThreshold(FilterPeptidesStep):
    display_name = "Filter Peptides: PEP Threshold"
    method_description = "Filter peptides by PEP-threshold"
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

    calc_method = staticmethod(filter_peptides_or_psm.filter_peptides_by_pep_value)
    plot_method = staticmethod(filter_peptides_or_psm.filter_peptides_by_pep_value_plot)


class FilterPeptidesByExistingProteins(FilterPeptidesStep):
    display_name = "Filter Peptides: Existing Proteins"
    method_description = "Filter peptides by existing proteins"
    output_keys = [DataKey.PEPTIDE_DF]

    def create_form(self):
        return Form(
            label="Filter peptides by existing proteins",
            input_fields=[],
        )

    calc_method = staticmethod(
        filter_peptides_or_psm.filter_peptides_by_existing_proteins
    )
    plot_method = staticmethod(filter_peptides_or_psm.peptide_filtering_pie_plot)


class FilterPeptidesByExistingSamples(FilterPeptidesStep):
    display_name = "Filter Peptides: Existing Samples"
    method_description = "Filter peptides by existing samples"
    output_keys = [DataKey.PEPTIDE_DF]

    def create_form(self):
        return Form(
            label="Filter peptides by existing samples",
            input_fields=[],
        )

    calc_method = staticmethod(
        filter_peptides_or_psm.filter_peptides_by_existing_samples
    )
    plot_method = staticmethod(filter_peptides_or_psm.peptide_filtering_pie_plot)


class FilterPsmByPEPThreshold(FilterPsmStep):
    display_name = "Filter PSMs: PEP Threshold"
    method_description = "Filter PSM by PEP-threshold"

    def create_form(self):
        return Form(
            label="Filter PSM by PEP threshold",
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

    calc_method = staticmethod(filter_peptides_or_psm.filter_psm_by_pep_value)
    plot_method = staticmethod(filter_peptides_or_psm.filter_psm_by_pep_value_plot)


class FilterPsmByExistingProteins(FilterPsmStep):
    display_name = "Filter PSMs: Existing Proteins"
    method_description = "Filter PSM by existing proteins"

    def create_form(self):
        return Form(
            label="Filter PSM by existing proteins",
            input_fields=[],
        )

    calc_method = staticmethod(filter_peptides_or_psm.filter_psm_by_existing_proteins)
    plot_method = staticmethod(filter_peptides_or_psm.psm_filtering_pie_plot)


class FilterPsmByExistingSamples(FilterPsmStep):
    display_name = "Filter PSMs: Existing Samples"
    method_description = "Filter PSM by existing samples"

    def create_form(self):
        return Form(
            label="Filter peptides by existing samples",
            input_fields=[],
        )

    calc_method = staticmethod(filter_peptides_or_psm.filter_psm_by_existing_samples)
    plot_method = staticmethod(filter_peptides_or_psm.psm_filtering_pie_plot)


class FilterSamplesByProteinsMissing(FilterSamplesStep):
    display_name = "Filter Samples: Missing Proteins"
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


class FilterSamplesByProteinIntensitiesSum(FilterSamplesStep):
    display_name = "Filter Samples: Sum of Intensities"
    method_description = "Filter Samples (Sum of Protein Intensities)"

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


class FilterSamplesByClass(FilterSamplesStep):
    display_name = "Filter Samples: Class in metadata"
    method_description = "Filter Samples (Class in metadata)"

    def create_form(self):
        return Form(
            label="Filter Samples by Class in metadata",
            input_fields=[
                DropdownField(
                    name="class_column",
                    label="The name of the class column in metadata",
                ),
                MultiSelectField(
                    name="classes_names",
                    label="The classes that should be filtered out",
                ),
                DropdownField(
                    name="graph_type",
                    label="Graph type",
                    value=BarAndPieChart.PIE_CHART.value,
                    options=BarAndPieChart,
                ),
            ],
        )

    def modify_form(self, run):
        self.set_grouping_options(run=run, column_field_name="class_column")
        self.set_selected_groups_options(
            run=run, column_field="class_column", group_field="classes_names"
        )

    calc_method = staticmethod(filter_samples.by_class_in_metadata)
    plot_method = staticmethod(filter_samples.by_class_in_metadata_plot)


class OutlierDetectionByPCA(OutlierDetectionStep):
    display_name = "Outlier Detection: PCA"
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
    display_name = "Outlier Detection: Local Outlier Factor"
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
    display_name = "Outlier Detection: Isolation Forest"
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
    display_name = "Transformation: Log"
    operation: StepOperation = StepOperation.TRANSFORMATION
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
                CheckboxField(
                    name="show_outliers",
                    label="Show outliers",
                    value=True,
                    isVisible=True,
                ),
                info_field_show_outliers,
            ],
        )

    def modify_form(self, run):
        if self.form["graph_type"].value == BoxAndHistogramGraph.BOXPLOT.value:
            self.form["show_outliers"].isVisible = True
            self.form["show_outliers_info"].isVisible = True
        else:
            self.form["show_outliers"].isVisible = False
            self.form["show_outliers_info"].isVisible = False

    calc_method = staticmethod(transformation.by_log)
    plot_method = staticmethod(transformation.transformation_plot)


class TransformationScaling(DataPreprocessingStep):
    display_name = "Transformation: Scaling"
    operation: StepOperation = StepOperation.TRANSFORMATION
    method_description = "Transform data by scaling"

    def create_form(self):
        return Form(
            label="Scaling Transformation",
            input_fields=[
                FloatField(
                    name="min_value",
                    label="Minimum value that data minimum should be mapped to",
                ),
                FloatField(
                    name="max_value",
                    label="Maximum value that data maximum should be mapped to",
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
                CheckboxField(
                    name="show_outliers",
                    label="Show outliers",
                    value=True,
                    isVisible=True,
                ),
                info_field_show_outliers,
            ],
        )

    def modify_form(self, run):
        if self.form["graph_type"].value == BoxAndHistogramGraph.BOXPLOT.value:
            self.form["show_outliers"].isVisible = True
            self.form["show_outliers_info"].isVisible = True
        else:
            self.form["show_outliers"].isVisible = False
            self.form["show_outliers_info"].isVisible = False

    calc_method = staticmethod(transformation.by_scaling)
    plot_method = staticmethod(transformation.transformation_plot)


class TransformationInversion(DataPreprocessingStep):
    display_name = "Transformation: Inversion"
    operation: StepOperation = StepOperation.TRANSFORMATION
    method_description = "Transform data by inversion"

    def create_form(self):
        return Form(
            label="Data Inversion Transformation",
            input_fields=[],
        )

    calc_method = staticmethod(transformation.by_inversion)


class NormalisationStep(DataPreprocessingStep, ABC):
    operation: StepOperation = StepOperation.NORMALIZATION
    output_keys = [DataKey.PROTEIN_DF]

    def modify_form(self, run):
        if self.form["graph_type"].value == BoxAndHistogramGraph.BOXPLOT.value:
            self.form["show_outliers"].isVisible = True
            self.form["show_outliers_info"].isVisible = True
        else:
            self.form["show_outliers"].isVisible = False
            self.form["show_outliers_info"].isVisible = False


class NormalisationByZScore(NormalisationStep):
    display_name = "Normalisation: Z-Score"
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
                CheckboxField(
                    name="show_outliers",
                    label="Show outliers",
                    value=True,
                    isVisible=True,
                ),
                info_field_show_outliers,
            ],
        )

    calc_method = staticmethod(normalisation.by_z_score)
    plot_method = staticmethod(normalisation.by_z_score_plot)


class NormalisationByTotalSum(NormalisationStep):
    display_name = "Normalisaton: Total Sum"
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
                CheckboxField(
                    name="show_outliers",
                    label="Show outliers",
                    value=True,
                    isVisible=True,
                ),
                info_field_show_outliers,
            ],
        )

    calc_method = staticmethod(normalisation.by_totalsum)
    plot_method = staticmethod(normalisation.by_totalsum_plot)


class NormalisationByMedian(NormalisationStep):
    display_name = "Normalisation: Median"
    method_description = "Normalise data by median"

    def create_form(self):
        self.log_field_status = True
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
                CheckboxField(
                    name="log",
                    label="Data was log-transformed before normalization",
                    value=False,
                ),
                InfoField(
                    name="log_before_normalisation_info",
                    label="The normalisation is calculated differently for log-transformed data, "
                    "using subtraction instead of division.",
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
                CheckboxField(
                    name="show_outliers",
                    label="Show outliers",
                    value=True,
                    isVisible=True,
                ),
                info_field_show_outliers,
            ],
        )

    def modify_form(self, run):
        log_field = self.form["log"]
        visual_transformation_field = self.form["visual_transformation"]

        if self.log_field_status != log_field.value:
            self.log_field_status = log_field.value
            if log_field.value:
                visual_transformation_field.value = VisualTransformations.LINEAR
            elif not log_field.value:
                visual_transformation_field.value = VisualTransformations.LOG10

    calc_method = staticmethod(normalisation.by_median)
    plot_method = staticmethod(normalisation.by_median_plot)


class NormalisationByWidthAdjustment(NormalisationStep):
    display_name = "Normalisation: Width Adjustment"
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
                CheckboxField(
                    name="show_outliers",
                    label="Show outliers",
                    value=True,
                    isVisible=True,
                ),
                info_field_show_outliers,
            ],
        )

    calc_method = staticmethod(normalisation.by_width_adjustment)
    plot_method = staticmethod(normalisation.by_width_adjustment_plot)


class NormalisationByReferenceProtein(NormalisationStep):
    display_name = "Normalisation: Reference Protein"
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
                CheckboxField(
                    name="show_outliers",
                    label="Show outliers",
                    value=True,
                    isVisible=True,
                ),
                info_field_show_outliers,
            ],
        )

    calc_method = staticmethod(normalisation.by_reference_protein)
    plot_method = staticmethod(normalisation.by_reference_protein_plot)


class ImputationStep(DataPreprocessingStep, ABC):
    operation: StepOperation = StepOperation.IMPUTATION
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
        CheckboxField(
            name="show_outliers", label="Show outliers", value=True, isVisible=True
        ),
        info_field_show_outliers,
    ]

    def modify_form(self, run):
        if self.form["graph_type"].value == BoxAndHistogramGraph.BOXPLOT.value:
            self.form["show_outliers"].isVisible = True
            self.form["show_outliers_info"].isVisible = True
        else:
            self.form["show_outliers"].isVisible = False
            self.form["show_outliers_info"].isVisible = False


class ImputationByMinPerDataset(ImputationStep):
    display_name = "Imputation: Min per Dataset"
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
    display_name = "Imputation: Min per Protein"
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
    display_name = "Imputation: Min per Sample"
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
    display_name = "Imputation: per Protein"
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
    display_name = "Imputation: kNN"
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
    display_name = "Imputation: Normal Dist. Sampling"
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
    operation: StepOperation = StepOperation.SIMPLIFICATION
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


class FilterMetadataByExistingSamples(Step):
    section = Section.DATA_PREPROCESSING
    display_name = "Filter Metadata: Existing Samples"
    operation: StepOperation = StepOperation.SIMPLIFICATION
    method_description = (
        "Only keep metadata of samples also represented in protein data"
    )
    output_keys = [DataKey.METADATA_DF]

    def create_form(self):
        return Form(
            label="Filter Metadata",
            input_fields=[
                DropdownField(
                    name="sample_column",
                    label="Column in metadata containing sample identifiers",
                ),
            ],
        )

    calc_method = staticmethod(simplification.metadata_filter_by_samples)

    def modify_form(self, run: Run) -> None:
        sample_column_field: DropdownField = self.form["sample_column"]
        metadata_df = self.get_input(run.steps, DataKey.METADATA_DF)
        if metadata_df is not None:
            sample_column_field.set_options(
                form_helper.to_choices(list(metadata_df.columns))
            )
        else:
            sample_column_field.set_options([])


class TransformToWideFormat(Step):
    section = Section.DATA_PREPROCESSING
    display_name = "Transform Dataframe: Wide Format"
    operation: StepOperation = StepOperation.DEBUG
    method_description = "Turns the protein dataframe into wide format"
    output_keys = [DataKey.DEBUG]

    def create_form(self):
        return Form(
            label="Transform into a wide format dataframe",
            input_fields=[],
        )

    calc_method = staticmethod(transform_to_wide)
