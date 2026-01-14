from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import requests
from textwrap import wrap
from CifFile import ReadCif
import shutil
import tempfile


from backend.protzilla.constants import paths
from backend.protzilla.constants.protzilla_logging import logger


def _download_file(session: requests.Session, url: str, dest: Path) -> Path | None:
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
    VALID_AA = set("ACDEFGHIKLMNPQRSTVWYBXZJUO*-")
    if not seq or any(c.isspace() for c in seq):
        raise ValueError("Sequence must be a single, whitespace-free string.")
    seq = seq.upper()
    bad = set(seq) - VALID_AA
    if bad:
        raise ValueError(f"Invalid characters in sequence: {''.join(sorted(bad))}")
    return ">" + header + "\n" + "\n".join(wrap(seq, width)) + "\n"


def fasta_to_dataframe(fasta_path: str):
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
                    records.append({
                        "id": seq_id,
                        "sequence": sequence,
                        "length": len(sequence),
                    })
                seq_id = line[1:].split()[0]
                seq = []
            else:
                seq.append(line)

        if seq_id is not None:
            sequence = "".join(seq)
            records.append({
                "id": seq_id,
                "sequence": sequence,
                "length": len(sequence),
            })

    return pd.DataFrame(records)


def cif_to_dataframe(cif_path):
    cif = ReadCif(str(cif_path))
    block = cif.first_block()

    df = pd.DataFrame({
        "label": block["_atom_site_label"],
        "element": block["_atom_site_type_symbol"],
        "x": block["_atom_site_fract_x"],
        "y": block["_atom_site_fract_y"],
        "z": block["_atom_site_fract_z"],
    })

    return df


def _handle_alphafold_files(
    session: requests.Session,
    files_urls: dict[str, Any],
    uniprot: str,
    seq: str,
    metadata_df: pd.DataFrame,
    acc: str,
    persist_upload: bool = False,
) -> tuple[
    dict[str, str],
    Path,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    """
    Either the files are persistently saved on disk and loaded into dataframes or only loaded into dataframes to be used only for the current run.
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
                            cif_df = cif_to_dataframe(saved)
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


def fetch_alphafold_protein_structure(uniprot: str, persistUploads: bool,) -> dict[str, Any]:
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

        cif_df, pae_df, plddt_df, sequence_df = _handle_alphafold_files(session=session, files_urls=files_urls, uniprot=uniprot, seq=seq_tmp, metadata_df=metadata_df, acc=acc, persist_upload=persistUploads)
        

        return {
            "metadata_df": metadata_df,
            "cif_df": cif_df,
            "pae_df": pae_df,
            "plddt_df": plddt_df,
            "sequence_df": sequence_df,
        }
