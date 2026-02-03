import pandas as pd
import pytest
from pathlib import Path
import json
import logging


from backend.protzilla.importing.alphafold_protein_structure_load import (
    fetch_alphafold_protein_structure,
    to_fasta,
    read_alphafold_mmcif,
    get_all_available_entry_ids,
    get_prot_structure_dfs,
    paths,
)


def test_to_fasta_default_header_and_newline():
    seq = "A" * 130
    out = to_fasta(seq, "test_id", 60)

    expected = (
        ">alpha|test_id\n" + ("A" * 60) + "\n" + ("A" * 60) + "\n" + ("A" * 10) + "\n"
    )
    assert out == expected


def test_to_fasta_invalid_characters():
    with pytest.raises(ValueError, match=r"Invalid characters in sequence: 01@"):
        to_fasta("AbbC@D1Eeff0")


def test_to_fasta_whitespace():
    with pytest.raises(
        ValueError, match=r"Sequence must be a single, whitespace-free string."
    ):
        to_fasta(" ")


def test_read_alphafold_mmcif_file_not_found(tmp_path):
    missing = tmp_path / "unexisting.cif"
    with pytest.raises(FileNotFoundError):
        read_alphafold_mmcif(str(missing))


def test_read_alphafold_mmcif_is_directory(tmp_path):
    with pytest.raises(IsADirectoryError):
        read_alphafold_mmcif(str(tmp_path))


def test_read_alphafold_mmcif_empty(tmp_path):
    cif = tmp_path / "empty.cif"
    cif.write_text("")
    with pytest.raises(ValueError, match="No CIF blocks found"):
        read_alphafold_mmcif(str(cif))


def test_read_alphafold_mmcif_atom_site_not_found(tmp_path):
    cif = tmp_path / "no_atom_site.cif"
    cif.write_text(
        """
data_test
_entry.id test
"""
    )
    df = read_alphafold_mmcif(str(cif))
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_read_alphafold_mmcif_valid_atom_site(tmp_path):
    cif = tmp_path / "atom_site.cif"
    cif.write_text(
        """
data_test
loop_
_atom_site.id
_atom_site.type_symbol
_atom_site.Cartn_x
N N 1.0
CA C 2.0
"""
    )

    df = read_alphafold_mmcif(str(cif))

    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == [
        "_atom_site.id",
        "_atom_site.type_symbol",
        "_atom_site.Cartn_x",
    ]
    assert len(df) == 2
    assert df["_atom_site.id"].tolist() == ["N", "CA"]
    assert df["_atom_site.type_symbol"].tolist() == ["N", "C"]
    assert df["_atom_site.Cartn_x"].tolist() == ["1.0", "2.0"]


def test_fetch_alphafold_protein_structure_wrong_uniprot_id():
    with pytest.raises(RuntimeError, match="AlphaFold request failed for NOPROTEIN"):
        fetch_alphafold_protein_structure(uniprot_id="NOPROTEIN", persist_uploads=True)


def test_fetch_alphafold_returned_keys(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "EXTERNAL_DATA_PATH", tmp_path)

    out = fetch_alphafold_protein_structure("Q8WP00", persist_uploads=True)
    assert out.keys() == {
        "metadata_df",
        "cif_df",
        "pae_df",
        "plddt_df",
        "sequence_df",
        "messages",
    }


def test_fetch_alphafold_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "EXTERNAL_DATA_PATH", tmp_path)
    out = fetch_alphafold_protein_structure("Q8WP00", persist_uploads=True)

    assert isinstance(out["metadata_df"], pd.DataFrame)
    assert not out["metadata_df"].empty
    assert out["metadata_df"].iloc[0]["uniprotAccession"] == "Q8WP00"
    assert out["metadata_df"].iloc[0]["modelCreatedDate"] == "2025-08-01T00:00:00Z"
    assert out["metadata_df"].iloc[0]["gene"] == "PRM1"
    assert (
        out["metadata_df"].iloc[0]["alphafold_version"]
        == "AlphaFold Monomer v2.0 pipeline"
    )


def test_fetch_alphafold_files_exist(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "EXTERNAL_DATA_PATH", tmp_path)
    fetch_alphafold_protein_structure("Q8WP00", persist_uploads=True)

    target_dir = tmp_path / "alphafold" / "Q8WP00"
    assert target_dir.exists()
    assert target_dir.is_dir()

    fasta_path = target_dir / "Q8WP00.fasta"
    assert fasta_path.exists()
    assert fasta_path.stat().st_size > 0

    cif_files = sorted(target_dir.glob("*.cif"))
    json_files = sorted(target_dir.glob("*.json"))

    # one mmCif file, confidence json and predicted aligned error
    assert len(cif_files) == 1
    assert len(json_files) == 2


def test_fetch_alphafold_dfs_exist(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "EXTERNAL_DATA_PATH", tmp_path)
    out = fetch_alphafold_protein_structure("Q8WP00", persist_uploads=True)

    cif_df = out["cif_df"]
    assert isinstance(cif_df, pd.DataFrame)
    assert not cif_df.empty
    assert any(col.startswith("_atom_site.") for col in cif_df.columns)

    pae_df = out["pae_df"]
    assert isinstance(pae_df, pd.DataFrame)
    assert not pae_df.empty

    plddt_df = out["plddt_df"]
    assert isinstance(plddt_df, pd.DataFrame)
    assert not plddt_df.empty

    seq_df = out["sequence_df"]
    assert isinstance(seq_df, pd.DataFrame)
    assert not seq_df.empty


def test_get_all_available_entry_ids_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "EXTERNAL_DATA_PATH", tmp_path)
    assert get_all_available_entry_ids() == []


def test_get_all_available_entry_ids_nonempty(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "EXTERNAL_DATA_PATH", tmp_path)
    meta_dir = tmp_path / "alphafold"
    meta_dir.mkdir(parents=True, exist_ok=True)
    csv = meta_dir / "alphafold_metadata.csv"
    df = pd.DataFrame([{"entryID": "Q8WP00", "uniprotAccession": "Q8WP00"}])
    df.to_csv(csv, index=False)

    assert get_all_available_entry_ids() == ["Q8WP00"]


def test_get_prot_structure_dfs_no_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "EXTERNAL_DATA_PATH", tmp_path)
    with pytest.raises(FileNotFoundError, match=r"AlphaFold metadata CSV not found"):
        get_prot_structure_dfs("Q8WP00")


def test_get_prot_structure_dfs_no_entry(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "EXTERNAL_DATA_PATH", tmp_path)
    meta_dir = tmp_path / "alphafold"
    meta_dir.mkdir(parents=True, exist_ok=True)
    csv = meta_dir / "alphafold_metadata.csv"
    pd.DataFrame([{"entryID": "OTHER", "uniprotAccession": "OTHER"}]).to_csv(
        csv, index=False
    )

    with pytest.raises(ValueError, match=r"No metadata for entryID 'Q8WP00'"):
        get_prot_structure_dfs("Q8WP00")


def test_get_prot_structure_dfs_missing_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "EXTERNAL_DATA_PATH", tmp_path)
    meta_dir = tmp_path / "alphafold"
    meta_dir.mkdir(parents=True, exist_ok=True)
    csv = meta_dir / "alphafold_metadata.csv"
    pd.DataFrame([{"entryID": "Q8WP00", "uniprotAccession": "Q8WP00"}]).to_csv(
        csv, index=False
    )

    with pytest.raises(FileNotFoundError, match=r"AlphaFold data directory not found"):
        get_prot_structure_dfs("Q8WP00")


def test_get_prot_structure_dfs_success(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "EXTERNAL_DATA_PATH", tmp_path)

    meta_dir = tmp_path / "alphafold"
    meta_dir.mkdir(parents=True, exist_ok=True)
    csv = meta_dir / "alphafold_metadata.csv"

    metadata = pd.DataFrame(
        [
            {
                "entryID": "Q8WP00",
                "uniprotAccession": "Q8WP00",
                "modelCreatedDate": "2025-08-01T00:00:00Z",
                "gene": "PRM1",
                "alphafold_version": "AlphaFold Monomer v2.0 pipeline",
            }
        ]
    )
    metadata.to_csv(csv, index=False)

    prot_dir = meta_dir / "Q8WP00"
    prot_dir.mkdir(parents=True, exist_ok=True)

    cif = prot_dir / "test.cif"
    cif.write_text(
        """
data_test
loop_
_atom_site.id
_atom_site.type_symbol
_atom_site.Cartn_x
N N 1.0
CA C 2.0
"""
    )

    fasta = prot_dir / "Q8WP00.fasta"
    fasta.write_text(">alpha|Q8WP00\nAAAA\n")

    pae = prot_dir / "pae.json"
    plddt = prot_dir / "plddt.json"
    pae_data = {"predicted_aligned_error": [0.1]}
    with open(pae, "w") as f:
        json.dump(pae_data, f)

    plddt_data = [{"residueNumber": 1, "confidenceScore": 90}]
    with open(plddt, "w") as f:
        json.dump(plddt_data, f)

    out = get_prot_structure_dfs("Q8WP00")

    assert isinstance(out["metadata_df"], pd.DataFrame)
    assert not out["metadata_df"].empty
    assert out["metadata_df"].iloc[0]["entryID"] == "Q8WP00"

    assert isinstance(out["cif_df"], pd.DataFrame)
    assert not out["cif_df"].empty

    assert isinstance(out["pae_df"], pd.DataFrame)
    assert not out["pae_df"].empty

    assert isinstance(out["plddt_df"], pd.DataFrame)
    assert not out["plddt_df"].empty

    assert isinstance(out["sequence_df"], pd.DataFrame)
    assert not out["sequence_df"].empty

    assert any(d.get("level") == logging.INFO for d in out["messages"]) or any(
        "Successfully loaded" in d.get("msg", "") for d in out["messages"]
    )
