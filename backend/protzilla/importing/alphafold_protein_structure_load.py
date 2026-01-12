from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import requests

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


def fetch_alphafold_protein_structure(uniprot: str) -> dict[str, Any]:
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
            "entryId": r.get("entryId"),
            "uniprotAccession": r.get("uniprotAccession"),
            "uniprotId": r.get("uniprotId"),
            "modelCreatedDate": r.get("modelCreatedDate"),
            "latestVersion": r.get("latestVersion"),
            "uniprotStart": r.get("uniprotStart"),
            "uniprotEnd": r.get("uniprotEnd"),
            "sequenceLength": (
                len(r["uniprotSequence"])
                if isinstance(r.get("uniprotSequence"), str)
                else None
            ),
        }

        for key in ("pdbUrl", "cifUrl", "paeDocUrl", "plddtDocUrl"):
            if isinstance(r.get(key), str) and r.get(key):
                data[key] = r[key]

        # prefer reading the existing AlphaFold metadata CSV into the dataframe
        meta_dir = paths.EXTERNAL_DATA_PATH / "alphafold"
        meta_dir.mkdir(parents=True, exist_ok=True)
        metadata_csv = meta_dir / "alphafold_metadata.csv"

        new_row = pd.DataFrame([data])
        try:
            if metadata_csv.exists():
                existing = pd.read_csv(metadata_csv, dtype=str)
                acc = data.get("uniprotAccession")
                if acc and "uniprotAccession" in existing.columns:
                    existing = existing[existing["uniprotAccession"] != acc]
                combined = pd.concat([existing, new_row], ignore_index=True)
            else:
                combined = new_row

            combined.to_csv(metadata_csv, index=False)
            logger.info("Wrote AlphaFold metadata to %s", metadata_csv)
            alphafold_df = combined
        except Exception:
            logger.exception(
                "Failed to write AlphaFold metadata CSV to %s", metadata_csv
            )
            alphafold_df = new_row

        downloaded: dict[str, str] = {}

        target_dir = meta_dir / (data.get("uniprotAccession") or uniprot)
        for key in ("cifUrl", "pdbUrl", "paeDocUrl", "plddtDocUrl"):
            urlval = data.get(key)
            if isinstance(urlval, str) and urlval:
                fname = urlval.split("?")[0].rstrip("/").split("/")[-1]
                dest = target_dir / fname
                saved = _download_file(session, urlval, dest)
                if saved:
                    downloaded[key] = str(saved)

        return {
            "alphafold_df": alphafold_df,
            "metadata_csv": str(metadata_csv),
            "downloaded_files": downloaded,
        }
