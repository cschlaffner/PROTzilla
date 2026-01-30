from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from textwrap import wrap
from typing import Any
import logging

import gemmi
import pandas as pd
import requests

from backend.protzilla.constants import paths
from backend.protzilla.constants.protzilla_logging import logger
from backend.protzilla.importing.fasta_import import fasta_import
from backend.protzilla.networking import download_file_from_url


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
    if table is None:
        return pd.DataFrame()

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


def handle_alphafold_files(
    files_urls: dict[str, Any],
    uniprot: str,
    seq: str,
    metadata_df: pd.DataFrame,
    entry_id: str,
    persist_uploads: bool = False,
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
    :param persist_uploads: If True, files are saved persistently; if False, only loaded into memory
    :return: A dictionary containing DataFrames for metadata, CIF, PAE, pLDDT, sequence data or None values for
    failed loads and messages such as warnings
    """
    cif_df = None
    pae_df = None
    plddt_df = None
    sequence_df = None
    messages = []

    meta_dir = paths.EXTERNAL_DATA_PATH / "alphafold"
    target_dir = meta_dir / uniprot
    downloaded: dict[str, str] = {}

    temp_dir = None

    if persist_uploads:
        target_dir.mkdir(parents=True, exist_ok=True)
        work_dir = target_dir
    else:
        temp_dir = Path(tempfile.mkdtemp())
        work_dir = temp_dir

    try:
        if persist_uploads and metadata_df is not None:
            meta_dir.mkdir(parents=True, exist_ok=True)
            metadata_csv = meta_dir / "alphafold_metadata.csv"
            try:
                if metadata_csv.exists():
                    existing = pd.read_csv(metadata_csv, dtype=str)
                    mask = existing["entryID"] == entry_id
                    if mask.any():
                        msg = (
                            f'Existing entry with EntryID "{entry_id}" was overwritten.'
                        )
                        logger.warning(msg)
                        messages.append(dict(level=logging.WARNING, msg=msg))
                        existing = existing[~mask]

                    combined = pd.concat([existing, metadata_df], ignore_index=True)
                    combined.to_csv(metadata_csv, index=False)
                else:
                    metadata_df.to_csv(metadata_csv, index=False)
                logger.info("Wrote AlphaFold metadata to %s", metadata_csv)
            except Exception:
                logger.exception(
                    "Failed to write AlphaFold metadata CSV to %s", metadata_csv
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
                        logger.exception("Failed to load %s into dataframe", key)

        sequence = to_fasta(seq=seq, header=uniprot)
        fasta_dest = work_dir / f"{uniprot.upper()}.fasta"
        try:
            fasta_dest.parent.mkdir(parents=True, exist_ok=True)
            with open(fasta_dest, "w") as f:
                f.write(sequence)
            logger.info("Wrote FASTA sequence to %s", fasta_dest)
            fasta_dict = fasta_import(str(fasta_dest))
            sequence_df = fasta_dict["fasta_df"]
        except OSError:
            logger.exception("Failed to write FASTA file %s", fasta_dest)
        except Exception:
            logger.exception("Failed to create sequence dataframe")

    finally:
        if temp_dir is not None:
            shutil.rmtree(temp_dir, ignore_errors=True)

    return {
        "cif_df": cif_df,
        "pae_df": pae_df,
        "plddt_df": plddt_df,
        "sequence_df": sequence_df,
        "messages": messages,
    }


def fetch_alphafold_protein_structure(
    uniprot_id: str, persist_uploads: bool
) -> dict[str, Any]:
    """
    Fetch AlphaFold protein structure data from the AlphaFold Database API.

    Retrieves metadata and structure files (CIF, PAE, pLDDT) from the AlphaFold Database
    for the given UniProt ID. Optionally persists the downloaded files to disk.

    :param uniprot_id: The UniProt ID of the protein
    :param persist_uploads: If True, files are saved persistently; if False, only loaded into memory
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
            "entryID": r.get("uniprotAccession"),
            "uniprotAccession": r.get("uniprotAccession"),
            "modelCreatedDate": r.get("modelCreatedDate"),
            "gene": r.get("gene"),
            "alphafold_version": r.get("toolUsed"),
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
            persist_uploads=persist_uploads,
        )

        return {
            "metadata_df": metadata_df,
            "cif_df": alpha_dfs["cif_df"],
            "pae_df": alpha_dfs["pae_df"],
            "plddt_df": alpha_dfs["plddt_df"],
            "sequence_df": alpha_dfs["sequence_df"],
            "messages": alpha_dfs.get("messages", []),
        }
