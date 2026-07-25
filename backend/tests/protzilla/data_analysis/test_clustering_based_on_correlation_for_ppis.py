import json

import pandas as pd
import pytest
import requests
from unittest import mock

from backend.protzilla.constants.option_types import StringDbNetworkType
from backend.protzilla.data_analysis.clustering_based_on_correlation_for_ppis import (
    _get_number_of_protein_ids_not_known_by_STRING,
    get_STRING_information_for_cluster,
    get_alphafold_query_file_for_specific_cluster,
    get_number_of_amino_acid_residues_in_cluster,
    get_proteins_of_specific_cluster,
    make_protein_ids_STRING_readable,
)


def test_make_protein_ids_STRING_readable_removes_isoform_identifiers():
    protein_ids = ["abc", "abc-0", "abc-11111"]
    processed_protein_ids = make_protein_ids_STRING_readable(protein_ids)
    STRING_compatible_ids = ["abc", "abc", "abc"]
    assert processed_protein_ids == STRING_compatible_ids


def _STRING_api_available() -> bool:
    url = "https://version-12-0.string-db.org/api/tsv-no-header/get_string_ids"

    try:
        response = requests.post(
            url,
            data={
                "identifiers": "O43242",
                "species": 9606,
                "caller_identity": "PROTzilla",
            },
            timeout=5,
        )

        return response.status_code == 200

    except requests.RequestException:
        return False


def test_get_number_of_protein_ids_not_known_by_STRING_with_no_unknown_ids():
    if not _STRING_api_available():
        pytest.skip("STRING unavailable")
    unknown_ids = _get_number_of_protein_ids_not_known_by_STRING(["O43242"], 9606)
    assert unknown_ids == 0


def test_get_number_of_protein_ids_not_known_by_STRING_with_unknown_ids():
    if not _STRING_api_available():
        pytest.skip("STRING unavailable")
    unknown_ids = _get_number_of_protein_ids_not_known_by_STRING(
        ["O43242", "ABCABCABCABC"], 9606
    )
    assert unknown_ids == 1


@pytest.fixture
def mock_STRING(monkeypatch):
    STRING_requests = []

    def mock_post(url, data):
        STRING_requests.append((url, data))
        response = mock.Mock()
        if "network" in url:
            response.content = b"fake_png"
        else:
            # STRING only knows Protein2
            response.text = "Protein2"

        response.status_code = 200
        return response

    monkeypatch.setattr(requests, "post", mock_post)
    return STRING_requests


def test_get_STRING_information_for_cluster_returns_image_bytes_and_unknown_proteins(
    mock_STRING,
):
    image, unknown_ids_count = get_STRING_information_for_cluster(
        proteins=["Protein1", "Protein2"],
        taxonomic_identifier=9606,
        network_flavor=StringDbNetworkType.evidence,
    )

    assert image == b"fake_png"
    assert unknown_ids_count == 1


def test_get_STRING_information_for_cluster_sends_correct_parameters(mock_STRING):
    proteins = ["Protein1", "Protein2"]
    network_flavor = StringDbNetworkType.evidence
    get_STRING_information_for_cluster(proteins, 9606, network_flavor)
    url, params = mock_STRING[0]

    assert url == "https://version-12-0.string-db.org/api/highres_image/network"
    assert params["identifiers"] == "\r".join(proteins)
    assert params["species"] == 9606
    assert params["network_flavor"] == network_flavor
    assert params["network_type"] == "physical"
    assert params["required_score"] == 0
    assert params["add_white_nodes"] == 0
    assert params["caller_identity"] == "PROTzilla"


def test_get_STRING_information_for_cluster_handles_STRING_connection_error(
    monkeypatch,
):

    def mock_post(*args, **kwargs):
        raise requests.ConnectionError()

    monkeypatch.setattr(requests, "post", mock_post)

    with pytest.raises(requests.ConnectionError):
        get_STRING_information_for_cluster(
            ["Protein1"],
            9606,
            StringDbNetworkType.evidence,
        )


def test_get_proteins_of_specific_cluster():
    all_labels = pd.Series(
        [1, 1, 2, 1, 3, 2, 1], index=("A", "B", "C", "D", "E", "F", "G")
    )
    proteins = get_proteins_of_specific_cluster(1, all_labels)
    expected_proteins = ["A", "B", "D", "G"]
    assert proteins == expected_proteins


def test_get_proteins_of_specific_cluster_with_nonexistent_label():
    all_labels = pd.Series(
        [1, 1, 2, 1, 3, 2, 1], index=("A", "B", "C", "D", "E", "F", "G")
    )
    proteins = get_proteins_of_specific_cluster(5, all_labels)
    expected_proteins = []
    assert proteins == expected_proteins


def test_get_proteins_of_specific_cluster_with_empty_labels_list():
    all_labels = pd.Series([], index=())
    proteins = get_proteins_of_specific_cluster(5, all_labels)
    expected_proteins = []
    assert proteins == expected_proteins


def test_get_alphafold_query_file_for_specific_cluster_creates_valid_query():
    fasta_df = pd.DataFrame(
        {
            "Protein ID": ["P1", "P2"],
            "Protein Sequence": ["AAAA", "BBBB"],
        }
    )

    result = get_alphafold_query_file_for_specific_cluster(
        name="test",
        model_seed=1,
        fasta_df=fasta_df,
        proteins=["P1", "P2"],
    )

    query = json.loads(result)[0]

    assert query["name"] == "test"
    assert query["modelSeeds"] == [1]
    assert query["dialect"] == "alphafoldserver"
    assert query["version"] == 1

    assert len(query["sequences"]) == 2
    assert query["sequences"][0]["proteinChain"]["sequence"] == "AAAA"
    assert query["sequences"][1]["proteinChain"]["sequence"] == "BBBB"
    assert query["sequences"][0]["proteinChain"]["count"] == 1
    assert query["sequences"][1]["proteinChain"]["count"] == 1


def test_get_alphafold_query_file_for_specific_cluster_without_model_seed():
    fasta_df = pd.DataFrame(
        {
            "Protein ID": ["P1", "P2"],
            "Protein Sequence": ["AAAA", "BBBB"],
        }
    )
    result = get_alphafold_query_file_for_specific_cluster(
        name="test",
        model_seed=-1,
        fasta_df=fasta_df,
        proteins=["P1", "P2"],
    )
    query = json.loads(result)[0]
    assert query["modelSeeds"] == []


def test_get_number_of_amino_acid_residues_in_cluster_with_known_protein_ids():
    uniprot_ids = ["A", "B"]
    protein_id_to_number_of_residues = {"A": 5, "B": 3}
    number_of_residues = get_number_of_amino_acid_residues_in_cluster(
        uniprot_ids, protein_id_to_number_of_residues
    )
    expected_number_of_residues = 8
    assert number_of_residues == expected_number_of_residues


def test_get_number_of_amino_acid_residues_in_cluster_with_unknown_protein_ids():
    uniprot_ids = ["A", "C"]
    protein_id_to_number_of_residues = {"A": 5, "B": 3}
    number_of_residues = get_number_of_amino_acid_residues_in_cluster(
        uniprot_ids, protein_id_to_number_of_residues
    )
    expected_number_of_residues = 5
    assert number_of_residues == expected_number_of_residues
