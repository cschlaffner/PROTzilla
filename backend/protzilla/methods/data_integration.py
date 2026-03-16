from __future__ import annotations
from abc import ABC
from typing_extensions import override

import restring
import gseapy
from backend.protzilla import form_helper
from backend.protzilla.constants.colors import PLOT_COLOR_SEQUENCE
from backend.protzilla.constants.data_types import DataKey
from backend.protzilla.data_integration import (
    database_integration,
    di_plots,
    enrichment_analysis,
)
from backend.protzilla.data_integration.database_query import (
    biomart_database,
    uniprot_databases,
)
from backend.protzilla.data_integration.enrichment_analysis_gsea import GeneSetsType
from backend.protzilla.form import (
    CheckboxField,
    DropdownField,
    Enum,
    FileInput,
    FloatField,
    Form,
    MultiSelectField,
    NumberField,
    TextField,
)
from backend.protzilla.run import Run
from backend.protzilla.steps import Plots, Step, Section
from backend.protzilla.step_manager import StepManager
from backend.protzilla.data_integration.enrichment_analysis import (
    GOAnalysisOflineBackgroundType,
    GOAnalysisWithEnrichrBackgroundType,
)


class Direction(Enum):
    up = "up"
    down = "down"
    both = "both"


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


class DataIntegrationStep(Step, ABC):
    section = Section.DATA_INTEGRATION


class EnrichmentAnalysisStep(DataIntegrationStep, ABC):
    operation = "enrichment_analysis"


class EnrichmentAnalysisGOStep(EnrichmentAnalysisStep, ABC):
    output_keys = [DataKey.ENRICHMENT_DF]

    @override
    def insert_dataframes(self, steps: StepManager) -> None:
        super().insert_dataframes(steps)
        if (
            self.inputs.get(DataKey.PROTEIN_DF) is None
            or not self.inputs["differential_expression_col"]
            in self.inputs[DataKey.PROTEIN_DF].columns
        ):
            raise ValueError(
                "No data found to be enriched. Please do a differential expression analysis first or select the correct step"
            )


class DataIntegrationPlotStep(DataIntegrationStep, ABC):
    operation = "plot"

    @override
    def handle_calc_outputs(self, outputs: dict) -> None:
        super().handle_calc_outputs(outputs)
        plots = outputs["plots"] if "plots" in outputs else []
        self.plots = Plots(plots)


class EnrichmentAnalysisGOAnalysisWithString(EnrichmentAnalysisGOStep):
    display_name = "GO analysis with STRING"
    method_description = "Online GO analysis using STRING API"

    def create_form(self):
        return Form(
            label="GO analysis with STRING",
            input_fields=[
                DropdownField(
                    name="differential_expression_col",
                    label="Column in the protein table containing the values for direction of expression change",
                ),
                NumberField(
                    name="differential_expression_threshold",
                    label="Threshold for differential expression: Proteins with fold change > threshold are upregulated, proteins fold change < threshold downregulated. Applied symmetrically to log fold changes:",
                    value=0,
                    min=0,
                    max=4294967295,
                    step=1,
                    hasStepButtons=True,
                ),
                MultiSelectField(
                    name="gene_sets_restring",
                    label="Knowledge bases for enrichment",
                ),
                NumberField(
                    name="organism",
                    label="Organism / NCBI taxon identifiers (e.g. Human is 9606)",
                    value=9606,
                ),
                DropdownField(
                    name="direction",
                    label="Direction of the analysis",
                    value=Direction.both.value,
                    options=Direction,
                ),
                FileInput(
                    name="background_path",
                    label="Background set (no upload = entire proteome), UniProt IDs (one per line, txt or csv)",
                ),
            ],
        )

    @override
    def modify_form(self, run: Run) -> None:
        gene_sets_restring_field: MultiSelectField = self.form["gene_sets_restring"]

        gene_sets_restring_field.set_options(
            form_helper.to_choices(restring.settings.file_types)
        )

        differential_expression_col_field: DropdownField = self.form[
            "differential_expression_col"
        ]

        prot_source, source_handle = self.input_source(run.steps, DataKey.PROTEIN_DF)

        if prot_source is not None and source_handle is not None:
            differential_expression_col_field.set_options(
                form_helper.get_choices_for_df_columns(
                    run, step_id=prot_source, output_key=source_handle, required=True
                )
            )

    calc_method = staticmethod(enrichment_analysis.GO_analysis_with_STRING)


class EnrichmentAnalysisGOAnalysisWithEnrichr(EnrichmentAnalysisGOStep):
    display_name = "GO analysis with Enrichr"
    method_description = "Online GO analysis using Enrichr API"

    calc_method = staticmethod(enrichment_analysis.GO_analysis_with_Enrichr)

    def create_form(self):
        return Form(
            label="GO analysis with Enrichr",
            input_fields=[
                DropdownField(
                    name="differential_expression_col",
                    label="Column in the protein table containing the values for direction of expression change",
                ),
                FloatField(
                    name="differential_expression_threshold",
                    label="Threshold for differential expression: Proteins with fold change > threshold are upregulated, proteins "
                    "fold change < threshold downregulated. Applied symmetrically to log fold changes:",
                    value=0.0,
                ),
                DropdownField(
                    name="direction",
                    label="Direction of the analysis",
                    value=Direction.both.value,
                    options=Direction,
                ),
                DropdownField(
                    name="organism",
                    label="Organism",
                    value=Organism.human.value,
                    options=Organism,
                ),
                DropdownField(
                    name="gene_sets_field",
                    label="Gene sets",
                    value=GeneSetsType.choose_from_enrichr_options.value,
                    options=GeneSetsType,
                ),
                FileInput(
                    name="gene_sets_path",
                    label="Upload gene sets with uppercase gene symbols (any of the following file types: .gmt, .txt, .csv, "
                    ".json \n"
                    ".txt (one set per line): SetName followed by tab-separated list of proteins\n"
                    ".csv (one set per line): SetName, Gene1, Gene2, ...\n"
                    r".json: {SetName: [Gene1, Gene2, ...], SetName2: [Gene2, Gene3,...]})",
                ),
                DropdownField(
                    name="gene_sets_enrichr",
                    label="Gene set libraries",
                ),
                DropdownField(
                    name="background_type",
                    label="Background",
                    value=GOAnalysisWithEnrichrBackgroundType.all_genes.value,
                    options=GOAnalysisWithEnrichrBackgroundType,
                ),
                FileInput(
                    name="background_path",
                    label="Background set with uppercase gene symbols (one gene per line, csv or txt)",
                ),
                NumberField(
                    name="background_number",
                    label="Number of expressed genes in the background",
                    min=1,
                    max=4294967295,
                    step=1,
                    value=1,
                ),
                DropdownField(
                    name="background_biomart",
                    label="Biomart dataset",
                ),
            ],
        )

    @override
    def modify_form(self, run: Run) -> None:
        gene_sets_field: DropdownField = self.form["gene_sets_field"]
        gene_sets_enricher_field: DropdownField = self.form["gene_sets_enrichr"]
        gene_sets_path_field: FileInput = self.form["gene_sets_path"]
        background_type_field: DropdownField = self.form["background_type"]
        background_biomart_field: DropdownField = self.form["background_biomart"]
        background_path_field: FileInput = self.form["background_path"]
        background_number_field: NumberField = self.form["background_number"]

        for field_name in [
            "gene_sets_enrichr",
            "gene_sets_path",
            "background_path",
            "background_number",
            "background_biomart",
        ]:
            self.form[field_name].isVisible = False

        if gene_sets_field.value == GeneSetsType.choose_from_enrichr_options.value:
            gene_sets_enricher_field.isVisible = True
            gene_sets_enricher_field.set_options(
                form_helper.to_choices(
                    gseapy.get_library_name()
                )  # TODO check whether we need to pass the organism name here
            )
        else:
            gene_sets_path_field.isVisible = True

        if (
            background_type_field.value
            == GOAnalysisWithEnrichrBackgroundType.choose_biomart_dataset.value
        ):
            background_biomart_field.isVisible = True
            database = biomart_database("ENSEMBL_MART_ENSEMBL")
            background_biomart_field.set_options(
                form_helper.to_choices(
                    [
                        database.datasets[dataset].display_name
                        for dataset in database.datasets
                    ]
                )
            )
        elif (
            background_type_field.value
            == GOAnalysisWithEnrichrBackgroundType.upload_a_file.value
        ):
            background_path_field.isVisible = True
        elif (
            background_type_field.value
            == GOAnalysisWithEnrichrBackgroundType.number_of_expressed_genes.value
        ):
            background_number_field.isVisible = True

        differential_expression_col_field: DropdownField = self.form[
            "differential_expression_col"
        ]

        prot_source, source_handle = self.input_source(run.steps, DataKey.PROTEIN_DF)

        if prot_source is not None and source_handle is not None:
            differential_expression_col_field.set_options(
                form_helper.get_choices_for_df_columns(
                    run, step_id=prot_source, output_key=source_handle, required=True
                )
            )


class EnrichmentAnalysisGOAnalysisOffline(EnrichmentAnalysisGOStep):
    display_name = "GO analysis offline"
    method_description = "Offline GO Analysis using a hypergeometric test"

    calc_method = staticmethod(enrichment_analysis.GO_analysis_offline)

    def create_form(self):
        return Form(
            label="GO analysis offline",
            input_fields=[
                DropdownField(
                    name="differential_expression_col",
                    label="Column in the protein table containing the values for direction of expression change",
                ),
                FloatField(
                    name="differential_expression_threshold",
                    label="Threshold for differential expression: proteins with values > threshold are upregulated, proteins "
                    'values < threshold downregulated. If "log" is in the name of differential_expression_col, '
                    "threshold is applied symmetrically: e.g. log2_fold_change > threshold is upregulated, "
                    "if log2_fold_change < -threshold downregulated",
                    value=0.0,
                ),
                FileInput(
                    name="gene_sets_path",
                    label="Upload gene sets with uppercase gene symbols (any of the following file "
                    "types: .gmt, .txt, .csv, .json | .txt (one set per line): SetName "
                    "followed by tab-separated list of proteins | .csv (one set per line): "
                    "SetName, Gene1, Gene2, ... | .json: {SetName: [Gene1, Gene2, ...], "
                    "SetName2: [Gene2, Gene3, ...]})",
                ),
                DropdownField(
                    name="direction",
                    label="Direction of the analysis",
                    value=Direction.both.value,
                    options=Direction,
                ),
                DropdownField(
                    name="background_type",
                    label="Background",
                    value=GOAnalysisOflineBackgroundType.upload_a_file.value,
                    options=GOAnalysisOflineBackgroundType,
                ),
                FileInput(
                    name="background_path",
                    label="Background set with uppercase gene symbols (one gene per line, csv or txt)",
                ),
                NumberField(
                    name="background_number",
                    label="Number of expressed genes in the background",
                    min=1,
                    max=4294967295,
                    step=1,
                    value=1,
                ),
            ],
        )

    @override
    def modify_form(self, run: Run) -> None:
        background_type_field: DropdownField = self.form["background_type"]
        background_path_field: FileInput = self.form["background_path"]
        background_number_field: NumberField = self.form["background_number"]

        background_path_field.isVisible = False
        background_number_field.isVisible = False
        print("Background type field value: ", background_type_field.value)
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

        differential_expression_col_field: DropdownField = self.form[
            "differential_expression_col"
        ]

        prot_source, source_handle = self.input_source(run.steps, DataKey.PROTEIN_DF)

        if prot_source is not None and source_handle is not None:
            differential_expression_col_field.set_options(
                form_helper.get_choices_for_df_columns(
                    run, step_id=prot_source, output_key=source_handle, required=True
                )
            )


class EnrichmentAnalysisWithGSEA(EnrichmentAnalysisStep):
    display_name = "GSEA"
    method_description = "Perform gene set enrichment analysis"

    output_keys = [DataKey.ENRICHMENT_DF, "ranking"]

    calc_method = staticmethod(enrichment_analysis.gsea)

    def create_form(self):
        return Form(
            label="GSEA",
            input_fields=[
                DropdownField(
                    # TODO: Dynamic parameters
                    name="gene_sets_type",
                    label="How do you want to provide the gene sets? (reselect to show dynamic fields)",
                    value=GeneSetsType.choose_from_enrichr_options.value,
                    options=GeneSetsType,
                ),
                FileInput(
                    name="gene_sets_path",
                    label="Upload gene sets with uppercase gene symbols (any of the following file "
                    "types: .gmt, .txt, .csv, .json | .txt (one set per line): SetName "
                    "followed by tab-separated list of proteins | .csv (one set per line): "
                    "SetName, Gene1, Gene2, ... | .json: {SetName: [Gene1, Gene2, ...], "
                    "SetName2: [Gene2, Gene3, ...]})",
                ),
                DropdownField(
                    name="gene_sets_enrichr",
                    label="Gene sets",
                ),
                DropdownField(
                    name="grouping",
                    label="Grouping from metadata",
                ),
                DropdownField(
                    name="group1",
                    label="Group1",
                ),
                DropdownField(
                    name="group2",
                    label="Group2",
                ),
                NumberField(
                    name="min_size",
                    label="Minimum number of genes from gene set also in data",
                    value=15,
                ),
                NumberField(
                    name="max_size",
                    label="Maximum number of genes from gene set also in data",
                    value=500,
                ),
                NumberField(
                    name="number_of_permutations",
                    label="Number of permutations",
                    value=1000,
                ),
                DropdownField(
                    name="permutation_type",
                    label="Permutation type (if samples >=15 set to phenotype)",
                    value=PermutationTypeField.phenotype.value,
                    options=PermutationTypeField,
                ),
                DropdownField(
                    name="ranking_method",
                    label="Method to calculate correlation or ranking",
                    value=RankingMethodField.signal_to_noise.value,
                    options=RankingMethodField,
                ),
                FloatField(
                    name="weighted_score",
                    label="Weighted score for the enrichment score calculation, recommended values: "
                    "0, 1, 1.5 or 2",
                    value=1,
                ),
                NumberField(
                    name="threads",
                    label="Number of CPU hardware threads to use for computation",
                    value=4,
                    min=1,
                    step=1,
                ),
                NumberField(
                    name="seed",
                    label="Seed used for random number generator",
                    value=123,
                    step=1,
                ),
            ],
        )

    @override
    def modify_form(self, run: Run) -> None:
        gene_sets_field: DropdownField = self.form["gene_sets_type"]
        gene_sets_enrichr_field: DropdownField = self.form["gene_sets_enrichr"]
        gene_sets_path_field: FileInput = self.form["gene_sets_path"]
        grouping_field: DropdownField = self.form["grouping"]
        group1_field: DropdownField = self.form["group1"]
        group2_field: DropdownField = self.form["group2"]

        gene_sets_enrichr_field.isVisible = False
        gene_sets_path_field.isVisible = False

        if gene_sets_field.value == GeneSetsType.choose_from_enrichr_options.value:
            gene_sets_enrichr_field.isVisible = True
            gene_sets_enrichr_field.set_options(
                form_helper.to_choices(
                    gseapy.get_library_name()
                )  # TODO check whether we need to pass the organism name here
            )
        else:
            gene_sets_path_field.isVisible = True

        # TODO: transfer method for this from data_analysis to form_helper

        metadata_df = self.get_input(run.steps, DataKey.METADATA_DF)

        if metadata_df is not None:
            grouping_field.set_options(
                form_helper.to_choices(metadata_df.columns.unique().to_list())
            )

        grouping = grouping_field.value
        if metadata_df is not None and grouping:

            groups_choices = form_helper.to_choices(
                metadata_df[grouping].unique().tolist()
            )

            group1_field.set_options(groups_choices)
            group2_field.set_options(
                [group for group in groups_choices if group.value != group1_field.value]
            )


class EnrichmentAnalysisWithPrerankedGSEA(EnrichmentAnalysisStep):
    display_name = "GSEA preranked"
    method_description = "Maps proteins to genes and performs GSEA according using provided numerical column for ranking"

    output_keys = [DataKey.ENRICHMENT_DF, "ranking"]

    calc_method = staticmethod(enrichment_analysis.gsea_preranked)

    def create_form(self):
        return Form(
            label="GSEA preranked",
            input_fields=[
                DropdownField(
                    name="ranking_column",
                    label="Column to use for ranking",
                ),
                DropdownField(
                    name="ranking_direction",
                    label="Sort the ranking column (ascending - smaller values are better, "
                    "descending - larger values are better)",
                    value=RankingDirectionField.ascending.value,
                    options=RankingDirectionField,
                ),
                DropdownField(
                    name="gene_sets_field",
                    label="How do you want to provide the gene sets? (reselect to show dynamic fields)",
                    value=GeneSetsType.choose_from_enrichr_options.value,
                    options=GeneSetsType,
                    # Todo: Dynamic parameters
                ),
                FileInput(
                    name="gene_sets_path",
                    label="Upload gene sets with uppercase gene symbols (any of the following file "
                    "types: .gmt, .txt, .csv, .json | .txt (one set per line): SetName "
                    "followed by tab-separated list of proteins | .csv (one set per line): "
                    "SetName, Gene1, Gene2, ... | .json: {SetName: [Gene1, Gene2, ...], "
                    "SetName2: [Gene2, Gene3, ...]})",
                ),
                DropdownField(
                    name="gene_sets_enrichr",
                    label="Gene sets",
                ),
                NumberField(
                    name="min_size",
                    label="Minimum number of genes from gene set also in data",
                    value=15,
                ),
                NumberField(
                    name="max_size",
                    label="Maximum number of genes from gene set also in data",
                    value=500,
                ),
                NumberField(
                    name="number_of_permutations",
                    label="Number of permutations",
                    value=1000,
                ),
                DropdownField(
                    name="permutation_type",
                    label="Permutation type (if samples >=15 set to phenotype)",
                    value=PermutationTypeField.phenotype.value,
                    options=PermutationTypeField,
                ),
                DropdownField(
                    name="ranking_method",
                    label="Method to calculate correlation or ranking",
                    value=RankingMethodField.signal_to_noise.value,
                    options=RankingMethodField,
                ),
                FloatField(
                    name="weighted_score",
                    label="Weighted score for the enrichment score calculation, recommended values: "
                    "0, 1, 1.5 or 2",
                    value=1,
                ),
                NumberField(
                    name="threads",
                    label="Number of CPU hardware threads to use for computation",
                    value=4,
                    min=1,
                    step=1,
                ),
                NumberField(
                    name="seed",
                    label="Seed used for random number generator",
                    value=123,
                    step=1,
                ),
            ],
        )

    @override
    def modify_form(self, run: Run) -> None:
        ranking_column_field: DropdownField = self.form["ranking_column"]

        protein_df = self.get_input(run.steps, DataKey.PROTEIN_DF)
        if protein_df is not None:
            columns = protein_df.columns.to_list()
            ranking_column_field.set_options(form_helper.to_choices(columns))

        gene_sets_field: DropdownField = self.form["gene_sets_field"]
        gene_sets_enrichr_field: DropdownField = self.form["gene_sets_enrichr"]
        gene_sets_path_field: FileInput = self.form["gene_sets_path"]

        gene_sets_enrichr_field.isVisible = False
        gene_sets_path_field.isVisible = False

        if gene_sets_field.value == GeneSetsType.choose_from_enrichr_options.value:
            gene_sets_enrichr_field.isVisible = True
            gene_sets_enrichr_field.set_options(
                form_helper.to_choices(gseapy.get_library_name())
            )
        else:
            gene_sets_path_field.isVisible = True


class DatabaseIntegrationByGeneMapping(DataIntegrationStep):
    display_name = "Gene mapping"
    operation = "database_integration"
    method_description = "Map protein groups to genes"

    output_keys = ["gene_mapping_df"]

    calc_method = staticmethod(database_integration.gene_mapping)

    def create_form(self):
        return Form(
            label="Gene mapping",
            input_fields=[
                MultiSelectField(
                    name="database_names",
                    label="Uniprot databases (offline)",
                ),
                CheckboxField(
                    name="use_biomart",
                    label="Use Biomart after Uniprot databases (online)",
                    value=False,
                ),
            ],
        )

    @override
    def modify_form(self, run: Run) -> None:
        database_names_field: MultiSelectField = self.form["database_names"]
        database_names_field.set_options(form_helper.to_choices(uniprot_databases()))


class DatabaseIntegrationByUniprot(DataIntegrationStep):
    display_name = "Uniprot"
    operation = "database_integration"
    method_description = "Add Uniprot data to a dataframe"

    output_keys = [DataKey.PROTEIN_DF]

    calc_method = staticmethod(database_integration.add_uniprot_data)

    # TODO: uniprot
    # TODO: Add dynamic fill for database name and fields
    def create_form(self):
        return Form(
            label="Uniprot",
            input_fields=[
                DropdownField(
                    name="database_name",
                    label="Uniprot databases (offline)",
                ),
                MultiSelectField(
                    name="fields",
                    label="Fields",
                ),
            ],
        )

    @override
    def modify_form(self, run: Run) -> None:
        database_names_field: MultiSelectField = self.form["database_name"]
        database_names_field.set_options(form_helper.to_choices(uniprot_databases()))


class PlotGOEnrichmentBarPlot(DataIntegrationPlotStep):
    display_name = "Bar plot for GO enrichment analysis"
    method_description = "Creates a bar plot from GO enrichment data"

    output_keys = []

    def create_form(self):
        return Form(
            label="Bar plot for GO enrichment analysis",
            input_fields=[
                DropdownField(
                    name="value",
                    label="Value (bars will be plotted as -log10(value)), fdr only for GO analysis with STRING, p_value is adjusted if available",
                    value=GOEnrichmentBarPlotValue.p_value.value,
                    options=GOEnrichmentBarPlotValue,
                ),
                MultiSelectField(
                    name="gene_sets",
                    label="Knowledge bases for enrichment",
                ),
                NumberField(
                    name="top_terms",
                    label="Number of top enriched terms per category",
                    min=1,
                    step=1,
                    value=10,
                    hasStepButtons=True,
                ),
                FloatField(
                    name="cutoff",
                    label="Only terms with adjusted p-value (or FDR) < cutoff will be shown",
                    min=0,
                    max=1,
                    step=0.01,
                    value=0.05,
                ),
                TextField(
                    name="title",
                    label="Title of the plot (optional)",
                ),
            ],
        )

    @override
    def modify_form(self, run: Run) -> None:
        gene_sets_field: MultiSelectField = self.form["gene_sets"]

        enrichment_df = self.get_input(run.steps, DataKey.ENRICHMENT_DF)

        if enrichment_df is not None:
            gene_sets_field.set_options(
                form_helper.to_choices(enrichment_df["Gene_set"].unique().tolist())
            )

    plot_method = staticmethod(di_plots.GO_enrichment_bar_plot)


class PlotGOEnrichmentDotPlot(DataIntegrationPlotStep):
    display_name = "Dot plot for GO enrichment analysis (offline & with Enrichr) "
    method_description = "Creates a categorical scatter plot from GO enrichment data"

    output_keys = []

    calc_method = staticmethod(di_plots.GO_enrichment_dot_plot)

    internal_inputs = {"figsize"}

    def create_form(self):
        return Form(
            label="Dot plot for GO enrichment analysis",
            input_fields=[
                DropdownField(
                    name="x_axis_type",
                    label="Variable for x-axis: categorical scatter plot for one or multiple gene "
                    "sets, or display combined score for one gene set",
                    value=GOEnrichmentDotPlotXAxisType.gene_sets.value,
                    options=GOEnrichmentDotPlotXAxisType,
                ),
                MultiSelectField(
                    name="gene_sets",
                    label="Sets to be plotted",
                ),
                NumberField(
                    name="top_terms",
                    label="Number of top enriched terms per category",
                    min=1,
                    max=100,
                    value=5,
                ),
                FloatField(
                    name="cutoff",
                    label="Only terms with adjusted p-value (or FDR) < cutoff will be shown",
                    min=0,
                    max=1,
                    step=0.01,
                    value=0.05,
                ),
                TextField(
                    name="title",
                    label="Title of the plot (optional)",
                ),
                CheckboxField(
                    name="rotate_x_labels",
                    label="Rotate x-axis labels (if multiple categories are selected)",
                    value=True,
                ),
                CheckboxField(
                    name="show_ring",
                    label="Show ring around the dots",
                    value=False,
                ),
                NumberField(
                    name="dot_size",
                    label="Scale the size of the dots",
                    value=5,
                ),
            ],
        )

    @override
    def modify_form(self, run: Run) -> None:
        gene_sets_field: MultiSelectField = self.form["gene_sets"]

        enrichment_df = self.get_input(run.steps, DataKey.ENRICHMENT_DF)

        if enrichment_df is not None and "Gene_set" in enrichment_df.columns:
            gene_sets_field.set_options(
                form_helper.to_choices(enrichment_df["Gene_set"].unique().tolist())
            )


class PlotGSEADotPlot(DataIntegrationPlotStep):
    display_name = "Dot plot for (pre-ranked) GSEA"
    method_description = "Creates a categorical scatter plot from GSEA data"

    output_keys = []

    calc_method = staticmethod(di_plots.gsea_dot_plot)

    internal_inputs = {"figsize"}

    def create_form(self):
        return Form(
            label="Dot plot for (pre-ranked) GSEA",
            input_fields=[
                MultiSelectField(
                    name="gene_sets",
                    label="Sets to be plotted",
                ),
                DropdownField(
                    name="dot_color_value",
                    label="Color the dots by value",
                    value=GSEADotPlotDotColorValue.fdr_q_val.value,
                    options=GSEADotPlotDotColorValue,
                ),
                DropdownField(
                    name="x_axis_value",
                    label="Value to display on x axis",
                    value=GSEADotPlotXAxisValue.nes.value,
                    options=GSEADotPlotXAxisValue,
                ),
                FloatField(
                    name="cutoff",
                    label="Cutoff value for fdr q-value or nominal p-value",
                    min=0,
                    max=1,
                    step=0.01,
                    value=0.05,
                ),
                TextField(
                    name="title",
                    label="Title of the plot (optional)",
                ),
                NumberField(
                    name="dot_size",
                    label="Scale the size of the dots",
                    value=5,
                ),
                CheckboxField(
                    name="show_ring",
                    label="Show ring around the dots",
                    value=False,
                ),
                CheckboxField(
                    name="remove_library_names",
                    label="Remove library names from gene sets (e.g. 'KEGG_2013__')",
                    value=False,
                ),
            ],
        )


class PlotGSEAEnrichmentPlot(DataIntegrationPlotStep):
    display_name = "Enrichment plot for (pre-ranked) GSEA"
    method_description = "Creates an enrichment plot from (pre-ranked) GSEA data with the enrichment score, ranked_metric, gene rank and hits"

    output_keys = []

    calc_method = staticmethod(di_plots.gsea_enrichment_plot)

    internal_inputs = {"figsize"}

    def create_form(self):
        return Form(
            label="Enrichment plot for (pre-ranked) GSEA",
            input_fields=[
                DropdownField(
                    name="term_dict",
                    label="Enrichment details gene set to be plotted",
                ),
                TextField(
                    name="term_name",
                    label="Name of the term_dict for title",
                ),
                DropdownField(
                    name="ranking",
                    label="Ranking from GSEA",
                ),
                TextField(
                    name="pos_pheno_label",
                    label="Label for positively correlated phenotype",
                ),
                TextField(
                    name="neg_pheno_label",
                    label="Label for negatively correlated phenotype",
                ),
            ],
        )
