from abc import ABC
import logging
from typing_extensions import override

from backend.protzilla.constants.option_types import (
    LogBaseWithNoneType,
    SimpleImputerStrategyType,
)
from backend.protzilla import form_helper
from backend.protzilla.run import Run
from backend.protzilla.constants.data_types import DataKey
from backend.protzilla.constants.option_types import MultipleTestingCorrectionMethod
from backend.protzilla.data_analysis.classification import random_forest, svm
from backend.protzilla.data_analysis.clustering import (
    expectation_maximisation,
    hierarchical_agglomerative_clustering,
    k_means,
)
from backend.protzilla.data_analysis.differential_expression_anova import anova
from backend.protzilla.data_analysis.differential_expression_kruskal_wallis import (
    kruskal_wallis_test_on_ptm_data,
    kruskal_wallis_test_on_intensity_data,
)
from backend.protzilla.data_analysis.differential_expression_linear_model import (
    linear_model,
)
from backend.protzilla.data_analysis.differential_expression_mann_whitney import (
    mann_whitney_test_on_intensity_data,
    mann_whitney_test_on_ptm_data,
)
from backend.protzilla.data_analysis.differential_expression_t_test import t_test
from backend.protzilla.data_analysis.dimension_reduction import t_sne, umap, TSNEMethod
from backend.protzilla.data_analysis.model_evaluation import (
    evaluate_classification_model,
)
from backend.protzilla.data_analysis.plots import (
    clustergram_plot,
    create_volcano_plot,
    prot_quant_plot,
    scatter_plot,
)
from backend.protzilla.utilities.clustergram import (
    HEATMAP_LOW_COLOR,
    HEATMAP_HIGH_COLOR,
)
from backend.protzilla.data_analysis.ptm_analysis import (
    ptms_per_protein_and_sample,
    ptms_per_sample,
)
from backend.protzilla.data_analysis.ptm_visualization.ptm_bar_plot import (
    create_bar_ptm_visualization,
)
from backend.protzilla.form import (
    CheckboxField,
    ColorField,
    DropdownField,
    Enum,
    FileInput,
    FloatField,
    Form,
    FormField,
    HeaderInfoField,
    InfoField,
    InputField,
    Option,
    MultiSelectField,
    NumberField,
    TextField,
)
from backend.protzilla.methods.data_preprocessing import (
    DataPreprocessingStep,
)
from backend.protzilla.steps import Step, Section
from backend.protzilla.step_manager import StepManager
from backend.protzilla.data_analysis.protein_coverage import (
    plot_protein_coverage,
    AggregationMethod as ProteinCoverageAggregationMethod,
)
from backend.protzilla.data_analysis.ptm_quantification.flexiquant import flexiquant_lf
from backend.protzilla.data_analysis.ptm_quantification.multiflex import (
    multiflex_lf,
    MultiFlexColorMaps,
)
from backend.protzilla.data_analysis.ptm_visualization.ptm_details_plot import (
    create_details_ptm_visualization,
)
from backend.protzilla.data_analysis.ptm_visualization.ptm_overview_plot import (
    create_overview_ptm_visualization,
    get_detected_modifications,
)


class TTestType(Enum):
    welchs_t_test = "Welch's t-Test"
    students_t_test = "Student's t-Test"


class AnalysisLevel(Enum):
    # TODO: what/why?
    protein = "Protein"


class PValueCalculationMethod(Enum):
    auto = "Auto"
    exact = "Exact"
    asymptotic = "Asymptotic"


class YesNo(Enum):
    yes = "Yes"
    no = "No"


class ProteinsOfInterest(Enum):
    # TODO: Add the proteins of interest
    pass


class DynamicProteinFill(Enum):
    # TODO: Add the dynamic protein fill options
    pass


class SimilarityMeasure(Enum):
    euclidean_distance = "Euclidean Distance"
    cosine_similarity = "Cosine Similarity"


class ModelSelection(Enum):
    grid_search = "Grid search"
    randomized_search = "Randomized search"
    Manual = "Manual"


class ClusteringCriterion(Enum):
    gini = "gini"
    log_loss = "log_loss"
    entropy = "entropy"


class ClusteringScoring(Enum):
    adjusted_rand_score = "adjusted_rand_score"
    completeness_score = "completeness_score"
    fowlkes_mallows_score = "fowlkes_mallows_score"
    homogeneity_score = "homogeneity_score"
    mutual_info_score = "mutual_info_score"
    normalized_mutual_info_score = "normalized_mutual_info_score"
    rand_score = "rand_score"
    v_measure_score = "v_measure_score"


class InitCentroidStrategy(Enum):
    kmeans_plus_plus = "k-means++"
    random = "random"


class ClusteringCovarianceType(Enum):
    full = "full"
    tied = "tied"
    diag = "diag"
    spherical = "spherical"


class ClusteringInitParams(Enum):
    kmeans = "kmeans"
    kmeans_plus_plus = "kmeans++"
    random = "random"
    random_from_data = "random from data"


class ClusteringMetric(Enum):
    euclidean = "euclidean"
    manhattan = "manhattan"
    cosine = "cosine"
    l1 = "l1"
    l2 = "l2"


class ClusteringLinkage(Enum):
    ward = "ward"
    complete = "complete"
    average = "average"
    single = "single"


class ClassificationValidationStrategy(Enum):
    k_fold = "KFold"
    repeated_k_fold = "repeated K-Fold"
    stratified_k_fold = "Stratified K-Fold"
    leave_one_out = "Leave One Out"
    leave_p_out = "Leave P Out"
    manual = "Manual"


class ClassificationScoring(Enum):
    accuracy = "accuracy"
    precision = "precision"
    recall = "recall"
    mathews_correlation_coefficient = "mathews correlation coefficient"


class ClassificationKernel(Enum):
    linear = "linear"
    poly = "poly"
    rbf = "rbf"
    sigmoid = "sigmoid"
    precomputed = "precomputed"


class DimensionReductionMetric(Enum):
    euclidean = "euclidean"
    manhattan = "manhattan"
    cosine = "cosine"


class DataAnalysisStep(Step, ABC):
    section = Section.DATA_ANALYSIS

    def set_protein_ids_options(
        self, run: Run, protein_ids_field_name: str, input_key: DataKey
    ) -> None:
        protein_ids_field: DropdownField = self.form[protein_ids_field_name]

        df = self.get_input(run.steps, input_key)

        if df is not None:
            protein_ids = df["Protein ID"].unique().tolist()
            protein_ids_field.set_options(form_helper.to_choices(protein_ids))

    def set_grouping_options(
        self,
        run: Run,
        column_field_name: str = "grouping",
        include_sample: bool = False,
    ) -> None:
        column_field: DropdownField = self.form[column_field_name]

        metadata_source, source_handle = self.input_source(
            run.steps, DataKey.METADATA_DF
        )

        if metadata_source is not None:
            grouping_choices = form_helper.get_choices_for_metadata(
                run, metadata_source, source_handle, include_sample
            )

            column_field.set_options(grouping_choices)

    def set_selected_groups_options(
        self, run: Run, column_field: str, group_field: str, required: bool = True
    ) -> None:
        grouping: str | None = self.form[column_field].value
        selected_groups_field: MultiSelectField | DropdownField = self.form[group_field]

        metadata_source, source_handle = self.input_source(
            run.steps, DataKey.METADATA_DF
        )

        if (
            metadata_source is not None
            and source_handle is not None
            and grouping is not None
        ):
            selected_groups_field.set_options(
                form_helper.get_choices_for_groups(
                    run, metadata_source, source_handle, grouping, required
                )
            )

    def set_two_groups_options(self, run: Run) -> None:
        group1_field: DropdownField = self.form["group1"]
        group2_field: DropdownField = self.form["group2"]
        grouping: str = self.form["grouping"].value

        metadata_source, source_handle = self.input_source(
            run.steps, DataKey.METADATA_DF
        )

        if metadata_source is not None and source_handle is not None:
            groups_choices = form_helper.get_choices_for_groups(
                run, metadata_source, source_handle, grouping
            )

            # Set choices for group1 field based on selected grouping
            group1_field.set_options(groups_choices)

            # set choices for group2 field based on selected grouping and group1
            group2_field.set_options(
                [group for group in groups_choices if group.value != group1_field.value]
            )


class DifferentialExpressionIntensityStep(DataAnalysisStep, ABC):

    operation = "differential_expression"


class DifferentialExpressionPTMStep(DataAnalysisStep, ABC):

    operation = "Peptide analysis"


class DifferentialExpressionANOVA(DifferentialExpressionIntensityStep):
    display_name = "ANOVA"
    method_description = "A function that uses ANOVA to test the difference between two or more groups defined in the clinical data. The ANOVA test is conducted on the level of each protein. The p-values are corrected for multiple testing."

    output_keys = [
        "differentially_expressed_proteins_df",
        DataKey.SIGNIFICANT_PROTEINS_DF,
        "corrected_p_values_df",
    ]

    def create_form(self):
        return Form(
            label="ANOVA",
            input_fields=[
                DropdownField(
                    name="multiple_testing_correction_method",
                    label="Multiple testing correction",
                    options=MultipleTestingCorrectionMethod,
                    value=MultipleTestingCorrectionMethod.benjamini_hochberg,
                ),
                FloatField(
                    name="alpha",
                    label="Error rate (alpha)",
                    value=0.05,
                    min=0,
                    max=1,
                    step=0.01,
                    separatePrefix="\u03b1",
                ),
                DropdownField(name="grouping", label="Grouping from metadata"),
                MultiSelectField(
                    name="selected_groups", label="Select groups to perform ANOVA on"
                ),
            ],
        )

    @override
    def modify_form(self, run: Run) -> None:
        self.set_grouping_options(run)
        self.set_selected_groups_options(
            run, column_field="grouping", group_field="selected_groups"
        )

    calc_method = staticmethod(anova)


class DifferentialExpressionTTest(DifferentialExpressionIntensityStep):
    display_name = "t-Test"
    method_description = "A function to conduct a two sample t-test between groups defined in the clinical data. The t-test is conducted on the level of each protein. The p-values are corrected for multiple testing. The fold change is calculated by group2/group1."

    output_keys = [
        "differentially_expressed_proteins_df",
        DataKey.SIGNIFICANT_PROTEINS_DF,
        "corrected_p_values_df",
        "t_statistic_df",
        "log2_fold_change_df",
        "fc_significance_df",
    ]

    def create_form(self):
        return Form(
            label="t-Test",
            input_fields=[
                DropdownField(
                    name="ttest_type",
                    label="T-test type",
                    value=TTestType.welchs_t_test,
                    options=TTestType,
                ),
                DropdownField(
                    name="multiple_testing_correction_method",
                    label="Multiple testing correction",
                    value=MultipleTestingCorrectionMethod.benjamini_hochberg,
                    options=MultipleTestingCorrectionMethod,
                ),
                FloatField(
                    name="alpha",
                    label="Error rate (alpha)",
                    value=0.05,
                    min=0,
                    max=1,
                    step=0.01,
                    separatePrefix="\u03b1",
                ),
                DropdownField(
                    name="log_base",
                    label="Data log base",
                    value=LogBaseWithNoneType.NONE,
                    options=LogBaseWithNoneType,
                ),
                DropdownField(
                    name="grouping",
                    label="Grouping from metadata",
                ),
                DropdownField(
                    name="group1",
                    label="Group 1",
                ),
                DropdownField(
                    name="group2",
                    label="Group 2",
                ),
                CheckboxField(
                    name="fc_zscore_filter",
                    label="Fold-change Z-score significance",
                    value=False,
                ),
                FloatField(
                    name="fc_zscore_alpha",
                    label="Z-score tail cutoff",
                    value=0.05,
                    min=0,
                    max=0.5,
                    step=0.01,
                    separatePrefix="p",
                ),
            ],
        )

    @override
    def modify_form(self, run: Run) -> None:
        self.set_grouping_options(run)
        self.set_two_groups_options(run)

    calc_method = staticmethod(t_test)


class DifferentialExpressionLinearModel(DifferentialExpressionIntensityStep):
    display_name = "Linear Model"
    method_description = "A function to fit a linear model using ordinary least squares for each protein. The linear model fits the protein intensities on Y axis and the grouping on X for group1 X=-1 and group2 X=1. The p-values are corrected for multiple testing."

    output_keys = [
        "differentially_expressed_proteins_df",
        DataKey.SIGNIFICANT_PROTEINS_DF,
        "corrected_p_values_df",
        "log2_fold_change_df",
    ]

    def create_form(self):
        return Form(
            label="Linear Model",
            input_fields=[
                DropdownField(
                    name="multiple_testing_correction_method",
                    label="Multiple testing correction",
                    options=MultipleTestingCorrectionMethod,
                    value=MultipleTestingCorrectionMethod.benjamini_hochberg,
                ),
                FloatField(
                    name="alpha",
                    label="Error rate (alpha)",
                    value=0.05,
                    min=0,
                    max=1,
                    step=0.01,
                    separatePrefix="\u03b1",
                ),
                DropdownField(
                    name="log_base",
                    label="Data log base",
                    value=LogBaseWithNoneType.NONE,
                    options=LogBaseWithNoneType,
                ),
                DropdownField(
                    name="grouping",
                    label="Grouping from metadata",
                ),
                DropdownField(
                    name="group1",
                    label="Group 1",
                ),
                DropdownField(
                    name="group2",
                    label="Group 2",
                ),
            ],
        )

    @override
    def modify_form(self, run: Run) -> None:
        self.set_grouping_options(run)
        self.set_two_groups_options(run)

    calc_method = staticmethod(linear_model)


class DifferentialExpressionMannWhitneyOnIntensity(DifferentialExpressionIntensityStep):
    display_name = "Mann-Whitney Test"
    method_description = (
        "A function to conduct a Mann-Whitney U test between groups defined in the clinical data."
        "The p-values are corrected for multiple testing."
    )

    output_keys = [
        "differentially_expressed_proteins_df",
        DataKey.SIGNIFICANT_PROTEINS_DF,
        "corrected_p_values_df",
        "u_statistic_df",
        "log2_fold_change_df",
    ]

    def create_form(self):
        return Form(
            label="Mann-Whitney Test",
            input_fields=[
                DropdownField(
                    name="multiple_testing_correction_method",
                    label="Multiple testing correction",
                    value=MultipleTestingCorrectionMethod.benjamini_hochberg,
                    options=MultipleTestingCorrectionMethod,
                ),
                FloatField(
                    name="alpha",
                    label="Error rate (alpha)",
                    value=0.05,
                    min=0,
                    max=1,
                    step=0.01,
                    separatePrefix="\u03b1",
                ),
                DropdownField(
                    name="log_base",
                    label="Data log base",
                    value=LogBaseWithNoneType.NONE,
                    options=LogBaseWithNoneType,
                ),
                DropdownField(
                    name="p_value_calculation_method",
                    label="P-value calculation method",
                    options=PValueCalculationMethod,
                    value=PValueCalculationMethod.auto,
                ),
                DropdownField(
                    name="grouping",
                    label="Grouping from metadata",
                ),
                DropdownField(
                    name="group1",
                    label="Group 1",
                ),
                DropdownField(
                    name="group2",
                    label="Group 2",
                ),
            ],
        )

    @override
    def modify_form(self, run: Run) -> None:
        self.set_grouping_options(run)
        self.set_two_groups_options(run)

    calc_method = staticmethod(mann_whitney_test_on_intensity_data)


class DifferentialExpressionMannWhitneyOnPTM(DifferentialExpressionPTMStep):
    display_name = "Mann-Whitney Test"
    method_description = (
        "A function to conduct a Mann-Whitney U test between groups defined in the clinical data."
        "The p-values are corrected for multiple testing."
    )

    output_keys = [
        "differentially_expressed_ptm_df",
        "significant_ptm_df",
        "corrected_p_values_df",
        "u_statistic_df",
        "log2_fold_change_df",
    ]

    def create_form(self):
        return Form(
            label="Mann-Whitney Test",
            input_fields=[
                DropdownField(
                    name="multiple_testing_correction_method",
                    label="Multiple testing correction",
                    value=MultipleTestingCorrectionMethod.benjamini_hochberg,
                    options=MultipleTestingCorrectionMethod,
                ),
                FloatField(
                    name="alpha",
                    label="Error rate (alpha)",
                    value=0.05,
                    min=0,
                    max=1,
                    step=0.01,
                    separatePrefix="\u03b1",
                ),
                DropdownField(
                    name="log_base",
                    label="Data log base",
                    value=LogBaseWithNoneType.NONE,
                    options=LogBaseWithNoneType,
                ),
                DropdownField(
                    name="p_value_calculation_method",
                    label="P-value calculation method",
                    options=PValueCalculationMethod,
                    value=PValueCalculationMethod.auto,
                ),
                DropdownField(
                    name="grouping",
                    label="Grouping from metadata",
                ),
                DropdownField(
                    name="group1",
                    label="Group 1",
                ),
                DropdownField(
                    name="group2",
                    label="Group 2",
                ),
            ],
        )

    @override
    def modify_form(self, run: Run) -> None:
        self.set_grouping_options(run)
        self.set_two_groups_options(run)

    calc_method = staticmethod(mann_whitney_test_on_ptm_data)


class DifferentialExpressionKruskalWallisOnIntensity(
    DifferentialExpressionIntensityStep
):
    display_name = "Kruskal-Wallis Test"
    method_description = (
        "A function to conduct a Kruskal-Wallis test between groups defined in the clinical data."
        "The p-values are corrected for multiple testing."
    )

    output_keys = [
        "differentially_expressed_proteins_df",
        DataKey.SIGNIFICANT_PROTEINS_DF,
        "corrected_p_values_df",
        "h_statistic_df",
    ]

    def create_form(self):
        return Form(
            label="Kruskal-Wallis Test",
            input_fields=[
                DropdownField(
                    name="multiple_testing_correction_method",
                    label="Multiple testing correction",
                    options=MultipleTestingCorrectionMethod,
                    value=MultipleTestingCorrectionMethod.benjamini_hochberg,
                ),
                FloatField(
                    name="alpha",
                    label="Error rate (alpha)",
                    value=0.05,
                    min=0,
                    max=1,
                    step=0.01,
                    separatePrefix="\u03b1",
                ),
                DropdownField(name="grouping", label="Grouping from metadata"),
                MultiSelectField(
                    name="selected_groups",
                    label="Select groups to perform Kruskal-Wallis Test on",
                ),
            ],
        )

    @override
    def modify_form(self, run: Run) -> None:
        self.set_grouping_options(run)
        self.set_selected_groups_options(
            run, column_field="grouping", group_field="selected_groups"
        )

    calc_method = staticmethod(kruskal_wallis_test_on_intensity_data)


class DifferentialExpressionKruskalWallisOnPTM(DifferentialExpressionPTMStep):
    display_name = "Kruskal-Wallis Test"
    method_description = (
        "A function to conduct a Kruskal-Wallis test between groups defined in the clinical data."
        "The p-values are corrected for multiple testing."
    )

    output_keys = [
        "differentially_expressed_ptm_df",
        "significant_ptm_df",
        "corrected_p_values_df",
        "h_statistic_df",
    ]

    def create_form(self):
        return Form(
            label="Kruskal-Wallis Test",
            input_fields=[
                DropdownField(
                    name="multiple_testing_correction_method",
                    label="Multiple testing correction",
                    options=MultipleTestingCorrectionMethod,
                    value=MultipleTestingCorrectionMethod.benjamini_hochberg,
                ),
                FloatField(
                    name="alpha",
                    label="Error rate (alpha)",
                    value=0.05,
                    min=0,
                    max=1,
                    step=0.01,
                    separatePrefix="\u03b1",
                ),
                DropdownField(name="grouping", label="Grouping from metadata"),
                MultiSelectField(
                    name="selected_groups",
                    label="Select groups to perform Kruskal-Wallis Test on",
                ),
            ],
        )

    @override
    def modify_form(self, run: Run) -> None:
        self.set_grouping_options(run)
        self.set_selected_groups_options(
            run, column_field="grouping", group_field="selected_groups"
        )

    calc_method = staticmethod(kruskal_wallis_test_on_ptm_data)


class DataAnalysisPlotStep(DataAnalysisStep, ABC):

    operation = "plot"


# TODO: broken - needs decision regarding inclusion as plot method for relevant steps
class PlotVolcano(DataAnalysisPlotStep):
    display_name = "Volcano Plot"
    method_description = (
        "Plots the results of a differential expression analysis in a volcano plot. The x-axis shows "
        "the log2 fold change and the y-axis shows the -log10 of the corrected p-values. The user "
        "can define a fold change threshold and an alpha level to highlight significant items."
    )

    plot_method = staticmethod(create_volcano_plot)
    output_keys = []

    def create_form(self):
        return Form(
            label="Volcano Plot",
            input_fields=[
                DropdownField(
                    name="input_dict",
                    label="Input data dict (generated by t-Test or Linear Model Diff Exp)",
                ),
                FloatField(
                    name="fc_threshold",
                    label="Log2 fold change threshold",
                    value=0,
                    min=0,
                    step=0.1,
                ),
                MultiSelectField(
                    name="items_of_interest",
                    label="Items of interest (will be highlighted)",
                ),
            ],
        )

    @override
    def modify_form(self, run: Run) -> None:
        input_dict_field = self.form["input_dict"]
        items_of_interest_field = self.form["items_of_interest"]

        input_dict_field.set_options(
            form_helper.to_choices(
                run.steps.get_instance_identifiers(
                    step_type=Step,
                    output_key=["corrected_p_values_df", "log2_fold_change_df"],
                )
            )
        )

        if input_dict_field.value == None:
            return

        input_dict_instance_id = input_dict_field.value

        items_of_interest = []
        step_output = run.steps.get_step_output(
            output_key="differentially_expressed_proteins_df",
            instance_identifier=input_dict_instance_id,
        )
        if step_output is not None:
            items_of_interest = step_output["Protein ID"].unique()
        step_output = run.steps.get_step_output(
            output_key="differentially_expressed_ptm_df",
            instance_identifier=input_dict_instance_id,
        )
        if step_output is not None:
            items_of_interest = step_output["PTM"].unique()

        items_of_interest_field.set_options(form_helper.to_choices(items_of_interest))

    @override
    def insert_dataframes(self, steps: StepManager) -> None:
        source_id = self.inputs["input_dict"]
        self.inputs["p_values"] = steps.get_step_output(
            output_key="corrected_p_values_df",
            instance_identifier=source_id,
        )
        self.inputs["log2_fc"] = steps.get_step_output(
            output_key="log2_fold_change_df",
            instance_identifier=source_id,
        )

        for input_key in ["alpha", "group1", "group2"]:
            self.inputs[input_key] = steps.get_step_input(
                input_key=input_key, instance_identifier=source_id
            )

        source_operation = steps.get_step_operation(source_id)
        if source_operation == "differential_expression":
            self.inputs["item_type"] = "Protein ID"
        elif source_operation == "Peptide analysis":
            self.inputs["item_type"] = "PTM"


class PlotProteinCoverage(DataAnalysisPlotStep):
    display_name = "Protein Coverage Plot"
    method_description = (
        "Create a protein coverage plot from a protein graph and peptide data"
    )

    output_keys = []

    plot_method = staticmethod(plot_protein_coverage)

    def create_form(self):
        # noinspection SqlNoDataSourceInspection
        return Form(
            label="Protein Coverage Plot",
            input_fields=[
                DropdownField(
                    name="protein_id",
                    label="Protein ID",
                ),
                DropdownField(
                    name="grouping",
                    label="Grouping from metadata",
                ),
                MultiSelectField(
                    name="selected_groups",
                    label="Select which options from the grouping column should be included in the plot",
                ),
                DropdownField(
                    name="aggregation_method",
                    label="Aggregation method",
                    value=ProteinCoverageAggregationMethod.median.value,
                    options=ProteinCoverageAggregationMethod,
                ),
            ],
        )

    @override
    def modify_form(self, run: Run) -> None:
        protein_id_field: DropdownField = self.form["protein_id"]
        selected_groups_field: MultiSelectField = self.form["selected_groups"]

        peptide_df = self.get_input(run.steps, DataKey.PEPTIDE_DF)

        if peptide_df is not None:
            proteins_from_peptide_df = (
                set(peptide_df["Protein ID"].dropna().unique())
                if peptide_df is not None
                else set()
            )
            # Make sure that we have a unified representation of the canonical protein, which is sometimes given without
            # the -1 suffix. Only important for getting the correct sequence from the fasta file, so we don't need to
            # change it in the peptide_df
            proteins_from_peptide_df = {
                p if "-" in p else f"{p}-1" for p in proteins_from_peptide_df
            }

            fasta_df = self.get_input(run.steps, DataKey.FASTA_DF)
            proteins_from_fasta_df = (
                set(fasta_df["Protein ID"].unique()) if fasta_df is not None else set()
            )

            common_proteins = list(proteins_from_peptide_df & proteins_from_fasta_df)
            protein_id_field.set_options(form_helper.to_choices(common_proteins))

        # We specifically want to allow grouping by Sample here
        self.set_grouping_options(run, include_sample=True)
        grouping = self.form["grouping"].value
        if grouping == "Sample" and peptide_df is not None:
            selected_groups_field.set_options(
                form_helper.to_choices(peptide_df["Sample"].unique().tolist())
            )
        elif grouping is not None:
            metadata_df = self.get_input(run.steps, DataKey.METADATA_DF)
            if metadata_df is not None:
                selected_groups_field.set_options(
                    form_helper.to_choices(metadata_df[grouping].unique().tolist())
                )
        self.form["aggregation_method"].isVisible = grouping != "Sample"


class PlotScatterPlot(DataAnalysisPlotStep):
    display_name = "Scatter Plot"
    method_description = "Creates a scatter plot from data. This requires a dimension reduction method to be run first, as the input dataframe should contain only 2 or 3 columns."

    plot_method = staticmethod(scatter_plot)

    def create_form(self):
        return Form(
            label="Scatter Plot",
            input_fields=[
                DropdownField(
                    name="metadata_column",
                    label="Choose the column of the metadata dataframe that should be used for coloring",
                ),
            ],
        )

    @override
    def modify_form(self, run: Run) -> None:
        metadata_column_field: DropdownField = self.form["metadata_column"]
        metadata_source, source_handle = self.input_source(
            run.steps, DataKey.METADATA_DF
        )
        if metadata_source is not None and source_handle is not None:
            metadata_column_field.set_options(
                form_helper.get_choices_for_metadata(
                    run,
                    instance_identifier=metadata_source,
                    include_sample=False,
                    output_key=source_handle,
                )
            )


class PlotClustergram(DataAnalysisPlotStep):
    display_name = "Clustergram"
    operation = "plot"
    method_description = (
        "Creates a 2D clustergram from data using the samples on one axis and the proteins on the "
        "other axis. The data is clustered using euclidean distances for hierarchical clustering."
    )

    plot_method = staticmethod(clustergram_plot)

    # TODO: handle isRequired with metadata_df
    def create_form(self):
        return Form(
            label="Clustergram",
            input_fields=[
                DropdownField(
                    name="metadata_column",
                    label="Choose the column of the metadata dataframe that should be used for annotation",
                ),
                CheckboxField(
                    name="flip_axes",
                    label="Flip axis",
                    text="Flip axes",
                ),
                DropdownField(
                    name="imputation_strategy",
                    label="Impute missing values per protein by:",
                    value=SimpleImputerStrategyType.MEAN.value,
                    options=SimpleImputerStrategyType,
                ),
                TextField(
                    name="heatmap_legend_title",
                    label="Heatmap legend title",
                    value="Heatmap legend",
                ),
                CheckboxField(
                    name="use_custom_color_scale",
                    label="Use custom color scale",
                ),
                FloatField(
                    name="heatmap_low_color_limit",
                    label="Heatmap lower color limit",
                    isVisible=False,
                ),
                ColorField(
                    name="heatmap_low_color",
                    label="Heatmap lower color",
                    value=HEATMAP_LOW_COLOR,
                    isVisible=False,
                ),
                FloatField(
                    name="heatmap_high_color_limit",
                    label="Heatmap upper color limit",
                    isVisible=False,
                ),
                ColorField(
                    name="heatmap_high_color",
                    label="Heatmap upper color",
                    value=HEATMAP_HIGH_COLOR,
                    isVisible=False,
                ),
            ],
        )

    @override
    def modify_form(self, run: Run) -> None:
        metadata_column_field: DropdownField = self.form["metadata_column"]
        metadata_source, source_handle = self.input_source(
            run.steps, DataKey.METADATA_DF
        )
        if metadata_source is not None and source_handle is not None:
            metadata_column_field.set_options(
                form_helper.get_choices_for_metadata(
                    run,
                    instance_identifier=metadata_source,
                    include_sample=False,
                    output_key=source_handle,
                )
            )

        custom_scale_toggled = bool(self.form.values["use_custom_color_scale"])
        self.form["heatmap_low_color_limit"].isVisible = custom_scale_toggled
        self.form["heatmap_high_color_limit"].isVisible = custom_scale_toggled
        self.form["heatmap_low_color"].isVisible = custom_scale_toggled
        self.form["heatmap_high_color"].isVisible = custom_scale_toggled


class PlotProtQuant(DataAnalysisPlotStep):
    display_name = "Protein Quantification Plot"
    method_description = (
        "Creates a line chart for intensity across samples for protein groups"
    )

    output_keys = []

    def create_form(self):
        return Form(
            label="Protein Quantification Plot",
            input_fields=[
                DropdownField(
                    name="protein_group",
                    label="Protein group: choose highlighted protein group",
                ),
                DropdownField(
                    name="similarity_measure",
                    label="Similarity Measurement: choose how to compare protein groups",
                    value=SimilarityMeasure.euclidean_distance,
                    options=SimilarityMeasure,
                ),
                NumberField(
                    name="similarity",
                    label="Similarity",
                    value=1,
                    min=-1,
                    max=999,
                    step=1,
                    hasStepButtons=True,
                ),
            ],
        )

    @override
    def modify_form(self, run: Run) -> None:
        self.set_protein_ids_options(
            run, protein_ids_field_name="protein_group", input_key=DataKey.PROTEIN_DF
        )

        if (
            self.form["similarity_measure"].value
            == SimilarityMeasure.cosine_similarity.value
        ):
            # TODO: at least the labels in the form do not change in the frontend
            self.form["similarity"] = FloatField(
                name="similarity",
                label="Cosine Similarity",
                value=0,
                min=-1,
                max=1,
                step=0.1,
            )
        else:
            self.form["similarity"] = NumberField(
                name="similarity",
                label="Euclidean Distance",
                value=1,
                min=0,
                max=999,
                step=1,
            )

    plot_method = staticmethod(prot_quant_plot)


class PlotPrecisionRecallCurve(DataAnalysisPlotStep):
    display_name = "Precision Recall"
    method_description = "The precision-recall curve shows the tradeoff between precision and recall for different threshold"

    # Todo: output_keys

    calc_method = staticmethod(evaluate_classification_model)

    # TODO: adapt method parameters


class PlotROC(DataAnalysisStep):
    display_name = "Receiver Operating Characteristic curve"
    operation = "plot"
    method_description = "The ROC curve helps assess the model's ability to discriminate between positive and negative classes and determine an optimal threshold for decision making"

    # Todo: output_keys

    calc_method = staticmethod(evaluate_classification_model)

    # TODO: adapt method parameters


class PositiveLabelStep(DataAnalysisStep, ABC):

    @override
    def modify_form(self, run: Run) -> None:
        self.set_grouping_options(run, column_field_name="labels_column")
        self.set_selected_groups_options(
            run,
            column_field="labels_column",
            group_field="positive_label",
            required=False,
        )


class ClusteringStep(PositiveLabelStep, ABC):
    operation = "clustering"


class ClusteringKMeans(ClusteringStep):
    display_name = "KMeans"
    method_description = "Partitions a number of samples in k clusters using k-means"

    output_keys = [
        "model",
        "model_evaluation_df",
        "cluster_labels_df",
        "cluster_centers_df",
    ]

    calc_method = staticmethod(k_means)

    def create_form(self):
        return Form(
            label="kMeans",
            input_fields=[
                DropdownField(
                    name="labels_column",
                    label="Choose labels column from metadata",
                ),
                DropdownField(
                    name="positive_label",
                    label="Choose positive class",
                ),
                DropdownField(
                    name="model_selection",
                    label="Choose strategy to perform parameter fine-tuning",
                    options=ModelSelection,
                    value=ModelSelection.grid_search,
                ),
                DropdownField(
                    name="model_selection_scoring",
                    label="Select a scoring for identifying the best estimator following a parameter search (grid or randomized)",
                    options=ClusteringScoring,
                    value=ClusteringScoring.completeness_score,
                ),
                DropdownField(
                    name="scoring",
                    label="Scoring for the model",
                    options=ClusteringScoring,
                    value=ClusteringScoring.completeness_score,
                ),
                NumberField(
                    name="n_clusters",
                    label="Number of clusters to find",
                    min=1,
                    step=1,
                    value=8,
                ),
                NumberField(
                    name="random_state",
                    label="Seed for centroid initialisation",
                    min=0,
                    max=4294967295,
                    step=1,
                    value=0,
                ),
                DropdownField(
                    name="init_centroid_strategy",
                    label="Method for initialisation of centroids",
                    options=InitCentroidStrategy,
                    value=InitCentroidStrategy.random,
                ),
                NumberField(
                    name="n_init",
                    label="Number of times the k-means algorithm is run with different centroid seeds",
                    min=1,
                    step=1,
                    value=10,
                ),
                NumberField(
                    name="max_iter",
                    label="Maximum number of iterations of the k-means algorithm for a single run",
                    min=1,
                    step=1,
                    value=30,
                ),
                NumberField(
                    name="tolerance",
                    label="Relative tolerance with regards to Frobenius norm",
                    min=0,
                    value=1e-4,
                ),
                NumberField(
                    name="cv",
                    label="Number of cross-validation folds for grid search",
                    min=2,
                    value=5,
                    isVisible=False,
                ),
                NumberField(
                    name="n_iter",
                    label="Number of parameter settings sampled for randomized search",
                    min=1,
                    value=10,
                    isVisible=False,
                ),
            ],
        )

    @override
    def modify_form(self, run: Run) -> None:
        super().modify_form(run)

        model_selection_raw = self.form["model_selection"].value
        model_selection = getattr(model_selection_raw, "value", model_selection_raw)

        is_grid = model_selection == ModelSelection.grid_search.value
        is_random = model_selection == ModelSelection.randomized_search.value
        is_search = is_grid or is_random

        self.form["cv"].isVisible = is_grid
        self.form["n_iter"].isVisible = is_random
        self.form["model_selection_scoring"].isVisible = is_search


class ClusteringExpectationMaximisation(ClusteringStep):
    display_name = "Expectation-maximization (EM)"
    method_description = "A clustering algorithm that seeks to find the maximum likelihood estimates for a mixture of multivariate Gaussian distributions"

    output_keys = [
        "model",
        "model_evaluation_df",
        "cluster_labels_df",
        "cluster_labels_probabilities_df",
    ]

    calc_method = staticmethod(expectation_maximisation)

    def create_form(self):
        return Form(
            label="Expectation-maximization (EM)",
            input_fields=[
                DropdownField(
                    name="labels_column",
                    label="Choose labels column from metadata",
                ),
                DropdownField(
                    name="positive_label",
                    label="Choose positive class",
                ),
                DropdownField(
                    name="model_selection",
                    label="Choose strategy to perform parameter fine-tuning",
                    options=ModelSelection,
                    value=ModelSelection.grid_search,
                ),
                DropdownField(
                    name="model_selection_scoring",
                    label="Select a scoring for identifying the best estimator following a parameter search (grid or randomized)",
                    options=ClusteringScoring,
                    value=ClusteringScoring.completeness_score,
                ),
                DropdownField(
                    name="scoring",
                    label="Scoring for the model",
                    options=ClusteringScoring,
                    value=ClusteringScoring.completeness_score,
                ),
                NumberField(
                    name="n_components",
                    label="The number of mixture components",
                    value=1,
                ),
                NumberField(
                    name="reg_covar",
                    label="Non-negative regularization added to the diagonal of covariance",
                    value=1e-6,
                ),
                MultiSelectField(
                    name="covariance_type",
                    label="Type of covariance",
                    options=ClusteringCovarianceType,
                    value=ClusteringCovarianceType.full,
                ),
                MultiSelectField(
                    name="int_params",
                    label="The method used to initialize the weights, the means and the precisions.",
                    options=ClusteringInitParams,
                ),
                NumberField(
                    name="max_iter",
                    label="The number of EM iterations to perform",
                    value=100,
                ),
                NumberField(
                    name="random_state",
                    label="Seed for random number generation",
                    min=0,
                    max=4294967295,
                    step=1,
                    value=0,
                ),
                NumberField(
                    name="cv",
                    label="Number of cross-validation folds for grid search",
                    min=2,
                    value=5,
                    isVisible=False,
                ),
                NumberField(
                    name="n_iter",
                    label="Number of parameter settings sampled for randomized search",
                    min=1,
                    value=10,
                    isVisible=False,
                ),
            ],
        )

    @override
    def modify_form(self, run: Run) -> None:
        super().modify_form(run)

        model_selection_raw = self.form["model_selection"].value
        model_selection = getattr(model_selection_raw, "value", model_selection_raw)

        is_grid = model_selection == ModelSelection.grid_search.value
        is_random = model_selection == ModelSelection.randomized_search.value
        is_search = is_grid or is_random

        self.form["cv"].isVisible = is_grid
        self.form["n_iter"].isVisible = is_random
        self.form["model_selection_scoring"].isVisible = is_search


class ClusteringHierarchicalAgglomerative(ClusteringStep):
    display_name = "Hierarchical Agglomerative Clustering"
    method_description = (
        "Performs hierarchical clustering utilizing a bottom-up approach"
    )

    output_keys = [
        "model",
        "model_evaluation_df",
        "cluster_labels_df",
    ]

    def create_form(self):
        return Form(
            label="Hierarchical Agglomerative Clustering",
            input_fields=[
                DropdownField(
                    name="labels_column",
                    label="Choose labels column from metadata",
                ),
                DropdownField(
                    name="positive_label",
                    label="Choose positive class",
                ),
                DropdownField(
                    name="model_selection",
                    label="Choose strategy to perform parameter fine-tuning",
                    options=ModelSelection,
                    value=ModelSelection.grid_search,
                ),
                DropdownField(
                    name="model_selection_scoring",
                    label="Select a scoring for identifying the best estimator following a parameter search (grid or randomized)",
                    options=ClusteringScoring,
                    value=ClusteringScoring.completeness_score,
                ),
                DropdownField(
                    name="scoring",
                    label="Scoring for the model",
                    options=ClusteringScoring,
                    value=ClusteringScoring.completeness_score,
                ),
                NumberField(
                    name="n_clusters",
                    label="The number of clusters to find",
                    min=1,
                    step=1,
                    value=2,
                ),
                MultiSelectField(
                    name="metric",
                    label="Distance metric",
                    options=ClusteringMetric,
                    value=ClusteringMetric.euclidean,
                ),
                MultiSelectField(
                    name="linkage",
                    label="The linkage criterion to use in order to to determine the distance to use between sets of observation",
                    options=ClusteringLinkage,
                    value=ClusteringLinkage.ward,
                ),
                NumberField(
                    name="cv",
                    label="Number of cross-validation folds for grid search",
                    min=2,
                    value=5,
                    isVisible=False,
                ),
                NumberField(
                    name="n_iter",
                    label="Number of parameter settings sampled for randomized search",
                    min=1,
                    value=10,
                    isVisible=False,
                ),
            ],
        )

    @override
    def modify_form(self, run: Run) -> None:
        super().modify_form(run)

        model_selection_raw = self.form["model_selection"].value
        model_selection = getattr(model_selection_raw, "value", model_selection_raw)

        is_grid = model_selection == ModelSelection.grid_search.value
        is_random = model_selection == ModelSelection.randomized_search.value
        is_search = is_grid or is_random

        self.form["cv"].isVisible = is_grid
        self.form["n_iter"].isVisible = is_random
        self.form["model_selection_scoring"].isVisible = is_search

    calc_method = staticmethod(hierarchical_agglomerative_clustering)


class ClassificationStep(PositiveLabelStep, ABC):
    operation = "classification"


class ClassificationRandomForest(ClassificationStep):
    display_name = "Random Forest"
    method_description = "A random forest is a meta estimator that fits a number of decision tree classifiers on various sub-samples of the dataset and uses averaging to improve the predictive accuracy and control over-fitting."

    output_keys = [
        "model",
        "model_evaluation_df",
        "X_train_df",
        "X_test_df",
        "y_train_df",
        "y_test_df",
    ]

    def create_form(self):
        return Form(
            label="Random Forest",
            input_fields=[
                DropdownField(
                    name="labels_column",
                    label="Choose labels column from metadata",
                ),
                DropdownField(
                    name="positive_label",
                    label="Choose positive class",
                ),
                NumberField(
                    name="test_size",
                    label="Test size",
                    min=0,
                    value=0.20,
                ),
                DropdownField(
                    name="split_stratisfy",
                    label="Stratify the split",
                    options=YesNo,
                    value=YesNo.yes,
                ),
                DropdownField(
                    name="validation_strategy",
                    label="Validation strategy",
                    options=ClassificationValidationStrategy,
                    value=ClassificationValidationStrategy.k_fold,
                ),
                NumberField(
                    name="train_val_split",
                    label="Choose the size of the validation data set (you can either enter the absolute number of validation "
                    "samples or a number between 0.0 and 1.0 to represent the percentage of validation samples)",
                    value=0.20,
                    isVisible=False,
                ),
                NumberField(
                    name="n_splits",
                    label="Number of folds",
                    min=2,
                    value=5,
                    isVisible=False,
                ),
                DropdownField(
                    name="shuffle",
                    label="Whether to shuffle the data before splitting into batches",
                    options=YesNo,
                    value=YesNo.yes,
                    isVisible=False,
                ),
                NumberField(
                    name="n_repeats",
                    label="Number of times cross-validator needs to be repeated",
                    min=1,
                    value=10,
                    isVisible=False,
                ),
                NumberField(
                    name="random_state_cv",
                    label="Seed for random number generation",
                    min=0,
                    max=4294967295,
                    step=1,
                    value=42,
                ),
                NumberField(
                    name="p_samples",
                    label="Size of the test sets",
                    value=1,
                    isVisible=False,
                ),
                MultiSelectField(
                    name="scoring",
                    label="Scoring for the model",
                    options=ClassificationScoring,
                    value=ClassificationScoring.accuracy,
                ),
                DropdownField(
                    name="model_selection",
                    label="Choose strategy to perform parameter fine-tuning",
                    options=ModelSelection,
                    value=ModelSelection.grid_search,
                ),
                DropdownField(
                    name="model_selection_scoring",
                    label="Select a scoring for identifying the best estimator following a grid search",
                    options=ClassificationScoring,
                    value=ClassificationScoring.accuracy,
                ),
                NumberField(
                    name="n_estimators",
                    label="The number of trees in the forest",
                    min=1,
                    step=1,
                    value=100,
                ),
                MultiSelectField(
                    name="criterion",
                    label="The function to measure the quality of a split",
                    options=ClusteringCriterion,
                    value=ClusteringCriterion.gini,
                ),
                NumberField(
                    name="max_depth",
                    label="The maximum depth of the tree",
                    min=1,
                    value=1,
                ),
                NumberField(
                    name="random_state",
                    label="Seed for random number generation",
                    min=0,
                    max=4294967295,
                    step=1,
                    value=6,
                ),
            ],
        )

    @override
    def modify_form(self, run: Run) -> None:
        validation_strategy_field: DropdownField = self.form["validation_strategy"]
        train_val_split_field: NumberField = self.form["train_val_split"]
        n_splits_field: NumberField = self.form["n_splits"]
        shuffle_field: DropdownField = self.form["shuffle"]
        n_repeats_field: NumberField = self.form["n_repeats"]
        p_samples_field: NumberField = self.form["p_samples"]

        if validation_strategy_field.value in [
            ClassificationValidationStrategy.k_fold.value,
            ClassificationValidationStrategy.stratified_k_fold.value,
        ]:
            n_splits_field.isVisible = True
            shuffle_field.isVisible = True
        elif (
            validation_strategy_field.value
            == ClassificationValidationStrategy.repeated_k_fold.value
        ):
            n_splits_field.isVisible = True
            shuffle_field.isVisible = True
            n_repeats_field.isVisible = True
        elif (
            validation_strategy_field.value
            == ClassificationValidationStrategy.leave_p_out.value
        ):
            p_samples_field.isVisible = True
        elif (
            validation_strategy_field.value
            == ClassificationValidationStrategy.manual.value
        ):
            train_val_split_field.isVisible = True

    calc_method = staticmethod(random_forest)


class ClassificationSVM(ClassificationStep):
    display_name = "Support Vector Machine"
    method_description = "A support vector machine constructs a hyperplane or set of hyperplanes in a high- or infinite-dimensional space, which can be used for classification."

    output_keys = [
        "model",
        "model_evaluation_df",
        "X_train_df",
        "X_test_df",
        "y_train_df",
        "y_test_df",
    ]

    def create_form(self):
        return Form(
            label="Support Vector Machine",
            input_fields=[
                DropdownField(
                    name="labels_column",
                    label="Choose labels column from metadata",
                ),
                DropdownField(
                    name="positive_label",
                    label="Choose positive class",
                ),
                NumberField(
                    name="test_size",
                    label="Test size",
                    min=0,
                    value=0.20,
                ),
                DropdownField(
                    name="split_stratisfy",
                    label="Stratify the split",
                    options=YesNo,
                    value=YesNo.yes,
                ),
                DropdownField(
                    name="validation_strategy",
                    label="Validation strategy",
                    options=ClassificationValidationStrategy,
                    value=ClassificationValidationStrategy.k_fold,
                ),
                NumberField(
                    name="train_val_split",
                    label="Choose the size of the validation data set (you can either enter the absolute number of validation "
                    "samples or a number between 0.0 and 1.0 to represent the percentage of validation samples)",
                    value=0.20,
                    isVisible=False,
                ),
                NumberField(
                    name="n_splits",
                    label="Number of folds",
                    min=2,
                    value=5,
                    isVisible=False,
                ),
                DropdownField(
                    name="shuffle",
                    label="Whether to shuffle the data before splitting into batches",
                    options=YesNo,
                    value=YesNo.yes,
                    isVisible=False,
                ),
                NumberField(
                    name="n_repeats",
                    label="Number of times cross-validator needs to be repeated",
                    min=1,
                    value=10,
                    isVisible=False,
                ),
                NumberField(
                    name="random_state_cv",
                    label="Seed for random number generation",
                    min=0,
                    max=4294967295,
                    step=1,
                    value=42,
                ),
                NumberField(
                    name="p_samples",
                    label="Size of the test sets",
                    value=1,
                    isVisible=False,
                ),
                MultiSelectField(
                    name="scoring",
                    label="Scoring for the model",
                    options=ClassificationScoring,
                    value=ClassificationScoring.accuracy,
                ),
                DropdownField(
                    name="model_selection",
                    label="Choose strategy to perform parameter fine-tuning",
                    options=ModelSelection,
                    value=ModelSelection.grid_search,
                ),
                DropdownField(
                    name="model_selection_scoring",
                    label="Select a scoring for identifying the best estimator following a grid search",
                    options=ClassificationScoring,
                    value=ClassificationScoring.accuracy,
                ),
                NumberField(
                    name="C",
                    label="C: regularization parameter (the strength of the regularization is inversely proportional to C)",
                    min=0.0,
                    value=1.0,
                ),
                MultiSelectField(
                    name="kernel",
                    label="Specifies the kernel type to be used in the algorithm",
                    options=ClassificationKernel,
                    value=ClassificationKernel.linear,
                ),
                NumberField(
                    name="tolerance",
                    label="Tolerance for stopping criterion",
                    min=0.0,
                    value=1e-4,
                ),
                NumberField(
                    name="random_state",
                    label="Seed for random number generation",
                    min=0.0,
                    max=4294967295,
                    step=1,
                    value=6,
                ),
            ],
        )

    @override
    def modify_form(self, run: Run) -> None:
        validation_strategy_field: DropdownField = self.form["validation_strategy"]
        train_val_split_field: NumberField = self.form["train_val_split"]
        n_splits_field: NumberField = self.form["n_splits"]
        shuffle_field: DropdownField = self.form["shuffle"]
        n_repeats_field: NumberField = self.form["n_repeats"]
        p_samples_field: NumberField = self.form["p_samples"]

        if validation_strategy_field.value in [
            ClassificationValidationStrategy.k_fold.value,
            ClassificationValidationStrategy.stratified_k_fold.value,
        ]:
            n_splits_field.isVisible = True
            shuffle_field.isVisible = True
        elif (
            validation_strategy_field.value
            == ClassificationValidationStrategy.repeated_k_fold.value
        ):
            n_splits_field.isVisible = True
            shuffle_field.isVisible = True
            n_repeats_field.isVisible = True
        elif (
            validation_strategy_field.value
            == ClassificationValidationStrategy.leave_p_out.value
        ):
            p_samples_field.isVisible = True
        elif (
            validation_strategy_field.value
            == ClassificationValidationStrategy.manual.value
        ):
            train_val_split_field.isVisible = True

    calc_method = staticmethod(svm)


class ModelEvaluationClassificationModel(DataAnalysisStep):
    display_name = "Evaluation of classification models"
    operation = "model_evaluation"
    method_description = "Assessing an already trained classification model on separate testing data using widely used scoring metrics"

    output_keys = ["scores_df"]

    def create_form(self):
        return Form(
            label="Evaluation of classification models",
            input_fields=[
                MultiSelectField(
                    name="scoring",
                    label="Scoring for the model",
                    options=ClassificationScoring,
                    value=ClassificationScoring.accuracy,
                ),
            ],
        )

    # TODO: This is completely broken. Method code is from 2023 and expects data that doesn't get set
    calc_method = staticmethod(evaluate_classification_model)


class DimensionReductionTSNE(DataAnalysisStep):
    display_name = "t-SNE"
    operation = "dimension_reduction"
    method_description = "Dimension reduction of a dataframe using t-SNE"

    output_keys = ["embedded_data"]

    def create_form(self):
        return Form(
            label="t-SNE",
            input_fields=[
                HeaderInfoField(
                    label="This step only performs the calculation for the dimension reduction using t-SNE. To "
                    "visualise the results, please use the 'Scatter Plot' step afterwards.",
                ),
                NumberField(
                    name="n_components",
                    label="Dimension of the embedded space",
                    min=1,
                    max=3,
                    step=1,
                    value=2,
                ),
                NumberField(
                    name="perplexity",
                    label="Perplexity",
                    min=5.0,
                    max=50.0,
                    value=30.0,
                ),
                DropdownField(
                    name="method",
                    label="Gradient calculation method",
                    options=TSNEMethod,
                ),
                DropdownField(
                    name="metric",
                    label="Distance metric",
                    options=DimensionReductionMetric,
                ),
                NumberField(
                    name="random_state",
                    label="Seed for random number generation",
                    min=0,
                    max=4294967295,
                    step=1,
                    value=6,
                ),
                NumberField(
                    name="max_iter",
                    label="Maximum number of iterations for the optimization",
                    min=250,
                    value=1000,
                ),
                NumberField(
                    name="n_iter_without_progress",
                    label="Maximum number of iterations without progress before we abort the optimization",
                    min=250,
                    step=1,
                    value=300,
                ),
            ],
        )

    # TODO: This method has the option to set a method (via a string), currently defaults to barnes_hut
    calc_method = staticmethod(t_sne)


class DimensionReductionUMAP(DataAnalysisStep):
    display_name = "UMAP"
    operation = "dimension_reduction"
    method_description = "Dimension reduction of a dataframe using UMAP"

    output_keys = ["embedded_data"]

    def create_form(self):
        return Form(
            label="UMAP",
            input_fields=[
                HeaderInfoField(
                    label="This step only performs the calculation for the dimension reduction using UMAP. To "
                    "visualise the results, please use the 'Scatter Plot' step afterwards.",
                ),
                NumberField(
                    name="n_neighbors",
                    label="The size of local neighborhood (in terms of number of neighboring sample points) used for manifold "
                    "approximation",
                    min=2,
                    max=100,
                    step=1,
                    value=15,
                ),
                NumberField(
                    name="n_components",
                    label="Number of components",
                    min=1,
                    max=100,
                    step=1,
                    value=2,
                ),
                FloatField(
                    name="min_dist",
                    label="The effective minimum distance between embedded points",
                    min=0.1,
                    step=0.1,
                    value=0.1,
                ),
                DropdownField(
                    name="metric",
                    label="Distance metric",
                    options=DimensionReductionMetric,
                ),
                NumberField(
                    name="random_state",
                    label="Seed for random number generation",
                    min=0,
                    max=4294967295,
                    step=1,
                    value=42,
                ),
                NumberField(
                    name="transform_seed",
                    label="Seed for stochastic aspects of the transform operation",
                    min=0,
                    max=4294967295,
                    step=1,
                    value=42,
                ),
            ],
        )

    calc_method = staticmethod(umap)


class BaseFLEXLF(DataAnalysisStep, ABC):
    """
    A base class for FLEXIQuantLF and MultiFLEXLF to reduce code duplication.
    """

    @override
    def modify_form(self, run: Run) -> None:
        self.set_grouping_options(run, column_field_name="grouping_column")
        self.set_selected_groups_options(
            run, column_field="grouping_column", group_field="reference_group"
        )

    def get_base_form_fields(self) -> list[InputField]:
        return [
            DropdownField(
                name="grouping_column",
                label="Grouping column in metadata",
            ),
            DropdownField(
                name="reference_group",
                label="Reference group",
            ),
            NumberField(
                name="num_init",
                label="Number of RANSAC initiations",
                value=30,
                min=1,
                max=60,
                step=1,
            ),
            FloatField(
                name="mod_cutoff", label="Modification cutoff", value=0.5, min=0, max=1
            ),
        ]


class FLEXIQuantLF(BaseFLEXLF):
    display_name = "FLEXIQuant-LF"
    operation = "modification_quantification"
    method_description = (
        "FLEXIQuant-LF is an unbiased, label-free computational tool to indirectly detect modified "
        "peptides and to quantify the degree of modification based solely on the unmodified peptide "
        "species."
    )

    output_keys = [
        "raw_scores",
        "RM_scores",
        "diff_modified",
        "removed_peptides",
    ]

    plot_method = staticmethod(flexiquant_lf)

    def create_form(self):
        return Form(
            label="FLEXIQuant-LF",
            input_fields=[
                DropdownField(
                    name="protein_group",
                    label="Protein Group",
                )
            ]
            + self.get_base_form_fields(),
        )

    @override
    def modify_form(self, run: Run) -> None:
        super().modify_form(run)
        self.set_protein_ids_options(run, "protein_group", DataKey.PEPTIDE_DF)


class MultiFLEXLF(BaseFLEXLF):
    display_name = "MultiFLEX-LF"
    operation = "modification_quantification"
    method_description = (
        "Quantifies the extent of protein modifications in proteomics data by using robust linear "
        "regression to compare modified and unmodified peptide precursors and facilitates the "
        "analysis of modification dynamics and coregulated modifications across large datasets "
        "without the need for preselecting specific proteins."
    )

    output_keys = [
        "RM_scores_clustered",
        "diff_modified",
        "raw_scores",
        "removed_peptides",
        "RM_scores",
        "skipped_proteins",
    ]

    plot_method = staticmethod(multiflex_lf)

    def create_form(self):
        return Form(
            label="multiFLEX-LF",
            input_fields=self.get_base_form_fields()
            + [
                FloatField(
                    name="imputation_cosine_similarity",
                    label="Cosine similarity for imputation",
                    value=0.98,
                    min=0,
                    max=1,
                ),
                CheckboxField(
                    name="deseq2_normalization",
                    label="DESeq2 normalization",
                    text="Use DESeq2 normalization",
                ),
                DropdownField(
                    name="colormap",
                    label="Color Map for Heatmap",
                    options=MultiFlexColorMaps,
                ),
            ],
        )


class PeptideAnalysisStep(DataAnalysisStep, ABC):
    operation = "Peptide analysis"


class PTMsPerSample(PeptideAnalysisStep):
    display_name = "PTMs per Sample"
    operation = "Peptide analysis"
    method_description = (
        "Analyze the post-translational modifications (PTMs) of a single protein of interest. "
        "This function requires a peptide dataframe with PTM information."
    )

    output_keys = [
        DataKey.PTM_DF,
    ]

    def create_form(self):
        return Form(
            label="PTMs per Sample",
            input_fields=[],
        )

    calc_method = staticmethod(ptms_per_sample)


class PTMsProteinAndPerSample(PeptideAnalysisStep):
    display_name = "PTMs per Sample and Protein"
    operation = "Peptide analysis"
    method_description = (
        "Analyze the post-translational modifications (PTMs) of all Proteins. "
        "This function requires a peptide dataframe with PTM information."
    )

    output_keys = [
        DataKey.PTM_DF,
    ]

    def create_form(self):
        return Form(
            label="PTMs per Sample and Protein",
            input_fields=[],
        )

    calc_method = staticmethod(ptms_per_protein_and_sample)


class _PTMVisualizationStep(DataAnalysisPlotStep, ABC):
    output_keys = []

    @classmethod
    def get_form_fields(cls) -> list[FormField]:
        return [
            FloatField(
                name="evidence_file_q_value_threshold",
                label="MaxQuant Evidence file q-value threshold",
                min=0.0,
                max=1.0,
                value=0.01,
                hasStepButtons=False,
            ),
            FileInput(
                name="fasta_file_path",
                label="FASTA file",
            ),
            FileInput(
                name="regions_file_path",
                label="Metadata used to define regions",
            ),
            InfoField(
                label="The file for regions should be a CSV file with the following columns: name, region_end, "
                "group, short_name. These specify the name of the region, the end position of the region "
                "(the start is either 1 or the end of the previous region), the (colour) group the "
                "region belongs to (which can be specified in the settings), and a short name for the "
                "region.",
            ),
        ]


class PTMOverviewVisualization(_PTMVisualizationStep):
    display_name = "PTM Visualization - Overview Plot"
    method_description = (
        "Visualizes selected PTMs on a given protein sequence (including isoforms)"
    )

    calc_method = staticmethod(get_detected_modifications)
    plot_method = staticmethod(create_overview_ptm_visualization)

    def create_form(self):
        return Form(
            label="PTM Overview Visualization",
            input_fields=_PTMVisualizationStep.get_form_fields(),
        )


class _PTMVisualizationWithGroups(_PTMVisualizationStep):
    @override
    @classmethod
    def get_form_fields(cls) -> list[FormField]:
        return _PTMVisualizationStep.get_form_fields() + [
            FileInput(
                name="groups_file_path",
                label="Metadata used to define groups",
            ),
            InfoField(
                label="The groups file should be a CSV file with the following columns: file_name, group_name, "
                "replicate. These specify the name of the name of the experiment in the evidence file (not "
                "raw file name), the name that should be displayed when referencing the group, and "
                "optionally the replicate number (1, 2, ...).",
            ),
        ]

    calc_method = staticmethod(get_detected_modifications)


class PTMBarVisualization(_PTMVisualizationWithGroups):
    display_name = "PTM Visualization - Bar Plot"
    method_description = (
        "Visualizes selected PTMs on a given protein sequence (including isoforms). Additionally, "
        "shows PTM frequency across groups as a bar plot."
    )

    plot_method = staticmethod(create_bar_ptm_visualization)

    def create_form(self):
        return Form(
            label="PTM Bar Visualization",
            input_fields=_PTMVisualizationWithGroups.get_form_fields(),
        )


class PTMDetailsVisualization(_PTMVisualizationWithGroups):
    display_name = "PTM Visualization - Details Plot"
    method_description = (
        "Visualizes selected PTMs on a given protein sequence (including isoforms). Additionally, "
        "shows PTM and cleavage frequency across groups as heatmaps."
    )

    plot_method = staticmethod(create_details_ptm_visualization)

    def create_form(self):
        return Form(
            label="PTM Details Visualization",
            input_fields=_PTMVisualizationWithGroups.get_form_fields(),
        )
