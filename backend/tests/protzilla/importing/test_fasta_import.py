import logging

import pytest
import pandas as pd
import requests

from backend.protzilla.constants.data_types import DataKey
from backend.protzilla.importing.fasta_import import (
    fasta_generation,
    parse_fasta_id,
    fasta_import,
)
from backend.tests.paths import TEST_FASTA_PATH


def test_parse_fasta_id():
    protein_id = "P14136-1"
    valid_fasta_id = (
        f">sp|{protein_id}|GFAP_HUMAN Isoform 1 of Glial fibrillary acidic protein OS=Homo sapiens "
        "OX=9606 GN=GFAP; "
    )
    metadata = parse_fasta_id(valid_fasta_id)
    assert metadata == protein_id

    invalid_fasta_id = ">sp"
    with pytest.raises(
        ValueError,
        match="Fasta file metadata is invalid. It has to include a protein id",
    ):
        parse_fasta_id(invalid_fasta_id)


@pytest.mark.parametrize(
    "fasta_file,protein_id",
    [
        (TEST_FASTA_PATH / "uniprotkb_P14136.fasta", ["P14136-1", "P14136-3"]),
        (
            TEST_FASTA_PATH / "uniprotkb_P10636.fasta",
            ["P10636-1", "P10636-6"],
        ),
        (TEST_FASTA_PATH / "malformed.fasta", ["P14136-1", "P14136-3"]),
    ],
)
def test_fasta_import(fasta_file, protein_id):
    output = fasta_import(fasta_file)
    assert DataKey.FASTA_DF in output
    assert set(output[DataKey.FASTA_DF]["Protein ID"]) == set(protein_id)


def test_import_of_malformed_fasta():
    malformed_fasta_file = TEST_FASTA_PATH / "even_more_malformed.fasta"
    with pytest.raises(
        ValueError,
        match="Fasta file metadata is invalid. It has to include a protein id",
    ):
        fasta_import(malformed_fasta_file)


def test_import_empty_fasta():
    empty_fasta_file = TEST_FASTA_PATH / "empty.fasta"
    with pytest.raises(ValueError, match="The provided fasta file is empty."):
        fasta_import(empty_fasta_file)


def test_import_fasta_with_no_sequences():
    no_sequences_fasta_file = TEST_FASTA_PATH / "no_sequences.fasta"
    with pytest.raises(
        ValueError,
        match="The provided fasta file does not contain protein sequences for all of the protein ids.",
    ):
        fasta_import(no_sequences_fasta_file)


@pytest.fixture
def mock_uniprot(monkeypatch):
    sequences = {
        "Protein1": "ABC",
        "Protein2": "XY",
    }

    def mock_get(url, timeout):
        requested_ids = url.split("accessions=")[1].split("&")[0].split(",")

        fasta = ""
        for protein_id in requested_ids:
            if protein_id in sequences:
                fasta += f">sp|{protein_id}|mock_protein\n" f"{sequences[protein_id]}\n"

        class MockResponse:
            status_code = 200
            text = fasta

        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)


def test_basic_fasta_generation(mock_uniprot):
    output = fasta_generation(pd.DataFrame({"Protein ID": ["Protein1"]}))
    generated_fasta_df: pd.DataFrame = output["fasta_df"]
    assert len(generated_fasta_df) == 1
    assert list(generated_fasta_df.columns) == ["Protein ID", "Protein Sequence"]
    assert generated_fasta_df["Protein ID"].iloc[0] == "Protein1-1"
    assert generated_fasta_df["Protein Sequence"].iloc[0] == "ABC"


def test_fasta_generation_with_more_than_one_protein(mock_uniprot):
    output = fasta_generation(pd.DataFrame({"Protein ID": ["Protein1", "Protein2"]}))
    generated_fasta_df: pd.DataFrame = output["fasta_df"]
    assert len(generated_fasta_df) == 2
    assert generated_fasta_df["Protein ID"].iloc[0] == "Protein1-1"
    assert generated_fasta_df["Protein Sequence"].iloc[0] == "ABC"
    assert generated_fasta_df["Protein ID"].iloc[1] == "Protein2-1"
    assert generated_fasta_df["Protein Sequence"].iloc[1] == "XY"


def test_fasta_generation_ignores_id_duplicates(mock_uniprot):
    output = fasta_generation(pd.DataFrame({"Protein ID": ["Protein1", "Protein1"]}))
    generated_fasta_df: pd.DataFrame = output["fasta_df"]
    assert len(generated_fasta_df) == 1


def test_fasta_generation_gives_warning_for_unknown_id(mock_uniprot):
    output = fasta_generation(pd.DataFrame({"Protein ID": ["abcxyz"]}))
    generated_fasta_df: pd.DataFrame = output["fasta_df"]
    messages: pd.DataFrame = output["messages"]
    assert len(generated_fasta_df) == 0
    assert len(messages) == 1
    assert messages[0]["level"] == logging.WARNING
    assert "1 protein ids were not found" in messages[0]["msg"]
