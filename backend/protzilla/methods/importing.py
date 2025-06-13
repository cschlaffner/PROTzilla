from __future__ import annotations

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
from backend.protzilla.steps import Step, StepManager


class IntensityType(Enum):
    IBAQ = "iBAQ"
    INTENSITY = "Intensity"
    LFQ_INTENSITY = "LFQ intensity"


class IntensityNameType(Enum):
    INTENSITY = "Intensity"
    MAXLFQ_TOTAL_iNTENSITY = "MaxLFQ Total Intensity"
    MAXLFQ_INTENSITY = "MaxLFQ Intensity"
    TOTAL_INTENSITY = "Total Intensity"
    MAXLFQ_UNIQUE_INTENSITY = "MaxLFQ Unique Intensity"
    UNIQUE_SPECTRAL_COUNT = "Unique Spectral Count"
    UNIQUE_INTENSITY = "Unique Intensity"
    SPECTRAL_COUNT = "Spectral Count"
    TOTAL_SPECTRAL_COUNT = "Total Spectral Count"


class FeatureOrientationType(Enum):
    COLUMNS = "Columns (samples in rows, features in columns)"
    ROWS = "Rows (features in rows, samples in columns)"


class EmptyEnum(Enum):
    pass


class AggregationMethods(Enum):
    sum = "Sum"
    median = "Median"
    mean = "Mean"


class ImportingStep(Step):
    section = "importing"

    def calc_method(self):
        raise NotImplementedError("This method must be implemented in a subclass.")

    def insert_dataframes(self, steps: StepManager, inputs) -> dict:
        return inputs


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
                    name = "file_path",
                    label = "MaxQuant intensities file (proteinGroups.txt)",
                    value = None,
                ),
                DropdownField(
                    name = "intensity_name",
                    label = "Intensity parameter",
                    value = IntensityType.IBAQ.value,
                    options = IntensityType
                ),
                CheckboxField(
                    name = "map_to_uniprot",
                    label = "Map to Uniprot IDs using Biomart (online)",
                    value = False
                ),
                DropdownField(
                    name = "aggregation_method",
                    label = "Aggregation method used to aggregate duplicate values for protein groups",
                    value = AggregationMethods.sum.value,
                    options = AggregationMethods,
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
                    name = "map_to_uniprot",
                    label = "Map to Uniprot IDs using Biomart (online)",
                    value = False
                ),
                DropdownField(
                    name = "aggregation_method",
                    label = "Aggregation method used to aggregate duplicate values for protein groups",
                    value = AggregationMethods.sum.value,
                    options = AggregationMethods,
                ),
            ]
        )

    calc_method = staticmethod(diann_import)


class MsFraggerImport(ImportingStep):
    display_name = "MS Fragger Combined Protein Import"
    operation = "Protein Data Import"
    method_description = "Import the combined_protein.tsv file form output of MS Fragger"

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
                    name = "map_to_uniprot",
                    label = "Map to Uniprot IDs using Biomart (online)",
                    value = False
                ),
                DropdownField(
                    name = "aggregation_method",
                    label = "Aggregation method used to aggregate duplicate values for protein groups",
                    value = AggregationMethods.sum.value,
                    options = AggregationMethods,
                ),
            ]
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
                    name = "file_path",
                    label = "Metadata file",
                ),
                DropdownField(
                    name = "feature_orientation",
                    label = "Feature orientation",
                    options = FeatureOrientationType,
                    value = FeatureOrientationType.COLUMNS.value,
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
            ]
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
                )
            ],
        )

    def modify_form(self, form, run):
        metadata_required_column = form["metadata_required_column"]
        metadata_unknown_column = form["metadata_unknown_column"]

        metadata = run.steps.get_step_output(
            ImportingStep, "metadata_df", include_current_step=True
        )

        if metadata is not None:
            metadata_required_column.set_options([
                Option(col, col)
                for col in ["Sample", "Group", "Batch"]
                if col not in metadata.columns
            ])
            if len(metadata_required_column.options) == 0:
                metadata_required_column.set_options([])
            
            unknown_columns = list(
                metadata.columns[
                    ~metadata.columns.isin(["Sample", "Group", "Batch"])
                ].unique()
            )

            metadata_unknown_column.set_options([
                Option(col, col) for col in unknown_columns
            ])
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
                    name = "file_path",
                    label = "Peptide file",
                ),
                DropdownField(
                    name = "intensity_name",
                    label = "Intensity parameter",
                    options = IntensityType,
                    value = IntensityType.INTENSITY.value,
                ),
                CheckboxField(
                    name = "map_to_uniprot",
                    label = "Map to Uniprot IDs using Biomart (online)",
                    value = False
                ),
            ]
        )
    
    def modify_form(self, form, run):
        intensity_name_field = form["intensity_name"]
        map_to_uniprot_field = form["map_to_uniprot"]

        intensity_name_field.value = run.steps.get_step_input(
            [MaxQuantImport, MsFraggerImport, DiannImport],
            "intensity_name",
            default = intensity_name_field.value
        )

        map_to_uniprot_field.value = run.steps.get_step_input(
            [MaxQuantImport, MsFraggerImport, DiannImport],
            "map_to_uniprot",
            default = map_to_uniprot_field.value
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
                    name = "map_to_uniprot",
                    label = "Map to Uniprot IDs using Biomart (online)",
                    value = False
                ),
            ]
        )
    
    def modify_form(self, form, run):
        map_to_uniprot_field = form["map_to_uniprot"]

        map_to_uniprot_field.value = run.steps.get_step_input(
            [MaxQuantImport, MsFraggerImport, DiannImport], "map_to_uniprot"
        )

    calc_method = staticmethod(evidence_import)