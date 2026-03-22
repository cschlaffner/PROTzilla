import pandas as pd
import pytest

from backend.protzilla.constants.intensity_types import IntensityType
from backend.protzilla.constants.data_types import DataKey
from backend.protzilla.data_analysis.protein_coverage import (
    distribute_to_rows,
    PeptideMatch,
)
from backend.protzilla.data_analysis.protein_coverage import (
    extract_peptide_from_slice,
    AggregationMethod,
)
from backend.protzilla.data_analysis.protein_coverage import (
    get_max_coverage,
)
from backend.protzilla.data_analysis.protein_coverage import increment_coverage_inplace
from backend.protzilla.data_analysis.protein_coverage import (
    match_peptide_to_protein_ids,
    ProteinHit,
)
from backend.protzilla.data_analysis.protein_coverage import plot_protein_coverage
from backend.protzilla.importing.fasta_import import fasta_import
from backend.protzilla.importing.peptide_import import evidence_import
from backend.tests.paths import TEST_FASTA_PATH, TEST_PEPTIDES_PATH


def test_match_peptide_to_protein_ids_empty_peptide():
    with pytest.raises(ValueError, match="Peptide sequence is empty."):
        match_peptide_to_protein_ids("", {}, {})


def test_match_peptide_to_protein_ids_no_matches():
    peptide_sequence = "ABCDE"
    protein_kmer_dictionary = {"ABCDE": [("protein1", 0)]}
    protein_dictionary = {"protein1": "XYZ"}
    result = match_peptide_to_protein_ids(
        peptide_sequence, protein_kmer_dictionary, protein_dictionary
    )
    assert result == []


def test_match_peptide_to_protein_ids_single_match():
    peptide_sequence = "ABCDE"
    protein_kmer_dictionary = {"ABCDE": [("protein1", 0)]}
    protein_dictionary = {"protein1": "ABCDE"}
    result = match_peptide_to_protein_ids(
        peptide_sequence, protein_kmer_dictionary, protein_dictionary
    )
    expected = [
        ProteinHit(
            protein_id="protein1",
            start_location_on_protein=0,
            end_location_on_protein=5,
        )
    ]
    assert result == expected


def test_match_peptide_to_protein_ids_multiple_matches():
    peptide_sequence = "ABCDE"
    protein_kmer_dictionary = {"ABCDE": [("protein1", 0), ("protein2", 0)]}
    protein_dictionary = {"protein1": "ABCDE", "protein2": "ABCDE"}
    result = match_peptide_to_protein_ids(
        peptide_sequence, protein_kmer_dictionary, protein_dictionary
    )
    expected = {
        ProteinHit(
            protein_id="protein1",
            start_location_on_protein=0,
            end_location_on_protein=5,
        ),
        ProteinHit(
            protein_id="protein2",
            start_location_on_protein=0,
            end_location_on_protein=5,
        ),
    }
    assert expected == set(result)


def test_match_peptide_to_protein_ids_partial_match():
    peptide_sequence = "ABCDE"
    protein_kmer_dictionary = {"ABCDE": [("protein1", 0)]}
    protein_dictionary = {"protein1": "ABCDEXYZ"}
    result = match_peptide_to_protein_ids(
        peptide_sequence, protein_kmer_dictionary, protein_dictionary
    )
    expected = [
        ProteinHit(
            protein_id="protein1",
            start_location_on_protein=0,
            end_location_on_protein=5,
        )
    ]
    assert result == expected


def test_increment_coverage():
    coverage = [0, 0, 0, 0, 0]
    protein_hit = ProteinHit(
        protein_id="P12345", start_location_on_protein=1, end_location_on_protein=4
    )
    increment_coverage_inplace(coverage, protein_hit)
    assert coverage == [0, 1, 1, 1, 0]


def test_increment_coverage_multiple_hits():
    coverage = [0, 0, 0, 0, 0]
    protein_hit1 = ProteinHit(
        protein_id="P12345", start_location_on_protein=1, end_location_on_protein=3
    )
    protein_hit2 = ProteinHit(
        protein_id="P12345", start_location_on_protein=2, end_location_on_protein=4
    )
    increment_coverage_inplace(coverage, protein_hit1)
    increment_coverage_inplace(coverage, protein_hit2)
    assert coverage == [0, 1, 2, 1, 0]


def test_increment_coverage_no_overlap():
    coverage = [0, 0, 0, 0, 0]
    protein_hit1 = ProteinHit(
        protein_id="P12345", start_location_on_protein=0, end_location_on_protein=2
    )
    protein_hit2 = ProteinHit(
        protein_id="P12345", start_location_on_protein=3, end_location_on_protein=5
    )
    increment_coverage_inplace(coverage, protein_hit1)
    increment_coverage_inplace(coverage, protein_hit2)
    assert coverage == [1, 1, 0, 1, 1]


def test_extract_peptide_from_slice_single_entry():
    data = {"Sequence": ["PEPTIDE"], "Intensity": [100]}
    df = pd.DataFrame(data)
    result = extract_peptide_from_slice(df)
    assert result.equals(df)


def test_extract_peptide_from_slice_multiple_entries():
    data = {"Sequence": ["PEPTIDE", "PEPTIDE", "PEPTIDE"], "Intensity": [100, 130, 200]}
    df = pd.DataFrame(data)
    result = extract_peptide_from_slice(df)
    expected = pd.DataFrame({"Sequence": "PEPTIDE", "Intensity": [130.0]})
    expected.set_index("Sequence", inplace=True)
    assert result.equals(expected)


def test_extract_peptide_from_slice_median():
    data = {"Sequence": ["PEPTIDE", "PEPTIDE"], "Intensity": [100, 200]}
    df = pd.DataFrame(data)
    result = extract_peptide_from_slice(df, AggregationMethod.median)
    expected = pd.DataFrame({"Sequence": "PEPTIDE", "Intensity": [150.0]})
    expected.set_index("Sequence", inplace=True)
    assert result.equals(expected)


def test_extract_peptide_from_slice_mean():
    data = {"Sequence": ["PEPTIDE", "PEPTIDE"], "Intensity": [100, 200]}
    df = pd.DataFrame(data)
    result = extract_peptide_from_slice(df, AggregationMethod.mean)
    expected = pd.DataFrame({"Sequence": "PEPTIDE", "Intensity": [150.0]})
    expected.set_index("Sequence", inplace=True)
    assert result.equals(expected)


def test_extract_peptide_from_slice_unknown_strategy():
    data = {"Sequence": ["PEPTIDE", "PEPTIDE"], "Intensity": [100, 200]}
    df = pd.DataFrame(data)
    with pytest.raises(ValueError, match="Unknown strategy: unknown"):
        extract_peptide_from_slice(df, "unknown")


def test_distribute_to_rows_empty():
    with pytest.raises(
        ValueError,
        match="Attempted to distribute empty list of peptide matches to rows in plot.",
    ):
        distribute_to_rows([])


def test_distribute_to_rows_single_peptide():
    peptide_matches = [
        PeptideMatch(
            peptide_sequence="AAA",
            start_location_on_protein=0,
            end_location_on_protein=3,
            metadata_group="group1",
        )
    ]
    expected = {"group1": [[peptide_matches[0]]]}
    assert distribute_to_rows(peptide_matches) == expected


def test_distribute_to_rows_non_overlapping():
    peptide_matches = [
        PeptideMatch(
            peptide_sequence="AAA",
            start_location_on_protein=0,
            end_location_on_protein=3,
            metadata_group="group1",
        ),
        PeptideMatch(
            peptide_sequence="BBB",
            start_location_on_protein=4,
            end_location_on_protein=7,
            metadata_group="group1",
        ),
    ]
    expected = {"group1": [[peptide_matches[0], peptide_matches[1]]]}
    assert distribute_to_rows(peptide_matches) == expected


def test_distribute_to_rows_overlapping():
    peptide_matches = [
        PeptideMatch(
            peptide_sequence="AAA",
            start_location_on_protein=0,
            end_location_on_protein=3,
            metadata_group="group1",
        ),
        PeptideMatch(
            peptide_sequence="BBB",
            start_location_on_protein=2,
            end_location_on_protein=5,
            metadata_group="group1",
        ),
    ]
    expected = {"group1": [[peptide_matches[0]], [peptide_matches[1]]]}
    assert distribute_to_rows(peptide_matches) == expected


def test_distribute_to_rows_multiple_groups():
    peptide_matches = [
        PeptideMatch(
            peptide_sequence="AAA",
            start_location_on_protein=0,
            end_location_on_protein=3,
            metadata_group="group1",
        ),
        PeptideMatch(
            peptide_sequence="BBB",
            start_location_on_protein=4,
            end_location_on_protein=7,
            metadata_group="group2",
        ),
    ]
    expected = {"group1": [[peptide_matches[0]]], "group2": [[peptide_matches[1]]]}
    assert distribute_to_rows(peptide_matches) == expected


def test_distribute_to_rows():
    peptide_matches = [
        PeptideMatch("PEPTIDE1", 0, 7, 1.0, "group1"),
        PeptideMatch("PEPTIDE2", 8, 15, 1.0, "group1"),
        PeptideMatch("PEPTIDE3", 16, 23, 1.0, "group1"),
        PeptideMatch("PEPTIDE4", 0, 7, 1.0, "group2"),
        PeptideMatch("PEPTIDE5", 8, 15, 1.0, "group2"),
    ]
    rows = distribute_to_rows(peptide_matches)
    assert len(rows["group1"]) == 1
    assert len(rows["group2"]) == 1


def test_get_max_coverage():
    coverage = {
        "group1": [1, 2, 3, 4, 5],
        "group2": [2, 3, 4, 5, 6],
    }
    max_coverage = get_max_coverage(coverage)
    assert max_coverage == 6


def test_get_max_coverage_empty():
    with pytest.raises(
        ValueError,
        match="Cannot calculate maximum coverage value: No coverage data provided.",
    ):
        get_max_coverage({})


@pytest.fixture
def fasta_df():
    fasta_path = TEST_FASTA_PATH / "uniprotkb_P10636.fasta"
    return fasta_import(fasta_path)[DataKey.FASTA_DF]


@pytest.fixture
def psm_df():
    outputs = evidence_import(
        file_path=TEST_PEPTIDES_PATH / "evidence_P10636.txt",
        intensity_name=IntensityType.INTENSITY.value,
        map_to_uniprot=False,
    )
    psm_df = outputs[DataKey.PSM_DF]
    return psm_df


@pytest.fixture
def metadata_df(psm_df):
    samples = psm_df["Sample"].drop_duplicates()
    filtered_samples = samples[samples.str.contains("AD|CTR")]
    groups = filtered_samples.apply(lambda s: "AD" if "AD" in s else "CTR")

    return pd.DataFrame(
        list(zip(filtered_samples, groups)),
        columns=["Sample", "Group"],
    )


@pytest.mark.parametrize(
    "protein_id,grouping,selected_groups,aggregation_method",
    [
        ("P10636-1", "Group", ["AD", "CTR"], AggregationMethod.mean),
        ("P10636-1", "Group", ["AD"], AggregationMethod.median),
        ("P10636-1", "Group", ["CTR"], AggregationMethod.mean),
        ("P10636-1", "Group", ["AD", "CTR"], AggregationMethod.median),
        ("P10636-6", "Group", ["AD", "CTR"], AggregationMethod.median),
        (
            "P10636-1",
            "Sample",
            ["AD01_C1_INSOLUBLE_01", "CTR01_C1_INSOLUBLE_01"],
            AggregationMethod.mean,
        ),
        (
            "P10636-6",
            "Sample",
            ["AD01_C1_INSOLUBLE_01", "CTR01_C1_INSOLUBLE_01"],
            AggregationMethod.mean,
        ),
    ],
)
def test_plot_protein_coverage(
    fasta_df,
    psm_df,
    metadata_df,
    protein_id,
    grouping,
    selected_groups,
    aggregation_method,
):
    result = plot_protein_coverage(
        fasta_df,
        psm_df,
        metadata_df,
        protein_id,
        grouping,
        selected_groups,
        aggregation_method,
    )
    assert len(result["plots"]) == len(selected_groups)
    assert "messages" not in result
    titles = [plot.layout.title.text for plot in result["plots"]]
    # Check that each group appears in one title
    assert all(any(group in title for group in selected_groups) for title in titles)


def test_plot_protein_coverage_protein_id_not_in_fasta(fasta_df, psm_df, metadata_df):
    protein_id = "NON_EXISTENT_PROTEIN"
    with pytest.raises(
        ValueError, match=f"Protein ID {protein_id} not found in protein dictionary."
    ):
        plot_protein_coverage(
            fasta_df,
            psm_df,
            metadata_df,
            protein_id=protein_id,
            grouping="Group",
            selected_groups=["AD", "CTR"],
            aggregation_method=AggregationMethod.mean,
        )


def test_plot_protein_coverage_selected_groups_not_in_grouping_column(
    fasta_df, psm_df, metadata_df
):
    with pytest.raises(ValueError, match="No peptides found for the samples provided"):
        plot_protein_coverage(
            fasta_df,
            psm_df,
            metadata_df,
            protein_id="P10636-1",
            grouping="Group",
            selected_groups=["NON_EXISTENT_GROUP"],
            aggregation_method=AggregationMethod.mean,
        )


def test_plot_protein_coverage_selected_groups_empty(fasta_df, psm_df, metadata_df):
    with pytest.raises(ValueError, match="No samples provided"):
        plot_protein_coverage(
            fasta_df,
            psm_df,
            metadata_df,
            protein_id="P10636-1",
            grouping="Group",
            selected_groups=[],
            aggregation_method=AggregationMethod.mean,
        )


def test_plot_protein_coverage_selected_groups_none(fasta_df, psm_df, metadata_df):
    with pytest.raises(ValueError, match="No samples provided"):
        plot_protein_coverage(
            fasta_df,
            psm_df,
            metadata_df,
            protein_id="P10636-1",
            grouping="Group",
            selected_groups=None,
            aggregation_method=AggregationMethod.mean,
        )


def test_plot_protein_coverage_metadata_not_matching_peptide_samples(fasta_df, psm_df):
    mismatched_metadata = pd.DataFrame(
        {
            "Sample": ["FAKE_SAMPLE_1", "FAKE_SAMPLE_2"],
            "Group": ["Group1", "Group2"],
        }
    )
    with pytest.raises(ValueError, match="No peptides found for the samples provided"):
        plot_protein_coverage(
            fasta_df,
            psm_df,
            mismatched_metadata,
            protein_id="P10636-1",
            grouping="Group",
            selected_groups=["Group1"],
            aggregation_method=AggregationMethod.mean,
        )


def test_plot_protein_coverage_empty_peptide_df_after_filtering(fasta_df, metadata_df):
    empty_peptide_df = pd.DataFrame(columns=["Sample", "Sequence", "Intensity"])
    with pytest.raises(ValueError, match="No peptides found for the samples provided"):
        plot_protein_coverage(
            fasta_df,
            empty_peptide_df,
            metadata_df,
            protein_id="P10636-1",
            grouping="Group",
            selected_groups=["AD"],
            aggregation_method=AggregationMethod.mean,
        )


def test_plot_protein_coverage_invalid_aggregation_method(
    fasta_df, psm_df, metadata_df
):
    with pytest.raises(ValueError, match="Unknown strategy"):
        plot_protein_coverage(
            fasta_df,
            psm_df,
            metadata_df,
            protein_id="P10636-1",
            grouping="Group",
            selected_groups=["AD"],
            aggregation_method="invalid_method",
        )


def test_plot_protein_coverage_malformed_fasta_sequence(psm_df, metadata_df):
    # Create a fasta_df with a protein that won't match any peptides
    protein_id = "P10636-1"
    fasta_with_unmatched_protein = pd.DataFrame(
        {
            "Protein ID": [protein_id],
            "Protein Sequence": ["Z" * 100],
        }
    )
    with pytest.raises(
        ValueError, match=f"No peptides matched for protein {protein_id}"
    ):
        plot_protein_coverage(
            fasta_with_unmatched_protein,
            psm_df,
            metadata_df,
            protein_id=protein_id,
            grouping="Group",
            selected_groups=["AD"],
            aggregation_method=AggregationMethod.mean,
        )

    fasta_with_empty_sequence = pd.DataFrame(
        {
            "Protein ID": [protein_id],
            "Protein Sequence": [""],
        }
    )
    with pytest.raises(
        ValueError, match="K-mer dictionary is empty. Is the FASTA file valid?"
    ):
        plot_protein_coverage(
            fasta_with_empty_sequence,
            psm_df,
            metadata_df,
            protein_id=protein_id,
            grouping="Group",
            selected_groups=["AD"],
            aggregation_method=AggregationMethod.mean,
        )
