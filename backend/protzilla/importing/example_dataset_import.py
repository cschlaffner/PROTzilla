import logging
from pathlib import Path

from pridepy import pridepy

from protzilla.constants.intensity_types import IntensityType
from protzilla.constants.paths import (
    EXAMPLE_DATASET_PROTEIN_FILE,
    EXAMPLE_DATASET_METADATA_FILE,
    EXAMPLE_DATASET_EVIDENCE_FILE,
    EXAMPLE_DATASET_DIR,
)
from protzilla.importing.import_utils import FeatureOrientationType
from protzilla.importing.metadata_import import metadata_import_method
from protzilla.importing.ms_data_import import max_quant_import
from protzilla.importing.peptide_import import evidence_import


# TODO: maybe update dependencies if we need pridepy


def example_dataset_import():
    # TODO: remove - only testing
    # accession = "PXD020517"
    # filename = "AD02_BA39-Cohort1_INSOLUBLE_03.wiff"
    accession = "PXD014997"
    filename = "SEARCH-IDENTIFICATION_REL-FREEvsRELAPSE_Label-free.7z"
    if (
        not EXAMPLE_DATASET_PROTEIN_FILE.exists()
        or not EXAMPLE_DATASET_METADATA_FILE.exists()
        or not EXAMPLE_DATASET_EVIDENCE_FILE.exists()
        or not Path(EXAMPLE_DATASET_DIR, filename).exists()
    ):

        # TODO: remove
        # use normal logger for now
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        logger.info(f"Downloading file {filename} from PRIDE project {accession}")

        raw_files = pridepy.Files()
        raw_files.download_file_by_name(
            accession=accession,
            file_name=filename,
            output_folder=str(EXAMPLE_DATASET_DIR),
            skip_if_downloaded_already=True,
            protocol="ftp",
            username=None,
            password=None,
            aspera_maximum_bandwidth=None,
            checksum_check=False,
        )
        print("Download completed")  # TODO: remove
        return

    # import py7zr  # TODO: install
    #
    # with py7zr.SevenZipFile('sample.7z', mode='r') as z:
    #     z.extractall()

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


# TODO: remove
def main():
    result = example_dataset_import()


if __name__ == "__main__":
    main()
