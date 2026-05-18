from __future__ import annotations
from abc import ABC
from typing_extensions import override

import pandas as pd

from backend.protzilla.form import *
from backend.protzilla import form_helper
from backend.protzilla.constants.data_types import DataKey
from backend.protzilla.form import (
    CheckboxField,
    DropdownField,
    FileInput,
    Form,
    FormDivider,
    HeaderInfoField,
    Option,
)
from backend.protzilla.importing.debug_import import arbitrary_csv_import
from backend.protzilla.importing.metadata_import import (
    metadata_column_assignment,
    metadata_import_method,
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
from backend.protzilla.steps import Step, Section
from backend.protzilla.importing.crosslinking_import import crosslinking_import
from backend.protzilla.run import Run
from backend.protzilla.importing.example_dataset_import import example_dataset_import
from backend.protzilla.importing.fasta_import import fasta_import
from backend.protzilla.importing.import_utils import (
    AggregationMethods,
    FeatureOrientationType,
)
from backend.protzilla.constants.intensity_types import IntensityType, IntensityNameType
from backend.protzilla.importing.query_generation import generate_alphafold_query_json


class ImportingStep(Step, ABC):
    section = Section.IMPORTING

    def modify_form(self, run: Run):
        if run.steps.current_step.calculation_status == "complete":
            for field in self.form.input_fields:
                if isinstance(field, FileInput):
                    field.value = None


class ArbitraryCSVImport(ImportingStep):
    display_name: str = "Arbitrary CSV import"
    operation: str = "(DEBUG)"
    method_description: str = "For debugging purposes. Imports any CSV as a dataframe"

    output_keys: list[DataKey] = [DataKey.DEBUG]

    def create_form(self) -> Form:
        return Form(
            label="Arbitrary CSV Import",
            input_fields=[
                FileInput(
                    name="file_path",
                    label="CSV file",
                    value=None,
                    accept=".csv",
                )
            ],
        )

    calc_method = staticmethod(arbitrary_csv_import)


class MetadataImportingStep(ImportingStep, ABC):

    operation = "metadataimport"


class MaxQuantImport(ImportingStep):
    display_name = "MaxQuant Protein Groups Import"
    operation = "Protein Data Import"
    method_description = "Import the protein groups file form output of MaxQuant"

    output_keys = [DataKey.PROTEIN_DF]

    def create_form(self):
        return Form(
            label="MaxQuant Protein Groups Import",
            input_fields=[
                FileInput(
                    name="file_path",
                    label="MaxQuant intensities file (proteinGroups.txt)",
                    value=None,
                    accept=".txt",
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

    output_keys = [DataKey.PROTEIN_DF]

    def create_form(self):
        return Form(
            label="DIA-NN Import",
            input_fields=[
                FileInput(
                    name="file_path",
                    label="DIA-NN intensities file (*.pg_matrix.tsv)",
                    value=None,
                    accept="txt,.tsv",
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

    output_keys = [DataKey.PROTEIN_DF]

    def create_form(self):
        return Form(
            label="MS Fragger Combined Protein Import",
            input_fields=[
                FileInput(
                    name="file_path",
                    label="MSFragger intensities file (combined_proteins.tsv)",
                    accept=".txt,.tsv",
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


class MetadataImport(MetadataImportingStep):
    display_name = "Metadata Import"
    method_description = "Import metadata"

    output_keys = [DataKey.METADATA_DF]

    def create_form(self):
        return Form(
            label="Metadata Import",
            input_fields=[
                FileInput(
                    name="file_path",
                    label="Metadata file",
                    accept=".csv,.xlsx,.psv,.tsv",
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


class MetadataColumnAssignment(MetadataImportingStep):
    display_name = "Metadata column assignment"
    method_description = (
        "Assign columns to metadata categories, repeatable for each category"
    )

    output_keys = [DataKey.METADATA_DF]

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

    def modify_form(self, run: Run):
        metadata_required_column: DropdownField = self.form["metadata_required_column"]
        metadata_unknown_column: DropdownField = self.form["metadata_unknown_column"]

        metadata_source, metadata_handle = self.input_source(
            run.steps, DataKey.METADATA_DF
        )

        if metadata_source is None or metadata_handle is None:
            return

        metadata = run.steps.get_step_output(
            output_key=metadata_handle, instance_identifier=metadata_source
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


class PeptideImport(ImportingStep):
    display_name = "MaxQuant Peptide Import"
    operation = "peptide_import"
    method_description = "Import peptide data"

    output_keys = [DataKey.PEPTIDE_DF]

    def create_form(self):
        return Form(
            label="MaxQuant Peptide Import",
            input_fields=[
                FileInput(
                    name="file_path",
                    label="Peptide file",
                    accept=".txt",
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

    calc_method = staticmethod(peptide_import)


class EvidenceImport(ImportingStep):
    display_name = "MaxQuant Evidence Import"
    operation = "peptide_import"
    method_description = "Import an evidence file"

    output_keys = [DataKey.PSM_DF]

    def create_form(self):
        return Form(
            label="MaxQuant Evidence Import",
            input_fields=[
                FileInput(
                    name="file_path",
                    label="Evidence file",
                    accept=".txt",
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

    calc_method = staticmethod(evidence_import)


class FastaImport(ImportingStep):
    display_name = "Fasta Protein Sequence Import"
    operation = "fasta_import"
    method_description = "Import a fasta file containing protein sequences."

    output_keys = [DataKey.FASTA_DF]

    calc_method = staticmethod(fasta_import)

    def create_form(self):
        return Form(
            label="Fasta Protein Sequence Import",
            input_fields=[
                FileInput(
                    name="file_path",
                    label="Fasta file",
                    accept=".fasta,.fa,.faa",
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
        "https://doi.org/10.3390/cancers12030709\n\n"
        "If you run this step for the first time, the data will be downloaded from PRIDE, which may take a few minutes."
    )

    output_keys = [DataKey.METADATA_DF, DataKey.PROTEIN_DF]

    def create_form(self):
        return Form(
            label="Example Dataset Import",
            input_fields=[
                HeaderInfoField(label=self.method_description),
                FormDivider("Settings"),
                CheckboxField(
                    name="import_peptide_data",
                    label="Import data from MaxQuant evidence.txt (may take longer and require more memory)",
                    value=False,
                ),
            ],
        )

    calc_method = staticmethod(example_dataset_import)

    @override
    def modify_form(self, run: Run) -> None:
        import_peptide_data_field = self.form["import_peptide_data"]
        self.output_keys = self.output_keys = (
            [
                DataKey.METADATA_DF,
                DataKey.PSM_DF,
                DataKey.PROTEIN_DF,
            ]
            if import_peptide_data_field.value
            else [DataKey.METADATA_DF, DataKey.PROTEIN_DF]
        )


class AlphaFoldPredictionLoad(ImportingStep):
    display_name = "AlphaFold DB Monomer Prediction Load"
    operation = "Monomer Structure Import"
    method_description = "Loads the predicted structure of the monomer with the given protein ID out of the AlphaFold DB."

    output_keys = [
        DataKey.STRUCTURE_METADATA_DF,
        DataKey.CIF_DF,
        DataKey.PLDDT_DF,
        DataKey.AMINO_ACID_SEQUENCES_DF,
        DataKey.PAE_MATRIX,
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

    output_keys = [DataKey.CROSSLINKING_DF]

    def create_form(self):
        return Form(
            label="Crosslinking Data Import",
            input_fields=[
                FileInput(
                    name="file_path",
                    label="Crosslinking Data file (.xlsx or .csv)",
                    value=None,
                    accept=".xlsx,.csv",
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
        DataKey.STRUCTURE_METADATA_DF,
        DataKey.CIF_DF,
        DataKey.PAE_MATRIX,
        DataKey.PLDDT_DF,
        DataKey.AMINO_ACID_SEQUENCES_DF,
    ]

    def create_form(self):
        return Form(
            label="Monomer Structure Predictions Import from Disk",
            input_fields=[
                DropdownField(
                    name="entry_id",
                    label="Entry ID of the monomer prediction to be loaded into the run. (Unless specified otherwise this is the Protein ID)",
                )
            ],
        )

    def modify_form(self, run: Run):
        entry_id_field = self.form["entry_id"]
        entry_id_field.set_options(
            form_helper.to_choices(get_all_available_entry_ids_of_monomer_metadata())
        )

    calc_method = staticmethod(get_monomer_structure_dfs)


class UploadMultimerPredictions(ImportingStep):
    display_name = "Multimer Structure Prediction Upload"
    operation = "Multimer Structure Import"
    method_description = "Upload a multimer protein prediction"

    output_keys = [
        DataKey.STRUCTURE_METADATA_DF,
        DataKey.CIF_DF,
        DataKey.CONFIDENCE_DF,
        DataKey.FULL_DATA_DF,
        DataKey.JOB_REQUEST_DF,
        DataKey.AMINO_ACID_SEQUENCES_DF,
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
                    label="Protein IDs of all proteins used in the sequence. ",
                ),
                InfoField(
                    label="Please provide a list of Protein IDs separated by a comma \n e.g.: P68871, P69905, Q5VSL9."
                ),
                TextField(
                    name="model_used",
                    label="The AlphaFold Model used to predict the structure.",
                ),
                FileInput(
                    name="amino_acid_sequences",
                    label="Amino acid sequences of proteins in the prediction (required)",
                    value=None,
                    accept=".fasta,.fa,.faa",
                ),
                FileInput(
                    name="cif_file",
                    label="CIF file (required)",
                    value=None,
                    accept=".cif,.mmcif",
                ),
                FileInput(
                    name="confidence_file",
                    label="Confidence summary json file (required)",
                    value=None,
                    accept=".json",
                ),
                FileInput(
                    name="full_data_file",
                    label="Full data json file (required)",
                    value=None,
                    accept=".json",
                ),
                FileInput(
                    name="job_request_file",
                    label="Job request json file (required)",
                    value=None,
                    accept=".json",
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
        DataKey.STRUCTURE_METADATA_DF,
        DataKey.CIF_DF,
        DataKey.CONFIDENCE_DF,
        DataKey.FULL_DATA_DF,
        DataKey.JOB_REQUEST_DF,
        DataKey.AMINO_ACID_SEQUENCES_DF,
    ]

    def create_form(self):
        return Form(
            label="Multimer Structure Predictions Import from Disk",
            input_fields=[
                DropdownField(
                    name="entry_id",
                    label="Entry ID of the multimer prediction to be loaded into the run.",
                )
            ],
        )

    def modify_form(self, run: Run):
        entry_id_field = self.form["entry_id"]
        entry_id_field.set_options(
            form_helper.to_choices(get_all_available_entry_ids_of_multimer_metadata())
        )

    calc_method = staticmethod(get_multimer_structure_dfs)


class AlphaFoldQueryJsonGeneration(Step):
    section = "importing"
    display_name = "AlphaFold Query JSON Generation"
    operation = "Query Generation"
    method_description = (
        "Generate a JSON to upload to AlphaFold-Server to generate a prediction."
    )

    def create_form(self):
        return Form(
            label="AlphaFold Query JSON Generation",
            input_fields=[
                TextField(
                    name="name",
                    label="File name and AlphaFold job name for generated query",
                ),
                InfoField(
                    label="Only enter file stem, '.json' will be added automatically."
                ),
                TextField(
                    name="protein_ids",
                    label="UniProt Protein IDs",
                ),
                InfoField(label="IDs should be space- or comma-separated."),
                TextField(
                    name="number_copies",
                    label="Number of copies of each protein monomer",
                ),
                InfoField(
                    label="For each entered ID a number should be entered.\n"
                    "Numbers should be should be space- or comma-separated."
                ),
                NumberField(
                    name="model_seed",
                    label="Model seed for AlphaFold",
                    min=-1,
                    max=4294967295,
                    value=-1,
                ),
                InfoField(
                    label="Leave -1 if you want to use a random seed.\n"
                    "Otherwise enter a seed (integer between 0 and 4294967295)"
                ),
            ],
        )

    calc_method = staticmethod(generate_alphafold_query_json)
