import pytest
import pandas as pd
from unittest.mock import patch, Mock
from requests.exceptions import Timeout
from protzilla.importing.crosslinking_import import (
    aggregate_data,
    remove_isoform_from_protein_id,
    remove_brackets_from_peptide,
    get_amino_acid_where_crosslink_is_connected_proteomediscoverer_xlinkx_format,
    validate_data_before_lookup,
    execute_uniprot_request,
    process_uniprot_response_containing_gene_names,
    iterate_for_protein_designation,
    get_missing_protein_designation,
    crosslinking_import,
)


def test_aggregate_data():
    df = pd.DataFrame({"Protein1": ["A", "B", None], "Protein2": ["C", "B", "D"]})
    result = aggregate_data(df, "Protein")
    assert result == {"A", "B", "C", "D"}


def test_remove_isoform_from_protein_id():
    assert remove_isoform_from_protein_id("P12345-2") == "P12345"
    assert remove_isoform_from_protein_id("Q67890") == "Q67890"


def test_remove_brackets_from_peptide():
    assert remove_brackets_from_peptide("[ABC]DE[FG]") == "ABCDEFG"


def test_get_amino_acid_where_crosslink_is_connected_proteomediscoverer_xlinkx_format():
    assert (
        get_amino_acid_where_crosslink_is_connected_proteomediscoverer_xlinkx_format(
            "[ACD]EF"
        )
        == 1
    )
    assert (
        get_amino_acid_where_crosslink_is_connected_proteomediscoverer_xlinkx_format(
            "ACDEF"
        )
        == 0
    )


def test_validate_data_before_lookup():
    data = {"A", "B", "C"}

    def validator(x):
        return x != "B"

    valid, results = validate_data_before_lookup(data, validator, "ERROR")
    assert valid == {"A", "C"}
    assert results == {"B": (False, None, "ERROR")}


def test_validate_data_before_lookup_empty():
    valid, results = validate_data_before_lookup(set(), lambda x: True, "ERR")
    assert valid == set()
    assert results == {}


def test_execute_uniprot_request_success():
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    results = {}
    valid_data = {"P12345"}
    with patch(
        "protzilla.importing.crosslinking_import.requests.get",
        return_value=mock_response,
    ):
        response = execute_uniprot_request(
            "url", {"param": "value"}, valid_data, results
        )
        assert response == mock_response
        assert results == {}


def test_execute_uniprot_request_timeout():
    results = {}
    valid_data = {"P12345"}
    with patch(
        "protzilla.importing.crosslinking_import.requests.get",
        side_effect=Timeout(),
    ):
        response = execute_uniprot_request(
            "url", {"param": "value"}, valid_data, results
        )
        assert response is None
        assert results["P12345"][2] == "TIMEOUT"


def test_process_uniprot_response_containing_gene_names():
    results = {}
    mock_response = Mock()
    mock_response.json.return_value = {
        "results": [
            {"primaryAccession": "P1", "genes": [{"geneName": {"value": "GENE1"}}]},
            {"primaryAccession": "P2", "genes": []},
        ]
    }
    process_uniprot_response_containing_gene_names(mock_response, results)
    assert results["P1"] == (True, "GENE1", None)
    assert results["P2"] == (False, None, "NO_GENE_NAME_FOUND")


def _minimal_valid_crosslinking_df():
    return pd.DataFrame(
        {
            "Protein_id1": ["P1"],
            "Protein_id2": ["P2"],
            "Protein1": ["GENE1"],
            "Protein2": ["GENE2"],
            "Is_intra_crosslink": [False],
            "Crosslinker": ["DSS"],
            "Peptide1": ["AAA"],
            "Peptide2": ["BBB"],
            "Peptide_position1": [1],
            "Peptide_position2": [2],
            "CL_position1": [3],
            "CL_position2": [4],
            "Q_value": [0.01],
        }
    )


def test_iterate_for_protein_designation():
    df = _minimal_valid_crosslinking_df()
    lookup_results = {
        "P1": (True, "GENE1", None),
        "P2": (True, "GENE2", None),
    }
    good_df, failed_df = iterate_for_protein_designation(
        df,
        "Protein_id",
        "Protein",
        lookup_results,
    )

    assert len(good_df) == 1
    assert failed_df.empty


def test_get_missing_protein_designation():
    df = _minimal_valid_crosslinking_df()

    def mock_lookup(ids):
        return {pid: (True, f"Gene_{pid}", None) for pid in ids}

    good_df, failed_df = get_missing_protein_designation(
        df,
        "Protein_id",
        "Protein",
        mock_lookup,
    )

    assert len(good_df) == 1
    assert failed_df.empty


def test_crosslinking_import_csv(tmp_path):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(
        "Protein1,Protein2,Peptide1,Peptide2,"
        "Peptide_position1,Peptide_position2,"
        "CL_position1,CL_position2,"
        "Crosslinker,Q_value\n"
        "RAD50,MRE11,AAA,BBB,1,2,3,4,DSS,0.01\n"
    )

    with patch(
        "protzilla.importing.crosslinking_import.get_protein_ids_from_gene_name",
        return_value={
            "RAD50": (True, {"protein_ids": ["P12345"]}, None),
            "MRE11": (True, {"protein_ids": ["Q67890"]}, None),
        },
    ):
        result = crosslinking_import(csv_file)

    assert "crosslinking_df" in result
    assert not result["crosslinking_df"].empty


def test_crosslinking_import_invalid_file(tmp_path):
    bad_file = tmp_path / "test.txt"
    bad_file.write_text("something invalid")
    result = crosslinking_import(bad_file)
    assert "messages" in result
    assert any("Unsupported file type" in m["msg"] for m in result["messages"])
