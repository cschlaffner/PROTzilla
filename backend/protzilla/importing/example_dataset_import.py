from protzilla.constants.paths import (
    EXAMPLE_DATASET_PROTEIN_FILE,
    EXAMPLE_DATASET_METADATA_FILE,
    EXAMPLE_DATASET_EVIDENCE_FILE,
)
from protzilla.importing.import_utils import FeatureOrientationType
from protzilla.constants.intensitiy_types import IntensityType
from protzilla.importing.metadata_import import metadata_import_method
from protzilla.importing.ms_data_import import max_quant_import
from protzilla.importing.peptide_import import evidence_import


def example_dataset_import():
    intensity_name = IntensityType.LFQ_INTENSITY.value
    protein_import_dict = max_quant_import(
        file_path=EXAMPLE_DATASET_PROTEIN_FILE,
        intensity_name=intensity_name,
        aggregation_method="Sum",
    )
    # Return messages
    if "protein_df" not in protein_import_dict:
        return protein_import_dict

    metadata_import_dict = metadata_import_method(
        protein_df=protein_import_dict["protein_df"],
        file_path=EXAMPLE_DATASET_METADATA_FILE,
        feature_orientation=FeatureOrientationType.COLUMNS.value,
    )

    peptide_import_dict = evidence_import(
        file_path=EXAMPLE_DATASET_EVIDENCE_FILE, map_to_uniprot=False
    )

    combined_messages = (
        protein_import_dict.pop("messages", [])
        + metadata_import_dict.pop("messages", [])
        + peptide_import_dict.pop("messages", [])
    )
    combined_dict = {
        **protein_import_dict,
        **metadata_import_dict,
        **peptide_import_dict,
        "messages": combined_messages,
    }

    return combined_dict
