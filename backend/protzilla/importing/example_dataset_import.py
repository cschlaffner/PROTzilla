import py7zr
from pridepy import pridepy

from backend.protzilla.constants.data_types import DataKey
from backend.protzilla.constants.intensity_types import IntensityType
from backend.protzilla.constants.paths import (
    EXAMPLE_DATASET_PROTEIN_FILE,
    EXAMPLE_DATASET_METADATA_FILE,
    EXAMPLE_DATASET_EVIDENCE_FILE,
    EXAMPLE_DATASET_DIR,
)
from backend.protzilla.constants.protzilla_logging import logger
from backend.protzilla.importing.import_utils import FeatureOrientationType
from backend.protzilla.importing.metadata_import import metadata_import_method
from backend.protzilla.importing.ms_data_import import max_quant_import
from backend.protzilla.importing.peptide_import import evidence_import


def download_example_data(
    import_peptide_data: bool,
    accession: str = "PXD014997",
    filename: str = "SEARCH-IDENTIFICATIONS_REL_FREE-RELAPSE.7z",
) -> None:
    archive_file_path = EXAMPLE_DATASET_DIR / filename
    if not archive_file_path.exists():
        logger.info("Downloading file %s from PRIDE project %s", filename, accession)
        try:
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
        except Exception as e:
            raise RuntimeError(
                f"Error downloading file {filename} from PRIDE project {accession}. "
                f"This is likely an issue with PRIDE.\nOriginal error: {e}\n"
            )
        logger.info("Completed download of file %s", filename)

    required_file_names = []
    if not EXAMPLE_DATASET_PROTEIN_FILE.exists():
        required_file_names.append(EXAMPLE_DATASET_PROTEIN_FILE.name)
    if import_peptide_data and not EXAMPLE_DATASET_EVIDENCE_FILE.exists():
        required_file_names.append(EXAMPLE_DATASET_EVIDENCE_FILE.name)

    with py7zr.SevenZipFile(EXAMPLE_DATASET_DIR / filename, mode="r") as archive:
        all_files = archive.getnames()
        selected_files = []
        for req_filename in required_file_names:
            for f in all_files:
                if req_filename in f:
                    selected_files.append(f)
        logger.info("Extracting files %s from archive", selected_files)
        archive.extract(targets=selected_files, path=EXAMPLE_DATASET_DIR)

    assert EXAMPLE_DATASET_PROTEIN_FILE.exists() and (
        not import_peptide_data or EXAMPLE_DATASET_EVIDENCE_FILE.exists()
    ), "Required files were not properly extracted from the archive."
    archive_file_path.unlink()


def example_dataset_import(import_peptide_data: bool = False) -> dict:
    if not EXAMPLE_DATASET_PROTEIN_FILE.exists() or (
        import_peptide_data and not EXAMPLE_DATASET_EVIDENCE_FILE.exists()
    ):
        download_example_data(import_peptide_data)

    intensity_name = IntensityType.RATIO_HL.value
    protein_import_dict = max_quant_import(
        file_path=EXAMPLE_DATASET_PROTEIN_FILE,
        intensity_name=intensity_name,
        aggregation_method="Sum",
        ignore_only_identified_by_site=True,
    )
    # Return messages
    if DataKey.PROTEIN_DF not in protein_import_dict:
        return protein_import_dict

    metadata_import_dict = metadata_import_method(
        protein_df=protein_import_dict[DataKey.PROTEIN_DF],
        file_path=EXAMPLE_DATASET_METADATA_FILE,
        feature_orientation=FeatureOrientationType.COLUMNS.value,
    )
    if "metadata_df" not in metadata_import_dict:
        return metadata_import_dict
    if DataKey.METADATA_DF not in metadata_import_dict:
        return metadata_import_dict

    if import_peptide_data:
        peptide_import_dict = evidence_import(
            file_path=EXAMPLE_DATASET_EVIDENCE_FILE,
            intensity_name=intensity_name,
            map_to_uniprot=False,
        )
        if DataKey.PEPTIDE_DF not in peptide_import_dict:
            return peptide_import_dict
    else:
        peptide_import_dict = {}

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
