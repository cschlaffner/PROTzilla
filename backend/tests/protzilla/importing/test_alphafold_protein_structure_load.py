import pandas as pd
import pytest
from pathlib import Path


from backend.protzilla.importing.alphafold_protein_structure_load import (
    fetch_alphafold_protein_structure,
    to_fasta,
    read_alphafold_mmcif,
)
import backend.protzilla.importing.alphafold_protein_structure_load as af


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
    monkeypatch.setattr(af.paths, "EXTERNAL_DATA_PATH", tmp_path)

    out = af.fetch_alphafold_protein_structure("Q8WP00", persist_uploads=True)
    assert set(out.keys()).issuperset(
        {
            "metadata_df",
            "cif_df",
            "pae_df",
            "plddt_df",
            "sequence_df",
        }
    )


def test_fetch_alphafold_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(af.paths, "EXTERNAL_DATA_PATH", tmp_path)
    out = af.fetch_alphafold_protein_structure("Q8WP00", persist_uploads=True)

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
    monkeypatch.setattr(af.paths, "EXTERNAL_DATA_PATH", tmp_path)
    af.fetch_alphafold_protein_structure("Q8WP00", persist_uploads=True)

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
    monkeypatch.setattr(af.paths, "EXTERNAL_DATA_PATH", tmp_path)
    out = af.fetch_alphafold_protein_structure("Q8WP00", persist_uploads=True)

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
