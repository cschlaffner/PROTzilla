from __future__ import annotations
from abc import ABC
from typing_extensions import override

from backend.protzilla.constants.data_types import DataKey
from backend.protzilla.form import *
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
from backend.protzilla.importing.peptide_import import peptide_import, evidence_import
from backend.protzilla.steps import Step, Section
from backend.protzilla.importing.example_dataset_import import example_dataset_import
from backend.protzilla.importing.fasta_import import fasta_import
from backend.protzilla.importing.import_utils import (
    AggregationMethods,
    FeatureOrientationType,
)
from backend.protzilla.constants.intensity_types import IntensityType, IntensityNameType


class ImportingStep(Step, ABC):
    section = Section.IMPORTING

    def modify_form(self, run: Run):
        if run.steps.current_step.calculation_status == "complete":
            self.form.input_fields[self.index_of_file_input()].value = None

    def index_of_file_input(self):
        """
        Returns the index of the FileInput that should be reset by modify_form. This method
        must be overridden if the FileInput is not index 0.
        """
        return 0


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


class MetadataImportMethodDiann(MetadataImportingStep):
    display_name = "DIA-NN Metadata Import"
    method_description = "Import metadata for run relationships of DIA-NN"

    output_keys = [DataKey.METADATA_DF, DataKey.PROTEIN_DF]

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


class MetadataColumnAssignment(MetadataImportingStep):
    display_name = "Metadata column assignment"
    method_description = (
        "Assign columns to metadata categories, repeatable for each category"
    )

    output_keys = [DataKey.METADATA_DF, DataKey.PROTEIN_DF]

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

    def modify_form(self, run: Run):
        super().modify_form(run)

        map_to_uniprot_field: CheckboxField = self.form["map_to_uniprot"]
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

    output_keys = [DataKey.PEPTIDE_DF]

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

    def modify_form(self, run: Run):
        super().modify_form(run)

        map_to_uniprot_field: CheckboxField = self.form["map_to_uniprot"]

        map_to_uniprot_field.value = run.steps.get_step_input(
            [MaxQuantImport, MsFraggerImport, DiannImport], "map_to_uniprot"
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

    output_keys = [DataKey.METADATA_DF, DataKey.PEPTIDE_DF, DataKey.PROTEIN_DF]

    def create_form(self):
        return Form(
            label="Example Dataset Import",
            input_fields=[HeaderInfoField(label=self.method_description)],
        )

    calc_method = staticmethod(example_dataset_import)
