import logging

from backend.protzilla import form_helper
from backend.protzilla.data_analysis.classification import random_forest, svm
from backend.protzilla.data_analysis.clustering import (
    expectation_maximisation,
    hierarchical_agglomerative_clustering,
    k_means,
)
from backend.protzilla.data_analysis.differential_expression_anova import anova
from backend.protzilla.data_analysis.differential_expression_kruskal_wallis import kruskal_wallis_test_on_ptm_data, \
    kruskal_wallis_test_on_intensity_data
from backend.protzilla.data_analysis.differential_expression_linear_model import linear_model
from backend.protzilla.data_analysis.differential_expression_mann_whitney import (
    mann_whitney_test_on_intensity_data, mann_whitney_test_on_ptm_data)
from backend.protzilla.data_analysis.differential_expression_t_test import t_test
from backend.protzilla.data_analysis.dimension_reduction import t_sne, umap
from backend.protzilla.data_analysis.model_evaluation import evaluate_classification_model
from backend.protzilla.data_analysis.plots import (
    clustergram_plot,
    create_volcano_plot,
    prot_quant_plot,
    scatter_plot,
)
from backend.protzilla.data_analysis.ptm_analysis import (
    select_peptides_of_protein,
    ptms_per_protein_and_sample,
    ptms_per_sample,
)
from backend.protzilla.data_analysis.ptm_quantification import flexiquant_lf
from backend.protzilla.data_analysis.ptm_visualization import create_bar_ptm_visualization
from backend.protzilla.form import *
from backend.protzilla.methods.data_preprocessing import TransformationLog
from backend.protzilla.methods.importing import EvidenceImport
from backend.protzilla.steps import Step, StepManager
from protzilla.data_analysis.ptm_visualization import create_overview_ptm_visualization, \
    create_details_ptm_visualization
from protzilla.data_analysis.ptm_visualization.ptm_overview_plot import get_detected_modifications


class TTestType(Enum):
    welchs_t_test = "Welch's t-Test"
    students_t_test = "Student's t-Test"


class AnalysisLevel(Enum):
    protein = "Protein"


class MultipleTestingCorrectionMethod(Enum):
    benjamini_hochberg = "Benjamini-Hochberg"
    bonferroni = "Bonferroni"


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
    adjusted_rand_score = "Adjusted Rand Score"
    completeness_score = "Completeness Score"
    fowlkes_mallows_score = "Fowlkes Mallows Score"
    homogeneity_score = "Homogeneity Score"
    mutual_info_score = "Mutual Info Score"
    normalized_mutual_info_score = "Normalized Mutual Info Score"
    rand_score = "Rand Score"
    v_measure_score = "V Measure Score"


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
    havensine = "havensine"


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

    calc_method = staticmethod(anova)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["log_base"] = steps.get_step_input(TransformationLog, "log_base")
        inputs["intensity_df"] = steps.protein_df
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
                    separatePrefix="\u03B1",
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
        grouping_field.set_options(form_helper.get_choices_for_metadata_non_sample_columns(run))

        if (grouping_field.options == []):
            return
        
        grouping = grouping_field.value

        # Set choices for group1 field based on selected grouping
        group1_field.set_options(form_helper.to_choices(run.steps.metadata_df[grouping].unique()))

        #set choices for group2 field based on selected grouping and group1
        if (group1_field.value in run.steps.metadata_df[grouping].unique()):
            group2_field.set_options([
                Option(el, el)
                for el in run.steps.metadata_df[grouping].unique()
                if el != group1_field.value
            ])
        else:
            group2_field.set_options(list(reversed(
                form_helper.to_choices(run.steps.metadata_df[grouping].unique()))
            ))

    calc_method = staticmethod(t_test)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["log_base"] = steps.get_step_input(TransformationLog, "log_base")
        inputs["intensity_df"] = steps.protein_df
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

    calc_method = staticmethod(linear_model)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["log_base"] = steps.get_step_input(TransformationLog, "log_base")
        inputs["intensity_df"] = steps.protein_df
        inputs["metadata_df"] = steps.metadata_df
        return inputs


class DifferentialExpressionMannWhitneyOnIntensity(DataAnalysisStep):
    display_name = "Mann-Whitney Test"
    operation = "differential_expression"
    method_description = ("A function to conduct a Mann-Whitney U test between groups defined in the clinical data."
                          "The p-values are corrected for multiple testing.")

    output_keys = [
        "differentially_expressed_proteins_df",
        "significant_proteins_df",
        "corrected_p_values_df",
        "u_statistic_df",
        "log2_fold_change_df",
        "corrected_alpha",
    ]

    calc_method = staticmethod(mann_whitney_test_on_intensity_data)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        if steps.get_step_output(Step, "protein_df", inputs["protein_df"]) is not None:
            inputs["protein_df"] = steps.get_step_output(Step, "protein_df", inputs["protein_df"])
        inputs["metadata_df"] = steps.metadata_df
        inputs["log_base"] = steps.get_step_input(TransformationLog, "log_base")
        return inputs


class DifferentialExpressionMannWhitneyOnPTM(DataAnalysisStep):
    display_name = "Mann-Whitney Test"
    operation = "Peptide analysis"
    method_description = ("A function to conduct a Mann-Whitney U test between groups defined in the clinical data."
                          "The p-values are corrected for multiple testing.")

    output_keys = [
        "differentially_expressed_ptm_df",
        "significant_ptm_df",
        "corrected_p_values_df",
        "u_statistic_df",
        "log2_fold_change_df",
        "corrected_alpha",
    ]

    calc_method = staticmethod(mann_whitney_test_on_ptm_data)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["ptm_df"] = steps.get_step_output(Step, "ptm_df", inputs["ptm_df"])
        inputs["metadata_df"] = steps.metadata_df
        return inputs


class DifferentialExpressionKruskalWallisOnIntensity(DataAnalysisStep):
    display_name = "Kruskal-Wallis Test"
    operation = "differential_expression"
    method_description = ("A function to conduct a Kruskal-Wallis test between groups defined in the clinical data."
                          "The p-values are corrected for multiple testing.")

    output_keys = [
        "differentially_expressed_proteins_df",
        "significant_proteins_df",
        "corrected_p_values_df",
        "corrected_alpha",
    ]

    calc_method = staticmethod(kruskal_wallis_test_on_intensity_data)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["ptm_df"] = steps.get_step_output(Step, "ptm_df", inputs["ptm_df"])
        inputs["metadata_df"] = steps.metadata_df
        return inputs


class DifferentialExpressionKruskalWallisOnIntensity(DataAnalysisStep):
    display_name = "Kruskal-Wallis Test"
    operation = "differential_expression"
    method_description = ("A function to conduct a Kruskal-Wallis test between groups defined in the clinical data."
                          "The p-values are corrected for multiple testing.")

    output_keys = [
        "differentially_expressed_proteins_df",
        "significant_proteins_df",
        "corrected_p_values_df",
        "corrected_alpha",
    ]

    calc_method = staticmethod(kruskal_wallis_test_on_intensity_data)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["protein_df"] = steps.get_step_output(Step, "protein_df", inputs["protein_df"])
        inputs["metadata_df"] = steps.metadata_df
        inputs["log_base"] = steps.get_step_input(TransformationLog, "log_base")
        return inputs


class DifferentialExpressionKruskalWallisOnPTM(DataAnalysisStep):
    display_name = "Kruskal-Wallis Test"
    operation = "Peptide analysis"
    method_description = ("A function to conduct a Kruskal-Wallis test between groups defined in the clinical data."
                          "The p-values are corrected for multiple testing.")

    output_keys = [
        "differentially_expressed_ptm_df",
        "significant_ptm_df",
        "corrected_p_values_df",
        "corrected_alpha",
    ]

    calc_method = staticmethod(kruskal_wallis_test_on_ptm_data)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["ptm_df"] = steps.get_step_output(Step, "ptm_df", inputs["ptm_df"])
        inputs["metadata_df"] = steps.metadata_df
        return inputs


class PlotVolcano(DataAnalysisStep):
    display_name = "Volcano Plot"
    operation = "plot"
    method_description = ("Plots the results of a differential expression analysis in a volcano plot. The x-axis shows "
                          "the log2 fold change and the y-axis shows the -log10 of the corrected p-values. The user "
                          "can define a fold change threshold and an alpha level to highlight significant items.")

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
                )
            ],
        )
    
    def modify_form(self, form, run):
        input_dict_field = form["input_dict"]
        items_of_interest_field = form["items_of_interest"]

        input_dict_field.set_options(
            form_helper.to_choices(
                run.steps.get_instance_identifiers(
                    Step, ["corrected_p_values_df", "log2_fold_change_df"],
                )
            )
        )

        if(input_dict_field.value == None):
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

        items_of_interest_field.options = (form_helper.to_choices(items_of_interest))

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


class PlotScatterPlot(DataAnalysisStep):
    display_name = "Scatter Plot"
    operation = "plot" 
    method_description = "Creates a scatter plot from data. This requires a dimension reduction method to be run first, as the input dataframe should contain only 2 or 3 columns."

    plot_method = staticmethod(scatter_plot)

    # TODO: input
    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.get_step_output(
            Step, "embedded_data", inputs["input_df"]
        )
        inputs["color_df"] = steps.get_step_output(Step, "color_df", inputs["color_df"])
        return inputs


class PlotClustergram(DataAnalysisStep):
    display_name = "Clustergram"
    operation = "plot"
    method_description = ("Creates a 2D clustergram from data using the samples on one axis and the proteins on the "
                          "other axis. The data is clustered using euclidean distances for hierarchical clustering.")

    plot_method = staticmethod(clustergram_plot)

    def create_form(self):
        return Form(
            label="Clustergram",
            input_fields=[
                DropdownField(
                    name="input_df",
                    label="Choose dataframe to be plotted",
                ),
                # TODO: might be overkill to add a field to let user select a metadata dataframe (since the convention
                #  seems to be that there's only one metadata dataframe and that one is pre-selected)
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
                    # TODO if flipping axis is possible wouldn't it be cool to also be able to specify which axis to
                    #  flip, i.e. which columns will be selected from the dataframe
                    text="Flip axes",
                ),
            ],
        )

    def modify_form(self, form, run):
        form["input_df"].options = form_helper.get_choices_for_protein_df_steps(
            run,
        )
        form["metadata_df"].options = form_helper.get_choices(
            run,
            output_key='metadata_df',
            required=False,
        )
        if form.values['metadata_df'] is not None:
            form["metadata_column"].options = form_helper.get_choices_for_metadata_non_sample_columns(
                run,
                instance_identifier=form.values['metadata_df']
            )

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.get_step_output(
            Step, "protein_df", inputs["input_df"]
        )
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
        form["input_df"].options = form_helper.get_choices_for_protein_df_steps(
            run
        )

        if form["input_df"].options:
            if not form["input_df"].value:
                form["input_df"].value = form["input_df"].options[0].label

            form["protein_group"].options = form_helper.to_choices(
                run.steps.get_step_output(
                    step_type=Step,
                    output_key="protein_df",
                    instance_identifier=form["input_df"].value,
                )["Protein ID"].unique()
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

    calc_method = staticmethod(hierarchical_agglomerative_clustering)

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

    def method(self, inputs: dict) -> dict:
        return evaluate_classification_model(**inputs)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["metadata_df"] = steps.metadata_df
        return inputs


class DimensionReductionTSNE(DataAnalysisStep):
    display_name = "t-SNE"
    operation = "dimension_reduction"
    method_description = "Dimension reduction of a dataframe using t-SNE"

    output_keys = ["embedded_data"]

    calc_method = staticmethod(t_sne)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.protein_df
        inputs["metadata_df"] = steps.metadata_df
        return inputs


class DimensionReductionUMAP(DataAnalysisStep):
    display_name = "UMAP"
    operation = "dimension_reduction"
    method_description = "Dimension reduction of a dataframe using UMAP"

    output_keys = ["embedded_data"]

    calc_method = staticmethod(umap)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["input_df"] = steps.get_step_output(
            Step, "protein_df", inputs["input_df"]
        )
        return inputs


class FLEXIQuantLF(DataAnalysisStep):
    display_name = "FLEXIQuant-LF"
    operation = "modification_quantification"
    method_description = "FLEXIQuant-LF is an unbiased, label-free computational tool to indirectly detect modified peptides and to quantify the degree of modification based solely on the unmodified peptide species."

    output_keys = [
        "raw_scores",
        "RM_scores",
        "diff_modified",
        "removed_peptides",
    ]

    plot_method = staticmethod(flexiquant_lf)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["peptide_df"] = steps.get_step_output(
            Step, "peptide_df", inputs["peptide_df"]
        )

        inputs["metadata_df"] = steps.metadata_df


class SelectPeptidesForProtein(DataAnalysisStep):
    display_name = "Select Peptides of Protein"
    operation = "Peptide analysis"
    method_description = "Filter peptides for the a selected Protein of Interest from a peptide dataframe"

    output_keys = [
        "peptide_df",
    ]

    calc_method = staticmethod(select_peptides_of_protein)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["peptide_df"] = steps.get_step_output(
            Step, "peptide_df", inputs["peptide_df"]
        )

        inputs["metadata_df"] = steps.metadata_df

        if inputs["auto_select"]:
            significant_proteins = (
                steps.get_step_output(DataAnalysisStep, "significant_proteins_df", inputs["protein_list"]))
            index_of_most_significant_protein = significant_proteins['corrected_p_value'].idxmin()
            most_significant_protein = significant_proteins.loc[index_of_most_significant_protein]
            inputs["protein_id"] = [most_significant_protein["Protein ID"]]
            self.messages.append({
                "level": logging.INFO,
                "msg":
                    f"Selected the most significant Protein: {most_significant_protein['Protein ID']}, "
                    f"from {inputs['protein_list']}"
            })

        return inputs


class PTMsPerSample(DataAnalysisStep):
    display_name = "PTMs per Sample"
    operation = "Peptide analysis"
    method_description = ("Analyze the post-translational modifications (PTMs) of a single protein of interest. "
                          "This function requires a peptide dataframe with PTM information.")

    output_keys = [
        "ptm_df",
    ]

    calc_method = staticmethod(ptms_per_sample)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["peptide_df"] = steps.get_step_output(
            Step, "peptide_df", inputs["peptide_df"]
        )
        return inputs


class PTMsProteinAndPerSample(DataAnalysisStep):
    display_name = "PTMs per Sample and Protein"
    operation = "Peptide analysis"
    method_description = ("Analyze the post-translational modifications (PTMs) of all Proteins. "
                          "This function requires a peptide dataframe with PTM information.")

    output_keys = [
        "ptm_df",
    ]

    calc_method = staticmethod(ptms_per_protein_and_sample)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["peptide_df"] = steps.get_step_output(
            Step, "peptide_df", inputs["peptide_df"]
        )
        return inputs


class PTMVisualizationStep(DataAnalysisStep):
    operation = "plot"
    output_keys = []

    def create_form(self):
        return Form(
            label="PTM Visualization",
            input_fields=[
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
                    hasStepButtons=False
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
                          "(the start is either 1 or the end of the previous region), the (color) group the "
                          "region belongs to (which can be specified in the settings), and a short name for the "
                          "region.",
                ),
            ]
        )

    def modify_form(self, form, run):
        form["evidence_df"].options = form_helper.get_choices(
            run,
            output_key='peptide_df',
            step_type=EvidenceImport,  # TODO: would the normal PeptideImport also work?
            required=True
        )

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["evidence_df"] = steps.get_step_output(
            Step, "peptide_df", inputs["evidence_df"]
        )
        return inputs


class PTMOverviewVisualization(PTMVisualizationStep):
    display_name = "PTM Visualization - Overview Plot"
    method_description = "Visualizes selected PTMs on a given protein sequence (including isoforms)"

    calc_method = staticmethod(get_detected_modifications)
    plot_method = staticmethod(create_overview_ptm_visualization)


class _PTMVisualizationWithGroups(PTMVisualizationStep):
    def create_form(self):
        base_form = super(_PTMVisualizationWithGroups, self).create_form()
        form = Form(
            label=base_form.label,
            input_fields=base_form.input_fields + [
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
        )
        return form

    calc_method = staticmethod(get_detected_modifications)


class PTMBarVisualization(_PTMVisualizationWithGroups):
    display_name = "PTM Visualization - Bar Plot"
    method_description = ("Visualizes selected PTMs on a given protein sequence (including isoforms). Additionally, "
                          "shows PTM frequency across groups as a bar plot.")

    plot_method = staticmethod(create_bar_ptm_visualization)


class PTMDetailsVisualization(_PTMVisualizationWithGroups):
    display_name = "PTM Visualization - Details Plot"
    method_description = ("Visualizes selected PTMs on a given protein sequence (including isoforms). Additionally, "
                          "shows PTM and cleavage frequency across groups as heatmaps.")

    plot_method = staticmethod(create_details_ptm_visualization)
