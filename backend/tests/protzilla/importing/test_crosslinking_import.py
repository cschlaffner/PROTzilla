import pytest
import pandas as pd
from unittest.mock import patch, Mock
from requests.exceptions import Timeout
from protzilla.importing.crosslinking_import import (
    aggregate_data,
    remove_brackets_from_peptide,
    get_amino_acid_where_crosslink_is_connected_proteomediscoverer_xlinkx_format,
    validate_data_before_lookup,
    execute_uniprot_request,
    process_uniprot_response,
    iterate_for_protein_designation,
    get_missing_protein_designation,
    crosslinking_import,
)


def test_aggregate_data():
    df = pd.DataFrame({"Protein1": ["A", "B", None], "Protein2": ["C", "B", "D"]})
    result = aggregate_data(df, "Protein")
    assert result == {"A", "B", "C", "D"}


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
    valid, results = validate_data_before_lookup(set(), lambda x: True, "ERROR")
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


def test_process_uniprot_response_id_to_gene_name():
    results = {}
    input_data = {"P1", "P2"}

    mock_response = Mock()
    mock_response.text = "Entry\tGene Names (primary)\n" "P1\tGENE1\n" "P2\t\n"

    process_uniprot_response(
        response=mock_response,
        results=results,
        input_data=input_data,
        mode="id_to_gene_name",
    )

    assert results["P1"] == (True, "GENE1", None)


def test_uniprot_lookup_successful_request_but_no_results(monkeypatch):
    from protzilla.importing.crosslinking_import import uniprot_lookup

    def mock_execute(*args, **kwargs):
        mock = Mock()
        mock.text = "Entry\tGene Names (primary)\n"
        return mock

    monkeypatch.setattr(
        "protzilla.importing.crosslinking_import.execute_uniprot_request",
        mock_execute,
    )

    results = {}
    uniprot_lookup(
        input_data={"P1"},
        mode="id_to_gene_name",
        results=results,
    )

    assert results == {}


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


@pytest.mark.parametrize(
    "input_string, mock_result, expected",
    [
        (
            "9606,10090",
            {
                "uids": ["9606", "10090"],
                "9606": {"scientificname": "Homo sapiens"},
                "10090": {"scientificname": "Mus musculus"},
            },
            (True, ["9606", "10090"], ["Homo sapiens", "Mus musculus"], None),
        ),
        (
            "9606,9999",
            {
                "uids": ["9606"],
                "9606": {"scientificname": "Homo sapiens"},
            },
            (False, "9999", None, "ORGANISM_ID_NOT_FOUND"),
        ),
    ],
)
def test_process_organism_id_from_text_field(
    monkeypatch, input_string, mock_result, expected
):
    from protzilla.importing.crosslinking_import import (
        process_organism_id_from_text_field,
    )

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": mock_result}

    monkeypatch.setattr(
        "protzilla.importing.crosslinking_import.requests.get",
        lambda *args, **kwargs: mock_response,
    )

    result = process_organism_id_from_text_field(input_string)

    assert result == expected


def test_aggregate_failed_proteins_for_display():
    df = pd.DataFrame(
        {
            "Protein1": ["A"],
            "Protein2": ["B"],
            "Protein1_error": ["ERR1"],
            "Protein2_error": [None],
        }
    )

    from protzilla.importing.crosslinking_import import (
        aggregate_failed_proteins_for_display,
    )

    result = aggregate_failed_proteins_for_display(df)
    assert result == "A -> ERR1"


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
            "RAD50": (True, "P12345", None),
            "MRE11": (True, "Q67890", None),
        },
    ):
        result = crosslinking_import(csv_file, organism_ids="9606")

    assert "crosslinking_df" in result
    assert not result["crosslinking_df"].empty


def test_crosslinking_import_xlsx(monkeypatch, tmp_path):
    xlsx = tmp_path / "test.xlsx"
    pd.DataFrame(
        {
            "Protein_id1": ["P1"],
            "Protein_id2": ["P2"],
            "Peptide1": ["[AAA]"],
            "Peptide2": ["[BBB]"],
            "Is_intra_crosslink": ["Intra"],
            "Peptide_position1": [1],
            "Peptide_position2": [2],
            "CL_position1": [3],
            "CL_position2": [4],
            "Crosslinker": ["DSS"],
            "Q_value": [0.01],
        }
    ).to_excel(xlsx, index=False)

    monkeypatch.setattr(
        "protzilla.importing.crosslinking_import.get_gene_name_from_protein_ids",
        lambda ids: {i: (True, f"G{i}", None) for i in ids},
    )

    result = crosslinking_import(xlsx, organism_ids="9606")
    assert "crosslinking_df" in result


def test_crosslinking_import_invalid_file(tmp_path):
    bad_file = tmp_path / "test.txt"
    bad_file.write_text("something invalid")
    result = crosslinking_import(bad_file, organism_ids="9606")
    assert "messages" in result
    assert any("Unsupported file type" in m["msg"] for m in result["messages"])
