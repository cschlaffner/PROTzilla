import json

import pytest
from unittest.mock import patch, Mock
import requests
from backend.protzilla.importing.query_generation import (
    generate_alphafold_multimer_query_json,
)

FAKE_FASTA_1 = ">P69905 Hemoglobin subunit alpha\nMVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSHGSAQVKGHG"
FAKE_FASTA_2 = ">P68871 Hemoglobin subunit beta\nVLSPADKTNVKAAWGKVGGHAAEYGAEALERMFLSFPTTKTYFPHFDLSHGSAQVKGHG"


@patch("backend.protzilla.importing.query_generation.requests.get")
def test_generate_alphafold_multimer_json_query_for_multiple_proteins(mock_get):
    mock_resp1 = Mock()
    mock_resp1.status_code = 200
    mock_resp1.text = FAKE_FASTA_1
    mock_resp1.raise_for_status = Mock()

    mock_resp2 = Mock()
    mock_resp2.status_code = 200
    mock_resp2.text = FAKE_FASTA_2
    mock_resp2.raise_for_status = Mock()

    mock_get.side_effect = [mock_resp1, mock_resp2]

    result = generate_alphafold_multimer_query_json("P69905 P68871", "2,3", -1, "name")
    downloads = result["downloads"]

    assert len(downloads) == 1
    key = list(downloads.keys())[0]
    assert key == "name"

    # Parse JSON string (after removing outer brackets)
    json_str = downloads[key]
    parsed_json = json.loads(json_str[1:-1])

    # Check top-level keys
    expected_keys = {"name", "modelSeeds", "sequences", "dialect", "version"}
    assert set(parsed_json.keys()) == expected_keys

    # Check name, version, dialect, modelSeeds
    assert parsed_json["name"] == "name"
    assert parsed_json["version"] == 1
    assert parsed_json["dialect"] == "alphafoldserver"
    assert parsed_json["modelSeeds"] == []

    # Check sequences
    sequences = parsed_json["sequences"]
    assert len(sequences) == 2

    # First protein
    protein_chain_1 = sequences[0]["proteinChain"]
    assert (
        protein_chain_1["sequence"]
        == "MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSHGSAQVKGHG"
    )
    assert protein_chain_1["count"] == 2

    # Second protein
    protein_chain_2 = sequences[1]["proteinChain"]
    assert (
        protein_chain_2["sequence"]
        == "VLSPADKTNVKAAWGKVGGHAAEYGAEALERMFLSFPTTKTYFPHFDLSHGSAQVKGHG"
    )
    assert protein_chain_2["count"] == 3


@patch("backend.protzilla.importing.query_generation.requests.get")
def test_generate_alphafold_multimer_json_query_with_model_seed(mock_get):
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.text = FAKE_FASTA_1
    mock_resp.raise_for_status = Mock()
    mock_get.return_value = mock_resp

    result = generate_alphafold_multimer_query_json(
        "P69905", "2", model_seed=12345, name="name"
    )
    downloads = result["downloads"]
    key = list(downloads.keys())[0]
    parsed_json = json.loads(downloads[key][1:-1])
    assert parsed_json["modelSeeds"] == [12345]


def test_generate_alphafold_multimer_json_query_with_mismatched_number_of_ids_and_number_of_copies():
    with pytest.raises(ValueError, match="number of copies is missing"):
        generate_alphafold_multimer_query_json("P69905 P68871", "2", -1, "name")


def test_generate_alphafold_multimer_json_query_with_invalid_copy_number():
    with pytest.raises(ValueError, match="Invalid list of number of copies per id"):
        generate_alphafold_multimer_query_json("P69905", "abc", -1, "name")


@patch("backend.protzilla.importing.query_generation.requests.get")
def test_generate_alphafold_multimer_json_query_with_http_error(mock_get):
    mock_resp = Mock()
    mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_get.return_value = mock_resp

    with pytest.raises(requests.exceptions.HTTPError):
        generate_alphafold_multimer_query_json("P69905", "2", -1, "name")
