import logging

from backend.protzilla import form_helper
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
    select_peptides_of_protein,
    ptms_per_protein_and_sample,
    ptms_per_sample,
)
from backend.protzilla.data_analysis.ptm_visualization import (
    create_bar_ptm_visualization,
)
from backend.protzilla.form import *
from backend.protzilla.methods.data_preprocessing import (
    DataPreprocessingStep,
)
from backend.protzilla.methods.data_preprocessing import TransformationLog
from backend.protzilla.steps import Step, StepManager
from protzilla.data_analysis.protein_coverage import (
    plot_protein_coverage,
    AggregationMethod as ProteinCoverageAggregationMethod,
)
from protzilla.data_analysis.ptm_quantification.flexiquant import flexiquant_lf
from protzilla.data_analysis.ptm_quantification.multiflex import (
    multiflex_lf,
    MultiFlexColorMaps,
)
from protzilla.data_analysis.ptm_visualization import (
    create_overview_ptm_visualization,
    create_details_ptm_visualization,
)
from protzilla.data_analysis.ptm_visualization.ptm_overview_plot import (
    get_detected_modifications,
)
from protzilla.methods.importing import MetadataImport


class TTestType(Enum):
    welchs_t_test = "Welch's t-Test"
    students_t_test = "Student's t-Test"


class AnalysisLevel(Enum):
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
    euclidean_distance = "euclidean distance"
    cosine_similarity = "cosine similarity"


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


class DataAnalysisStep(Step):
    section = "data_analysis"

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        return inputs


class DifferentialExpressionANOVA(DataAnalysisStep):
    display_name = "ANOVA"
    operation = "differential_expression"
    method_description = "A function that uses ANOVA to test the difference between two or more groups defined in the clinical data. The ANOVA test is conducted on the level of each protein. The p-values are corrected for multiple testing."

    output_keys = [
        "differentially_expressed_proteins_df",
        "significant_proteins_df",
        "corrected_p_values_df",
        "sample_group_df",
        "corrected_alpha",
        "filtered_proteins",
    ]

    def create_form(self):
        return Form(
            label="ANOVA",
            input_fields=[
                DropdownField(
                    name="protein_df", label="Step to use protein intensities from"
                ),
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

    def modify_form(self, form, run):
        protein_df_field = form["protein_df"]
        grouping_field = form["grouping"]
        selected_groups_field = form["selected_groups"]

        protein_df_field.set_options(form_helper.get_choices_for_protein_df_steps(run))
        grouping_field.set_options(
            form_helper.get_choices_for_metadata_non_sample_columns(run)
        )
        grouping = grouping_field.value
        selected_groups_field.set_options(
            form_helper.to_choices(run.steps.metadata_df[grouping].unique())
        )

    calc_method = staticmethod(anova)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["log_base"] = steps.get_step_input(TransformationLog, "log_base")
        inputs["intensity_df"] = steps.get_step_output(
            Step, "protein_df", inputs["protein_df"]
        )
        inputs["metadata_df"] = steps.metadata_df
        return inputs


class DifferentialExpressionTTest(DataAnalysisStep):
    display_name = "t-Test"
    operation = "differential_expression"
    method_description = "A function to conduct a two sample t-test between groups defined in the clinical data. The t-test is conducted on the level of each protein. The p-values are corrected for multiple testing. The fold change is calculated by group2/group1."

    output_keys = [
        "differentially_expressed_proteins_df",
        "significant_proteins_df",
        "corrected_p_values_df",
        "t_statistic_df",
        "log2_fold_change_df",
        "corrected_alpha",
        "fc_significance_df",
        "fc_zscore_alpha",
        "fc_zscore_filter",
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
                    name="protein_df",
                    label="Step to use protein intensities from",
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

    def modify_form(self, form, run):
        protein_field = form["protein_df"]
        grouping_field = form["grouping"]
        group1_field = form["group1"]
        group2_field = form["group2"]

        protein_field.set_options(form_helper.get_choices_for_protein_df_steps(run))
        grouping_field.set_options(
            form_helper.get_choices_for_metadata_non_sample_columns(run)
        )

        if grouping_field.options == []:
            return

        grouping = grouping_field.value

        # Set choices for group1 field based on selected grouping
        group1_field.set_options(
            form_helper.to_choices(run.steps.metadata_df[grouping].unique())
        )

        # set choices for group2 field based on selected grouping and group1
        if group1_field.value in run.steps.metadata_df[grouping].unique():
            group2_field.set_options(
                [
                    Option(el, el)
                    for el in run.steps.metadata_df[grouping].unique()
                    if el != group1_field.value
                ]
            )
        else:
            group2_field.set_options(
                list(
                    reversed(
                        form_helper.to_choices(run.steps.metadata_df[grouping].unique())
                    )
                )
            )

    calc_method = staticmethod(t_test)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["log_base"] = steps.get_step_input(TransformationLog, "log_base")
        inputs["intensity_df"] = steps.get_step_output(
            Step, "protein_df", inputs["protein_df"]
        )
        inputs["metadata_df"] = steps.metadata_df
        return inputs


class DifferentialExpressionLinearModel(DataAnalysisStep):
    display_name = "Linear Model"
    operation = "differential_expression"
    method_description = "A function to fit a linear model using ordinary least squares for each protein. The linear model fits the protein intensities on Y axis and the grouping on X for group1 X=-1 and group2 X=1. The p-values are corrected for multiple testing."

    output_keys = [
        "differentially_expressed_proteins_df",
        "significant_proteins_df",
        "corrected_p_values_df",
        "log2_fold_change_df",
        "corrected_alpha",
        "filtered_proteins",
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

    def modify_form(self, form, run):
        grouping_field = form["grouping"]
        group1_field = form["group1"]
        group2_field = form["group2"]

        grouping_field.set_options(
            form_helper.get_choices_for_metadata_non_sample_columns(run)
        )

        if grouping_field.options == []:
            return

        grouping = grouping_field.value

        # Set choices for group1 field based on selected grouping
        group1_field.set_options(
            form_helper.to_choices(run.steps.metadata_df[grouping].unique())
        )

        # set choices for group2 field based on selected grouping and group1
        if group1_field.value in run.steps.metadata_df[grouping].unique():
            group2_field.set_options(
                [
                    Option(el, el)
                    for el in run.steps.metadata_df[grouping].unique()
                    if el != group1_field.value
                ]
            )
        else:
            group2_field.set_options(
                list(
                    reversed(
                        form_helper.to_choices(run.steps.metadata_df[grouping].unique())
                    )
                )
            )

    calc_method = staticmethod(linear_model)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["log_base"] = steps.get_step_input(TransformationLog, "log_base")
        inputs["intensity_df"] = steps.protein_df
        inputs["metadata_df"] = steps.metadata_df
        return inputs


class DifferentialExpressionMannWhitneyOnIntensity(DataAnalysisStep):
    display_name = "Mann-Whitney Test"
    operation = "differential_expression"
    method_description = (
        "A function to conduct a Mann-Whitney U test between groups defined in the clinical data."
        "The p-values are corrected for multiple testing."
    )

    output_keys = [
        "differentially_expressed_proteins_df",
        "significant_proteins_df",
        "corrected_p_values_df",
        "u_statistic_df",
        "log2_fold_change_df",
        "corrected_alpha",
    ]

    def create_form(self):
        return Form(
            label="Mann-Whitney Test",
            input_fields=[
                DropdownField(
                    name="protein_df",
                    label="Step to use protein intensities from",
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

    def modify_form(self, form, run):
        protein_field = form["protein_df"]
        grouping_field = form["grouping"]
        group1_field = form["group1"]
        group2_field = form["group2"]

        protein_field.set_options(form_helper.get_choices_for_protein_df_steps(run))
        grouping_field.set_options(
            form_helper.get_choices_for_metadata_non_sample_columns(run)
        )

        if grouping_field.options == []:
            return

        grouping = grouping_field.value

        # Set choices for group1 field based on selected grouping
        group1_field.set_options(
            form_helper.to_choices(run.steps.metadata_df[grouping].unique())
        )

        # set choices for group2 field based on selected grouping and group1
        if group1_field.value in run.steps.metadata_df[grouping].unique():
            group2_field.set_options(
                [
                    Option(el, el)
                    for el in run.steps.metadata_df[grouping].unique()
                    if el != group1_field.value
                ]
            )
        else:
            group2_field.set_options(
                list(
                    reversed(
                        form_helper.to_choices(run.steps.metadata_df[grouping].unique())
                    )
                )
            )

    calc_method = staticmethod(mann_whitney_test_on_intensity_data)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        if steps.get_step_output(Step, "protein_df", inputs["protein_df"]) is not None:
            inputs["protein_df"] = steps.get_step_output(
                Step, "protein_df", inputs["protein_df"]
            )
        inputs["metadata_df"] = steps.metadata_df
        inputs["log_base"] = steps.get_step_input(TransformationLog, "log_base")
        return inputs


class DifferentialExpressionMannWhitneyOnPTM(DataAnalysisStep):
    display_name = "Mann-Whitney Test"
    operation = "Peptide analysis"
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
        "corrected_alpha",
    ]

    def create_form(self):
        return Form(
            label="Mann-Whitney Test",
            input_fields=[
                DropdownField(
                    name="ptm_df",
                    label="Step to use ptm data from",
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

    def modify_form(self, form, run):
        ptm_df_field = form["ptm_df"]
        grouping_field = form["grouping"]
        group1_field = form["group1"]
        group2_field = form["group2"]

        ptm_df_field.set_options(
            form_helper.to_choices(
                run.steps.get_instance_identifiers(PTMsPerSample, "ptm_df")
            )
        )
        grouping_field.set_options(
            form_helper.get_choices_for_metadata_non_sample_columns(run)
        )

        if grouping_field.options == []:
            return

        grouping = grouping_field.value

        # Set choices for group1 field based on selected grouping
        group1_field.set_options(
            form_helper.to_choices(run.steps.metadata_df[grouping].unique())
        )

        # set choices for group2 field based on selected grouping and group1
        if group1_field.value in run.steps.metadata_df[grouping].unique():
            group2_field.set_options(
                [
                    Option(el, el)
                    for el in run.steps.metadata_df[grouping].unique()
                    if el != group1_field.value
                ]
            )
        else:
            group2_field.set_options(
                list(
                    reversed(
                        form_helper.to_choices(run.steps.metadata_df[grouping].unique())
                    )
                )
            )

    calc_method = staticmethod(mann_whitney_test_on_ptm_data)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["ptm_df"] = steps.get_step_output(Step, "ptm_df", inputs["ptm_df"])
        inputs["metadata_df"] = steps.metadata_df
        return inputs


class DifferentialExpressionKruskalWallisOnIntensity(DataAnalysisStep):
    display_name = "Kruskal-Wallis Test"
    operation = "differential_expression"
    method_description = (
        "A function to conduct a Kruskal-Wallis test between groups defined in the clinical data."
        "The p-values are corrected for multiple testing."
    )

    output_keys = [
        "differentially_expressed_proteins_df",
        "significant_proteins_df",
        "corrected_p_values_df",
        "corrected_alpha",
    ]

    def create_form(self):
        return Form(
            label="Kruskal-Wallis Test",
            input_fields=[
                DropdownField(name="protein_df", label="Step to use protein data from"),
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

    def modify_form(self, form, run):
        protein_df_field = form["protein_df"]
        grouping_field = form["grouping"]
        selected_groups_field = form["selected_groups"]
        protein_df_field.set_options(form_helper.get_choices_for_protein_df_steps(run))
        grouping_field.set_options(
            form_helper.get_choices_for_metadata_non_sample_columns(run)
        )
        grouping = grouping_field.value
        selected_groups_field.set_options(
            form_helper.to_choices(run.steps.metadata_df[grouping].unique())
        )

    calc_method = staticmethod(kruskal_wallis_test_on_intensity_data)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["protein_df"] = steps.get_step_output(
            Step, "protein_df", inputs["protein_df"]
        )
        inputs["metadata_df"] = steps.metadata_df
        inputs["log_base"] = steps.get_step_input(TransformationLog, "log_base")
        return inputs


class DifferentialExpressionKruskalWallisOnPTM(DataAnalysisStep):
    display_name = "Kruskal-Wallis Test"
    operation = "Peptide analysis"
    method_description = (
        "A function to conduct a Kruskal-Wallis test between groups defined in the clinical data."
        "The p-values are corrected for multiple testing."
    )

    output_keys = [
        "differentially_expressed_ptm_df",
        "significant_ptm_df",
        "corrected_p_values_df",
        "corrected_alpha",
    ]

    def create_form(self):
        return Form(
            label="Kruskal-Wallis Test",
            input_fields=[
                DropdownField(
                    name="ptm_df",
                    label="Step to use ptm data from. ('PTMs per Sample' step needed for preproceesing)",
                ),
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

    def modify_form(self, form, run):
        ptm_df_field = form["ptm_df"]
        grouping_field = form["grouping"]
        selected_groups_field = form["selected_groups"]

        ptm_df_field.set_options(
            form_helper.to_choices(
                run.steps.get_instance_identifiers(PTMsPerSample, "ptm_df")
            )
        )
        grouping_field.set_options(
            form_helper.get_choices_for_metadata_non_sample_columns(run)
        )
        grouping = grouping_field.value
        selected_groups_field.set_options(
            form_helper.to_choices(run.steps.metadata_df[grouping].unique())
        )

    calc_method = staticmethod(kruskal_wallis_test_on_ptm_data)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["ptm_df"] = steps.get_step_output(Step, "ptm_df", inputs["ptm_df"])
        inputs["metadata_df"] = steps.metadata_df
        return inputs


class PlotVolcano(DataAnalysisStep):
    display_name = "Volcano Plot"
    operation = "plot"
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

    def modify_form(self, form, run):
        input_dict_field = form["input_dict"]
        items_of_interest_field = form["items_of_interest"]

        input_dict_field.set_options(
            form_helper.to_choices(
                run.steps.get_instance_identifiers(
                    Step,
                    ["corrected_p_values_df", "log2_fold_change_df"],
                )
            )
        )

        if input_dict_field.value == None:
            return

        input_dict_instance_id = input_dict_field.value

        items_of_interest = []
        step_output = run.steps.get_step_output(
            Step, "differentially_expressed_proteins_df", input_dict_instance_id
        )
        if step_output is not None:
            items_of_interest = step_output["Protein ID"].unique()
        step_output = run.steps.get_step_output(
            Step, "differentially_expressed_ptm_df", input_dict_instance_id
        )
        if step_output is not None:
            items_of_interest = step_output["PTM"].unique()

        items_of_interest_field.set_options(form_helper.to_choices(items_of_interest))

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["p_values"] = steps.get_step_output(
            Step, "corrected_p_values_df", inputs["input_dict"]
        )

        step = next(
            s for s in steps.all_steps if s.instance_identifier == inputs["input_dict"]
        )
        inputs["alpha"] = step.inputs["alpha"]
        inputs["group1"] = step.inputs["group1"]
        inputs["group2"] = step.inputs["group2"]
        inputs["log2_fc"] = steps.get_step_output(
            Step, "log2_fold_change_df", inputs["input_dict"]
        )

        if step.operation == "differential_expression":
            inputs["item_type"] = "Protein ID"
        elif step.operation == "Peptide analysis":
            inputs["item_type"] = "PTM"

        return inputs


class PlotProteinCoverage(DataAnalysisStep):
    display_name = "Protein Coverage Plot"
    operation = "plot"
    method_description = (
        "Create a protein coverage plot from a protein graph and peptide data"
    )

    input_keys = [
        "protein_id",
        "fasta_df",
        "metadata_df",
        "peptide_df",
        "grouping",
        "selected_groups",
        "aggregation_method",
    ]
    output_keys = []

    plot_method = staticmethod(plot_protein_coverage)

    def create_form(self):
        # noinspection SqlNoDataSourceInspection
        return Form(
            label="Protein Coverage Plot",
            input_fields=[
                DropdownField(
                    name="peptide_df",
                    label="Step to use peptide data from",
                ),
                DropdownField(
                    name="fasta_df",
                    label="Step to use fasta protein data from",
                ),
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

    def modify_form(self, form, run):
        peptide_df_field = form["peptide_df"]
        fasta_df_field = form["fasta_df"]
        protein_id_field = form["protein_id"]
        grouping_field = form["grouping"]
        selected_groups_field = form["selected_groups"]

        peptide_df_field.set_options(form_helper.get_choices(run, "peptide_df"))
        fasta_df_field.set_options(form_helper.get_choices(run, "fasta_df"))

        peptide_df_instance_id = peptide_df_field.value
        peptide_df = run.steps.get_step_output(
            Step, "peptide_df", peptide_df_instance_id
        )
        proteins_from_peptide_df = (
            set(peptide_df["Protein ID"].dropna().unique())
            if peptide_df is not None
            else {}
        )
        # Make sure that we have a unified representation of the canonical protein, which is sometimes given without
        # the -1 suffix. Only important for getting the correct sequence from the fasta file, so we don't need to
        # change it in the peptide_df
        proteins_from_peptide_df = {
            p if "-" in p else f"{p}-1" for p in proteins_from_peptide_df
        }

        fasta_df_instance_id = fasta_df_field.value
        fasta_df = run.steps.get_step_output(Step, "fasta_df", fasta_df_instance_id)
        proteins_from_fasta_df = (
            set(fasta_df["Protein ID"].unique()) if fasta_df is not None else {}
        )

        common_proteins = list(proteins_from_peptide_df & proteins_from_fasta_df)
        protein_id_field.set_options(form_helper.to_choices(common_proteins))

        # We specifically want to allow grouping by Sample here
        grouping_field.set_options(form_helper.get_choices_for_metadata(run))
        grouping = grouping_field.value
        if grouping == "Sample":
            selected_groups_field.set_options(
                form_helper.to_choices(peptide_df["Sample"].unique())
            )
        else:
            selected_groups_field.set_options(
                form_helper.to_choices(run.steps.metadata_df[grouping].unique())
            )
        form["aggregation_method"].isVisible = grouping != "Sample"

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["fasta_df"] = steps.get_step_output(Step, "fasta_df", inputs["fasta_df"])
        inputs["peptide_df"] = steps.get_step_output(
            Step, "peptide_df", inputs["peptide_df"]
        )
        inputs["metadata_df"] = steps.metadata_df
        return inputs


class PlotScatterPlot(DataAnalysisStep):
    display_name = "Scatter Plot"
    operation = "plot"
    method_description = "Creates a scatter plot from data. This requires a dimension reduction method to be run first, as the input dataframe should contain only 2 or 3 columns."

    plot_method = staticmethod(scatter_plot)

    def create_form(self):
        return Form(
            label="Scatter Plot",
            input_fields=[
                DropdownField(
                    name="input_df",
                    label="Choose dataframe to be plotted",
                ),
                # TODO: handle isRequired
                DropdownField(
                    name="metadata_df",
                    label="Choose dataframe to be used for coloring",
                ),
                DropdownField(
                    name="metadata_column",
                    label="Choose the column of the metadata dataframe that should be used for coloring",
                ),
            ],
        )

    def modify_form(self, form, run):
        input_df_field = form["input_df"]
        metadata_field = form["metadata_df"]

        input_df_field.set_options(
            form_helper.to_choices(
                run.steps.get_instance_identifiers(Step, "embedded_data")
            )
        )

        metadata_field.set_options(
            form_helper.get_choices(
                run,
                output_key="metadata_df",
                required=False,
            )
        )
        if form.values["metadata_df"] is not None:
            form["metadata_column"].set_options(
                form_helper.get_choices_for_metadata_non_sample_columns(
                    run, instance_identifier=form.values["metadata_df"]
                )
            )

    # TODO: input
    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.get_step_output(
            Step, "embedded_data", inputs["input_df"]
        )
        inputs["metadata_df"] = steps.metadata_df
        return inputs


class PlotClustergram(DataAnalysisStep):
    display_name = "Clustergram"
    operation = "plot"
    method_description = (
        "Creates a 2D clustergram from data using the samples on one axis and the proteins on the "
        "other axis. The data is clustered using euclidean distances for hierarchical clustering."
    )

    plot_method = staticmethod(clustergram_plot)

    # TODO: handle isRequired with sample_group_df
    def create_form(self):
        return Form(
            label="Clustergram",
            input_fields=[
                DropdownField(
                    name="input_df",
                    label="Choose dataframe to be plotted",
                ),
                DropdownField(
                    name="metadata_df",
                    label="Choose dataframe to be used for annotating sample metadata",
                ),
                DropdownField(
                    name="metadata_column",
                    label="Choose the column of the metadata dataframe that should be used for annotation",
                ),
                CheckboxField(
                    name="flip_axes",
                    label="Flip axis",
                    text="Flip axes",
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

    def modify_form(self, form, run):
        form["input_df"].set_options(
            form_helper.get_choices_for_protein_df_steps(
                run,
            )
            + form_helper.to_choices(
                run.steps.get_instance_identifiers(
                    Step,
                    "significant_proteins_df",
                )
            )
        )

        form["metadata_df"].set_options(
            form_helper.get_choices(
                run,
                output_key="metadata_df",
                required=True,
            )
        )

        if form.values["metadata_df"] is not None:
            form["metadata_column"].set_options(
                form_helper.get_choices_for_metadata_non_sample_columns(
                    run, instance_identifier=form.values["metadata_df"]
                )
            )

        custom_scale_toggled = form.values["use_custom_color_scale"]
        form["heatmap_low_color_limit"].isVisible = custom_scale_toggled
        form["heatmap_high_color_limit"].isVisible = custom_scale_toggled
        form["heatmap_low_color"].isVisible = custom_scale_toggled
        form["heatmap_high_color"].isVisible = custom_scale_toggled

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        # Note: This is a hotfix that will be overridden anyway as soon
        # as the node-based workflow has been finished.
        # So the code is not top notch
        selected_prot_df = steps.get_step_output(
            Step, "significant_proteins_df", inputs["input_df"]
        )

        if selected_prot_df is None:
            selected_prot_df = steps.get_step_output(
                Step, "protein_df", inputs["input_df"]
            )

        inputs["input_df"] = selected_prot_df

        inputs["metadata_df"] = steps.get_step_output(
            Step, "metadata_df", inputs["metadata_df"]
        )
        return inputs


class PlotProtQuant(DataAnalysisStep):
    display_name = "Protein Quantification Plot"
    operation = "plot"
    method_description = (
        "Creates a line chart for intensity across samples for protein groups"
    )

    input_keys = ["input_df", "protein_group", "similarity_measure", "similarity"]
    output_keys = []

    def create_form(self):
        return Form(
            label="Protein Quantification Plot",
            input_fields=[
                DropdownField(
                    name="input_df",
                    label="Choose dataframe to be plotted",
                ),
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

    def modify_form(self, form, run):
        form["input_df"].set_options(form_helper.get_choices_for_protein_df_steps(run))

        if form["input_df"].options:
            if not form["input_df"].value:
                form["input_df"].value = form["input_df"].options[0].label

            form["protein_group"].set_options(
                form_helper.to_choices(
                    run.steps.get_step_output(
                        step_type=Step,
                        output_key="protein_df",
                        instance_identifier=form["input_df"].value,
                    )["Protein ID"].unique()
                )
            )

        if form["similarity_measure"].value == SimilarityMeasure.cosine_similarity:
            form["similarity"] = FloatField(
                name="similarity",
                label="Cosine Similarity",
                value=0,
                min=-1,
                max=1,
                step=0.1,
            )
        else:
            form["similarity"] = NumberField(
                name="similarity",
                label="Euclidean Distance",
                value=1,
                min=0,
                max=999,
                step=1,
            )

    plot_method = staticmethod(prot_quant_plot)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.get_step_output(
            Step, "protein_df", inputs["input_df"]
        )
        return inputs


class PlotPrecisionRecallCurve(DataAnalysisStep):
    display_name = "Precision Recall"
    operation = "plot"
    method_description = "The precision-recall curve shows the tradeoff between precision and recall for different threshold"

    # Todo: output_keys

    calc_method = staticmethod(evaluate_classification_model)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        # TODO: Input
        return inputs


class PlotROC(DataAnalysisStep):
    display_name = "Receiver Operating Characteristic curve"
    operation = "plot"
    method_description = "The ROC curve helps assess the model's ability to discriminate between positive and negative classes and determine an optimal threshold for decision making"

    # Todo: output_keys

    calc_method = staticmethod(evaluate_classification_model)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        # Todo: Input
        return inputs


class ClusteringKMeans(DataAnalysisStep):
    display_name = "KMeans"
    operation = "clustering"
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
                    name="input_df",
                    label="Choose dataframe to be plotted",
                ),
                # TODO: Add dynamic fill for labels_column & positive_label
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
                # TODO: Add dynamic parameters for grid search & randomized search
                # TODO Add dynamic parameter for model selection scoring
                DropdownField(
                    name="model_selection_scoring",
                    label="Select a scoring for identifying the best estimator following a grid search",
                    options=ClusteringScoring,
                ),
                DropdownField(
                    name="scoring",
                    label="Scoring for the model",
                    options=ClusteringScoring,
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
            ],
        )

    def modify_form(self, form, run):
        labels_field = form["labels_column"]
        positive_label_field = form["positive_label"]

        labels_field.set_options(
            form_helper.get_choices_for_metadata_non_sample_columns(run)
        )

        positive_label_field.set_options(
            form_helper.to_choices(
                run.steps.metadata_df[labels_field.value].dropna().unique(),
                required=False,
            )
        )

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["metadata_df"] = steps.metadata_df
        return inputs


class ClusteringExpectationMaximisation(DataAnalysisStep):
    display_name = "Expectation-maximization (EM)"
    operation = "clustering"
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
                    name="input_df",
                    label="Choose dataframe to be plotted",
                    options=AnalysisLevel,
                ),
                # TODO: Add dynamic fill for labels_column & positive_label
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
                # TODO: Add dynamic parameters for grid search & randomized search
                # TODO Add dynamic parameter for model selection scoring
                DropdownField(
                    name="model_selection_scoring",
                    label="Select a scoring for identifying the best estimator following a grid search",
                    options=ClusteringScoring,
                ),
                DropdownField(
                    name="scoring",
                    label="Scoring for the model",
                    options=ClusteringScoring,
                    value=ClusteringScoring.adjusted_rand_score,
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
            ],
        )

    def modify_form(self, form, run):
        labels_field = form["labels_column"]
        positive_label_field = form["positive_label"]

        labels_field.set_options(
            form_helper.get_choices_for_metadata_non_sample_columns(run)
        )

        positive_label_field.set_options(
            form_helper.to_choices(
                run.steps.metadata_df[labels_field.value].dropna().unique(),
                required=False,
            )
        )

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["metadata_df"] = steps.metadata_df
        return inputs


class ClusteringHierarchicalAgglomerative(DataAnalysisStep):
    display_name = "Hierarchical Agglomerative Clustering"
    operation = "clustering"
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
                    name="input_df",
                    label="Choose dataframe to be plotted",
                    options=AnalysisLevel,
                ),
                # TODO: Add dynamic fill for labels_column & positive_label
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
                # TODO: Add dynamic parameters for grid search & randomized search
                # TODO Add dynamic parameter for model selection scoring
                DropdownField(
                    name="model_selection_scoring",
                    label="Select a scoring for identifying the best estimator following a grid search",
                    options=ClusteringScoring,
                ),
                DropdownField(
                    name="scoring",
                    label="Scoring for the model",
                    options=ClusteringScoring,
                    value=ClusteringScoring.adjusted_rand_score,
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
            ],
        )

    calc_method = staticmethod(hierarchical_agglomerative_clustering)

    def modify_form(self, form, run):
        labels_field = form["labels_column"]
        positive_label_field = form["positive_label"]

        labels_field.set_options(
            form_helper.get_choices_for_metadata_non_sample_columns(run)
        )

        positive_label_field.set_options(
            form_helper.to_choices(
                run.steps.metadata_df[labels_field.value].dropna().unique(),
                required=False,
            )
        )

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["metadata_df"] = steps.metadata_df
        return inputs


class ClassificationRandomForest(DataAnalysisStep):
    display_name = "Random Forest"
    operation = "classification"
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
                    name="input_df",
                    label="Choose dataframe to be plotted",
                    options=AnalysisLevel,
                ),
                # TODO: Add dynamic fill for labels_column & positive_label
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
                # TODO: Validation strategy
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
                ),
                NumberField(
                    name="n_splits",
                    label="Number of folds",
                    min=2,
                    value=5,
                ),
                DropdownField(
                    name="shuffle",
                    label="Whether to shuffle the data before splitting into batches",
                    options=YesNo,
                    value=YesNo.yes,
                ),
                NumberField(
                    name="n_repeats",
                    label="Number of times cross-validator needs to be repeated",
                    min=1,
                    value=10,
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

    calc_method = staticmethod(random_forest)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["metadata_df"] = steps.metadata_df
        return inputs


class ClassificationSVM(DataAnalysisStep):
    display_name = "Support Vector Machine"
    operation = "classification"
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
                    name="input_df",
                    label="Choose dataframe to be plotted",
                    options=AnalysisLevel,
                ),
                # TODO: Add dynamic fill for labels_column & positive_label
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
                # TODO: Validation strategy
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
                ),
                NumberField(
                    name="n_splits",
                    label="Number of folds",
                    min=2,
                    value=5,
                ),
                DropdownField(
                    name="shuffle",
                    label="Whether to shuffle the data before splitting into batches",
                    options=YesNo,
                    value=YesNo.yes,
                ),
                NumberField(
                    name="n_repeats",
                    label="Number of times cross-validator needs to be repeated",
                    min=1,
                    value=10,
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

    calc_method = staticmethod(svm)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["metadata_df"] = steps.metadata_df
        return inputs


class ModelEvaluationClassificationModel(DataAnalysisStep):
    display_name = "Evaluation of classification models"
    operation = "model_evaluation"
    method_description = "Assessing an already trained classification model on separate testing data using widely used scoring metrics"

    input_keys = [
        # Todo: input_dict
        "scoring",
    ]
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

    def method(self, inputs: dict) -> dict:
        return evaluate_classification_model(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["sample_group_df"] = steps.metadata_df
        return inputs


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
                    "visualize the results, please use the 'Scatter Plot' step afterwards.",
                ),
                DropdownField(
                    name="input_df",
                    label="Dimension reduction of a dataframe using t-SNE",
                    options=AnalysisLevel,
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
                    name="n_iter",
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

    calc_method = staticmethod(t_sne)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["sample_group_df"] = steps.metadata_df
        return inputs


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
                    "visualize the results, please use the 'Scatter Plot' step afterwards.",
                ),
                DropdownField(
                    name="input_df",
                    label="Dimension reduction of a dataframe using UMAP",
                    options=AnalysisLevel,
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
            ],
        )

    def modify_form(self, form, run):
        input_df_field = form["input_df"]
        input_df_field.set_options(form_helper.get_choices_for_protein_df_steps(run))

    calc_method = staticmethod(umap)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.get_step_output(
            Step, "protein_df", inputs["input_df"]
        )
        return inputs


class BaseFLEXLF(DataAnalysisStep):
    """
    A base class for FLEXIQuantLF and MultiFLEXLF to reduce code duplication.
    """

    def modify_form(self, form, run):
        grouping_field = form["grouping_column"]
        grouping_field.set_options(
            form_helper.get_choices_for_metadata_non_sample_columns(run)
        )

        if grouping_field.options == []:
            return
        grouping = grouping_field.value

        reference_group_field = form["reference_group"]
        reference_group_field.set_options(
            form_helper.to_choices(run.steps.metadata_df[grouping].unique())
        )

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["peptide_df"] = steps.get_step_output(
            step_type=Step,
            output_key="peptide_df",
        )
        inputs["metadata_df"] = steps.metadata_df
        return inputs

    def get_base_form_fields(self) -> tuple:
        return (
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
        )


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
                ),
                *self.get_base_form_fields(),
            ],
        )

    def modify_form(self, form, run):
        super().modify_form(form, run)
        form["protein_group"].options = form_helper.to_choices(
            run.steps.get_step_output(
                step_type=Step,
                output_key="peptide_df",
            )["Protein ID"].unique()
        )


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
            input_fields=[
                *self.get_base_form_fields(),
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


class SelectPeptidesForProtein(DataAnalysisStep):
    display_name = "Select Peptides of Protein"
    operation = "Peptide analysis"
    method_description = "Filter peptides for the a selected Protein of Interest from a peptide dataframe"

    output_keys = [
        "peptide_df",
    ]

    def create_form(self):
        return Form(
            label="Select Peptides of Protein",
            input_fields=[
                DropdownField(
                    name="peptide_df",
                    label="Step to use peptide dataframe from",
                ),
                DropdownField(
                    name="auto_select",
                    label="Automatically select most significant Protein",
                    options=YesNo,
                    value=YesNo.no,
                ),
                DropdownField(
                    name="protein_list",
                    label="Select a list of Proteins from which you want to choose your Proteins of Interest",
                ),
                DropdownField(
                    name="sort_proteins",
                    label="Sort Proteins by p-value (requires a list of Proteins from a Differential Expression Analysis to be selected)",
                    options=YesNo,
                    value=YesNo.no,
                ),
                MultiSelectField(
                    name="protein_ids",
                    label="Protein IDs",
                ),
            ],
        )

    def modify_form(self, form, run):
        peptide_df_field = form["peptide_df"]
        auto_select_field = form["auto_select"]
        sort_proteins_field = form["sort_proteins"]
        protein_list_field = form["protein_list"]
        protein_ids_field = form["protein_ids"]

        peptide_df_field.set_options(form_helper.get_choices(run, "peptide_df", Step))
        peptide_df_field.value = run.steps.get_instance_identifiers(
            DataPreprocessingStep, "peptide_df"
        )[-1]

        selected_auto_select = True if auto_select_field.value == YesNo.yes else False

        protein_list_options = form_helper.to_choices(
            [] if selected_auto_select else ["all proteins"]
        )
        protein_list_options.extend(
            form_helper.get_choices(run, "significant_proteins_df", DataAnalysisStep)
        )
        protein_list_field.set_options(protein_list_options)

        chosen_list = protein_list_field.value
        if not selected_auto_select:
            # TODO: Enable toggling
            if chosen_list == "all_proteins":
                protein_ids_field.set_options(
                    form_helper.to_choices(
                        run.steps.get_step_output(Step, "protein_df")[
                            "Protein ID"
                        ].unique()
                    )
                )
            else:
                if sort_proteins_field.value == YesNo.yes:
                    protein_ids_field.set_options(
                        form_helper.to_choices(
                            run.steps.get_step_output(
                                DataAnalysisStep, "significant_proteins_df", chosen_list
                            )
                            .sort_values(by="corrected_p_value")["Protein ID"]
                            .unique()
                        )
                    )
                else:
                    significant_proteins = run.steps.get_step_output(
                        DataAnalysisStep, "significant_proteins_df", chosen_list
                    )
                    if significant_proteins is not None:
                        protein_ids_field.set_options(
                            form_helper.to_choices(
                                significant_proteins["Protein ID"].unique()
                            )
                        )

    calc_method = staticmethod(select_peptides_of_protein)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["peptide_df"] = steps.get_step_output(
            Step, "peptide_df", inputs["peptide_df"]
        )

        inputs["metadata_df"] = steps.metadata_df

        if inputs["auto_select"]:
            significant_proteins = steps.get_step_output(
                DataAnalysisStep, "significant_proteins_df", inputs["protein_list"]
            )
            index_of_most_significant_protein = significant_proteins[
                "corrected_p_value"
            ].idxmin()
            most_significant_protein = significant_proteins.loc[
                index_of_most_significant_protein
            ]
            inputs["protein_id"] = [most_significant_protein["Protein ID"]]
            self.messages.append(
                {
                    "level": logging.INFO,
                    "msg": f"Selected the most significant Protein: {most_significant_protein['Protein ID']}, "
                    f"from {inputs['protein_list']}",
                }
            )

        return inputs


class PTMsPerSample(DataAnalysisStep):
    display_name = "PTMs per Sample"
    operation = "Peptide analysis"
    method_description = (
        "Analyze the post-translational modifications (PTMs) of a single protein of interest. "
        "This function requires a peptide dataframe with PTM information."
    )

    output_keys = [
        "ptm_df",
    ]

    def create_form(self):
        return Form(
            label="PTMs per Sample",
            input_fields=[
                DropdownField(
                    name="peptide_df",
                    label="Peptide dataframe containing the peptides of a single protein including their modifications "
                    "(e.g. from evidence.txt)",
                )
            ],
        )

    def modify_form(self, form, run):
        peptide_df_field = form["peptide_df"]

        peptide_df_field.set_options(form_helper.get_choices(run, "peptide_df"))

        single_protein_peptides = run.steps.get_instance_identifiers(
            SelectPeptidesForProtein, "peptide_df"
        )

        if single_protein_peptides:
            peptide_df_field.value = single_protein_peptides[0]

    calc_method = staticmethod(ptms_per_sample)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["peptide_df"] = steps.get_step_output(
            Step, "peptide_df", inputs["peptide_df"]
        )
        return inputs


class PTMsProteinAndPerSample(DataAnalysisStep):
    display_name = "PTMs per Sample and Protein"
    operation = "Peptide analysis"
    method_description = (
        "Analyze the post-translational modifications (PTMs) of all Proteins. "
        "This function requires a peptide dataframe with PTM information."
    )

    output_keys = [
        "ptm_df",
    ]

    def create_form(self):
        return Form(
            label="PTMs per Sample and Protein",
            input_fields=[
                DropdownField(
                    name="peptide_df",
                    label="Peptide dataframe containing the peptides of a single protein",
                )
            ],
        )

    def modify_form(self, form, run):
        peptide_df_field = form["peptide_df"]

        peptide_df_field.set_options(form_helper.get_choices(run, "peptide_df"))

        single_protein_peptides = run.steps.get_instance_identifiers(
            SelectPeptidesForProtein, "peptide_df"
        )

        if single_protein_peptides:
            peptide_df_field.value = single_protein_peptides[0]

    calc_method = staticmethod(ptms_per_protein_and_sample)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["peptide_df"] = steps.get_step_output(
            Step, "peptide_df", inputs["peptide_df"]
        )
        return inputs


class _PTMVisualizationStep(DataAnalysisStep):
    operation = "plot"
    output_keys = []

    @classmethod
    def get_form_fields(cls) -> list:
        return [
            DropdownField(
                name="evidence_df",
                label="Dataframe that contains the MaxQuant evidence data",
            ),
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

    def modify_form(self, form, run):
        form["evidence_df"].set_options(
            form_helper.get_choices(
                run, output_key="peptide_df", step_type=Step, required=True
            )
        )

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["evidence_df"] = steps.get_step_output(
            Step, "peptide_df", inputs["evidence_df"]
        )
        return inputs


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
    @classmethod
    def get_form_fields(cls) -> list:
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
