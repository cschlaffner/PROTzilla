from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from textwrap import wrap
from typing import Any
import logging
import json

from datetime import datetime, timezone
import gemmi
import pandas as pd
import requests

from backend.protzilla.constants import paths
from backend.protzilla.constants.protzilla_logging import logger
from backend.protzilla.importing.fasta_import import fasta_import
from backend.protzilla.networking import download_file_from_url
from backend.protzilla.utilities.utilities import copy_file_to_directory


def get_monomer_metadata_df() -> pd.DataFrame:
    """
    Returns all data from alphafold_monomer_metadata.csv in form of a dataframe. If no such csv exist, it returns
    a dataframe with the corresponding keys but no values and creates a csv with the expected column names.
    """
    metadata_csv = paths.AF_MONOMER_METADATA_CSV_PATH
    if not metadata_csv.exists():
        metadata_df = pd.DataFrame(
            columns=[
                "entry_id",
                "uniprot_accession",
                "model_created_date",
                "gene",
                "model_used",
            ]
        )
        metadata_csv.parent.mkdir(parents=True, exist_ok=True)
        metadata_df.to_csv(metadata_csv, index=False)
        return metadata_df
    return pd.read_csv(metadata_csv, dtype=str)


def get_multimer_metadata_df() -> pd.DataFrame:
    """
    Returns all data from alphafold_multimer_metadata.csv in form of a dataframe. If no such csv exist, it returns
    a dataframe with the corresponding keys but no values and creates a csv with the expected column names.
    """
    metadata_csv = paths.AF_MULTIMER_METADATA_CSV_PATH

    if not metadata_csv.exists():
        metadata_df = pd.DataFrame(
            columns=[
                "entry_id",
                "uniprot_ids",
                "model_created_date",
                "model_used",
            ]
        )
        metadata_csv.parent.mkdir(parents=True, exist_ok=True)
        metadata_df.to_csv(metadata_csv, index=False)
        return metadata_df
    return pd.read_csv(metadata_csv, dtype=str)


def to_fasta(seq: str, header: str = "protein_sequence", width: int = 60) -> str:
    """
    Convert a protein sequence to FASTA format.

    :param seq: The protein sequence to convert
    :param header: The header line for the FASTA record (default: "protein_sequence")
    :param width: The maximum line width for sequence wrapping (default: 60)
    :return: The sequence in FASTA format
    :raises ValueError: If the sequence contains invalid characters or whitespace
    """
    VALID_AMINO_ACIDS = set("ACDEFGHIKLMNPQRSTVWYBXZJUO*-")
    if not seq or any(c.isspace() for c in seq):
        raise ValueError("Sequence must be a single, whitespace-free string.")
    seq = seq.upper()
    bad = set(seq) - VALID_AMINO_ACIDS
    if bad:
        raise ValueError(f"Invalid characters in sequence: {''.join(sorted(bad))}")
    joined = "\n".join(wrap(seq, width))
    return f">alpha|{header}\n{joined}\n"


def read_alphafold_mmcif(path: str) -> pd.DataFrame:
    """
    Parse an AlphaFold mmCIF (Macromolecular Crystallographic Information File) file.

    :param path: The path to the mmCIF file
    :return: A DataFrame containing the atom site information from the CIF file
    :raises FileNotFoundError: If the file does not exist
    :raises IsADirectoryError: If the path points to a directory instead of a file
    :raises ValueError: If no CIF blocks are found in the file
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")
    if p.is_dir():
        raise IsADirectoryError(f"Expected a file path, got a directory: {p}")

    doc = gemmi.cif.read_file(str(p))
    if len(doc) == 0:
        raise ValueError(f"No CIF blocks found in file: {p}")

    block = doc.sole_block()

    cat_name = "_atom_site."
    if cat_name not in block.get_mmcif_category_names():
        return pd.DataFrame()

    table = block.find_mmcif_category(cat_name)

    columns = list(table.tags)
    nrows = len(table)
    data = {}
    for j, col in enumerate(columns):
        col_values = []
        for i in range(nrows):
            row = table[i]
            if j < len(row):
                col_values.append(row[j])
            else:
                col_values.append(None)
        data[col] = col_values

    return pd.DataFrame(data)


def get_correct_af_directories(
    entry_id: str, directory_name: Path, persist_upload: bool
) -> list[Path, Path]:
    target_dir = directory_name / entry_id.upper()
    temp_dir = None

    if persist_upload:
        target_dir.mkdir(parents=True, exist_ok=True)
        work_dir = target_dir
    else:
        temp_dir = Path(tempfile.mkdtemp())
        work_dir = temp_dir

    return temp_dir, work_dir


def extend_metadata_csv(
    entry_id: str,
    metadata_csv: Path,
    exsisting_metadata_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    messages: list,
) -> None:
    try:
        mask = exsisting_metadata_df["entry_id"] == entry_id
        if mask.any():
            msg = f'Existing entry with Entry ID "{entry_id}" was overwritten.'
            logger.warning(msg)
            messages.append(dict(level=logging.WARNING, msg=msg))
            exsisting_metadata_df = exsisting_metadata_df[~mask]

        combined = pd.concat(
                [exsisting_metadata_df, metadata_df], ignore_index=True
            )
        combined.to_csv(metadata_csv, index=False)
    except Exception:
        msg = f'Failed to write AlphaFold metadata CSV to "{metadata_csv}".'
        logger.exception(msg)
        messages.append(dict(level=logging.ERROR, msg=msg))


def get_amino_acid_sequence_df(
    entry_id: str, work_dir: Path, fasta_dest: Path, messages: list
) -> pd.DataFrame:
    try:
        fasta_dict = fasta_import(str(fasta_dest))
        amino_acid_sequence_df = fasta_dict["fasta_df"]
    except Exception:
        msg = "Failed to create sequence dataframe"
        logger.exception(msg)
        messages.append(dict(level=logging.ERROR, msg=msg))
    return amino_acid_sequence_df


def handle_alphafold_files(
    files_urls: dict[str, Any],
    uniprot: str,
    seq: str,
    metadata_df: pd.DataFrame,
    entry_id: str,
    persist_upload: bool = False,
) -> dict[str, pd.DataFrame | None]:
    """
    Download AlphaFold structure files and convert them to DataFrames.

    Files can either be persistently saved to disk or only loaded into memory for the current run.
    The function downloads CIF, PAE, and pLDDT files, converts them to DataFrames, and optionally
    saves metadata to a CSV file.

    :param files_urls: Dictionary containing URLs for CIF, PAE, and pLDDT files
    :param uniprot: The UniProt ID of the protein
    :param seq: The protein sequence
    :param metadata_df: DataFrame containing AlphaFold metadata
    :param entry_id: The entry_id (in the case of fetching from AF DB the same as uniprot id) (used for directory naming)
    :param persist_upload: If True, files are saved persistently; if False, only loaded into memory
    :return: A dictionary containing DataFrames for metadata, CIF, PAE, pLDDT, sequence data or None values for
    failed loads and messages such as warnings
    """
    cif_df = None
    pae_df = None
    plddt_df = None
    amino_acid_sequence_df = None
    messages = []
    downloaded: dict[str, str] = {}

    temp_dir, work_dir = get_correct_af_directories(
        entry_id=uniprot,
        directory_name=paths.ALPHAFOLD_MONOMER_PATH,
        persist_upload=persist_upload,
    )

    try:
        if persist_upload:
            paths.ALPHAFOLD_MONOMER_PATH.mkdir(parents=True, exist_ok=True)
            existing_metadata_df = get_monomer_metadata_df()
            extend_metadata_csv(
                entry_id=uniprot,
                metadata_csv=paths.AF_MONOMER_METADATA_CSV_PATH,
                exsisting_metadata_df=existing_metadata_df,
                metadata_df=metadata_df,
                messages=messages,
            )

        for key in ("cifUrl", "paeDocUrl", "plddtDocUrl"):
            urlval = files_urls.get(key)
            if isinstance(urlval, str) and urlval:
                fname = urlval.split("?")[0].rstrip("/").split("/")[-1]
                dest = work_dir / fname
                saved = download_file_from_url(urlval, dest)
                if saved:
                    downloaded[key] = str(saved)
                    try:
                        if key == "cifUrl":
                            cif_df = read_alphafold_mmcif(saved)
                        elif key == "paeDocUrl":
                            pae_df = pd.read_json(saved)
                        elif key == "plddtDocUrl":
                            plddt_df = pd.read_json(saved)
                    except Exception:
                        msg = f'Failed to load "{key}" into dataframe'
                        logger.exception(msg)
                        messages.append(dict(level=logging.ERROR, msg=msg))
        try:
            sequence = to_fasta(seq=seq, header=uniprot)
            fasta_dest = work_dir / f"{entry_id.upper()}.fasta"
            fasta_dest.parent.mkdir(parents=True, exist_ok=True)
            with open(fasta_dest, "w") as f:
                f.write(sequence)
        except OSError:
            msg = f'Failed to write FASTA file "{fasta_dest}"'
            logger.exception(msg)
            messages.append(dict(level=logging.ERROR, msg=msg))
        amino_acid_sequence_df = get_amino_acid_sequence_df(
            entry_id=uniprot,
            work_dir=work_dir,
            fasta_dest=fasta_dest,
            messages=messages,
        )

    finally:
        if temp_dir is not None:
            shutil.rmtree(temp_dir, ignore_errors=True)

    return {
        "cif_df": cif_df,
        "pae_df": pae_df,
        "plddt_df": plddt_df,
        "amino_acid_sequence_df": amino_acid_sequence_df,
        "messages": messages,
    }


def fetch_alphafold_protein_structure(
    uniprot_id: str, persist_upload: bool
) -> dict[str, Any]:
    """
    Fetch AlphaFold protein structure data from the AlphaFold Database API.

    Retrieves metadata and structure files (CIF, PAE, pLDDT) from the AlphaFold Database
    for the given UniProt ID. Optionally persists the downloaded files to disk.

    :param uniprot_id: The UniProt ID of the protein
    :param persist_upload: If True, files are saved persistently; if False, only loaded into memory
    :return: A dictionary containing DataFrames for metadata, CIF, PAE, pLDDT, and sequence data
    :raises RuntimeError: If the API request fails or returns invalid data
    :raises ValueError: If no predictions are found for the given UniProt ID
    """
    url = f"https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}"
    with requests.Session() as session:
        try:
            resp = session.get(url, timeout=30)
            resp.raise_for_status()
            records = resp.json()
        except requests.RequestException as e:
            raise RuntimeError(f"AlphaFold request failed for {uniprot_id}: {e}") from e
        except ValueError as e:
            raise RuntimeError(
                f"AlphaFold returned non-JSON for {uniprot_id}: {e}"
            ) from e

        if not isinstance(records, list) or not records:
            raise ValueError(f"No AlphaFold DB predictions for {uniprot_id}")

        r = records[0]
        if not isinstance(r, dict):
            raise RuntimeError(f"Unexpected AlphaFold payload for {uniprot_id}")

        data: dict[str, Any] = {
            "entry_id": r.get("uniprotAccession"),
            "uniprot_accession": r.get("uniprotAccession"),
            "model_created_date": r.get("modelCreatedDate"),
            "gene": r.get("gene"),
            "model_used": r.get("toolUsed"),
        }

        seq_tmp = r.get("sequence")

        files_urls: dict[str, Any] = {}

        for key in ("cifUrl", "paeDocUrl", "plddtDocUrl"):
            if isinstance(r.get(key), str) and r.get(key):
                files_urls[key] = r[key]

        metadata_df = pd.DataFrame([data])

        alpha_dfs = handle_alphafold_files(
            files_urls=files_urls,
            uniprot=uniprot_id,
            seq=seq_tmp,
            metadata_df=metadata_df,
            entry_id=uniprot_id,
            persist_upload=persist_upload,
        )
    df_dict = {
        "metadata_df": metadata_df,
        "cif_df": alpha_dfs["cif_df"],
        "pae_df": alpha_dfs["pae_df"],
        "plddt_df": alpha_dfs["plddt_df"],
        "amino_acid_sequence_df": alpha_dfs["amino_acid_sequence_df"],
    }
    messages = alpha_dfs["messages"]
    if not any(df.empty for df in df_dict.values()):
        success_msg = f"Successfully loaded AlphaFold data for protein with Protein ID '{uniprot_id}'"
        logger.info(success_msg)
        messages.append(dict(level=logging.INFO, msg=success_msg))
    else:
        message = (
            f"Could not load AlphaFold data for protein with Protein ID '{uniprot_id}'"
        )
        logger.warning(message)
        messages.append(dict(level=logging.WARNING, msg=message))
    df_dict["messages"] = messages
    return df_dict


def get_all_available_entry_ids_of_monomer_metadata() -> list[str]:
    """ "
    Get the entry ids of all the protein structure predictions that can be found on disk.
    """
    df = get_monomer_metadata_df()
    return df["entry_id"].tolist()


def get_all_available_entry_ids_of_multimer_metadata() -> list[str]:
    """ "
    Get the entry ids of all the protein structure predictions that can be found on disk.
    """
    df = get_multimer_metadata_df()
    return df["entry_id"].tolist()


def check_and_get_metadata_df(entry_id: str, all_metadata_df: pd.DataFrame, csv_file: Path) -> pd.DataFrame:
    metadata_df = all_metadata_df[all_metadata_df["entry_id"] == entry_id]
    if metadata_df.empty:
        msg = f"No metadata for Entry ID '{entry_id}' in {csv_file}"
        logger.error(msg)
        raise ValueError(msg)
    return metadata_df


def check_dir(entry_id: str, dir: Path):
    if not dir.exists() or not dir.is_dir():
        msg = f"AlphaFold data directory not found for entry '{entry_id}': {dir}"
        logger.error(msg)
        raise FileNotFoundError(msg)


def get_cif_df_from_disk(entry_id: str, structure_dir: Path, messages: list) -> pd.DataFrame:
    cif_files = list(structure_dir.glob("*.cif"))
    if not cif_files:
        msg = f"No CIF file found in {structure_dir} for entry '{entry_id}'"
        logger.error(msg)
        raise FileNotFoundError(msg)

    if len(cif_files) > 1:
        message = "There are several CIF files for this protein structure prediction. The first one will be read, all others will be ignored."
        logger.info(message)
        messages.append(dict(level=logging.WARNING, msg=message))

    cif_file = cif_files[0]
    try:
        cif_df = read_alphafold_mmcif(str(cif_file))
        return cif_df
    except Exception as e:
        msg = f"Failed to read CIF file '{cif_file}': {e}"
        logger.exception(msg)
        raise RuntimeError(msg) from e
    

def get_amino_acid_sequences_df_from_disk(entry_id: str, structure_dir: Path) -> pd.DataFrame:
    fasta_files = list(structure_dir.glob("*.fasta")) + list(structure_dir.glob("*.fa"))
    if not fasta_files:
        msg = f"No FASTA file found in {structure_dir} for entry '{entry_id}'"
        logger.error(msg)
        raise FileNotFoundError(msg)

    fasta_file = fasta_files[0]
    try:
        fasta_dict = fasta_import(str(fasta_file))
        amino_acid_sequences_df = fasta_dict.get("fasta_df")
        if amino_acid_sequences_df is None:
            msg = f"FASTA importer did not return 'fasta_df' for {fasta_file}"
            logger.error(msg)
            raise RuntimeError(msg)
    except Exception as e:
        msg = f"Failed to load FASTA '{fasta_file}': {e}"
        logger.exception(msg)
        raise RuntimeError(msg) from e
    return amino_acid_sequences_df


def get_json_files_in_dir(entry_id: str, structure_dir: Path) -> list:
    json_files = list(structure_dir.glob("*.json"))
    if not json_files:
        msg = f"No JSON files found in {structure_dir} for entry '{entry_id}'"
        logger.error(msg)
        raise FileNotFoundError(msg)
    return json_files


def check_success_of_get_df(entry_id:str, df_dict: dict, messages: list) -> None:
    if not any(df.empty for df in df_dict.values()):
        success_msg = f"Successfully loaded AlphaFold data for entry '{entry_id}'"
        logger.info(success_msg)
        messages.append(dict(level=logging.INFO, msg=success_msg))
    else:
        message = f"Could not load AlphaFold data for entry '{entry_id}'"
        logger.warning(message)
        messages.append(dict(level=logging.WARNING, msg=message))


def get_monomer_structure_dfs(entry_id: str) -> dict[str, Any]:
    """
    Writes monomer structure data from disk of a specific entry ID into dataframes.

    :param entry_id: entry_id of the uploaded monomer structure
    :return: A dictionary containing DataFrames for metadata, CIF, PAE, pLDDT, and sequence data
    """
    messages: list[dict[str, str | int]] = []
    all_metadata_df = get_monomer_metadata_df()

    metadata_df = check_and_get_metadata_df(entry_id=entry_id, all_metadata_df=all_metadata_df, csv_file=paths.AF_MONOMER_METADATA_CSV_PATH)

    structure_dir = paths.ALPHAFOLD_MONOMER_PATH / entry_id.upper()
    check_dir(entry_id=entry_id, dir=structure_dir)

    # get cif file
    cif_df = get_cif_df_from_disk(entry_id=entry_id, structure_dir=structure_dir, messages=messages)

    # get fasta file
    amino_acid_sequence_df = get_amino_acid_sequences_df_from_disk(entry_id=entry_id, structure_dir=structure_dir)

    # get jsons (PAE and pLDDT)
    json_files = list(structure_dir.glob("*.json"))
    if not json_files:
        msg = f"No JSON files (PAE/pLDDT) found in {structure_dir} for entry '{entry_id}'"
        logger.error(msg)
        raise FileNotFoundError(msg)

    try:
        if len(json_files) == 1:
            msg = f"Only one json file found in {structure_dir} for entry '{entry_id}'. Two json files are expected"
            logger.error(msg)
            raise RuntimeError()
        else:
            json1 = pd.read_json(json_files[0])
            json2 = pd.read_json(json_files[1])
            if (
                "predicted_aligned_error" in json1.columns
                and "residueNumber" in json2.columns
            ):
                pae_df = json1
                plddt_df = json2
            elif (
                "predicted_aligned_error" in json2.columns
                and "residueNumber" in json1.columns
            ):
                pae_df = json2
                plddt_df = json1
            else:
                # Fallback: assign and warn
                pae_df = json1
                plddt_df = json2
                warn = f"Could not detect PAE/pLDDT in JSON files for entry '{entry_id}'; ''{json_files[0]} is read as PAE, {json_files[1]} is read as pLDDT."
                logger.warning(warn)
                messages.append(dict(level=logging.WARNING, msg=warn))
    except Exception as e:
        msg = f"Failed to read JSON files in {structure_dir}: {e}"
        logger.exception(msg)
        raise RuntimeError(msg) from e

    df_dict = {
        "metadata_df": metadata_df,
        "cif_df": cif_df,
        "pae_df": pae_df,
        "plddt_df": plddt_df,
        "amino_acid_sequence_df": amino_acid_sequence_df,
    }
    check_success_of_get_df(entry_id=entry_id, df_dict=df_dict)
    df_dict["messages"] = messages
    return df_dict


def get_multimer_structure_dfs(entry_id: str) -> dict[str, Any]:
    """
    Writes multimer structure data from disk of a specific entry ID into dataframes.

    :param entry_id: entry_id of the uploaded monomer structure
    :return: A dictionary containing DataFrames for metadata, CIF, confidence, full data, and sequence data
    """
    messages: list[dict[str, str | int]] = []
    all_metadata_df = get_multimer_metadata_df()

    metadata_df = check_and_get_metadata_df(entry_id=entry_id, all_metadata_df=all_metadata_df, csv_file=paths.AF_MULTIMER_METADATA_CSV_PATH)

    structure_dir = paths.ALPHAFOLD_MULTIMER_PATH / entry_id.upper()
    check_dir(entry_id=entry_id, dir=structure_dir)

    # get cif file
    cif_df = get_cif_df_from_disk(entry_id=entry_id, structure_dir=structure_dir, messages=messages)

    # get fasta file
    amino_acid_sequences_df = get_amino_acid_sequences_df_from_disk(entry_id=entry_id, structure_dir=structure_dir)

    # get jsons (PAE and pLDDT)
    json_files = get_json_files_in_dir(entry_id=entry_id, structure_dir=structure_dir)

    try:
        if len(json_files) == 1:
            msg = f"Only one json file found in {structure_dir} for entry '{entry_id}'. Two json files are expected"
            logger.error(msg)
            raise RuntimeError()
        else:
            with open(json_files[0], "r") as f:
                obj1 = json.load(f)
            with open(json_files[1], "r") as f:
                obj2 = json.load(f)

            json1 = pd.json_normalize(obj1)
            json2 = pd.json_normalize(obj2)
            # iptm stands for interface predicted TM score
            if (
                "chain_iptm" in json1.columns
                and "pae" in json2.columns
            ):
                confidence_df = json1
                full_data_df = json2
            elif (
                "chain_iptm" in json2.columns
                and "pae" in json1.columns
            ):
                confidence_df = json2
                full_data_df = json1
            else:
                # Fallback: assign and warn
                confidence_df = json1
                full_data_df = json2
                warn = f"Could not detect confidence scores/full data information in JSON files for entry '{entry_id}'; ''{json_files[0]} is read as confidenc, {json_files[1]} is read as full data summary."
                logger.warning(warn)
                messages.append(dict(level=logging.WARNING, msg=warn))
    except Exception as e:
        msg = f"Failed to read JSON files in {structure_dir}: {e}"
        logger.exception(msg)
        raise RuntimeError(msg) from e

    df_dict = {
        "metadata_df": metadata_df,
        "amino_acid_sequences_df": amino_acid_sequences_df,
        "cif_df": cif_df,
        "confidence_df": confidence_df,
        "full_data_df": full_data_df,   
    }

    check_success_of_get_df(entry_id=entry_id, df_dict=df_dict, messages=messages)
    df_dict["messages"] = messages
    return df_dict


def upload_multimer_prediction(
    entry_id: str,
    uniprot_ids: list[str],
    model_used: str,
    amino_acid_sequences: Path,
    cif_file: Path,
    confidence_file: Path,
    full_data_file: Path,
    persist_upload: bool,
) -> dict[str, Any]:

    messages = []

    temp_dir, work_dir = get_correct_af_directories(
        entry_id=entry_id,
        directory_name=paths.ALPHAFOLD_MULTIMER_PATH,
        persist_upload=persist_upload,
    )

    now_utc = datetime.now(timezone.utc)
    formatted = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    data: dict[str, Any] = {
        "entry_id": entry_id,
        "uniprot_ids": uniprot_ids,
        "model_created_date": formatted,
        "model_used": model_used,
    }

    metadata_df = pd.DataFrame([data])
    exsisting_metadata_df = get_multimer_metadata_df()
    extend_metadata_csv(
        entry_id=entry_id,
        metadata_csv=paths.AF_MULTIMER_METADATA_CSV_PATH,
        exsisting_metadata_df=exsisting_metadata_df,
        metadata_df=metadata_df,
        messages=messages,
    )

    upload_dir = paths.ALPHAFOLD_MULTIMER_PATH / entry_id.upper()
    if not upload_dir.exists():
        upload_dir.mkdir(parents=True, exist_ok=True)

    if persist_upload:
        for file_name in [
            amino_acid_sequences,
            cif_file,
            confidence_file,
            full_data_file,
        ]:
            success, msg = copy_file_to_directory(file_name, upload_dir)
            if not success:
                logger.error(msg)
                messages.append(dict(level=logging.ERROR, msg=msg))

    fasta_dict = fasta_import(str(amino_acid_sequences))
    amino_acid_sequence_df = fasta_dict["fasta_df"]

    confidence_df = pd.read_json(confidence_file)

    # full_data json has arrays of unequal lengths so we need to normalize
    with open(full_data_file, "r") as f:
        full_data = json.load(f)
    if isinstance(full_data, dict):
        full_data_df = pd.json_normalize(full_data)

    cif_df = read_alphafold_mmcif(cif_file)

    df_dict = {
        "metadata_df": metadata_df,
        "cif_df": cif_df,
        "confidence_df": confidence_df,
        "full_data_df": full_data_df,
        "amino_acid_sequences_df": amino_acid_sequence_df,
    }

    if not any(df.empty for df in df_dict.values()):
        success_msg = f"Successfully loaded AlphaFold data for entry '{entry_id}'"
        logger.info(success_msg)
        messages.append(dict(level=logging.INFO, msg=success_msg))
    else:
        message = f"Could not load AlphaFold data for entry '{entry_id}'"
        logger.warning(message)
        messages.append(dict(level=logging.WARNING, msg=message))
    df_dict["messages"] = messages
    return df_dict
