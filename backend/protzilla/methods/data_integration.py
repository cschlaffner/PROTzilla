from __future__ import annotations

import restring
import gseapy
from backend.protzilla import form_helper
from backend.protzilla.constants.colors import PLOT_COLOR_SEQUENCE
from backend.protzilla.data_integration import (
    database_integration,
    di_plots,
    enrichment_analysis,
)
from backend.protzilla.data_integration.database_query import uniprot_databases
from backend.protzilla.form import *
from backend.protzilla.steps import Plots, Step, StepManager
from backend.protzilla.data_integration.enrichment_analysis import GOAnalysisOflineBackgroundType, GOAnalysisWithEnrichrBackgroundType
import matplotlib.colors as mcolors

PROTEIN_DF = "protein_df"
DIFFERENTIALLY_EXPRESSED_PROTEINS_DF = "differentially_expressed_proteins_df"


class Direction(Enum):
    up = "up"
    down = "down"
    both = "both"


class GeneSetsField(Enum):
    upload_a_file = "Upload a file"
    choose_from_enrichr_options = "Choose from Enrichr options"


class Organism(Enum):
    human = "Human"
    mouse = "Mouse"
    rat = "Rat"
    yeast = "Yeast"
    fly = "Fly"
    fish = "Fish"
    worm = "Worm"


class PermutationTypeField(Enum):
    phenotype = "phenotype"
    gene_set = "gene_set"


class RankingMethodField(Enum):
    log2_ratio_of_classes = "log2_ratio_of_classes"
    signal_to_noise = "signal_to_noise"
    t_test = "t_test"
    ratio_of_classes = "ratio_of_classes"
    diff_of_classes = "diff_of_classes"


class RankingDirectionField(Enum):
    ascending = "ascending"
    descending = "descending"


class GOEnrichmentBarPlotValue(Enum):
    p_value = "p-value"
    fdr = "fdr"


class GOEnrichmentDotPlotXAxisType(Enum):
    gene_sets = "Gene Sets"
    combined_score = "Combined Score"


class GSEADotPlotDotColorValue(Enum):
    fdr_q_val = "FDR q-val"
    nom_p_val = "NOM p-val"


class GSEADotPlotXAxisValue(Enum):
    es = "ES"
    nes = "NES"


class PlotColors(Enum):
    PROTzilla_default = PLOT_COLOR_SEQUENCE


class EmptyEnum(Enum):
    pass


class DataIntegrationStep(Step):
    section = "data_integration"

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        return inputs


class PlotStep(DataIntegrationStep):
    operation = "plot"

    def handle_calc_outputs(self, outputs: dict):
        super().handle_calc_outputs(outputs)
        plots = outputs["plots"] if "plots" in outputs else []
        self.plots = Plots(plots)


class EnrichmentAnalysisGOAnalysisWithString(DataIntegrationStep):
    display_name = "GO analysis with STRING"
    operation = "enrichment_analysis"
    method_description = "Online GO analysis using STRING API"

    output_keys = ["enrichment_df"]

    def create_form(self):
        return Form(
            label="GO analysis with STRING",
            input_fields=[
                DropdownField(
                    name = "proteins_df",
                    label = "Dataframe with protein IDs and direction of expression change column (e.g. log2FC)",
                ),
                NumberField(
                    name = "differential_expression_threshold",
                    label = "Threshold for differential expression: Proteins with fold change > threshold are upregulated, proteins fold change < threshold downregulated. Applied symmetrically to log fold changes:",
                    value = 0,
                    min = 0,
                    max = 4294967295,
                ),
                MultiSelectField(
                    name = "gene_sets_restring",
                    label = "Knowledge bases for enrichment",
                ),
                NumberField(
                    name = "organism",
                    label = "Organism / NCBI taxon identifiers (e.g. Human is 9606)",
                    value = 9606,
                ),
                DropdownField(
                    name = "direction",
                    label = "Direction of the analysis",
                    value = Direction.both,
                    options = Direction,
                ),
                FileInput(
                    name = "background_path",
                    label = "Background set (no upload = entire proteome), UniProt IDs (one per line, txt or csv)",
                ),
            ]
        )

    def modify_form(self, form, run):
        proteins_df_field = form["proteins_df"]
        gene_sets_restring_field = form["gene_sets_restring"]

        proteins_df_field.set_options(
            form_helper.get_choices(
                run, DIFFERENTIALLY_EXPRESSED_PROTEINS_DF
            )
        )

        gene_sets_restring_field.options = form_helper.to_choices(
            restring.settings.file_types
        )
        
    calc_method = staticmethod(enrichment_analysis.GO_analysis_with_STRING)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["proteins_df"] = steps.get_step_output(
            Step, "differentially_expressed_proteins_df", inputs["proteins_df"]
        )  # TODO name fix
        if (
            inputs.get("proteins_df") is None
            or not "log2_fold_change" in inputs["proteins_df"].columns
        ):
            raise ValueError(
                "No data found to be enriched. Please do a differential expression analysis first or select the corrent step"
            )
        inputs["differential_expression_col"] = "log2_fold_change"

        return inputs


class EnrichmentAnalysisGOAnalysisWithEnrichr(DataIntegrationStep):
    display_name = "GO analysis with Enrichr"
    operation = "enrichment_analysis"
    method_description = "Online GO analysis using Enrichr API"
    output_keys = ["enrichment_df"]

    calc_method = staticmethod(enrichment_analysis.GO_analysis_with_Enrichr)

    def create_form(self):
        return Form(
            label = "GO analysis with Enrichr",
            input_fields = [
                DropdownField(
                    name = "protein_df_step_instance",
                    label = "Dataframe with protein IDs and direction of expression change column (e.g. log2FC). Maybe do a differential expression analysis first",
                ),
                NumberField(
                    name = "differential_expression_threshold",
                    label = "Threshold for differential expression: Proteins with fold change > threshold are upregulated, proteins "
                            "fold change < threshold downregulated. Applied symmetrically to log fold changes:",
                    min = 0,
                    max = 4294967295,
                    value = 0,
                ),
                DropdownField(
                    name = "gene_mapping_step_instance",
                    label = "Gene mapping",
                ),
                DropdownField(
                    name = "direction",
                    label = "Direction of the analysis",
                    value = Direction.both,
                    options = Direction,
                ),
                DropdownField(
                    name = "organism",
                    label = "Organism",
                    value = Organism.human,
                    options = Organism,
                ),
                DropdownField(
                    name = "gene_sets_field",
                    label = "Gene sets",
                    value = GeneSetsField.choose_from_enrichr_options,
                    options = GeneSetsField,
                ),
                FileInput(
                    name = "gene_sets_path",
                    label = "Upload gene sets with uppercase gene symbols (any of the following file types: .gmt, .txt, .csv, "
                            ".json \n"
                            ".txt (one set per line): SetName followed by tab-separated list of proteins\n"
                            ".csv (one set per line): SetName, Gene1, Gene2, ...\n"
                            r".json: {SetName: [Gene1, Gene2, ...], SetName2: [Gene2, Gene3,...]})"
                ),
                DropdownField(
                    name = "gene_sets_enrichr",
                    label = "Gene set libraries",
                ),
                DropdownField(
                    name = "background_type",
                    label = "Background",
                    value = GOAnalysisWithEnrichrBackgroundType.all_genes,
                    options = GOAnalysisWithEnrichrBackgroundType,
                ),
                FileInput(
                    name = "background_path",
                    label = "Background set with uppercase gene symbols (one gene per line, csv or txt)",
                ),
                NumberField(
                    name = "background_number",
                    label = "Number of expressed genes in the background",
                    min = 1,
                    max = 4294967295,
                    step = 1,
                    value = 0,
                ),
                DropdownField(
                    name = "background_biomart",
                    label = "Biomart dataset",
                ),
            ]
        )

    def modify_form(self, form, run):
        protein_df_step_instance_field = form["protein_df_step_instance"]
        gene_mapping_step_instance_field = form["gene_mapping_step_instance"]
        gene_sets_field = form["gene_sets_field"]
        gene_sets_enricher_field = form["gene_sets_enrichr"]
        gene_sets_path_field = form["gene_sets_path"]
        background_type_field = form["background_type"]
        background_biomart_field = form["background_biomart"]
        background_path_field = form["background_path"]
        background_number_field = form["background_number"]


        protein_df_step_instance_field.set_options(
            form_helper.get_choices(
                run, DIFFERENTIALLY_EXPRESSED_PROTEINS_DF
            )
        )
        gene_mapping_step_instance_field.set_options(
            form_helper.get_choices(
                run, "gene_mapping_df"
            )
        )

        for field_name in [
            "gene_sets_enrichr",
            "gene_sets_path",
            "background_path",
            "background_number",
            "background_biomart",
        ]:
            form[field_name].isVisible = False
        
        if gene_sets_field.value == GeneSetsField.choose_from_enrichr_options.value:
            gene_sets_enricher_field.isVisible = True
            gene_sets_enricher_field.set_options(
                form_helper.to_choices(
                    gseapy.get_library_name()
                )  # TODO check whether we need to pass the organism name here
            )
        else:
            gene_sets_path_field.isVisible = True
        
        if (
           background_type_field.value == GOAnalysisWithEnrichrBackgroundType.choose_biomart_dataset.value 
        ):
            background_biomart_field.isVisible = True
            database = restring.biomart_database("ENSEMBL_MART_ENSEMBL")
            background_biomart_field.set_options(
                form_helper.to_choices(
                    [
                        database.datasets[dataset].display_name
                        for dataset in database.datasets
                    ]
                )
            )
        elif (
            background_type_field.value == GOAnalysisWithEnrichrBackgroundType.upload_a_file.value
        ):
            background_path_field.isVisible = True
        elif (
            background_type_field.value == GOAnalysisWithEnrichrBackgroundType.number_of_expressed_genes.value
        ):
            background_number_field.isVisible = True


    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["proteins_df"] = steps.get_step_output(
            Step,
            "differentially_expressed_proteins_df",
            inputs["protein_df_step_instance"],
        )  # TODO name fix
        if (
            inputs.get("proteins_df") is None
            or not "log2_fold_change" in inputs["proteins_df"].columns
        ):
            raise ValueError(
                "No data found to be enriched. Please do a differential expression analysis first or select the corrent step"
            )
        inputs["differential_expression_col"] = "log2_fold_change"
        inputs["gene_mapping_df"] = steps.get_step_output(
            Step, "gene_mapping_df", inputs["gene_mapping_step_instance"]
        )
        return inputs


class EnrichmentAnalysisGOAnalysisOffline(DataIntegrationStep):
    display_name = "GO analysis offline"
    operation = "enrichment_analysis"
    method_description = "Offline GO Analysis using a hypergeometric test"

    output_keys = ["enrichment_df"]

    calc_method = staticmethod(enrichment_analysis.GO_analysis_offline)
    # TODO gene_mapping - adjust this method to use the gene_mapping_df from gene_mapping

    def create_form(self):
        return Form(
            label = "GO analysis offline",
            input_fields = [
                DropdownField(
                    name = "protein_df_step_instance",
                    label = "Dataframe with protein IDs and direction of expression change column (e.g. log2FC)",
                ),
                NumberField(
                    name = "differential_expression_threshold",
                    label = "Threshold for differential expression: proteins with values > threshold are upregulated, proteins "
                    'values < threshold downregulated. If "log" is in the name of differential_expression_col, '
                    "threshold is applied symmetrically: e.g. log2_fold_change > threshold is upregulated, "
                    "if log2_fold_change < -threshold downregulated",
                    value = 0,
                    min = 0,
                    max = 4294967295,
                ),
                DropdownField(
                    name = "gene_mapping_step_instance",
                    label = "Gene mapping",
                ),
                FileInput(
                    name = "gene_sets_path",
                    label = "Upload gene sets with uppercase gene symbols (any of the following file "
                    "types: .gmt, .txt, .csv, .json | .txt (one set per line): SetName "
                    "followed by tab-separated list of proteins | .csv (one set per line): "
                    "SetName, Gene1, Gene2, ... | .json: {SetName: [Gene1, Gene2, ...], "
                    "SetName2: [Gene2, Gene3, ...]})",
                ),
                DropdownField(
                    name = "direction",
                    label = "Direction of the analysis",
                    value = Direction.both,
                    options = Direction,
                ),
                DropdownField(
                    name = "background_type",
                    label = "Background",
                    value = GOAnalysisOflineBackgroundType.all_genes,
                    options = GOAnalysisOflineBackgroundType,
                ),
                FileInput(
                    name = "background_path",
                    label = "Background set with uppercase gene symbols (one gene per line, csv or txt)",
                ),
                NumberField(
                    name = "background_number",
                    label = "Number of expressed genes in the background",
                    min = 1,
                    max = 4294967295,
                    step = 1,
                    value = 1
                ),
            ]
        )

    def modify_form(self, form, run):
        protein_df_step_instance_field = form["protein_df_step_instance"]
        gene_mapping_step_instance_field = form["gene_mapping_step_instance"]
        background_type_field = form["background_type"]
        background_path_field = form["background_path"]
        background_number_field = form["background_number"]

        protein_df_step_instance_field.set_options(
            form_helper.get_choices(
                run, DIFFERENTIALLY_EXPRESSED_PROTEINS_DF
            )
        )
        gene_mapping_step_instance_field.set_options(
            form_helper.get_choices(
                run, "gene_mapping_df"
            )
        )

        background_path_field.isVisible = False
        background_number_field.isVisible = False

        if (
            background_type_field.value
            == GOAnalysisOflineBackgroundType.upload_a_file.value
        ):
            background_path_field.isVisible = True
        elif (
            background_type_field.value
            == GOAnalysisOflineBackgroundType.number_of_expressed_genes.value
        ):
            background_number_field.isVisible = True
        


    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["proteins_df"] = steps.get_step_output(
            Step, "differentially_expressed_proteins_df", inputs["protein_df_step_instance"]
        )  # TODO name fix
        if (
            inputs.get("proteins_df") is None
            or not "log2_fold_change" in inputs["proteins_df"].columns
        ):
            raise ValueError(
                "No data found to be enriched. Please do a differential expression analysis first or select the corrent step"
            )
        inputs["differential_expression_col"] = "log2_fold_change"
        inputs["gene_mapping_df"] = steps.get_step_output(
            Step, "gene_mapping_df", inputs["gene_mapping_step_instance"]
        )
        return inputs


class EnrichmentAnalysisWithGSEA(DataIntegrationStep):
    display_name = "GSEA"
    operation = "enrichment_analysis"
    method_description = "Perform gene set enrichment analysis"

    output_keys = ["enrichment_df", "ranking"]

    calc_method = staticmethod(enrichment_analysis.gsea)

    def create_form(self):
        return Form(
            label = "GSEA",
            input_fields = [
                DropdownField(
                    name = "protein_df_step_instance",
                    label = "Dataframe with protein IDs, samples and intensities",
                ),
                DropdownField(
                    name = "gene_mapping_step_instance",
                    label = "Gene mapping",
                ),
                DropdownField(
                    # TODO: Dynamic parameters
                    name = "gene_sets_field",
                    label = "How do you want to provide the gene sets? (reselect to show dynamic fields)",
                    value = GeneSetsField.choose_from_enrichr_options,
                    options = GeneSetsField,
                ),
                FileInput(
                    name = "gene_sets_path",
                    label = "Upload gene sets with uppercase gene symbols (any of the following file "
                            "types: .gmt, .txt, .csv, .json | .txt (one set per line): SetName "
                            "followed by tab-separated list of proteins | .csv (one set per line): "
                            "SetName, Gene1, Gene2, ... | .json: {SetName: [Gene1, Gene2, ...], "
                            "SetName2: [Gene2, Gene3, ...]})",
                ),
                DropdownField(
                    name = "gene_sets_enrichr",
                    label = "Gene sets",
                ),
                DropdownField(
                    name = "grouping",
                    label = "Grouping from metadata",
                ),
                DropdownField(
                    name = "group1",
                    label = "Group1",
                ),
                DropdownField(
                    name = "group2",
                    label = "Group2",
                ),
                NumberField(
                    name = "min_size",
                    label = "Minimum number of genes from gene set also in data",
                    value = 15,
                ),
                NumberField(
                    name = "max_size",
                    label = "Maximum number of genes from gene set also in data",
                    value = 500,
                ),
                NumberField(
                    name = "number_of_permutations",
                    label = "Number of permutations",
                    value = 1000,
                ),
                DropdownField(
                    name = "permutation_type",
                    label = "Permutation type (if samples >=15 set to phenotype)",
                    value = PermutationTypeField.phenotype,
                    options = PermutationTypeField,
                ),
                DropdownField(
                    name = "ranking_method",
                    label = "Method to calculate correlation or ranking",
                    value = RankingMethodField.signal_to_noise,
                    options = RankingMethodField,
                ),
                FloatField(
                    name = "weighted_score",
                    label = "Weighted score for the enrichment score calculation, recommended values: "
                            "0, 1, 1.5 or 2",
                    value = 1,
                ),
            ]
        )

    def modify_form(self, form, run):
        protein_df_field = form["protein_df_step_instance"]
        gene_mapping_step_instance_field = form["gene_mapping_step_instance"]
        gene_sets_field = form["gene_sets_field"]
        gene_sets_enrichr_field = form["gene_sets_enrichr"]
        gene_sets_path_field = form["gene_sets_path"]
        grouping_field = form["grouping"]
        group1_field = form["group1"]
        group2_field = form["group2"]

        protein_df_field.set_options(
            form_helper.get_choices(
                run, DIFFERENTIALLY_EXPRESSED_PROTEINS_DF
            )
        )
        gene_mapping_step_instance_field.set_options(
            form_helper.get_choices(
                run, "gene_mapping_df"
            )
        )

        gene_sets_enrichr_field.isVisible = False
        gene_sets_path_field.isVisible = False

        if gene_sets_field.value == GeneSetsField.choose_from_enrichr_options.value:
            gene_sets_enrichr_field.isVisible = True
            gene_sets_enrichr_field.set_options(
                form_helper.to_choices(
                    gseapy.get_library_name()
                )  # TODO check whether we need to pass the organism name here
            )
        else:
            gene_sets_path_field.isVisible = True

        grouping_field.set_options(
            form_helper.get_choices_for_metadata_non_sample_columns(run)
        )

        if not grouping_field.value:
            return
        
        group1_field.set_options(
            form_helper.to_choices(
                run.steps.metadata_df[grouping_field.value].unique()
            )
        )
        if (group1_field.value in run.steps.metadata_df[grouping_field.value].unique()):
            group2_field.set_options(
                [
                    Option(el, el)
                    for el in run.steps.metadata_df[grouping_field.value].unique()
                    if el != group1_field.value
                ]
            )
        else:
            group2_field.set_options(
                reversed(
                    form_helper.to_choices(
                        run.steps.metadata_df[grouping_field.value].unique()
                    )
                )
            )
    
    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["protein_df"] = steps.get_step_output(
            Step, "differentially_expressed_proteins_df", inputs["protein_df_step_instance"]
        )
        inputs["metadata_df"] = steps.metadata_df
        inputs["gene_mapping_df"] = steps.get_step_output(
            Step, "gene_mapping_df", inputs["gene_mapping_step_instance"]
        )


class EnrichmentAnalysisWithPrerankedGSEA(DataIntegrationStep):
    display_name = "GSEA preranked"
    operation = "enrichment_analysis"
    method_description = "Maps proteins to genes and performs GSEA according using provided numerical column for ranking"

    output_keys = ["enrichment_df", "ranking"]

    calc_method = staticmethod(enrichment_analysis.gsea_preranked)

    def create_form(self):
        return Form(
            label = "GSEA preranked",
            input_fields = [
                DropdownField(
                    name = "protein_df_step_instance",
                    label = "Dataframe with protein IDs, samples and intensities",
                ),
                DropdownField(
                    name = "gene_mapping_step_instance",
                    label = "Gene mapping",
                ),
                DropdownField(
                    name = "ranking_column",
                    label = "Column to use for ranking",
                ),
                DropdownField(
                    name = "ranking_direction",
                    label = "Sort the ranking column (ascending - smaller values are better, "
                            "descending - larger values are better)",
                    value = RankingDirectionField.ascending,
                    options = RankingDirectionField,
                ),
                DropdownField(
                    name = "gene_sets_field",
                    label = "How do you want to provide the gene sets? (reselect to show dynamic fields)",
                    value = GeneSetsField.choose_from_enrichr_options,
                    options = GeneSetsField,
                    # Todo: Dynamic parameters
                ),
                FileInput(
                    name = "gene_sets_path",
                    label = "Upload gene sets with uppercase gene symbols (any of the following file "
                            "types: .gmt, .txt, .csv, .json | .txt (one set per line): SetName "
                            "followed by tab-separated list of proteins | .csv (one set per line): "
                            "SetName, Gene1, Gene2, ... | .json: {SetName: [Gene1, Gene2, ...], "
                            "SetName2: [Gene2, Gene3, ...]})",
                ),
                DropdownField(
                    name = "gene_sets_enrichr",
                    label = "Gene sets",
                ),
                NumberField(
                    name = "min_size",
                    label = "Minimum number of genes from gene set also in data",
                    value = 15,
                ),
                NumberField(
                    name = "max_size",
                    label = "Maximum number of genes from gene set also in data",
                    value = 500,
                ),
                NumberField(
                    name = "number_of_permutations",
                    label = "Number of permutations",
                    value = 1000,
                ),
                DropdownField(
                    name = "permutation_type",
                    label = "Permutation type (if samples >=15 set to phenotype)",
                    value = PermutationTypeField.phenotype,
                    options = PermutationTypeField,
                ), 
                DropdownField(
                    name = "ranking_method",
                    label = "Method to calculate correlation or ranking",
                    value = RankingMethodField.signal_to_noise,
                    options = RankingMethodField,
                ),
                FloatField(
                    name = "weighted_score",
                    label = "Weighted score for the enrichment score calculation, recommended values: "
                            "0, 1, 1.5 or 2",
                    value = 1,
                ),
            ]
        )
    
    def modify_form(self, form, run):
        protein_df_step_instance_field = form["protein_df_step_instance"]
        gene_mapping_step_instance_field = form["gene_mapping_step_instance"]
        ranking_column_field = form["ranking_column"]

        protein_df_step_instance_field.set_options(
            form_helper.get_choices(
                run, DIFFERENTIALLY_EXPRESSED_PROTEINS_DF
            )
        )

        gene_mapping_step_instance_field.set_options(
            form_helper.get_choices(
                run, "gene_mapping_df"
            )
        )

        if protein_df_step_instance_field.value:
            column_names = list(run.steps.get_step_output(
                Step, "differentially_expressed_proteins_df", protein_df_step_instance_field.value
            ))
            ranking_column_field.set_options([Option(el, el) for el in column_names])
        else:
            ranking_column_field.set_options()
        
        gene_sets_field = form["gene_sets_field"]
        gene_sets_enrichr_field = form["gene_sets_enrichr"]
        gene_sets_path_field = form["gene_sets_path"]
        
        gene_sets_enrichr_field.isVisible = False
        gene_sets_path_field.isVisible = False

        if gene_sets_field.value == GeneSetsField.choose_from_enrichr_options.value:
            gene_sets_enrichr_field.isVisible = True
            gene_sets_enrichr_field.set_options(
                form_helper.to_choices(
                    gseapy.get_library_name()
                )
            )
        else:
            gene_sets_path_field.isVisible = True


    def insert_dataframes(self, steps, inputs):
        inputs["protein_df"] = steps.get_step_output(
            Step, "differentially_expressed_proteins_df", inputs["protein_df_step_instance"]
        )
        inputs["gene_mapping_df"] = steps.get_step_output(
            Step, "gene_mapping_df", inputs["gene_mapping_step_instance"]
        )



class DatabaseIntegrationByGeneMapping(DataIntegrationStep):
    display_name = "Gene mapping"
    operation = "database_integration"
    method_description = "Map protein groups to genes"

    output_keys = ["gene_mapping_df", "filtered_protein_ids"]

    calc_method = staticmethod(database_integration.gene_mapping)

    def create_form(self):
        return Form(
            label = "Gene mapping",
            input_fields = [
                MultiSelectField(
                    name = "database_names",
                    label = "Uniprot databases (offline)",
                ),
                CheckboxField(
                    name = "use_biomart",
                    label = "Use Biomart after Uniprot databases (online)",
                    value = False,
                ),
                DropdownField(
                    name = "dataframe",
                    label = "Step to use",
                ),
            ]
        )
        
    def modify_form(self, form, run):
        form["database_names"].set_options(
            form_helper.to_choices(
                uniprot_databases()
            )
        )

        form["dataframe"].set_options(
            form_helper.get_choices(
                run, DIFFERENTIALLY_EXPRESSED_PROTEINS_DF
            )
        ) # TODO this looks and sounds very generic, be more specific, maybe it needs diffexp step

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["dataframe"] = steps.get_step_output(
            Step, "differentially_expressed_proteins_df", inputs["dataframe"]
        )
        return inputs


class DatabaseIntegrationByUniprot(DataIntegrationStep):
    display_name = "Uniprot"
    operation = "database_integration"
    method_description = "Add Uniprot data to a dataframe"

    output_keys = ["results_df"]

    calc_method = staticmethod(database_integration.add_uniprot_data)

    # TODO: uniprot
    # TODO: Add dynamic fill for database name and fields
    def create_form(self):
        return Form(
            label = "Uniprot",
            input_fields = [
                DropdownField(
                    name = "database_name",
                    label = "Uniprot databases (offline)",
                ),
                MultiSelectField(
                    name = "fields",
                    label = "Fields",
                ),
            ]
        )


class PlotGOEnrichmentBarPlot(PlotStep):
    display_name = "Bar plot for GO enrichment analysis"
    operation = "plot"
    method_description = "Creates a bar plot from GO enrichment data"

    output_keys = ["plots"]

    def create_form(self):
        return Form(
            label = "Bar plot for GO enrichment analysis",
            input_fields = [
                DropdownField(
                    name = "input_df_step_instance",
                    label = "Choose dataframe to be plotted",
                ),
                DropdownField(
                    name = "value",
                    label = "Value (bars will be plotted as -log10(value)), fdr only for GO analysis with STRING, p_value is adjusted if available",
                    value = GOEnrichmentBarPlotValue.p_value,
                    options = GOEnrichmentBarPlotValue,
                ),
                MultiSelectField(
                    name = "gene_sets",
                    label = "Knowledge bases for enrichment",
                ),
                NumberField(
                    name = "top_terms",
                    label = "Number of top enriched terms per category",
                    min = 1,
                    max = 100,
                    step = 1,
                    value = 10,
                ),
                FloatField(
                    name = "cutoff",
                    label = "Only terms with adjusted p-value (or FDR) < cutoff will be shown",
                    min = 0,
                    max = 1,
                    step = 0.01,
                    value = 0.05,
                ),
                TextField(
                    name = "title",
                    label = "Title of the plot (optional)",
                ),
            ]
        )
    
    def modify_form(self, form, run):
        form["input_df_step_instance"].options = form_helper.get_choices(
            run, "enrichment_df"
        )
        if(not form["input_df_step_instance"].value) and form["input_df_step_instance"].options:
            form["input_df_step_instance"].value = form["input_df_step_instance"].options[0].label

        if form["input_df_step_instance"].value:
            form["gene_sets"].options = form_helper.to_choices(
                run.steps.get_step_output(
                    Step, "enrichment_df", form["input_df_step_instance"].value
                )["Gene_set"].unique()
            )

    plot_method = staticmethod(di_plots.GO_enrichment_bar_plot)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs[
            "figsize"
        ] = None  # TODO this should not have to be done manually if the parameter is optional
        inputs["input_df"] = steps.get_step_output(
            Step, "enrichment_df", inputs["input_df_step_instance"]
        )
        return inputs


class PlotGOEnrichmentDotPlot(PlotStep):
    display_name = "Dot plot for GO enrichment analysis (offline & with Enrichr) "
    operation = "plot"
    method_description = "Creates a categorical scatter plot from GO enrichment data"

    output_keys = ["plots"]

    calc_method = staticmethod(di_plots.GO_enrichment_dot_plot)

    def create_form(self):
        return Form(
            label = "Dot plot for GO enrichment analysis",
            input_fields = [
                DropdownField(
                    # TODO: input_df fill dynamic with modify_form
                    name = "input_df",
                    label = "Choose Enrichment dataframe to be plotted",
                ),
                DropdownField(
                    name = "x_axis_type",
                    label = "Variable for x-axis: categorical scatter plot for one or multiple gene "
                            "sets, or display combined score for one gene set",
                    value = GOEnrichmentDotPlotXAxisType.gene_sets,
                    options = GOEnrichmentDotPlotXAxisType,
                ),
                MultiSelectField(
                    name = "gene_sets",
                    label = "Sets to be plotted",
                ),
                NumberField(
                    name = "top_terms",
                    label = "Number of top enriched terms per category",
                    min = 1,
                    max = 100,
                    value = 5,
                ),
                FloatField(
                    name = "cutoff",
                    label = "Only terms with adjusted p-value (or FDR) < cutoff will be shown",
                    min = 0,
                    max = 1,
                    step = 0.01,
                    value = 0.05,
                ),
                TextField(
                    name = "title",
                    label = "Title of the plot (optional)",
                ),
                CheckboxField(
                    name = "rotate_x_labels",
                    label = "Rotate x-axis labels (if multiple categories are selected)",
                    value = True,
                ),
                CheckboxField(
                    name = "show_ring",
                    label = "Show ring around the dots",
                    value = False,
                ),
                NumberField(
                    name = "dot_size",
                    label = "Scale the size of the dots",
                    value = 5,
                ),
            ]
        )
    
    def modify_form(self, form, run):
        form["gene_sets"].set_options([
            Option(el, el)
            for el in run.steps.protein_df["enrichment_categories"].unique()
        ])


class PlotGSEADotPlot(PlotStep):
    display_name = "Dot plot for (pre-ranked) GSEA"
    operation = "plot"
    method_description = "Creates a categorical scatter plot from GSEA data"

    output_keys = ["plots"]

    calc_method = staticmethod(di_plots.gsea_dot_plot)

    def create_form(self):
        return Form(
            label = "Dot plot for (pre-ranked) GSEA",
            input_fields = [
                DropdownField(
                    name = "gsea_df_step_instance",
                    label = "Choose enrichment dataframe to be plotted",
                ),
                MultiSelectField(
                    name = "gene_sets",
                    label = "Sets to be plotted",
                ),
                DropdownField(
                    name = "dot_color_value",
                    label = "Color the dots by value",
                    value = GSEADotPlotDotColorValue.fdr_q_val,
                    options = GSEADotPlotDotColorValue,
                ),
                DropdownField(
                    name = "x_axis_value",
                    label = "Value to display on x axis",
                    value = GSEADotPlotXAxisValue.nes,
                    options = GSEADotPlotXAxisValue,
                ),
                FloatField(
                    name = "cutoff",
                    label = "Cutoff value for fdr q-value or nominal p-value",
                    min = 0,
                    max = 1,
                    step = 0.01,
                    value = 0.05,
                ),
                TextField(
                    name = "title",
                    label = "Title of the plot (optional)",
                ),
                NumberField(
                    name = "dot_size",
                    label = "Scale the size of the dots",
                    value = 5,
                ),
                CheckboxField(
                    name = "show_ring",
                    label = "Show ring around the dots",
                    value = False,
                ),
                CheckboxField(
                    name = "remove_library_names",
                    label = "Remove library names from gene sets (e.g. 'KEGG_2013__')",
                    value = False,
                ),
            ]
        )
    
    def modify_form(self, form, run):
        gsea_df_step_instance_field = form["gsea_df_step_instance"]
        gsea_df_step_instance_field.set_options(
            form_helper.get_choices(
                run, "enrichment_df"
            )
        )
    
    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["gsea_df"] = steps.get_step_output(
            Step, "enrichment_df", inputs["gsea_df_step_instance"]
        )
        return inputs


class PlotGSEAEnrichmentPlot(PlotStep):
    display_name = "Enrichment plot for (pre-ranked) GSEA"
    operation = "plot"
    method_description = "Creates an enrichment plot from (pre-ranked) GSEA data with the enrichment score, ranked_metric, gene rank and hits"

    output_keys = ["plots"]

    calc_method = staticmethod(di_plots.gsea_enrichment_plot)

    def create_form(self):
        return Form(
            label = "Enrichment plot for (pre-ranked) GSEA",
            input_fields = [
                DropdownField(
                    name = "term_dict",
                    label = "Enrichment details gene set to be plotted",
                ),
                TextField(
                    name = "term_name",
                    label = "Name of the term_dict for title",
                ),
                DropdownField(
                    name = "ranking",
                    label = "Ranking from GSEA",
                ),
                TextField(
                    name = "pos_pheno_label",
                    label = "Label for positively correlated phenotype",
                ),
                TextField(
                    name = "neg_pheno_label",
                    label = "Label for negatively correlated phenotype",
                ),
            ]
        )        
