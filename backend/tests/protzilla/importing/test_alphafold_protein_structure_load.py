import pandas as pd
import pytest
import json
import logging
import shutil
from pathlib import Path


from backend.protzilla.importing.alphafold_protein_structure_load import (
    fetch_alphafold_protein_structure,
    to_fasta,
    read_alphafold_mmcif,
    get_all_available_entry_ids_of_monomer_metadata,
    get_all_available_entry_ids_of_multimer_metadata,
    get_monomer_structure_dfs,
    get_multimer_structure_dfs,
    get_monomer_metadata_df,
    get_multimer_metadata_df,
    get_correct_af_directories,
    extend_metadata_csv,
    get_amino_acid_sequences_df,
    handle_alphafold_files,
    upload_multimer_prediction,
    check_and_get_metadata_df,
    check_dir,
    get_json_files_in_dir,
    get_cif_df_from_disk,
    get_amino_acid_sequences_df_from_disk,
    check_success_of_get_df,
)
from backend.protzilla.constants import paths


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
        read_alphafold_mmcif(missing)


def test_read_alphafold_mmcif_is_directory(tmp_path):
    with pytest.raises(IsADirectoryError):
        read_alphafold_mmcif(tmp_path)


def test_read_alphafold_mmcif_empty(tmp_path):
    cif = tmp_path / "empty.cif"
    cif.write_text("")
    with pytest.raises(ValueError, match="No CIF blocks found"):
        read_alphafold_mmcif(cif)


def test_read_alphafold_mmcif_atom_site_not_found(tmp_path):
    cif = tmp_path / "no_atom_site.cif"
    cif.write_text(
        """
data_test
_entry.id test
"""
    )
    df = read_alphafold_mmcif(cif)
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

    df = read_alphafold_mmcif(cif)

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
        fetch_alphafold_protein_structure(uniprot_id="NOPROTEIN", persist_upload=True)


def test_fetch_alphafold_returned_keys(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "ALPHAFOLD_MONOMER_PATH", tmp_path / "alphafold_monomer")
    monkeypatch.setattr(
        paths,
        "AF_MONOMER_METADATA_CSV_PATH",
        tmp_path / "alphafold_monomer_metadata.csv",
    )

    out = fetch_alphafold_protein_structure("Q8WP00", persist_upload=True)
    assert out.keys() == {
        "structure_metadata_df",
        "cif_df",
        "pae_df",
        "plddt_df",
        "amino_acid_sequences_df",
        "messages",
    }


def test_fetch_alphafold_monomer_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "ALPHAFOLD_MONOMER_PATH", tmp_path / "alphafold_monomer")
    monkeypatch.setattr(
        paths,
        "AF_MONOMER_METADATA_CSV_PATH",
        tmp_path / "alphafold_monomer_metadata.csv",
    )
    out = fetch_alphafold_protein_structure("Q8WP00", persist_upload=True)

    assert isinstance(out["structure_metadata_df"], pd.DataFrame)
    assert not out["structure_metadata_df"].empty
    assert out["structure_metadata_df"].iloc[0]["uniprot_accession"] == "Q8WP00"
    assert (
        out["structure_metadata_df"].iloc[0]["model_created_date"]
        == "2025-08-01T00:00:00Z"
    )
    assert out["structure_metadata_df"].iloc[0]["gene"] == "PRM1"
    assert (
        out["structure_metadata_df"].iloc[0]["model_used"]
        == "AlphaFold Monomer v2.0 pipeline"
    )


def test_fetch_alphafold_files_exist(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "ALPHAFOLD_MONOMER_PATH", tmp_path / "alphafold_monomer")
    monkeypatch.setattr(
        paths,
        "AF_MONOMER_METADATA_CSV_PATH",
        tmp_path / "alphafold_monomer_metadata.csv",
    )

    fetch_alphafold_protein_structure("Q8WP00", persist_upload=True)

    target_dir = (tmp_path / "alphafold_monomer") / "Q8WP00"

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
    monkeypatch.setattr(paths, "ALPHAFOLD_MONOMER_PATH", tmp_path / "alphafold_monomer")
    monkeypatch.setattr(
        paths,
        "AF_MONOMER_METADATA_CSV_PATH",
        tmp_path / "alphafold_monomer_metadata.csv",
    )

    out = fetch_alphafold_protein_structure("Q8WP00", persist_upload=True)

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

    seq_df = out["amino_acid_sequences_df"]
    assert isinstance(seq_df, pd.DataFrame)
    assert not seq_df.empty


def test_get_all_available_entry_ids_empty(tmp_path, monkeypatch):
    metadata_csv = tmp_path / "alphafold_monomer_metadata.csv"
    monkeypatch.setattr(paths, "AF_MONOMER_METADATA_CSV_PATH", metadata_csv)

    assert get_all_available_entry_ids_of_monomer_metadata() == []
    assert metadata_csv.exists()

    df = pd.read_csv(metadata_csv, dtype=str)
    assert list(df.columns) == [
        "entry_id",
        "uniprot_accession",
        "model_created_date",
        "gene",
        "model_used",
    ]
    assert len(df) == 0


def test_get_all_available_entry_ids_nonempty(tmp_path, monkeypatch):
    metadata_csv = tmp_path / "alphafold_monomer_metadata.csv"
    monkeypatch.setattr(paths, "AF_MONOMER_METADATA_CSV_PATH", metadata_csv)
    df = pd.DataFrame([{"entry_id": "Q8WP00", "uniprot_accession": "Q8WP00"}])
    df.to_csv(metadata_csv, index=False)

    assert get_all_available_entry_ids_of_monomer_metadata() == ["Q8WP00"]


def test_get_prot_structure_dfs_no_entry(tmp_path, monkeypatch):
    metadata_csv = tmp_path / "alphafold_monomer_metadata.csv"
    monkeypatch.setattr(paths, "AF_MONOMER_METADATA_CSV_PATH", metadata_csv)
    pd.DataFrame([{"entry_id": "OTHER", "uniprot_accession": "OTHER"}]).to_csv(
        metadata_csv, index=False
    )

    with pytest.raises(ValueError, match=r"No metadata for Entry ID 'Q8WP00'"):
        get_monomer_structure_dfs("Q8WP00")


def test_get_prot_structure_dfs_success(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "ALPHAFOLD_MONOMER_PATH", tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    metadata_csv = tmp_path / "alphafold_monomer_metadata.csv"
    monkeypatch.setattr(paths, "AF_MONOMER_METADATA_CSV_PATH", metadata_csv)

    metadata = pd.DataFrame(
        [
            {
                "entry_id": "Q8WP00",
                "uniprot_accession": "Q8WP00",
                "model_created_date": "2025-08-01T00:00:00Z",
                "gene": "PRM1",
                "model_used": "AlphaFold Monomer v2.0 pipeline",
            }
        ]
    )
    metadata.to_csv(metadata_csv, index=False)

    prot_dir = tmp_path / "Q8WP00"
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

    out = get_monomer_structure_dfs("Q8WP00")

    assert isinstance(out["structure_metadata_df"], pd.DataFrame)
    assert not out["structure_metadata_df"].empty
    assert out["structure_metadata_df"].iloc[0]["entry_id"] == "Q8WP00"

    assert isinstance(out["cif_df"], pd.DataFrame)
    assert not out["cif_df"].empty
    assert list(out["cif_df"].columns) == [
        "_atom_site.id",
        "_atom_site.type_symbol",
        "_atom_site.Cartn_x",
    ]
    assert out["cif_df"]["_atom_site.id"].tolist() == ["N", "CA"]
    assert out["cif_df"]["_atom_site.type_symbol"].tolist() == ["N", "C"]
    assert out["cif_df"]["_atom_site.Cartn_x"].tolist() == ["1.0", "2.0"]

    assert isinstance(out["pae_df"], pd.DataFrame)
    assert not out["pae_df"].empty
    assert out["pae_df"]["predicted_aligned_error"].tolist() == [0.1]

    assert isinstance(out["plddt_df"], pd.DataFrame)
    assert not out["plddt_df"].empty
    assert out["plddt_df"]["residueNumber"].tolist() == [1]
    assert out["plddt_df"]["confidenceScore"].tolist() == [90]

    assert isinstance(out["amino_acid_sequences_df"], pd.DataFrame)
    assert not out["amino_acid_sequences_df"].empty
    assert out["amino_acid_sequences_df"]["Protein ID"].tolist() == ["Q8WP00-1"]
    assert out["amino_acid_sequences_df"]["Protein Sequence"].tolist() == ["AAAA"]

    assert any(d.get("level") == logging.INFO for d in out["messages"]) or any(
        "Successfully loaded" in d.get("msg", "") for d in out["messages"]
    )


def test_get_monomer_and_multimer_metadata_df_create(tmp_path, monkeypatch):
    mon_csv = tmp_path / "alphafold_monomer_metadata.csv"
    multi_csv = tmp_path / "alphafold_multimer_metadata.csv"
    monkeypatch.setattr(paths, "AF_MONOMER_METADATA_CSV_PATH", mon_csv)
    monkeypatch.setattr(paths, "AF_MULTIMER_METADATA_CSV_PATH", multi_csv)

    mon_df = get_monomer_metadata_df()
    assert isinstance(mon_df, pd.DataFrame)
    assert list(mon_df.columns) == [
        "entry_id",
        "uniprot_accession",
        "model_created_date",
        "gene",
        "model_used",
    ]
    assert mon_csv.exists()

    multi_df = get_multimer_metadata_df()
    assert isinstance(multi_df, pd.DataFrame)
    assert list(multi_df.columns) == [
        "entry_id",
        "uniprot_ids",
        "model_created_date",
        "model_used",
    ]
    assert multi_csv.exists()


def test_get_correct_af_directories_persist_and_temp(tmp_path):
    # persist_upload True
    temp, work = get_correct_af_directories("abc", tmp_path, True)
    assert temp is None
    assert work == tmp_path / "ABC"
    assert work.exists()

    # persist_upload False -> temporary directory created
    temp2, work2 = get_correct_af_directories("xyz", tmp_path, False)
    assert temp2 is not None
    assert Path(work2).exists()
    # cleanup
    shutil.rmtree(temp2, ignore_errors=True)


def test_extend_metadata_csv_overwrite_and_new(tmp_path):
    csv_path = tmp_path / "meta.csv"
    existing = pd.DataFrame([{"entry_id": "A", "x": "1"}, {"entry_id": "B", "x": "2"}])
    existing.to_csv(csv_path, index=False)

    messages = []
    new_md = pd.DataFrame([{"entry_id": "A", "x": "9"}])
    extend_metadata_csv("A", csv_path, existing, new_md, messages)
    out = pd.read_csv(csv_path, dtype=str)
    # entry A should be the updated one, B preserved
    assert set(out["entry_id"].tolist()) == {"A", "B"}
    assert out[out["entry_id"] == "A"]["x"].iloc[0] == "9"

    # when not present, should write only the provided metadata_df
    csv2 = tmp_path / "meta2.csv"
    messages2 = []
    extend_metadata_csv(
        "C",
        csv2,
        pd.DataFrame(columns=["entry_id"]),
        pd.DataFrame([{"entry_id": "C", "y": "7"}]),
        messages2,
    )
    out2 = pd.read_csv(csv2, dtype=str)
    assert out2.iloc[0]["entry_id"] == "C"


def test_get_amino_acid_sequences_df_and_handle_files(tmp_path, monkeypatch):
    # create a fasta and call get_amino_acid_sequences_df directly
    fasta = tmp_path / "P.fasta"
    fasta.write_text(">alpha|P\nTESTSEQ\n")
    messages = []
    seq_df = get_amino_acid_sequences_df(fasta, messages)
    assert isinstance(seq_df, pd.DataFrame)
    assert not seq_df.empty

    # test handle_alphafold_files with no remote files (should still create fasta)
    metadata_df = pd.DataFrame([{"entry_id": "P", "uniprot_accession": "P"}])
    out = handle_alphafold_files(
        {}, "P", "TESTSEQ", metadata_df, "P", persist_upload=False
    )
    assert "amino_acid_sequences_df" in out
    assert isinstance(out["cif_df"], pd.DataFrame) and out["cif_df"].empty
    assert isinstance(out["pae_df"], pd.DataFrame) and out["pae_df"].empty
    assert isinstance(out["plddt_df"], pd.DataFrame) and out["plddt_df"].empty
    assert isinstance(out["amino_acid_sequences_df"], pd.DataFrame)


def test_upload_multimer_prediction_basic(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "ALPHAFOLD_MULTIMER_PATH", tmp_path)

    # prepare files
    fasta = tmp_path / "seqs.fasta"
    fasta.write_text(">alpha|X\nAAAA\n")
    cif = tmp_path / "m.cif"
    cif.write_text(
        """
data_test
loop_
_atom_site.id
_atom_site.type_symbol
N N
"""
    )
    conf = tmp_path / "conf.json"
    conf.write_text('[{"residueNumber":1, "confidenceScore":99}]')
    full = tmp_path / "full.json"
    full.write_text('{"a": [1,2]}')

    # monkeypatch copy to actually copy files
    def _copy(src, dest_dir):
        target = Path(dest_dir) / Path(src).name
        shutil.copy(src, target)
        return True, ""

    monkeypatch.setattr(
        "backend.protzilla.importing.alphafold_protein_structure_load.copy_file_to_directory",
        _copy,
    )

    out = upload_multimer_prediction(
        entry_id="M1",
        uniprot_ids="X",
        model_used="m",
        amino_acid_sequences=fasta,
        cif_file=cif,
        confidence_file=conf,
        full_data_file=full,
        persist_upload=True,
    )

    assert isinstance(out["structure_metadata_df"], pd.DataFrame)
    # check metadata contents
    mdf = out["structure_metadata_df"]
    assert mdf.iloc[0]["entry_id"] == "M1"
    assert mdf.iloc[0]["uniprot_ids"] == ["X"]
    assert mdf.iloc[0]["model_used"] == "m"

    # cif contents
    cif_df = out["cif_df"]
    assert isinstance(cif_df, pd.DataFrame)
    assert list(cif_df.columns) == ["_atom_site.id", "_atom_site.type_symbol"]
    assert cif_df["_atom_site.id"].tolist() == ["N"]
    assert cif_df["_atom_site.type_symbol"].tolist() == ["N"]

    # confidence JSON
    conf_df = out["confidence_df"]
    assert isinstance(conf_df, pd.DataFrame)
    assert conf_df["residueNumber"].tolist() == [1]
    assert conf_df["confidenceScore"].tolist() == [99]

    # full data normalization
    full_df = out["full_data_df"]
    assert isinstance(full_df, pd.DataFrame)
    assert full_df.iloc[0]["a"] == [1, 2]

    # sequences
    seqs = out["amino_acid_sequences_df"]
    assert isinstance(seqs, pd.DataFrame)
    assert seqs["Protein Sequence"].tolist() == ["AAAA"]
    assert any(str(v).startswith("X") for v in seqs["Protein ID"].tolist())

    upload_dir = tmp_path / "M1"
    assert upload_dir.exists()
    assert any(upload_dir.glob("*.fasta")) or any(upload_dir.glob("*.fa"))
    assert any(upload_dir.glob("*.json"))
    assert any(upload_dir.glob("*.cif"))


# Additional comprehensive tests for error cases and edge cases


def test_get_monomer_metadata_df_existing_csv(tmp_path, monkeypatch):
    """Test reading existing monomer metadata CSV"""
    csv_path = tmp_path / "alphafold_monomer_metadata.csv"
    monkeypatch.setattr(paths, "AF_MONOMER_METADATA_CSV_PATH", csv_path)

    # create and write existing CSV
    existing_data = pd.DataFrame(
        [
            {
                "entry_id": "P1",
                "uniprot_accession": "P1",
                "model_created_date": "2025-01-01",
                "gene": "G1",
                "model_used": "m1",
            }
        ]
    )
    existing_data.to_csv(csv_path, index=False)

    # read it back
    df = get_monomer_metadata_df()
    assert len(df) == 1
    assert df.iloc[0]["entry_id"] == "P1"
    assert df.iloc[0]["gene"] == "G1"


def test_get_multimer_metadata_df_existing_csv(tmp_path, monkeypatch):
    """Test reading existing multimer metadata CSV"""
    csv_path = tmp_path / "alphafold_multimer_metadata.csv"
    monkeypatch.setattr(paths, "AF_MULTIMER_METADATA_CSV_PATH", csv_path)

    existing_data = pd.DataFrame(
        [
            {
                "entry_id": "M1",
                "uniprot_ids": "P1,P2",
                "model_created_date": "2025-01-01",
                "model_used": "m1",
            }
        ]
    )
    existing_data.to_csv(csv_path, index=False)

    df = get_multimer_metadata_df()
    assert len(df) == 1
    assert df.iloc[0]["entry_id"] == "M1"


def test_to_fasta_empty_sequence():
    """Test to_fasta with empty sequence"""
    with pytest.raises(
        ValueError, match="Sequence must be a single, whitespace-free string"
    ):
        to_fasta("")


def test_to_fasta_lowercase_conversion():
    """Test that lowercase sequences are converted to uppercase"""
    result = to_fasta("acdefg", "test", 10)
    assert "ACDEFG" in result
    assert "acdefg" not in result


def test_upload_multimer_prediction_no_persist(tmp_path, monkeypatch):
    """Test upload_multimer_prediction with persist_upload=False"""
    monkeypatch.setattr(paths, "ALPHAFOLD_MONOMER_PATH", tmp_path)
    monkeypatch.setattr(paths, "ALPHAFOLD_MULTIMER_PATH", tmp_path)

    fasta = tmp_path / "seqs.fasta"
    fasta.write_text(">alpha|X\nAAAA\n")
    cif = tmp_path / "m.cif"
    cif.write_text("data_test\nloop_\n_atom_site.id\nN\n")
    conf = tmp_path / "conf.json"
    conf.write_text('[{"residueNumber":1, "confidenceScore":99}]')
    full = tmp_path / "full.json"
    full.write_text('{"a": [1,2]}')

    out = upload_multimer_prediction(
        entry_id="M2",
        uniprot_ids="Y",
        model_used="test",
        amino_acid_sequences=fasta,
        cif_file=cif,
        confidence_file=conf,
        full_data_file=full,
        persist_upload=False,
    )

    # verify dataframes are returned
    assert isinstance(out["structure_metadata_df"], pd.DataFrame)
    assert isinstance(out["cif_df"], pd.DataFrame)
    # directory should still exist (created for the entry)
    upload_dir = tmp_path / "M2"
    assert not upload_dir.exists()


def test_get_prot_structure_dfs_missing_cif(tmp_path, monkeypatch):
    """Test get_prot_structure_dfs when CIF file is missing"""
    metadata_csv = tmp_path / "alphafold_monomer_metadata.csv"
    monkeypatch.setattr(paths, "AF_MONOMER_METADATA_CSV_PATH", metadata_csv)
    monkeypatch.setattr(paths, "ALPHAFOLD_MONOMER_PATH", tmp_path)

    metadata = pd.DataFrame([{"entry_id": "NOCIF", "uniprot_accession": "NOCIF"}])
    metadata.to_csv(metadata_csv, index=False)

    prot_dir = tmp_path / "NOCIF"
    prot_dir.mkdir(parents=True, exist_ok=True)

    with pytest.raises(FileNotFoundError, match="No CIF file found"):
        get_monomer_structure_dfs("NOCIF")


def test_get_prot_structure_dfs_missing_fasta(tmp_path, monkeypatch):
    """Test get_prot_structure_dfs when FASTA file is missing"""
    metadata_csv = tmp_path / "alphafold_monomer_metadata.csv"
    monkeypatch.setattr(paths, "AF_MONOMER_METADATA_CSV_PATH", metadata_csv)
    monkeypatch.setattr(paths, "ALPHAFOLD_MONOMER_PATH", tmp_path)

    metadata = pd.DataFrame([{"entry_id": "NOFASTA", "uniprot_accession": "NOFASTA"}])
    metadata.to_csv(metadata_csv, index=False)

    prot_dir = tmp_path / "NOFASTA"
    prot_dir.mkdir(parents=True, exist_ok=True)

    # create CIF but no FASTA
    cif = prot_dir / "test.cif"
    cif.write_text("data_test\nloop_\n_atom_site.id\nN\n")

    with pytest.raises(FileNotFoundError, match="No FASTA file found"):
        get_monomer_structure_dfs("NOFASTA")


def test_get_prot_structure_dfs_missing_json(tmp_path, monkeypatch):
    """Test get_prot_structure_dfs when JSON files are missing"""
    metadata_csv = tmp_path / "alphafold_monomer_metadata.csv"
    monkeypatch.setattr(paths, "AF_MONOMER_METADATA_CSV_PATH", metadata_csv)
    monkeypatch.setattr(paths, "ALPHAFOLD_MONOMER_PATH", tmp_path)

    metadata = pd.DataFrame([{"entry_id": "NOJSON", "uniprot_accession": "NOJSON"}])
    metadata.to_csv(metadata_csv, index=False)

    prot_dir = tmp_path / "NOJSON"
    prot_dir.mkdir(parents=True, exist_ok=True)

    # create CIF and FASTA but no JSON
    cif = prot_dir / "test.cif"
    cif.write_text("data_test\nloop_\n_atom_site.id\nN\n")

    fasta = prot_dir / "test.fasta"
    # valid header for parse_fasta_id (expects at least one "|" in the id)
    fasta.write_text(">alpha|NOJSON\nAAAA\n")

    with pytest.raises(FileNotFoundError, match="No JSON files"):
        get_monomer_structure_dfs("NOJSON")


def test_extend_metadata_csv_empty_existing(tmp_path):
    """Test extend_metadata_csv with empty existing DataFrame"""
    csv_path = tmp_path / "meta_empty.csv"
    existing = pd.DataFrame(columns=["entry_id", "x"])
    existing.to_csv(csv_path, index=False)

    messages = []
    new_md = pd.DataFrame([{"entry_id": "Z", "x": "new"}])
    extend_metadata_csv("Z", csv_path, existing, new_md, messages)

    out = pd.read_csv(csv_path, dtype=str)
    assert out.iloc[0]["entry_id"] == "Z"


def test_get_all_available_entry_ids_of_multimer_metadata_empty(tmp_path, monkeypatch):
    metadata_csv = tmp_path / "alphafold_multimer_metadata.csv"
    monkeypatch.setattr(paths, "AF_MULTIMER_METADATA_CSV_PATH", metadata_csv)

    assert get_all_available_entry_ids_of_multimer_metadata() == []
    assert metadata_csv.exists()

    df = pd.read_csv(metadata_csv, dtype=str)
    assert list(df.columns) == [
        "entry_id",
        "uniprot_ids",
        "model_created_date",
        "model_used",
    ]
    assert len(df) == 0


def test_get_all_available_entry_ids_of_multimer_metadata_nonempty(
    tmp_path, monkeypatch
):
    metadata_csv = tmp_path / "alphafold_multimer_metadata.csv"
    monkeypatch.setattr(paths, "AF_MULTIMER_METADATA_CSV_PATH", metadata_csv)

    df = pd.DataFrame(
        [
            {
                "entry_id": "M1",
                "uniprot_ids": "P1,P2",
                "model_created_date": "2025-01-01T00:00:00Z",
                "model_used": "test",
            }
        ]
    )
    df.to_csv(metadata_csv, index=False)

    assert get_all_available_entry_ids_of_multimer_metadata() == ["M1"]


def test_check_and_get_metadata_df_success(tmp_path):
    all_df = pd.DataFrame(
        [
            {"entry_id": "A", "x": "1"},
            {"entry_id": "B", "x": "2"},
        ]
    )
    out = check_and_get_metadata_df("B", all_df, tmp_path / "meta.csv")
    assert isinstance(out, pd.DataFrame)
    assert len(out) == 1
    assert out.iloc[0]["entry_id"] == "B"


def test_check_dir_missing_raises(tmp_path):
    d = tmp_path / "MISSING"
    with pytest.raises(FileNotFoundError, match="AlphaFold data directory not found"):
        check_dir("MISSING", d)


def test_get_json_files_in_dir_success(tmp_path):
    d = tmp_path / "D"
    d.mkdir()
    (d / "a.json").write_text('{"x": 1}')
    (d / "b.json").write_text('{"y": 2}')
    files = get_json_files_in_dir("E1", d)
    assert len(files) == 2
    assert all(f.suffix == ".json" for f in files)


def test_get_json_files_in_dir_missing_raises(tmp_path):
    d = tmp_path / "D"
    d.mkdir()
    with pytest.raises(FileNotFoundError, match="No JSON files found"):
        get_json_files_in_dir("E1", d)


def test_get_cif_df_from_disk_multiple_cif_warns(tmp_path):
    d = tmp_path / "E1"
    d.mkdir()

    cif1 = d / "a.cif"
    cif2 = d / "b.cif"
    cif1.write_text(
        """
data_test
loop_
_atom_site.id
_atom_site.type_symbol
N N
"""
    )
    cif2.write_text(
        """
data_test
loop_
_atom_site.id
_atom_site.type_symbol
CA C
"""
    )

    messages = []
    df = get_cif_df_from_disk("E1", d, messages)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert any(m.get("level") == logging.WARNING for m in messages)


def test_get_multimer_structure_dfs_success(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "ALPHAFOLD_MULTIMER_PATH", tmp_path / "multimer")
    monkeypatch.setattr(
        paths,
        "AF_MULTIMER_METADATA_CSV_PATH",
        tmp_path / "alphafold_multimer_metadata.csv",
    )

    paths.ALPHAFOLD_MULTIMER_PATH.mkdir(parents=True, exist_ok=True)

    md = pd.DataFrame(
        [
            {
                "entry_id": "M1",
                "uniprot_ids": "P1,P2",
                "model_created_date": "2025-01-01T00:00:00Z",
                "model_used": "Multimer",
            }
        ]
    )
    md.to_csv(paths.AF_MULTIMER_METADATA_CSV_PATH, index=False)

    prot_dir = paths.ALPHAFOLD_MULTIMER_PATH / "M1"
    prot_dir.mkdir(parents=True, exist_ok=True)

    cif = prot_dir / "m1.cif"
    cif.write_text(
        """
data_test
loop_
_atom_site.id
_atom_site.type_symbol
N N
"""
    )

    fasta = prot_dir / "m1.fasta"
    fasta.write_text(">alpha|M1\nAAAA\n")

    confidence = prot_dir / "confidence.json"
    full_data = prot_dir / "full.json"
    confidence.write_text(json.dumps({"chain_iptm": [0.75]}))
    full_data.write_text(json.dumps({"pae": [[0.1, 0.2], [0.3, 0.4]]}))

    out = get_multimer_structure_dfs("M1")
    assert isinstance(out["structure_metadata_df"], pd.DataFrame)
    assert isinstance(out["cif_df"], pd.DataFrame)
    assert isinstance(out["amino_acid_sequences_df"], pd.DataFrame)
    assert isinstance(out["confidence_df"], pd.DataFrame)
    assert isinstance(out["full_data_df"], pd.DataFrame)

    assert "chain_iptm" in out["confidence_df"].columns
    assert "pae" in out["full_data_df"].columns

    assert any(m.get("level") == logging.INFO for m in out["messages"]) or any(
        "Successfully loaded" in str(m.get("msg", "")) for m in out["messages"]
    )


def test_get_multimer_structure_dfs_json_fallback_warns(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "ALPHAFOLD_MULTIMER_PATH", tmp_path / "multimer")
    monkeypatch.setattr(
        paths,
        "AF_MULTIMER_METADATA_CSV_PATH",
        tmp_path / "alphafold_multimer_metadata.csv",
    )

    paths.ALPHAFOLD_MULTIMER_PATH.mkdir(parents=True, exist_ok=True)

    md = pd.DataFrame(
        [
            {
                "entry_id": "M2",
                "uniprot_ids": "P1,P2",
                "model_created_date": "2025-01-01T00:00:00Z",
                "model_used": "Multimer",
            }
        ]
    )
    md.to_csv(paths.AF_MULTIMER_METADATA_CSV_PATH, index=False)

    prot_dir = paths.ALPHAFOLD_MULTIMER_PATH / "M2"
    prot_dir.mkdir(parents=True, exist_ok=True)

    cif = prot_dir / "m2.cif"
    cif.write_text(
        """
data_test
loop_
_atom_site.id
_atom_site.type_symbol
N N
"""
    )

    fasta = prot_dir / "m2.fasta"
    fasta.write_text(">alpha|M2\nAAAA\n")

    j1 = prot_dir / "j1.json"
    j2 = prot_dir / "j2.json"
    j1.write_text(json.dumps({"something": 1}))
    j2.write_text(json.dumps({"other": 2}))

    out = get_multimer_structure_dfs("M2")
    assert any(m.get("level") == logging.WARNING for m in out["messages"])
    assert any(
        "Could not detect confidence scores" in str(m.get("msg", ""))
        for m in out["messages"]
    )
