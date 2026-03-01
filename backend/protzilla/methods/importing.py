from __future__ import annotations

import pandas as pd

from backend.protzilla.form import *
from backend.protzilla import form_helper
from backend.protzilla.importing.metadata_import import (
    metadata_column_assignment,
    metadata_import_method,
    metadata_import_method_diann,
)
from backend.protzilla.importing.ms_data_import import (
    diann_import,
    max_quant_import,
    ms_fragger_import,
)
from backend.protzilla.importing.alphafold_protein_structure_load import (
    fetch_alphafold_protein_structure,
    get_all_available_entry_ids_of_monomer_metadata,
    get_all_available_entry_ids_of_multimer_metadata,
    get_monomer_structure_dfs,
    upload_multimer_prediction,
    get_multimer_structure_dfs,
)
from backend.protzilla.importing.peptide_import import peptide_import, evidence_import
from backend.protzilla.steps import Step, StepManager
from protzilla.importing.example_dataset_import import example_dataset_import
from protzilla.importing.fasta_import import fasta_import
from protzilla.importing.crosslinking_import import crosslinking_import
from protzilla.importing.import_utils import (
    AggregationMethods,
    FeatureOrientationType,
)
from backend.protzilla.constants.intensity_types import IntensityType, IntensityNameType
from protzilla.importing.query_generation import generate_alphafold_multimer_query_json


class ImportingStep(Step):
    section = "importing"

    def calc_method(self):
        raise NotImplementedError("This method must be implemented in a subclass.")

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        return inputs

    def modify_form(self, form, run):
        Step.modify_form(self, form, run)
        if run.steps.current_step.calculation_status == "complete":
            form.input_fields[self.index_of_file_input()].value = None

    def index_of_file_input(self):
        """
        Returns the index of the FileInput that should be reset by modify_form. This method
        must be overridden if the FileInput is not index 0.
        """
        return 0


class MaxQuantImport(ImportingStep):
    display_name = "MaxQuant Protein Groups Import"
    operation = "Protein Data Import"
    method_description = "Import the protein groups file form output of MaxQuant"

    output_keys = ["protein_df"]

    def create_form(self):
        return Form(
            label="MaxQuant Protein Groups Import",
            input_fields=[
                FileInput(
                    name="file_path",
                    label="MaxQuant intensities file (proteinGroups.txt)",
                    value=None,
                ),
                DropdownField(
                    name="intensity_name",
                    label="Intensity parameter",
                    value=IntensityType.IBAQ.value,
                    options=IntensityType,
                ),
                CheckboxField(
                    name="ignore_only_identified_by_site",
                    label="Ignore proteins only identified by site",
                    value=False,
                ),
                CheckboxField(
                    name="map_to_uniprot",
                    label="Map to Uniprot IDs using Biomart (online)",
                    value=False,
                ),
                DropdownField(
                    name="aggregation_method",
                    label="Aggregation method used to aggregate duplicate values for protein groups",
                    value=AggregationMethods.sum.value,
                    options=AggregationMethods,
                ),
            ],
        )

    calc_method = staticmethod(max_quant_import)


class DiannImport(ImportingStep):
    display_name = "DIA-NN Import"
    operation = "Protein Data Import"
    method_description = "DIA-NN data import"

    output_keys = ["protein_df"]

    def create_form(self):
        return Form(
            label="DIA-NN Import",
            input_fields=[
                FileInput(
                    name="file_path",
                    label="DIA-NN intensities file (*.pg_matrix.tsv)",
                    value=None,
                ),
                CheckboxField(
                    name="map_to_uniprot",
                    label="Map to Uniprot IDs using Biomart (online)",
                    value=False,
                ),
                DropdownField(
                    name="aggregation_method",
                    label="Aggregation method used to aggregate duplicate values for protein groups",
                    value=AggregationMethods.sum.value,
                    options=AggregationMethods,
                ),
            ],
        )

    calc_method = staticmethod(diann_import)


class MsFraggerImport(ImportingStep):
    display_name = "MS Fragger Combined Protein Import"
    operation = "Protein Data Import"
    method_description = (
        "Import the combined_protein.tsv file form output of MS Fragger"
    )

    output_keys = ["protein_df"]

    def create_form(self):
        return Form(
            label="MS Fragger Combined Protein Import",
            input_fields=[
                FileInput(
                    name="file_path",
                    label="MSFragger intensities file (combined_proteins.tsv)",
                ),
                DropdownField(
                    name="intensity_name",
                    label="intensity name",
                    value=IntensityNameType.INTENSITY.value,
                    options=IntensityNameType,
                ),
                CheckboxField(
                    name="map_to_uniprot",
                    label="Map to Uniprot IDs using Biomart (online)",
                    value=False,
                ),
                DropdownField(
                    name="aggregation_method",
                    label="Aggregation method used to aggregate duplicate values for protein groups",
                    value=AggregationMethods.sum.value,
                    options=AggregationMethods,
                ),
            ],
        )

    calc_method = staticmethod(ms_fragger_import)


class MetadataImport(ImportingStep):
    display_name = "Metadata Import"
    operation = "metadataimport"
    method_description = "Import metadata"

    output_keys = ["metadata_df"]

    def create_form(self):
        return Form(
            label="Metadata Import",
            input_fields=[
                FileInput(
                    name="file_path",
                    label="Metadata file",
                ),
                DropdownField(
                    name="feature_orientation",
                    label="Feature orientation",
                    options=FeatureOrientationType,
                    value=FeatureOrientationType.COLUMNS.value,
                ),
            ],
        )

    calc_method = staticmethod(metadata_import_method)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["protein_df"] = steps.get_step_output(ImportingStep, "protein_df")
        return inputs


class MetadataImportMethodDiann(ImportingStep):
    display_name = "DIA-NN Metadata Import"
    operation = "metadataimport"
    method_description = "Import metadata for run relationships of DIA-NN"

    output_keys = ["metadata_df", "protein_df"]

    def create_form(self):
        return Form(
            label="DIA-NN Metadata Import",
            input_fields=[
                FileInput(
                    name="file_path",
                    label="Run-Relationship metadata file:",
                ),
                CheckboxField(
                    name="groupby_sample",
                    label="Group replicate runs by sample using median",
                    value=False,
                ),
            ],
        )

    calc_method = staticmethod(metadata_import_method_diann)

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        inputs["protein_df"] = steps.get_step_output(DiannImport, "protein_df")
        return inputs


class MetadataColumnAssignment(ImportingStep):
    display_name = "Metadata column assignment"
    operation = "metadataimport"
    method_description = (
        "Assign columns to metadata categories, repeatable for each category"
    )

    output_keys = ["metadata_df", "protein_df"]

    def create_form(self):
        return Form(
            label="Metadata column assignment",
            input_fields=[
                DropdownField(
                    name="metadata_required_column",
                    label="Missing, but required metadata columns",
                ),
                DropdownField(
                    name="metadata_unknown_column",
                    label="Existing, but unknown metadata columns",
                ),
            ],
        )

    def modify_form(self, form, run):
        metadata_required_column = form["metadata_required_column"]
        metadata_unknown_column = form["metadata_unknown_column"]

        metadata = run.steps.get_step_output(
            ImportingStep, "metadata_df", include_current_step=True
        )

        if metadata is not None:
            metadata_required_column.set_options(
                [
                    Option(col, col)
                    for col in ["Sample", "Group", "Batch"]
                    if col not in metadata.columns
                ]
            )
            if len(metadata_required_column.options) == 0:
                metadata_required_column.set_options([])

            unknown_columns = list(
                metadata.columns[
                    ~metadata.columns.isin(["Sample", "Group", "Batch"])
                ].unique()
            )

            metadata_unknown_column.set_options(
                [Option(col, col) for col in unknown_columns]
            )
            if len(metadata_unknown_column.options) == 0:
                metadata_unknown_column.set_options([])

    calc_method = staticmethod(metadata_column_assignment)

    def insert_dataframes(self, steps: StepManager, inputs: dict) -> dict:
        inputs["protein_df"] = steps.get_step_output(ImportingStep, "protein_df")
        inputs["metadata_df"] = steps.get_step_output(
            ImportingStep, "metadata_df", include_current_step=True
        )
        return inputs


class PeptideImport(ImportingStep):
    display_name = "MaxQuant Peptide Import"
    operation = "peptide_import"
    method_description = "Import peptide data"

    output_keys = ["peptide_df"]

    def create_form(self):
        return Form(
            label="MaxQuant Peptide Import",
            input_fields=[
                FileInput(
                    name="file_path",
                    label="Peptide file",
                ),
                DropdownField(
                    name="intensity_name",
                    label="Intensity parameter",
                    value=IntensityType.INTENSITY.value,
                    options=IntensityType,
                ),
                CheckboxField(
                    name="map_to_uniprot",
                    label="Map to Uniprot IDs using Biomart (online)",
                    value=False,
                ),
            ],
        )

    def modify_form(self, form, run):
        ImportingStep.modify_form(self, form, run)

        map_to_uniprot_field = form["map_to_uniprot"]
        map_to_uniprot_field.value = run.steps.get_step_input(
            [MaxQuantImport, MsFraggerImport, DiannImport],
            "map_to_uniprot",
            default=map_to_uniprot_field.value,
        )

    calc_method = staticmethod(peptide_import)


class EvidenceImport(ImportingStep):
    display_name = "MaxQuant Evidence Import"
    operation = "peptide_import"
    method_description = "Import an evidence file"

    output_keys = ["peptide_df"]

    def create_form(self):
        return Form(
            label="MaxQuant Evidence Import",
            input_fields=[
                FileInput(
                    name="file_path",
                    label="Evidence file",
                ),
                CheckboxField(
                    name="map_to_uniprot",
                    label="Map to Uniprot IDs using Biomart (online)",
                    value=False,
                ),
            ],
        )

    def modify_form(self, form, run):
        ImportingStep.modify_form(self, form, run)

        map_to_uniprot_field = form["map_to_uniprot"]

        map_to_uniprot_field.value = run.steps.get_step_input(
            [MaxQuantImport, MsFraggerImport, DiannImport], "map_to_uniprot"
        )

    calc_method = staticmethod(evidence_import)


class FastaImport(ImportingStep):
    display_name = "Fasta Protein Sequence Import"
    operation = "fasta_import"
    method_description = "Import a fasta file containing protein sequences."

    input_keys = ["file_path"]
    output_keys = ["fasta_df"]

    calc_method = staticmethod(fasta_import)

    def create_form(self):
        return Form(
            label="Fasta Protein Sequence Import",
            input_fields=[
                FileInput(
                    name="file_path",
                    label="Fasta file",
                ),
            ],
        )


class ExampleDatasetImport(ImportingStep):
    display_name = "Example Dataset Import"
    operation = "example_import"
    method_description = (
        "Import the proteins, peptides, and metadata of the PRIDE repository PXD014997, which belongs to the following "
        "paper:\n\n"
        "Aasebø, E.; Berven, F.S.; Bartaula-Brevik, S.; Stokowy, T.; Hovland, R.; Vaudel, M.; Døskeland, S.O.; "
        "McCormack, E.; Batth, T.S.; Olsen, J.V.; et al. Proteome and Phosphoproteome Changes Associated with "
        "Prognosis in Acute Myeloid Leukemia. Cancers 2020, 12, 709.\n"
        "https://doi.org/10.3390/cancers12030709 "
    )

    output_keys = ["metadata_df", "peptide_df", "protein_df"]

    def create_form(self):
        return Form(
            label="Example Dataset Import",
            input_fields=[HeaderInfoField(label=self.method_description)],
        )

    calc_method = staticmethod(example_dataset_import)


class AlphaFoldPredictionLoad(ImportingStep):
    display_name = "AlphaFold DB Monomer Prediction Load"
    operation = "Monomer Structure Import"
    method_description = "Loads the predicted structure of the monomer with the given protein ID out of the AlphaFold DB."

    output_keys = [
        "metadata_df",
        "cif_df",
        "pae_df",
        "plddt_df",
        "amino_acid_sequence_df",
    ]

    plot_method = None

    def create_form(self):
        return Form(
            label="AlphaFold DB Monomer Prediction Load",
            input_fields=[
                TextField(
                    name="uniprot_id",
                    label="Protein ID",
                ),
                CheckboxField(
                    name="persist_upload",
                    label="Upload should be saved persistently across runs",
                    value=True,
                ),
            ],
        )

    calc_method = staticmethod(fetch_alphafold_protein_structure)


class CrosslinkingImport(ImportingStep):
    display_name = "Crosslinking Data Import"
    operation = "Crosslinking Data Import"
    method_description = "Import a file containing crosslinking data"

    output_keys = ["crosslinking_df", "imported_rows_with_errors_df"]

    def create_form(self):
        return Form(
            label="Crosslinking Data Import",
            input_fields=[
                FileInput(
                    name="file_path",
                    label="Crosslinking Data file (.xlsx or .csv)",
                    value=None,
                ),
                TextField(
                    name="organism_ids",
                    label="Organism IDs \n(only required when importing a CSM file)",
                    value="",
                ),
                InfoField(
                    label="Please list them in the order in which they should be applied, separated by a comma \n e.g.: 9606, 10090, 10116"
                ),
            ],
        )

    calc_method = staticmethod(crosslinking_import)


class ImportMonomerStructurePredictionFromDisk(ImportingStep):
    display_name = "Monomer Structure Prediction Import from Disk"
    operation = "Monomer Structure Import"
    method_description = "Load an already uploaded monomer structure prediction from disk into current run"

    output_keys = [
        "metadata_df",
        "cif_df",
        "pae_df",
        "plddt_df",
        "amino_acid_sequence_df",
    ]

    def create_form(self):
        return Form(
            label="Monomer Structure Predictions Import from Disk",
            input_fields=[
                DropdownField(
                    name="entry_id",
                    label="Entry ID of the monomer prediction to be loaded into the run. (Unless specified otherwise this is the Protein ID)",
                    options=form_helper.to_choices(
                        get_all_available_entry_ids_of_monomer_metadata()
                    ),
                )
            ],
        )

    calc_method = staticmethod(get_monomer_structure_dfs)


class UploadMultimerPredictions(ImportingStep):
    display_name = "Multimer Structure Prediction Upload"
    operation = "Multimer Structure Import"
    method_description = "Upload a multimer protein prediction"

    output_keys = [
        "metadata_df",
        "cif_df",
        "confidence_df",
        "full_data_df",
        "amino_acid_sequences_df",
    ]

    def create_form(self):
        return Form(
            label="Multimer Structure Prediction Upload",
            input_fields=[
                TextField(
                    name="entry_id",
                    label="Entry ID of the prediction to be loaded into the run.",
                ),
                InfoField(
                    label="The entry ID should be a unique name given to the uploaded prediction.",
                ),
                TextField(
                    name="uniprot_ids",
                    label="Protein IDs of all proteins used in the sequence.",
                ),
                InfoField(
                    label="Please provide a list of Protein IDs separated by a comma \n e.g.: P68871, P69905, Q5VSL9"
                ),
                TextField(
                    name="model_used",
                    label="The AlphaFold Model used to predict the structure.",
                ),
                FileInput(
                    name="amino_acid_sequences",
                    label="Amino acid sequences of proteins in the prediction (required)",
                    value=None,
                ),
                FileInput(
                    name="cif_file",
                    label="CIF file (required)",
                    value=None,
                ),
                FileInput(
                    name="confidence_file",
                    label="Confidence summary json file (required)",
                    value=None,
                ),
                FileInput(
                    name="full_data_file",
                    label="Full data json file (required)",
                    value=None,
                ),
                CheckboxField(
                    name="persist_upload",
                    label="Upload should be saved persistently across runs",
                    value=True,
                ),
            ],
        )

    calc_method = staticmethod(upload_multimer_prediction)


class ImportMultimerStructurePredictionFromDisk(ImportingStep):
    display_name = "Multimer Structure Prediction Import from Disk"
    operation = "Multimer Structure Import"
    method_description = "Load an already uploaded multimer structure prediction from disk into current run"

    output_keys = [
        "metadata_df",
        "amino_acid_sequences_df",
        "cif_df",
        "confidence_df",
        "full_data_df",
    ]

    def create_form(self):
        return Form(
            label="Multimer Structure Predictions Import from Disk",
            input_fields=[
                DropdownField(
                    name="entry_id",
                    label="Entry ID of the multimer prediction to be loaded into the run.",
                    options=form_helper.to_choices(
                        get_all_available_entry_ids_of_multimer_metadata()
                    ),
                )
            ],
        )

    calc_method = staticmethod(get_multimer_structure_dfs)


class AlphaFoldMultimerQueryJsonGeneration(ImportingStep):
    display_name = "AlphaFold Multimer Query JSON Generation"
    operation = "Query Generation"
    method_description = "Generate a JSON to upload to AlphaFold-Server to generate a prediction on a multimer."

    output_keys = ["downloads"]

    def create_form(self):
        return Form(
            label="AlphaFold Multimer Query JSON Generation",
            input_fields=[
                TextField(
                    name="protein_ids",
                    label="Protein UniProt IDs",
                ),
                InfoField(label="IDs should be separated by a space."),
                TextField(
                    name="number_copies",
                    label="Number of copies for each protein ID",
                ),
                InfoField(
                    label="For each entered ID a number should be entered.\n"
                    "Numbers should be separated by a space."
                ),
            ],
        )
    calc_method = staticmethod(lambda: dict(downloads=pd.DataFrame()))
    download_method = staticmethod(generate_alphafold_multimer_query_json)
