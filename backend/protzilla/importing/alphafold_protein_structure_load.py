from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from textwrap import wrap
from typing import Any

import gemmi
import pandas as pd
import requests

from backend.protzilla.constants import paths
from backend.protzilla.constants.protzilla_logging import logger


def _download_file(session: requests.Session, url: str, dest: Path) -> Path | None:
    """
    Download a file from a URL and save it to the specified destination path.

    :param session: The requests session to use for the download
    :param url: The URL of the file to download
    :param dest: The destination path where the file should be saved
    :return: The destination path if successful, None otherwise
    """
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        with session.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        logger.info("Downloaded %s -> %s", url, dest)
        return dest
    except requests.RequestException:
        logger.exception("Failed to download %s", url)
        return None
    except OSError:
        logger.exception("Failed to write file %s", dest)
        return None


def to_fasta(seq: str, header: str = "protein_sequence", width: int = 60) -> str:
    """
    Convert a protein sequence to FASTA format.

    :param seq: The protein sequence to convert
    :param header: The header line for the FASTA record (default: "protein_sequence")
    :param width: The maximum line width for sequence wrapping (default: 60)
    :return: The sequence in FASTA format
    :raises ValueError: If the sequence contains invalid characters or whitespace
    """
    VALID_AA = set("ACDEFGHIKLMNPQRSTVWYBXZJUO*-")
    if not seq or any(c.isspace() for c in seq):
        raise ValueError("Sequence must be a single, whitespace-free string.")
    seq = seq.upper()
    bad = set(seq) - VALID_AA
    if bad:
        raise ValueError(f"Invalid characters in sequence: {''.join(sorted(bad))}")
    return ">" + header + "\n" + "\n".join(wrap(seq, width)) + "\n"


def fasta_to_dataframe(fasta_path: str) -> pd.DataFrame:
    """
    Parse a FASTA file and convert it to a DataFrame.

    :param fasta_path: The path to the FASTA file
    :return: A DataFrame with columns 'id', 'sequence', and 'length'
    """
    records = []
    seq_id = None
    seq = []

    with open(fasta_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if seq_id is not None:
                    sequence = "".join(seq)
                    records.append(
                        {
                            "id": seq_id,
                            "sequence": sequence,
                            "length": len(sequence),
                        }
                    )
                seq_id = line[1:].split()[0]
                seq = []
            else:
                seq.append(line)

        if seq_id is not None:
            sequence = "".join(seq)
            records.append(
                {
                    "id": seq_id,
                    "sequence": sequence,
                    "length": len(sequence),
                }
            )

    return pd.DataFrame(records)


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


def _handle_alphafold_files(
    session: requests.Session,
    files_urls: dict[str, Any],
    uniprot: str,
    seq: str,
    metadata_df: pd.DataFrame,
    acc: str,
    persist_upload: bool = False,
) -> tuple[
    pd.DataFrame | None,
    pd.DataFrame | None,
    pd.DataFrame | None,
    pd.DataFrame | None,
]:
    """
    Download AlphaFold structure files and convert them to DataFrames.

    Files can either be persistently saved to disk or only loaded into memory for the current run.
    The function downloads CIF, PAE, and pLDDT files, converts them to DataFrames, and optionally
    saves metadata to a CSV file.

    :param session: The requests session to use for downloading files
    :param files_urls: Dictionary containing URLs for CIF, PAE, and pLDDT files
    :param uniprot: The UniProt ID of the protein
    :param seq: The protein sequence
    :param metadata_df: DataFrame containing AlphaFold metadata
    :param acc: The accession number (used for directory naming)
    :param persist_upload: If True, files are saved persistently; if False, only loaded into memory
    :return: Tuple of (cif_df, pae_df, plddt_df, sequence_df) or None values for failed loads
    """
    cif_df = None
    pae_df = None
    plddt_df = None
    sequence_df = None

    meta_dir = paths.EXTERNAL_DATA_PATH / "alphafold"
    target_dir = meta_dir / (acc or uniprot)
    downloaded: dict[str, str] = {}

    temp_dir = None
    work_dir = target_dir

    if persist_upload:
        target_dir.mkdir(parents=True, exist_ok=True)
    else:
        temp_dir = Path(tempfile.mkdtemp())
        work_dir = temp_dir

    try:
        if persist_upload and metadata_df is not None:
            meta_dir.mkdir(parents=True, exist_ok=True)
            metadata_csv = meta_dir / "alphafold_metadata.csv"
            try:
                if metadata_csv.exists():
                    existing = pd.read_csv(metadata_csv, dtype=str)
                    if acc and "uniprotAccession" in existing.columns:
                        existing = existing[existing["uniprotAccession"] != acc]
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
                saved = _download_file(session, urlval, dest)
                if saved:
                    downloaded[key] = str(saved)
                    try:
                        if key == "cifUrl":
                            try:
                                cif_df = read_alphafold_mmcif(str(saved))
                            except Exception:
                                logger.exception(
                                    "Failed to load CIF into dataframe. Path=%s",
                                    str(saved),
                                )
                                raise
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
            sequence_df = fasta_to_dataframe(str(fasta_dest))
        except OSError:
            logger.exception("Failed to write FASTA file %s", fasta_dest)
        except Exception:
            logger.exception("Failed to create sequence dataframe")

    finally:
        if temp_dir is not None:
            shutil.rmtree(temp_dir, ignore_errors=True)

    return cif_df, pae_df, plddt_df, sequence_df


def fetch_alphafold_protein_structure(
    uniprot: str, persist_uploads: bool
) -> dict[str, Any]:
    """
    Fetch AlphaFold protein structure data from the AlphaFold Database API.

    Retrieves metadata and structure files (CIF, PAE, pLDDT) from the AlphaFold Database
    for the given UniProt ID. Optionally persists the downloaded files to disk.

    :param uniprot: The UniProt ID of the protein
    :param persist_uploads: If True, files are saved persistently; if False, only loaded into memory
    :return: A dictionary containing DataFrames for metadata, CIF, PAE, pLDDT, and sequence data
    :raises RuntimeError: If the API request fails or returns invalid data
    :raises ValueError: If no predictions are found for the given UniProt ID
    """
    url = f"https://alphafold.ebi.ac.uk/api/prediction/{uniprot}"
    with requests.Session() as session:
        try:
            resp = session.get(url, timeout=30)
            resp.raise_for_status()
            records = resp.json()
        except requests.RequestException as e:
            raise RuntimeError(f"AlphaFold request failed for {uniprot}: {e}") from e
        except ValueError as e:
            raise RuntimeError(f"AlphaFold returned non-JSON for {uniprot}: {e}") from e

        if not isinstance(records, list) or not records:
            raise ValueError(f"No AlphaFold DB predictions for {uniprot}")

        r = records[0]
        if not isinstance(r, dict):
            raise RuntimeError(f"Unexpected AlphaFold payload for {uniprot}")

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
        acc = data.get("uniprotAccession")

        cif_df, pae_df, plddt_df, sequence_df = _handle_alphafold_files(
            session=session,
            files_urls=files_urls,
            uniprot=uniprot,
            seq=seq_tmp,
            metadata_df=metadata_df,
            acc=acc,
            persist_upload=persist_uploads,
        )

        return {
            "metadata_df": metadata_df,
            "cif_df": cif_df,
            "pae_df": pae_df,
            "plddt_df": plddt_df,
            "sequence_df": sequence_df,
        }
