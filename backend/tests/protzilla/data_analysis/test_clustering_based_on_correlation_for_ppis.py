import json

import numpy as np
import pandas as pd
import pytest
import requests
from unittest import mock

from sklearn.metrics import silhouette_samples

from backend.protzilla.constants.option_types import (
    CorrelationMethod,
    DistanceFromCorrelation,
    StringDbNetworkType,
)
from backend.protzilla.data_analysis.clustering_based_on_correlation_for_ppis import (
    _get_number_of_protein_ids_not_known_by_STRING,
    get_STRING_information_for_cluster,
    get_alphafold_query_file_for_specific_cluster,
    get_cluster_silhouette_histogram,
    get_correlation_matrix,
    get_correlation_mean_of_cluster,
    get_distance_matrix_from_correlation_matrix_df,
    get_number_of_amino_acid_residues_in_cluster,
    get_protein_id_to_number_of_residues,
    get_proteins_of_specific_cluster,
    hdbscan_for_ppi,
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


def test_get_protein_id_to_number_of_residues():
    fasta_df = pd.DataFrame(
        {
            "Protein ID": ["P4", "P3", "P0"],
            "Protein Sequence": ["AAAA", "BBB", ""],
        }
    )
    protein_id_to_number_of_residues = get_protein_id_to_number_of_residues(fasta_df)
    expected_protein_id_to_number_of_residues = {"P4": 4, "P3": 3, "P0": 0}
    assert protein_id_to_number_of_residues == expected_protein_id_to_number_of_residues


def test_get_correlation_mean_of_cluster():
    labels = pd.Series([1, 1, 2, 1], index=("A", "B", "C", "D"))
    correlation_matrix_df = pd.DataFrame(
        [
            [1.0, 0.8, 0.5, 0.5],
            [0.8, 1.0, 0.7, 0.5],
            [0.8, 0.5, 1.0, 0.5],
            [0.8, 0.4, 0.7, 1.0],
        ],
        index=["A", "B", "C", "D"],
        columns=["A", "B", "C", "D"],
    )
    correlation_mean = get_correlation_mean_of_cluster(labels, 1, correlation_matrix_df)
    expected_correlation_mean = 3.8 / 6
    assert abs(correlation_mean - expected_correlation_mean) < 0.000001


def test_get_correlation_mean_of_cluster_raises_error_for_cluster_of_size_one():
    with pytest.raises(AssertionError):
        labels = pd.Series([1], index=["A"])
        correlation_matrix_df = pd.DataFrame([[1.0]], index=["A"], columns=["A"])
        get_correlation_mean_of_cluster(labels, 1, correlation_matrix_df)


@pytest.fixture
def protein_df_for_correlation_matrix():
    return pd.DataFrame(
        [
            ["A", "Sample1", 100],
            ["A", "Sample2", 20],
            ["A", "Sample3", 40],
            ["A", "Sample4", 80],
            ["B", "Sample1", 95],
            ["B", "Sample2", 15],
            ["B", "Sample3", 35],
            ["B", "Sample4", 75],
            ["C-2", "Sample1", 105],
            ["C-2", "Sample2", 22],
            ["C-2", "Sample3", 45],
            ["C-2", "Sample4", 85],
            ["D", "Sample1", 200],
            ["D", "Sample2", 150],
            ["D", "Sample3", 100],
            ["D", "Sample4", 50],
            ["E", "Sample1", 205],
            ["E", "Sample2", 155],
            ["E", "Sample3", 105],
            ["E", "Sample4", 55],
            ["F", "Sample1", 195],
            ["F", "Sample2", 145],
            ["F", "Sample3", 95],
            ["F", "Sample4", 45],
        ],
        columns=["Protein ID", "Sample", "Intensity"],
    )


@pytest.fixture
def fasta_df_for_correlation_matrix():
    return pd.DataFrame(
        [
            ["A-1", "AA"],
            ["B-1", "BBB"],
            ["C-2", "CCCC"],
            ["D-1", "DDDDD"],
            ["E-1", "E"],
            ["F-1", "FFFF"],
        ],
        columns=["Protein ID", "Protein Sequence"],
    )


@pytest.mark.parametrize(
    "correlation_method", [CorrelationMethod.pearson, CorrelationMethod.spearman]
)
def test_get_correlation_matrix_with_different_correlation_methods(
    protein_df_for_correlation_matrix,
    fasta_df_for_correlation_matrix,
    correlation_method,
):
    output = get_correlation_matrix(
        protein_df_for_correlation_matrix,
        fasta_df_for_correlation_matrix,
        correlation_method,
    )
    correlation_matrix_df = output["correlation_matrix_df"]
    removed_protein_ids_df = output["removed_protein_ids_df"]
    protein_to_intensities = {
        id: pd.Series(group["Intensity"].to_list())
        for id, group in protein_df_for_correlation_matrix.sort_values(
            "Sample"
        ).groupby("Protein ID")
    }
    expected_correlation_matrix_df = pd.DataFrame(protein_to_intensities).corr(
        correlation_method
    )
    expected_correlation_matrix_df.columns = ["A-1", "B-1", "C-2", "D-1", "E-1", "F-1"]
    expected_correlation_matrix_df.index = ["A-1", "B-1", "C-2", "D-1", "E-1", "F-1"]
    pd.testing.assert_frame_equal(correlation_matrix_df, expected_correlation_matrix_df)


def test_get_correlation_matrix_removes_nans(
    protein_df_for_correlation_matrix, fasta_df_for_correlation_matrix
):
    protein_df = protein_df_for_correlation_matrix.copy()
    # A-1 and B-1 will have a correlation of nan with each other
    protein_df.loc[0, "Intensity"] = np.nan
    protein_df.loc[1, "Intensity"] = np.nan
    protein_df.loc[6, "Intensity"] = np.nan
    protein_df.loc[7, "Intensity"] = np.nan
    output = get_correlation_matrix(
        protein_df, fasta_df_for_correlation_matrix, CorrelationMethod.pearson
    )
    correlation_matrix_df = output["correlation_matrix_df"]
    removed_protein_ids_df = output["removed_protein_ids_df"]
    messages = output["messages"]
    protein_to_intensities = {
        id: pd.Series(group["Intensity"].to_list())
        for id, group in protein_df.sort_values("Sample").groupby("Protein ID")
        if pd.Series(group["Intensity"].to_list()).nunique(dropna=True) > 1
    }
    expected_correlation_matrix_df = (
        pd.DataFrame(protein_to_intensities)
        .corr("pearson")
        .drop(index=["A-1", "B-1"], columns=["A-1", "B-1"])
    )
    expected_correlation_matrix_df.columns = ["C-2", "D-1", "E-1", "F-1"]
    expected_correlation_matrix_df.index = ["C-2", "D-1", "E-1", "F-1"]
    pd.testing.assert_frame_equal(correlation_matrix_df, expected_correlation_matrix_df)
    pd.testing.assert_frame_equal(
        removed_protein_ids_df, pd.DataFrame(["A-1", "B-1"], columns=["Protein ID"])
    )
    assert "2 proteins had a correlation of NaN" in messages[0]["msg"]


def test_get_correlation_matrix_removes_proteins_with_identical_intensities(
    protein_df_for_correlation_matrix, fasta_df_for_correlation_matrix
):
    protein_df = protein_df_for_correlation_matrix.copy()
    protein_df_for_correlation_matrix.loc[0, "Intensity"] = 80
    protein_df_for_correlation_matrix.loc[1, "Intensity"] = 80
    protein_df_for_correlation_matrix.loc[2, "Intensity"] = 80
    protein_df_for_correlation_matrix.loc[3, "Intensity"] = 80
    output = get_correlation_matrix(
        protein_df_for_correlation_matrix,
        fasta_df_for_correlation_matrix,
        CorrelationMethod.pearson,
    )
    correlation_matrix_df = output["correlation_matrix_df"]
    removed_protein_ids_df = output["removed_protein_ids_df"]
    messages = output["messages"]
    protein_to_intensities = {
        id: pd.Series(group["Intensity"].to_list())
        for id, group in protein_df_for_correlation_matrix.sort_values(
            "Sample"
        ).groupby("Protein ID")
        if pd.Series(group["Intensity"].to_list()).nunique(dropna=True) > 1
    }
    expected_correlation_matrix_df = pd.DataFrame(protein_to_intensities).corr(
        "pearson"
    )
    expected_correlation_matrix_df.columns = ["B-1", "C-2", "D-1", "E-1", "F-1"]
    expected_correlation_matrix_df.index = ["B-1", "C-2", "D-1", "E-1", "F-1"]
    pd.testing.assert_frame_equal(correlation_matrix_df, expected_correlation_matrix_df)
    pd.testing.assert_frame_equal(
        removed_protein_ids_df, pd.DataFrame(["A-1"], columns=["Protein ID"])
    )
    assert "all the protein's intensity values were identical" in messages[0]["msg"]


def test_get_correlation_matrix_removes_proteins_that_miss_in_the_fasta(
    protein_df_for_correlation_matrix, fasta_df_for_correlation_matrix
):
    fasta_df = fasta_df_for_correlation_matrix.copy()
    fasta_df = fasta_df.drop(fasta_df.index[0])
    output = get_correlation_matrix(
        protein_df_for_correlation_matrix,
        fasta_df,
        CorrelationMethod.pearson,
    )
    correlation_matrix_df = output["correlation_matrix_df"]
    removed_protein_ids_df = output["removed_protein_ids_df"]
    messages = output["messages"]
    protein_to_intensities = {
        id: pd.Series(group["Intensity"].to_list())
        for id, group in protein_df_for_correlation_matrix.sort_values(
            "Sample"
        ).groupby("Protein ID")
        if pd.Series(group["Intensity"].to_list()).nunique(dropna=True) > 1
    }
    expected_correlation_matrix_df = (
        pd.DataFrame(protein_to_intensities)
        .corr("pearson")
        .drop(index=["A-1"], columns=["A-1"])
    )
    expected_correlation_matrix_df.columns = ["B-1", "C-2", "D-1", "E-1", "F-1"]
    expected_correlation_matrix_df.index = ["B-1", "C-2", "D-1", "E-1", "F-1"]
    pd.testing.assert_frame_equal(correlation_matrix_df, expected_correlation_matrix_df)
    pd.testing.assert_frame_equal(
        removed_protein_ids_df, pd.DataFrame(["A-1"], columns=["Protein ID"])
    )
    assert "since the ids were not found in the provided fasta." in messages[0]["msg"]


@pytest.fixture
def correlation_matrix_df(
    protein_df_for_correlation_matrix, fasta_df_for_correlation_matrix
):
    return get_correlation_matrix(
        protein_df_for_correlation_matrix,
        fasta_df_for_correlation_matrix,
        CorrelationMethod.pearson,
    )["correlation_matrix_df"]


@pytest.mark.parametrize(
    "distance_method, hdbscan_suitable",
    [
        (DistanceFromCorrelation.weight_in_negative_correlations, True),
        (DistanceFromCorrelation.weight_in_negative_correlations, False),
        (DistanceFromCorrelation.do_not_weight_in_negative_correlations, True),
        (DistanceFromCorrelation.do_not_weight_in_negative_correlations, False),
    ],
)
def test_get_distance_matrix_from_correlation_matrix_df(
    correlation_matrix_df, distance_method, hdbscan_suitable
):
    distance_matrix_df = get_distance_matrix_from_correlation_matrix_df(
        correlation_matrix_df, distance_method, hdbscan_suitable
    )["distance_matrix_df"]
    expected_distance_matrix = correlation_matrix_df.to_numpy()
    if hdbscan_suitable:
        expected_distance_matrix = np.clip(
            expected_distance_matrix, -0.999999, 0.999999
        )
    else:
        expected_distance_matrix = np.clip(expected_distance_matrix, -1, 1)
    if distance_method == DistanceFromCorrelation.weight_in_negative_correlations:
        expected_distance_matrix = np.sqrt(2 * (1 - expected_distance_matrix))
    else:
        expected_distance_matrix = 1 - np.maximum(0, expected_distance_matrix)
    np.fill_diagonal(expected_distance_matrix, 0)
    expected_distance_matrix = pd.DataFrame(
        expected_distance_matrix,
        index=correlation_matrix_df.columns,
        columns=correlation_matrix_df.columns,
    )
    pd.testing.assert_frame_equal(
        distance_matrix_df, expected_distance_matrix, atol=1e-5
    )


@pytest.fixture
def distance_matrix_df(correlation_matrix_df):
    return get_distance_matrix_from_correlation_matrix_df(
        correlation_matrix_df,
        DistanceFromCorrelation.weight_in_negative_correlations,
        hdbscan_suitable=True,
    )["distance_matrix_df"]


@pytest.mark.parametrize("clusters_of_size_one_ommitted", [True, False])
def test_get_cluster_silhouette_histograms_determines_right_silhouette_score_for_each_cluster(
    distance_matrix_df, clusters_of_size_one_ommitted
):
    labels = pd.Series(
        [1, 1, 1, -1, 1, -1], index=["A-1", "B-1", "C-2", "D-1", "E-1", "F-1"]
    )
    figure, silhouette_per_cluster = get_cluster_silhouette_histogram(
        distance_matrix_df.to_numpy(), labels, clusters_of_size_one_ommitted
    )
    expected_silhouette_per_cluster = pd.Series(dtype=float)
    silhouette_scores_per_sample = silhouette_samples(
        distance_matrix_df.to_numpy(), labels, metric="precomputed"
    )
    for label in labels.unique():
        if clusters_of_size_one_ommitted and label == -1:
            continue
        mask = labels == label
        expected_silhouette_per_cluster.loc[label] = silhouette_scores_per_sample[
            mask
        ].mean()
    pd.testing.assert_series_equal(
        silhouette_per_cluster, expected_silhouette_per_cluster
    )


def test_hdbscan_for_ppi(
    distance_matrix_df, correlation_matrix_df, protein_df_for_correlation_matrix
):
    output = hdbscan_for_ppi(
        distance_matrix_df,
        correlation_matrix_df,
        protein_df_for_correlation_matrix,
        min_cluster_size=2,
    )
    expected_cluster_labels_df = pd.DataFrame(
        [[0], [0], [0], [1], [1], [1]],
        columns=["Label"],
        index=["A-1", "B-1", "C-2", "D-1", "E-1", "F-1"],
    )
    pd.testing.assert_frame_equal(
        output["cluster_labels_df"].value, expected_cluster_labels_df
    )
    # assert 1 == output["cluster_labels_df"]["Label"]
