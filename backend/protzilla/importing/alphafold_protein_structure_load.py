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
import numpy as np
import ast
import requests
import re

from backend.protzilla.constants import paths
from backend.protzilla.constants.protzilla_logging import logger
from backend.protzilla.importing.fasta_import import fasta_import
from backend.protzilla.networking import download_file_from_url
from backend.protzilla.utilities.utilities import copy_file_to_directory
from backend.protzilla.steps import Output, OutputItem, OutputType


def get_monomer_metadata_df() -> pd.DataFrame:
    """
    Returns all data from alphafold_monomer_metadata.csv in form of a dataframe. If no such csv exist, it returns
    a dataframe with the corresponding keys but no values and creates a csv with the expected column names.
    """
    monomer_metadata_csv = paths.AF_MONOMER_METADATA_CSV_PATH
    if not monomer_metadata_csv.exists():
        metadata_df = pd.DataFrame(
            columns=[
                "entry_id",
                "uniprot_accession",
                "model_created_date",
                "gene",
                "model_used",
            ]
        )
        monomer_metadata_csv.parent.mkdir(parents=True, exist_ok=True)
        metadata_df.to_csv(monomer_metadata_csv, index=False)
        return metadata_df
    return pd.read_csv(monomer_metadata_csv, dtype=str)


def get_multimer_metadata_df() -> pd.DataFrame:
    """
    Returns all data from alphafold_multimer_metadata.csv in form of a dataframe. If no such csv exist, it returns
    a dataframe with the corresponding keys but no values and creates a csv with the expected column names.
    """
    multimer_metadata_csv = paths.AF_MULTIMER_METADATA_CSV_PATH

    if not multimer_metadata_csv.exists():
        metadata_df = pd.DataFrame(
            columns=[
                "entry_id",
                "uniprot_ids",
                "model_created_date",
                "model_used",
            ]
        )
        multimer_metadata_csv.parent.mkdir(parents=True, exist_ok=True)
        metadata_df.to_csv(multimer_metadata_csv, index=False)
        return metadata_df
    return pd.read_csv(multimer_metadata_csv, dtype=str)


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


def read_alphafold_mmcif(path: Path) -> pd.DataFrame:
    """
    Parse an AlphaFold mmCIF (Macromolecular Crystallographic Information File) file.

    :param path: The path to the mmCIF file
    :return: A DataFrame containing the atom site information from the CIF file
    :raises FileNotFoundError: If the file does not exist
    :raises IsADirectoryError: If the path points to a directory instead of a file
    :raises ValueError: If no CIF blocks are found in the file
    """
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if path.is_dir():
        raise IsADirectoryError(f"Expected a file path, got a directory: {path}")

    doc = gemmi.cif.read_file(str(path))
    if len(doc) == 0:
        raise ValueError(f"No CIF blocks found in file: {path}")

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
) -> tuple[Path | None, Path]:
    """
    Determine and prepare the appropriate working directory for an entry.

    If persist_upload is True, a persistent directory named after the
    uppercased entry_id is created inside directory_name and used as the
    working directory. If persist_upload is False, a temporary directory
    is created and used instead.

    :param entry_id: Identifier of the entry. Used as the name of the
        subdirectory (uppercased) when persist_upload is True.
    :param directory_name: Base directory under which the persistent
        entry-specific directory is created.
    :param persist_upload: Whether to create and use a persistent
        directory or a temporary one.
    :return: A tuple containing the temporary directory (or None if not
        created) and the working directory to use.
    """

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
    existing_metadata_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    messages: list,
) -> None:
    """
    Extend or update the AlphaFold metadata CSV with a new entry.

    If an entry with the given entry_id already exists in the provided
    existing_metadata_df, it is removed and replaced with the data from
    metadata_df. The combined DataFrame is then written to metadata_csv.

    Any warnings or errors encountered during processing are logged and
    appended to the provided messages list.

    :param entry_id: The Entry ID used to identify and potentially
        overwrite an existing row in the metadata.
    :param metadata_csv: Path to the metadata CSV file that should be
        updated.
    :param exsisting_metadata_df: The current metadata DataFrame loaded
        from the CSV file.
    :param metadata_df: The new metadata DataFrame to append to the
        existing data.
    :param messages: A list used to collect structured log messages
        with level and message content.
    :return: None.
    :raises Exception: Propagates unexpected errors that occur during
        concatenation or writing to disk after logging them.
    """
    try:
        mask = (
            existing_metadata_df["entry_id"].astype(str).str.upper() == entry_id.upper()
        )
        if mask.any():
            msg = f'Existing entry with Entry ID "{entry_id}" was overwritten. Entry IDs are compared case insensitively, so "ABC" and "abc" are treated as the same ID.'
            logger.warning(msg)
            messages.append(dict(level=logging.WARNING, msg=msg))
            existing_metadata_df = existing_metadata_df[~mask]

        combined = pd.concat([existing_metadata_df, metadata_df], ignore_index=True)
        combined.to_csv(metadata_csv, index=False)
    except Exception:
        msg = f'Failed to write AlphaFold metadata CSV to "{metadata_csv}".'
        logger.exception(msg)
        messages.append(dict(level=logging.ERROR, msg=msg))


def get_amino_acid_sequences_df(fasta_dest: Path, messages: list) -> pd.DataFrame:
    """
    Load a FASTA file and return its amino acid sequence DataFrame.

    The function uses fasta_import to parse the FASTA file and extracts
    the DataFrame stored under the key "fasta_df". If an error occurs
    during parsing, the exception is logged, a message is appended to
    the provided messages list, and an empty DataFrame is returned.

    :param fasta_dest: Path to the FASTA file to be imported.
    :param messages: A list used to collect structured log messages
        with level and message content.
    :return: A DataFrame containing the amino acid sequence information,
        or an empty DataFrame if parsing fails.
    :raises Exception: Propagates unexpected errors from fasta_import
        after logging them.
    """
    try:
        fasta_dict = fasta_import(str(fasta_dest))
        amino_acid_sequences_df = fasta_dict["fasta_df"]
        return amino_acid_sequences_df
    except Exception:
        msg = "Failed to create sequence dataframe"
        logger.exception(msg)
        messages.append(dict(level=logging.ERROR, msg=msg))
        return pd.DataFrame()


def handle_alphafold_files(
    files_urls: dict[str, Any],
    uniprot: str,
    seq: str,
    monomer_metadata_df: pd.DataFrame,
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
    :param monomer_metadata_df: DataFrame containing AlphaFold monomer metadata
    :param entry_id: The entry_id (in the case of fetching from AF DB the same as uniprot id) (used for directory naming)
    :param persist_upload: If True, files are saved persistently; if False, only loaded into memory
    :return: A dictionary containing DataFrames for monomer metadata, CIF, PAE, pLDDT, sequence data or None values for
    failed loads and messages such as warnings
    """
    cif_df = pd.DataFrame()
    pae_df = pd.DataFrame()
    plddt_df = pd.DataFrame()
    amino_acid_sequences_df = pd.DataFrame()
    messages = []

    temp_dir, work_dir = get_correct_af_directories(
        entry_id=entry_id,
        directory_name=paths.ALPHAFOLD_MONOMER_PATH,
        persist_upload=persist_upload,
    )

    try:
        if persist_upload:
            paths.ALPHAFOLD_MONOMER_PATH.mkdir(parents=True, exist_ok=True)
            existing_metadata_df = get_monomer_metadata_df()
            extend_metadata_csv(
                entry_id=entry_id,
                metadata_csv=paths.AF_MONOMER_METADATA_CSV_PATH,
                existing_metadata_df=existing_metadata_df,
                metadata_df=monomer_metadata_df,
                messages=messages,
            )

        for key in ("cifUrl", "paeDocUrl", "plddtDocUrl"):
            urlval = files_urls.get(key)
            if isinstance(urlval, str) and urlval:
                fname = urlval.split("?")[0].rstrip("/").split("/")[-1]
                dest = work_dir / fname
                saved = download_file_from_url(urlval, dest)
                if saved:
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
        fasta_dest: Path | None = None
        try:
            sequence = to_fasta(seq=seq, header=uniprot)
            fasta_dest = work_dir / f"{entry_id}.fasta"
            fasta_dest.parent.mkdir(parents=True, exist_ok=True)
            with open(fasta_dest, "w") as f:
                f.write(sequence)
        except OSError:
            msg = f'Failed to write FASTA file "{fasta_dest}"'
            logger.exception(msg)
            messages.append(dict(level=logging.ERROR, msg=msg))
        if fasta_dest is not None:
            amino_acid_sequences_df = get_amino_acid_sequences_df(
                fasta_dest=fasta_dest,
                messages=messages,
            )

    finally:
        if temp_dir is not None:
            shutil.rmtree(temp_dir, ignore_errors=True)

    # For consistency with multimer pLDDT
    plddt_df["chainID"] = "A"

    return {
        "cif_df": cif_df,
        "pae_df": pae_df,
        "plddt_df": plddt_df,
        "amino_acid_sequences_df": amino_acid_sequences_df,
        "messages": messages,
    }


def fetch_alphafold_protein_structure(
    uniprot_id: str, persist_upload: bool
) -> dict[str, Any]:
    """
    Fetch AlphaFold protein structure data from the AlphaFold Database API.

    Retrieves monomer metadata and structure files (CIF, PAE, pLDDT) from the AlphaFold Database
    for the given UniProt ID. Optionally persists the downloaded files to disk.

    :param uniprot_id: The UniProt ID of the protein
    :param persist_upload: If True, files are saved persistently; if False, only loaded into memory
    :return: A dictionary containing DataFrames for monomer metadata, CIF, PAE, pLDDT, and sequence data
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
        if not isinstance(seq_tmp, str) or not seq_tmp.strip():
            raise RuntimeError(
                f"AlphaFold payload for {uniprot_id} does not contain a valid protein sequence."
            )

        files_urls: dict[str, Any] = {}

        for key in ("cifUrl", "paeDocUrl", "plddtDocUrl"):
            if isinstance(r.get(key), str) and r.get(key):
                files_urls[key] = r[key]

        monomer_metadata_df = pd.DataFrame([data])

        alpha_dfs = handle_alphafold_files(
            files_urls=files_urls,
            uniprot=uniprot_id,
            seq=seq_tmp,
            monomer_metadata_df=monomer_metadata_df,
            entry_id=uniprot_id,
            persist_upload=persist_upload,
        )
    df_dict = {
        "structure_metadata_df": monomer_metadata_df,
        "cif_df": alpha_dfs["cif_df"],
        "pae_df": alpha_dfs["pae_df"],
        "plddt_df": alpha_dfs["plddt_df"],
        "amino_acid_sequences_df": alpha_dfs["amino_acid_sequences_df"],
    }
    messages = alpha_dfs["messages"]
    if not any(df.empty for df in df_dict.values()):
        success_msg = f"Successfully loaded AlphaFold data for protein with Protein ID '{uniprot_id}'"
        logger.info(success_msg)
        messages.append(dict(level=logging.INFO, msg=success_msg))
        data_for_visualization = {
            "structure_entry_id": uniprot_id,
            "cif_df": alpha_dfs["cif_df"],
        }
    else:
        message = (
            f"Could not load AlphaFold data for protein with Protein ID '{uniprot_id}'"
        )
        logger.warning(message)
        messages.append(dict(level=logging.WARNING, msg=message))
        data_for_visualization = None

    pae_string = str(df_dict["pae_df"]["predicted_aligned_error"].iloc[0])
    pae_matrix = np.array(ast.literal_eval(pae_string))
    del df_dict["pae_df"]

    return dict(
        **df_dict,
        pae_matrix=OutputItem(output_type=OutputType.JOBLIB_ARTIFACT, value=pae_matrix),
        messages=messages,
        visualization=OutputItem(
            output_type=OutputType.VISUALIZATION, value=data_for_visualization
        ),
    )


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


def check_and_get_metadata_df(
    entry_id: str, all_metadata_df: pd.DataFrame, csv_file: Path
) -> pd.DataFrame:
    """
    Retrieve the metadata row for a given Entry ID from a DataFrame.

    The function filters all_metadata_df for rows matching the provided
    entry_id. If no matching metadata is found, an error is logged and
    a ValueError is raised.

    :param entry_id: The Entry ID used to filter the metadata DataFrame.
    :param all_metadata_df: The complete metadata DataFrame containing
        all entries.
    :param csv_file: Path to the CSV file from which the metadata was
        loaded. Used for error reporting.
    :return: A DataFrame containing the metadata for the specified
        Entry ID.
    :raises ValueError: If no metadata for the given Entry ID is found.
    """
    metadata_df = all_metadata_df[
        all_metadata_df["entry_id"].astype(str).str.upper() == entry_id.upper()
    ]
    if metadata_df.empty:
        msg = f"No metadata for Entry ID '{entry_id}' in {csv_file}"
        logger.error(msg)
        raise ValueError(msg)
    return metadata_df


def check_dir(entry_id: str, dir: Path) -> None:
    """
    Validate that the given directory exists and is a directory.

    :param entry_id: The Entry ID used for error reporting.
    :param dir: Path to the expected AlphaFold data directory.
    :return: None.
    :raises FileNotFoundError: If the directory does not exist or is
        not a valid directory.
    """
    if not dir.exists() or not dir.is_dir():
        msg = f"AlphaFold data directory not found for entry '{entry_id}': {dir}"
        logger.error(msg)
        raise FileNotFoundError(msg)


def get_cif_df_from_disk(
    entry_id: str, structure_dir: Path, messages: list
) -> pd.DataFrame:
    """
    Load the AlphaFold mmCIF file from disk and return it as a DataFrame.

    The function searches the given structure directory for files with
    the .cif extension. If multiple CIF files are found, only the first
    one is read and a warning message is logged and appended to the
    messages list. If no CIF file is found, a FileNotFoundError is raised.

    :param entry_id: The Entry ID used for error reporting.
    :param structure_dir: Path to the directory containing the structure
        files.
    :param messages: A list used to collect structured log messages
        with level and message content.
    :return: A DataFrame containing the parsed mmCIF data.
    :raises FileNotFoundError: If no CIF file is found in the directory.
    :raises RuntimeError: If reading the CIF file fails.
    """
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
        cif_df = read_alphafold_mmcif(cif_file)
        return cif_df
    except Exception as e:
        msg = f"Failed to read CIF file '{cif_file}': {e}"
        logger.exception(msg)
        raise RuntimeError(msg) from e


def get_amino_acid_sequences_df_from_disk(
    entry_id: str, structure_dir: Path
) -> pd.DataFrame:
    """
    Load the amino acid sequence DataFrame from a FASTA file on disk.

    The function searches the given structure directory for files with
    the .fasta or .fa extension. The first matching file is parsed using
    fasta_import and the DataFrame stored under the key "fasta_df" is
    returned.

    :param entry_id: The Entry ID used for error reporting.
    :param structure_dir: Path to the directory containing the FASTA file.
    :return: A DataFrame containing the amino acid sequence data.
    :raises FileNotFoundError: If no FASTA file is found in the directory.
    :raises RuntimeError: If loading the FASTA file fails or if the
        importer does not return a "fasta_df" entry.
    """
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
    """
    Retrieve all JSON files from a given structure directory.

    The function searches the specified directory for files with the
    .json extension and returns them as a list. If no JSON files are
    found, an error is logged and a FileNotFoundError is raised.

    :param entry_id: The Entry ID used for error reporting.
    :param structure_dir: Path to the directory to search for JSON files.
    :return: A list of Path objects representing the JSON files found
        in the directory.
    :raises FileNotFoundError: If no JSON files are found in the directory.
    """
    json_files = list(structure_dir.glob("*.json"))
    if not json_files:
        msg = f"No JSON files found in {structure_dir} for entry '{entry_id}'"
        logger.error(msg)
        raise FileNotFoundError(msg)
    return json_files


def check_success_of_get_df(entry_id: str, df_dict: dict, messages: list) -> None:
    """
    Evaluate whether all retrieved DataFrames contain data and log the result.

    The function checks if any DataFrame in df_dict is empty. If none are
    empty, a success message is logged and appended to the messages list.
    If at least one DataFrame is empty, a warning message is logged and
    appended instead.

    :param entry_id: The Entry ID used for logging the result.
    :param df_dict: A dictionary containing DataFrames that were loaded
        for the given entry.
    :param messages: A list used to collect structured log messages
        with level and message content.
    :return: None.
    """
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
    :return: A dictionary containing DataFrames for monomer metadata, CIF, PAE, pLDDT, and sequence data
    """
    messages: list[dict[str, str | int]] = []
    all_metadata_df = get_monomer_metadata_df()

    monomer_metadata_df = check_and_get_metadata_df(
        entry_id=entry_id,
        all_metadata_df=all_metadata_df,
        csv_file=paths.AF_MONOMER_METADATA_CSV_PATH,
    )

    structure_dir = paths.ALPHAFOLD_MONOMER_PATH / entry_id.upper()
    check_dir(entry_id=entry_id, dir=structure_dir)

    # get cif file
    cif_df = get_cif_df_from_disk(
        entry_id=entry_id, structure_dir=structure_dir, messages=messages
    )

    # get fasta file
    amino_acid_sequences_df = get_amino_acid_sequences_df_from_disk(
        entry_id=entry_id, structure_dir=structure_dir
    )

    # get jsons (PAE and pLDDT)
    json_files = list(structure_dir.glob("*.json"))
    if not json_files:
        msg = (
            f"No JSON files (PAE/pLDDT) found in {structure_dir} for entry '{entry_id}'"
        )
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

    # For consistency with multimer pLDDT
    plddt_df["chainID"] = "A"

    df_dict = {
        "structure_metadata_df": monomer_metadata_df,
        "cif_df": cif_df,
        "pae_df": pae_df,
        "plddt_df": plddt_df,
        "amino_acid_sequences_df": amino_acid_sequences_df,
    }
    check_success_of_get_df(entry_id=entry_id, df_dict=df_dict, messages=messages)

    data_for_visualization = {
        "structure_entry_id": entry_id,
        "cif_df": cif_df,
    }

    pae_string = str(df_dict["pae_df"]["predicted_aligned_error"].iloc[0])
    pae_matrix = np.array(ast.literal_eval(pae_string))
    del df_dict["pae_df"]

    return dict(
        **df_dict,
        pae_matrix=OutputItem(output_type=OutputType.JOBLIB_ARTIFACT, value=pae_matrix),
        messages=messages,
        visualization=OutputItem(
            output_type=OutputType.VISUALIZATION, value=data_for_visualization
        ),
    )


def unwrap_full_data_df(full_data_df: pd.DataFrame) -> dict[str, Any]:
    """
    Extracts certain data from a full_data_df, deletes the extracted columns
    and returns the "remaining" full_data_df as well as the extracted data.

    :param full_data_df: The AlphaFold3 full_data_df
    :return dict:
        - "full_data_df": The updated reduced full_data_df
        - "pae_matrix": Numpy matrix with the PAE values for each residue pair
    """

    # Construct plDDT dataframe
    # TODO: Getting pLDDT from AlphaFold3 is a bit harder as its on a per-atom level
    # rather than per-residue, so we'd need to extract it from the cif file
    # (column _atom_site.B_iso_or_equiv, see https://github.com/google-deepmind/alphafold3/issues/330).
    # Skipping this for now.

    pae_matrix = np.array(full_data_df["pae"].iloc[0])
    full_data_df = full_data_df.drop(columns=["pae"])

    return dict(
        full_data_df=full_data_df,
        pae_matrix=pae_matrix,
    )


def get_plddt_from_cif(cif_df: pd.DataFrame):
    """
    For use with multimers predicted using Alphafold3.
    Returns per-residue pLDDT values for the predicted structure.
    Note that sine AlphaFold3 uses per-atom pLDDT, we use the pLDDT for the CA atom.
    See also https://github.com/google-deepmind/alphafold3/issues/330

    :param cif_df: the cif_df holding the _atom_site table.
    :return: DataFrame containing columns
                "chainID", "residueNumber", "confidenceScore", "confidenceCategory"
    """

    filtered_cif_df = cif_df[cif_df["_atom_site.label_atom_id"] == "CA"]
    filtered_cif_df = filtered_cif_df[
        [
            "_atom_site.auth_asym_id",
            "_atom_site.label_seq_id",
            "_atom_site.B_iso_or_equiv",
        ]
    ]
    filtered_cif_df = filtered_cif_df.rename(
        columns={
            "_atom_site.auth_asym_id": "chainID",
            "_atom_site.label_seq_id": "residueNumber",
            "_atom_site.B_iso_or_equiv": "confidenceScore",
        }
    )

    # TODO: ConfidenceCategory maybe yes?

    return filtered_cif_df


def get_multimer_structure_dfs(entry_id: str) -> dict[str, Any]:
    """
    Writes multimer structure data from disk of a specific entry ID into dataframes.

    :param entry_id: entry_id of the uploaded monomer structure
    :return: A dictionary containing DataFrames for multimer metadata, CIF, confidence, full data, and sequence data
    """
    messages: list[dict[str, str | int]] = []
    all_metadata_df = get_multimer_metadata_df()

    multimer_metadata_df = check_and_get_metadata_df(
        entry_id=entry_id,
        all_metadata_df=all_metadata_df,
        csv_file=paths.AF_MULTIMER_METADATA_CSV_PATH,
    )

    structure_dir = paths.ALPHAFOLD_MULTIMER_PATH / entry_id.upper()
    check_dir(entry_id=entry_id, dir=structure_dir)

    # get cif file
    cif_df = get_cif_df_from_disk(
        entry_id=entry_id, structure_dir=structure_dir, messages=messages
    )

    # get fasta file
    amino_acid_sequences_df = get_amino_acid_sequences_df_from_disk(
        entry_id=entry_id, structure_dir=structure_dir
    )

    # get jsons (full data and confidence and job requests)
    json_files = get_json_files_in_dir(entry_id=entry_id, structure_dir=structure_dir)

    try:
        if len(json_files) == 1:
            msg = f"Only one json file found in {structure_dir} for entry '{entry_id}'. Two json files are expected"
            logger.error(msg)
            raise RuntimeError()
        elif len(json_files) == 2:
            msg = f"Only two json file found in {structure_dir} for entry '{entry_id}'. Three json files are expected"
            logger.error(msg)
            raise RuntimeError()
        else:
            with open(json_files[0], "r") as f:
                obj1 = json.load(f)
            with open(json_files[1], "r") as f:
                obj2 = json.load(f)
            with open(json_files[2], "r") as f:
                obj3 = json.load(f)

            json1 = pd.json_normalize(obj1)
            json2 = pd.json_normalize(obj2)
            json3 = pd.json_normalize(obj3)
            # iptm stands for interface predicted TM score

            confidence_df, full_data_df, job_request_df = None, None, None
            for json_df in [json1, json2, json3]:
                if "chain_iptm" in json_df.columns:
                    confidence_df = json_df
                elif "pae" in json_df.columns:
                    full_data_df = json_df
                elif "sequences" in json_df.columns:
                    job_request_df = json_df
            if confidence_df is None or full_data_df is None or job_request_df is None:
                msg = f"Could not detect confidence scores/full data/job request in JSON files for entry '{entry_id}'."
                logger.exception(msg)
                raise RuntimeError(msg)
    except Exception as e:
        msg = f"Failed to read JSON files in {structure_dir}: {e}"
        logger.exception(msg)
        raise RuntimeError(msg) from e
    df_dict = {
        "structure_metadata_df": multimer_metadata_df,
        "amino_acid_sequences_df": amino_acid_sequences_df,
        "cif_df": cif_df,
        "confidence_df": confidence_df,
        "full_data_df": full_data_df,
        "job_request_df": job_request_df,
    }
    check_success_of_get_df(entry_id=entry_id, df_dict=df_dict, messages=messages)
    data_for_visualization = {
        "structure_entry_id": entry_id,
        "cif_df": cif_df,
    }

    unwrapped_full_data = unwrap_full_data_df(df_dict["full_data_df"])
    df_dict["full_data_df"] = unwrapped_full_data["full_data_df"]

    pae_matrix = unwrapped_full_data["pae_matrix"]
    plddt_df = get_plddt_from_cif(df_dict["cif_df"])

    return dict(
        **df_dict,
        messages=messages,
        plddt_df=plddt_df,
        pae_matrix=OutputItem(output_type=OutputType.JOBLIB_ARTIFACT, value=pae_matrix),
        visualization=OutputItem(
            output_type=OutputType.VISUALIZATION, value=data_for_visualization
        ),
    )


def upload_multimer_prediction(
    entry_id: str,
    uniprot_ids: str,
    model_used: str,
    amino_acid_sequences: Path,
    cif_file: Path,
    confidence_file: Path,
    full_data_file: Path,
    job_request_file: Path,
    persist_upload: bool,
) -> dict[str, Any]:
    """
    Process an AlphaFold multimer prediction and return its parsed data as DataFrames.

    The function assembles multimer metadata for the prediction, optionally persists both
    multimer metadata and input files to the configured multimer storage directory, and
    parses the provided files into DataFrames:
    - FASTA sequences via fasta_import, key "fasta_df".
    - mmCIF structure via read_alphafold_mmcif.
    - Confidence JSON via pandas.read_json.
    - Full data JSON via json.load and pandas.json_normalize if it is a dict.

    The returned dictionary contains the DataFrames and a "messages" list with
    structured log entries describing warnings or errors encountered.

    Temporary working directories created when persist_upload is False are
    removed in a finally block.

    :param entry_id: Unique identifier for the prediction entry. Used for
        directory naming and mulitmer metadata.
    :param uniprot_ids: UniProt identifiers associated with the multimer
        prediction.
    :param model_used: Name or identifier of the AlphaFold model used to
        create the prediction.
    :param amino_acid_sequences: Path to the FASTA file containing the amino
        acid sequences.
    :param cif_file: Path to the mmCIF structure file.
    :param confidence_file: Path to the confidence JSON file.
    :param full_data_file: Path to the full data JSON file. If the JSON
        content is a dict it is normalized into a single-row DataFrame.
        Otherwise, an empty DataFrame is returned and a warning is recorded.
    :param persist_upload: If True, persist multimer metadata and copy input files into
        the configured multimer directory. If False, use a temporary directory
        and do not persist multimer metadata.
    :return: A dictionary containing:
        - "structure_metadata_df": DataFrame with entry multimer metadata.
        - "cif_df": DataFrame parsed from the mmCIF file.
        - "confidence_df": DataFrame loaded from the confidence JSON.
        - "full_data_df": Normalized DataFrame from the full data JSON or empty.
        - "amino_acid_sequences_df": DataFrame from the FASTA import.
        - "messages": List of structured log messages with level and msg.
    :raises Exception: Any exception raised during parsing or file operations
        will propagate after cleanup of any temporary directory.
    """

    messages = []

    temp_dir, work_dir = get_correct_af_directories(
        entry_id=entry_id,
        directory_name=paths.ALPHAFOLD_MULTIMER_PATH,
        persist_upload=persist_upload,
    )

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    uniprot_ids_as_list = re.split(r"\s*,\s*", uniprot_ids.strip())

    data: dict[str, Any] = {
        "entry_id": entry_id,
        "uniprot_ids": uniprot_ids_as_list,
        "model_created_date": timestamp,
        "model_used": model_used,
    }

    try:
        multimer_metadata_df = pd.DataFrame([data])
        if persist_upload:
            exsisting_metadata_df = get_multimer_metadata_df()
            extend_metadata_csv(
                entry_id=entry_id,
                metadata_csv=paths.AF_MULTIMER_METADATA_CSV_PATH,
                existing_metadata_df=exsisting_metadata_df,
                metadata_df=multimer_metadata_df,
                messages=messages,
            )
            for file_name in [
                amino_acid_sequences,
                cif_file,
                confidence_file,
                full_data_file,
                job_request_file,
            ]:
                success, msg = copy_file_to_directory(file_name, work_dir)
                if not success:
                    logger.error(msg)
                    messages.append(dict(level=logging.ERROR, msg=msg))

        fasta_dict = fasta_import(str(amino_acid_sequences))
        amino_acid_sequences_df = fasta_dict["fasta_df"]

        confidence_df = pd.read_json(confidence_file)
        job_request_df = pd.read_json(job_request_file)

        # full_data json has arrays of unequal lengths so we need to normalize
        full_data_df = pd.DataFrame()
        with open(full_data_file, "r") as f:
            full_data = json.load(f)
        if isinstance(full_data, dict):
            full_data_df = pd.json_normalize(full_data)
        else:
            messages.append(
                {
                    "level": logging.WARNING,
                    "msg": "Could not load full data Json",
                }
            )

        cif_df = read_alphafold_mmcif(cif_file)

        df_dict = {
            "structure_metadata_df": multimer_metadata_df,
            "cif_df": cif_df,
            "confidence_df": confidence_df,
            "full_data_df": full_data_df,
            "amino_acid_sequences_df": amino_acid_sequences_df,
            "job_request_df": job_request_df,
        }

        if not any(df.empty for df in df_dict.values()):

            unwrapped_full_data = unwrap_full_data_df(df_dict["full_data_df"])
            df_dict["full_data_df"] = unwrapped_full_data["full_data_df"]

            pae_matrix = OutputItem(
                output_type=OutputType.JOBLIB_ARTIFACT,
                value=unwrapped_full_data["pae_matrix"],
            )
            df_dict["pae_matrix"] = pae_matrix
            df_dict["plddt_df"] = get_plddt_from_cif(df_dict["cif_df"])

            data_for_visualization = {
                "structure_entry_id": entry_id,
                "cif_df": cif_df,
            }

            success_msg = f"Successfully loaded AlphaFold data for entry '{entry_id}'"
            logger.info(success_msg)
            messages.append(dict(level=logging.INFO, msg=success_msg))
        else:
            message = f"Could not load AlphaFold data for entry '{entry_id}'"
            logger.warning(message)
            messages.append(dict(level=logging.WARNING, msg=message))
            data_for_visualization = None

    finally:
        if temp_dir is not None:
            shutil.rmtree(temp_dir, ignore_errors=True)

    return dict(
        **df_dict,
        messages=messages,
        visualization=OutputItem(
            output_type=OutputType.VISUALIZATION, value=data_for_visualization
        ),
    )
