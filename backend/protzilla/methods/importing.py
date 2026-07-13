from __future__ import annotations
from abc import ABC
import textwrap
import numpy as np
import pandas as pd
from typing_extensions import override

from backend.protzilla.constants.data_types import DataKey
from backend.protzilla.constants.option_types import Separators
from backend.protzilla.form import (
    CheckboxField,
    DropdownField,
    FileInput,
    Form,
    FormDivider,
    HeaderInfoField,
    MultiSelectField,
    Option,
    TextField,
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
from backend.protzilla.importing.peptide_import import peptide_import, evidence_import
from backend.protzilla.run import Run
from backend.protzilla.steps import Step, Section, StepOperation
from backend.protzilla.importing.example_dataset_import import example_dataset_import
from backend.protzilla.importing.fasta_import import fasta_import
from backend.protzilla.importing.import_utils import (
    AggregationMethods,
    FeatureOrientationType,
)
from backend.protzilla.constants.intensity_types import IntensityType, IntensityNameType
from backend.protzilla.utilities.utilities import default_intensity_column


def custom_python_step(code: str, selected_outputs: list[str], **inputs):
    if not code.strip():
        raise ValueError("Please provide Python code.")
    if not selected_outputs:
        raise ValueError("Please select at least one output.")

    namespace = {
        "np": np,
        "pd": pd,
        "default_intensity_column": default_intensity_column,
        **inputs,
    }
    exec(
        "def _custom_step():\n" + textwrap.indent(code, "    "),
        namespace,
    )
    result = namespace["_custom_step"]()
    if not isinstance(result, dict):
        raise ValueError("Custom step code must return a dictionary.")

    missing_outputs = [
        output_key for output_key in selected_outputs if output_key not in result
    ]
    if missing_outputs:
        raise ValueError(
            f"Custom step did not return the selected outputs: {', '.join(missing_outputs)}."
        )

    return result


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


class ArbitraryCSVImport(ImportingStep):
    display_name: str = "Arbitrary CSV"
    operation: StepOperation = StepOperation.DEBUG
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
    operation: StepOperation = StepOperation.METADATA_IMPORT


class ProteinImportingStep(ImportingStep, ABC):
    operation: StepOperation = StepOperation.PROTEIN_IMPORT


class MaxQuantImport(ProteinImportingStep):
    display_name = "MaxQuant Protein Groups"
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


class DiannImport(ProteinImportingStep):
    display_name = "DIA-NN Proteins"
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


class MsFraggerImport(ProteinImportingStep):
    display_name = "MSFragger Combined Proteins"
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
    display_name = "Metadata"
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
                DropdownField(
                    name="separator",
                    label="Separator",
                    options=Separators,
                    value=Separators.comma.value,
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
    display_name = "MaxQuant Peptides"
    operation = StepOperation.PEPTIDE_IMPORT
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
    display_name = "MaxQuant Evidence"
    operation = StepOperation.PSM_IMPORT
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
    display_name = "FASTA Protein Sequences"
    operation = StepOperation.FASTA_IMPORT
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
    display_name = "Example Dataset"
    operation = StepOperation.EXAMPLE_IMPORT
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


class CustomPythonStep(ImportingStep):
    display_name = "Custom Python Step"
    operation = StepOperation.NOT_CATEGORIZED
    method_description = "Run custom Python code inside PROTzilla."

    def create_form(self):
        data_key_options = [Option(data_key.value, data_key.value) for data_key in DataKey]
        return Form(
            label="Custom Python Step",
            input_fields=[
                HeaderInfoField(label=self.method_description),
                MultiSelectField(
                    name="selected_inputs",
                    label="Inputs",
                    options=data_key_options,
                    value=[],
                ),
                MultiSelectField(
                    name="selected_outputs",
                    label="Outputs",
                    options=data_key_options,
                    value=[],
                ),
                TextField(
                    name="code",
                    label="Python code",
                    rows=12,
                    isCodeEditor=True,
                    value="return dict()",
                ),
            ],
        )

    @property
    def external_input_keys(self) -> list[DataKey]:
        return [DataKey(key) for key in self.form["selected_inputs"].value]

    @property
    def output_keys(self) -> list[DataKey]:
        return [DataKey(key) for key in self.form["selected_outputs"].value]

    @property
    def calculation_input(self) -> dict:
        return {
            "code": self.form["code"].value,
            "selected_outputs": self.form["selected_outputs"].value,
            **{key: self.inputs.get(key) for key in self.form["selected_inputs"].value},
        }

    calc_method = staticmethod(custom_python_step)
