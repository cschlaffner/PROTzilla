import py7zr
from pridepy import pridepy

from protzilla.constants.intensity_types import IntensityType
from protzilla.constants.paths import (
    EXAMPLE_DATASET_PROTEIN_FILE,
    EXAMPLE_DATASET_METADATA_FILE,
    EXAMPLE_DATASET_EVIDENCE_FILE,
    EXAMPLE_DATASET_DIR,
)
from protzilla.constants.protzilla_logging import logger
from protzilla.importing.import_utils import FeatureOrientationType
from protzilla.importing.metadata_import import metadata_import_method
from protzilla.importing.ms_data_import import max_quant_import
from protzilla.importing.peptide_import import evidence_import


def example_dataset_import():
    ACCESSION = "PXD014997"
    FILENAME = "SEARCH-IDENTIFICATION_REL-FREEvsRELAPSE_Label-free.7z"
    archive_file_path = EXAMPLE_DATASET_DIR / FILENAME
    if (
        not EXAMPLE_DATASET_PROTEIN_FILE.exists()
        or not EXAMPLE_DATASET_EVIDENCE_FILE.exists()
    ):
        if not archive_file_path.exists():
            logger.info(
                f"Downloading file %s from PRIDE project %s", FILENAME, ACCESSION
            )
            try:
                raw_files = pridepy.Files()
                raw_files.download_file_by_name(
                    accession=ACCESSION,
                    file_name=FILENAME,
                    output_folder=str(EXAMPLE_DATASET_DIR),
                    skip_if_downloaded_already=True,
                    protocol="ftp",
                    username=None,
                    password=None,
                    aspera_maximum_bandwidth=None,
                    checksum_check=False,
                )
            except Exception as e:
                raise RuntimeError(
                    f"Error downloading file {FILENAME} from PRIDE project {ACCESSION}. "
                    f"This is likely and issue with PRIDE.\nOriginal error: {e}\n"
                )
            logger.info(f"Completed download of file %s", FILENAME)

        required_file_names = [
            f.name
            for f in (EXAMPLE_DATASET_EVIDENCE_FILE, EXAMPLE_DATASET_PROTEIN_FILE)
            if not f.exists()
        ]

        with py7zr.SevenZipFile(EXAMPLE_DATASET_DIR / FILENAME, mode="r") as archive:
            all_files = archive.getnames()
            selected_files = []
            for req_filename in required_file_names:
                for f in all_files:
                    if req_filename in f:
                        selected_files.append(f)
            logger.info("Extracting files %s from archive", selected_files)
            archive.extract(targets=selected_files, path=EXAMPLE_DATASET_DIR)

        archive_file_path.unlink()

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
