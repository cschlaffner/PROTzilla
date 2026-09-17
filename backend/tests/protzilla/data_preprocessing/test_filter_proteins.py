import numpy as np
import pandas as pd
import pytest

from backend.protzilla.constants.data_types import DataKey
from backend.protzilla.constants.option_types import GroupValueRequirement
from backend.protzilla.data_preprocessing.filter_proteins import (
    by_samples_missing,
    by_samples_missing_plot,
    by_number_of_values_per_group,
    by_number_of_values_per_group_plot,
    by_protein_ids,
    keep_n_most_significant_proteins,
)
from backend.protzilla.data_preprocessing.filter_peptides_or_psm import (
    filter_peptides_by_existing_proteins,
)
from backend.tests.protzilla.data_preprocessing.test_peptide_preprocessing import (
    assert_peptide_filtering_matches_protein_filtering,
)


@pytest.fixture
def filter_proteins_df():
    filter_proteins_df = pd.DataFrame(
        (
            ["Sample2", "Protein2", "Gene2", 1],
            ["Sample4", "Protein4", "Gene4", 1],
            ["Sample1", "Protein1", "Gene1", np.nan],
            ["Sample3", "Protein3", "Gene3", 1],
            ["Sample1", "Protein2", "Gene2", 1],
            ["Sample1", "Protein3", "Gene3", 1],
            ["Sample2", "Protein1", "Gene1", np.nan],
            ["Sample2", "Protein3", "Gene3", 1],
            ["Sample3", "Protein1", "Gene1", np.nan],
            ["Sample3", "Protein2", "Gene2", 1],
            ["Sample4", "Protein2", "Gene2", np.nan],
            ["Sample4", "Protein3", "Gene3", 1],
            ["Sample1", "Protein4", "Gene4", np.nan],
            ["Sample2", "Protein4", "Gene4", 1],
            ["Sample3", "Protein4", "Gene4", np.nan],
            ["Sample4", "Protein1", "Gene1", 1],
        ),
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    filter_proteins_df.sort_values(
        by=["Sample", "Protein ID"], ignore_index=True, inplace=True
    )

    return filter_proteins_df


@pytest.fixture
def filter_proteins_by_samples_missing_df():
    df = pd.DataFrame(
        (
            ["Sample1", "Protein1", "Gene1", 1],
            ["Sample1", "Protein2", "Gene1", np.nan],
            ["Sample1", "Protein3", "Gene1", np.nan],
            ["Sample1", "Protein4", "Gene1", np.nan],
            ["Sample1", "Protein5", "Gene1", np.nan],
            ["Sample2", "Protein1", "Gene1", 1],
            ["Sample2", "Protein2", "Gene1", 1],
            ["Sample2", "Protein3", "Gene1", np.nan],
            ["Sample2", "Protein4", "Gene1", np.nan],
            ["Sample2", "Protein5", "Gene1", np.nan],
            ["Sample3", "Protein1", "Gene1", 1],
            ["Sample3", "Protein2", "Gene1", 1],
            ["Sample3", "Protein3", "Gene1", 1],
            ["Sample3", "Protein4", "Gene1", np.nan],
            ["Sample3", "Protein5", "Gene1", np.nan],
            ["Sample4", "Protein1", "Gene1", 1],
            ["Sample4", "Protein2", "Gene1", 1],
            ["Sample4", "Protein3", "Gene1", 1],
            ["Sample4", "Protein4", "Gene1", 1],
            ["Sample4", "Protein5", "Gene1", np.nan],
        ),
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    return df


@pytest.fixture
def filter_proteins_by_number_of_values_per_group_df():
    filter_proteins_df = pd.DataFrame(
        (
            ["Sample2", "Protein2", "Gene2", 0.5],
            ["Sample4", "Protein4", "Gene4", 0.7],
            ["Sample1", "Protein1", "Gene1", np.nan],
            ["Sample3", "Protein3", "Gene3", 0.8],
            ["Sample1", "Protein2", "Gene2", 0.5],
            ["Sample1", "Protein3", "Gene3", 1.2],
            ["Sample2", "Protein1", "Gene1", np.nan],
            ["Sample2", "Protein3", "Gene3", 0.35],
            ["Sample3", "Protein1", "Gene1", np.nan],
            ["Sample3", "Protein2", "Gene2", np.nan],
            ["Sample4", "Protein2", "Gene2", np.nan],
            ["Sample4", "Protein3", "Gene3", 0.85],
            ["Sample1", "Protein4", "Gene4", np.nan],
            ["Sample2", "Protein4", "Gene4", 0.51],
            ["Sample3", "Protein4", "Gene4", 0.9],
            ["Sample4", "Protein1", "Gene1", 0.25],
        ),
        columns=["Sample", "Protein ID", "Gene", "Ratio H/L"],
    )

    filter_proteins_df.sort_values(
        by=["Sample", "Protein ID"], ignore_index=True, inplace=True
    )

    return filter_proteins_df


@pytest.fixture
def filter_proteins_by_number_of_values_per_group_metadata_df():
    return pd.DataFrame(
        {
            "Group": ["POS", "NEG", "NEG", "POS"],
            "Sample": ["Sample1", "Sample2", "Sample3", "Sample4"],
        }
    )


def test_filter_proteins_by_missing_samples(
    filter_proteins_by_samples_missing_df, peptides_df, show_figures
):
    method_output = by_samples_missing(
        filter_proteins_by_samples_missing_df, percentage=1.0
    )

    fig = by_samples_missing_plot(
        method_output["remaining_proteins"],
        method_output["filtered_proteins"],
        "Pie chart",
    )[0]
    if show_figures:
        fig.show()
    assert method_output["filtered_proteins"] == [
        "Protein2",
        "Protein3",
        "Protein4",
        "Protein5",
    ]

    method_output = by_samples_missing(
        filter_proteins_by_samples_missing_df, percentage=0.5
    )

    assert method_output["filtered_proteins"] == ["Protein4", "Protein5"]

    method_output = by_samples_missing(
        filter_proteins_by_samples_missing_df, percentage=0.0
    )

    peptide_filtering_output = filter_peptides_by_existing_proteins(
        peptides_df, method_output["protein_df"]
    )

    assert method_output["filtered_proteins"] == []

    assert_peptide_filtering_matches_protein_filtering(
        method_output[DataKey.PROTEIN_DF],
        peptides_df,
        peptide_filtering_output[DataKey.PEPTIDE_DF],
        "Protein ID",
    )


def test_filter_proteins_by_values_per_group(
    filter_proteins_by_number_of_values_per_group_df,
    filter_proteins_by_number_of_values_per_group_metadata_df,
    peptides_df,
    show_figures,
):

    method_output = by_number_of_values_per_group(
        filter_proteins_by_number_of_values_per_group_df,
        filter_proteins_by_number_of_values_per_group_metadata_df,
        min_amount=2,
    )

    fig = by_number_of_values_per_group_plot(
        method_output["remaining_proteins"],
        method_output["filtered_proteins"],
        "Pie chart",
    )[0]
    if show_figures:
        fig.show()

    assert method_output["remaining_proteins"] == ["Protein3"]
    assert method_output["filtered_proteins"] == ["Protein1", "Protein2", "Protein4"]

    method_output = by_number_of_values_per_group(
        filter_proteins_by_number_of_values_per_group_df,
        filter_proteins_by_number_of_values_per_group_metadata_df,
        min_amount=4,
    )

    assert method_output["remaining_proteins"] == []
    assert method_output["filtered_proteins"] == [
        "Protein1",
        "Protein2",
        "Protein3",
        "Protein4",
    ]

    method_output = by_number_of_values_per_group(
        filter_proteins_by_number_of_values_per_group_df,
        filter_proteins_by_number_of_values_per_group_metadata_df,
        min_amount=4,
    )

    peptide_filtering_output = filter_peptides_by_existing_proteins(
        peptides_df, method_output["protein_df"]
    )

    assert_peptide_filtering_matches_protein_filtering(
        method_output[DataKey.PROTEIN_DF],
        peptides_df,
        peptide_filtering_output[DataKey.PEPTIDE_DF],
        "Protein ID",
    )


def test_filter_proteins_by_protein_ids_filters_correctly(filter_proteins_df):
    protein_ids = ["Protein1", "Protein3"]
    result = by_protein_ids(filter_proteins_df, protein_ids)

    filtered_protein_df = result["protein_df"]

    expected_protein_df = filter_proteins_df[
        filter_proteins_df["Protein ID"].isin(protein_ids)
    ]

    pd.testing.assert_frame_equal(
        filtered_protein_df.reset_index(drop=True),
        expected_protein_df.reset_index(drop=True),
    )


def test_keep_n_most_significant_proteins_with_duplicates():
    df = pd.DataFrame(
        {
            "Protein ID": ["p1", "p1", "p2", "p3", "p4"],
            "corrected_p_value": [0.05, 0.01, 0.02, 0.03, 0.04],
        }
    )

    result = keep_n_most_significant_proteins(3, df)
    result_df = result["differentially_expressed_proteins_df"]

    expected_proteins = ["p1", "p2", "p3"]
    expected_p_values = [0.01, 0.02, 0.03]

    assert len(result_df) == 3
    assert result_df["Protein ID"].tolist() == expected_proteins
    assert result_df["corrected_p_value"].tolist() == expected_p_values


def test_keep_n_most_significant_proteins_with_less_rows_than_requested():
    df = pd.DataFrame(
        {
            "Protein ID": ["p1", "p2"],
            "corrected_p_value": [0.01, 0.02],
        }
    )

    result = keep_n_most_significant_proteins(5, df)
    result_df = result["differentially_expressed_proteins_df"]

    assert len(result_df) == 2


@pytest.fixture
def cell_line_protein_df():
    """Two cell lines with three replicates each, plus one sample missing from the metadata."""
    rows = []
    intensities = {
        # valid in every LineA replicate, missing throughout LineB
        "ProteinOneGroup": [0.1, 0.2, 0.3, np.nan, np.nan, np.nan],
        # valid everywhere
        "ProteinBothGroups": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
        # three valid values in LineA, but all of them identical
        "ProteinTied": [0.5, 0.5, 0.5, np.nan, np.nan, np.nan],
        # never measured
        "ProteinAllMissing": [np.nan] * 6,
    }
    samples = ["Sample1", "Sample2", "Sample3", "Sample4", "Sample5", "Sample6"]
    for protein, values in intensities.items():
        for sample, value in zip(samples, values):
            rows.append([sample, protein, value])
    # only present in a sample that has no metadata row
    rows.append(["Sample7", "ProteinUnlabeled", 0.9])

    return pd.DataFrame(
        rows, columns=["Sample", "Protein ID", "Intensity"]
    ).sort_values(by=["Sample", "Protein ID"], ignore_index=True)


@pytest.fixture
def cell_line_metadata_df():
    return pd.DataFrame(
        {
            "Sample": [
                "Sample1",
                "Sample2",
                "Sample3",
                "Sample4",
                "Sample5",
                "Sample6",
            ],
            "CellLine": ["LineA", "LineA", "LineA", "LineB", "LineB", "LineB"],
            "Batch": ["Batch1", "Batch2", "Batch3", "Batch1", "Batch2", "Batch3"],
        }
    )


def test_filter_proteins_by_values_per_group_keeps_protein_valid_in_at_least_one_group(
    cell_line_protein_df, cell_line_metadata_df
):
    method_output = by_number_of_values_per_group(
        cell_line_protein_df,
        cell_line_metadata_df,
        min_amount=2,
        group_column="CellLine",
        mode=GroupValueRequirement.AT_LEAST_ONE_GROUP,
    )

    assert "ProteinOneGroup" in method_output["remaining_proteins"]


def test_filter_proteins_by_values_per_group_filters_protein_missing_in_one_group(
    cell_line_protein_df, cell_line_metadata_df
):
    method_output = by_number_of_values_per_group(
        cell_line_protein_df,
        cell_line_metadata_df,
        min_amount=2,
        group_column="CellLine",
        mode=GroupValueRequirement.EVERY_GROUP,
    )

    assert "ProteinOneGroup" in method_output["filtered_proteins"]
    assert "ProteinBothGroups" in method_output["remaining_proteins"]


def test_filter_proteins_by_values_per_group_counts_repeated_intensities_separately(
    cell_line_protein_df, cell_line_metadata_df
):
    method_output = by_number_of_values_per_group(
        cell_line_protein_df,
        cell_line_metadata_df,
        min_amount=3,
        group_column="CellLine",
        mode=GroupValueRequirement.AT_LEAST_ONE_GROUP,
    )

    assert "ProteinTied" in method_output["remaining_proteins"]


def test_filter_proteins_by_values_per_group_reports_protein_without_any_values(
    cell_line_protein_df, cell_line_metadata_df
):
    method_output = by_number_of_values_per_group(
        cell_line_protein_df,
        cell_line_metadata_df,
        min_amount=1,
        group_column="CellLine",
        mode=GroupValueRequirement.AT_LEAST_ONE_GROUP,
    )

    assert "ProteinAllMissing" in method_output["filtered_proteins"]


def test_filter_proteins_by_values_per_group_reports_protein_of_unlabeled_sample(
    cell_line_protein_df, cell_line_metadata_df
):
    method_output = by_number_of_values_per_group(
        cell_line_protein_df,
        cell_line_metadata_df,
        min_amount=1,
        group_column="CellLine",
        mode=GroupValueRequirement.AT_LEAST_ONE_GROUP,
    )

    assert "ProteinUnlabeled" in method_output["filtered_proteins"]
    assert "ProteinUnlabeled" not in method_output["protein_df"]["Protein ID"].tolist()


def test_filter_proteins_by_values_per_group_uses_the_selected_group_column(
    cell_line_protein_df, cell_line_metadata_df
):
    by_cell_line = by_number_of_values_per_group(
        cell_line_protein_df,
        cell_line_metadata_df,
        min_amount=1,
        group_column="CellLine",
        mode=GroupValueRequirement.EVERY_GROUP,
    )
    by_batch = by_number_of_values_per_group(
        cell_line_protein_df,
        cell_line_metadata_df,
        min_amount=1,
        group_column="Batch",
        mode=GroupValueRequirement.EVERY_GROUP,
    )

    # LineB has no values at all, but every batch contains one of the LineA replicates
    assert "ProteinOneGroup" in by_cell_line["filtered_proteins"]
    assert "ProteinOneGroup" in by_batch["remaining_proteins"]


def test_filter_proteins_by_values_per_group_rejects_unknown_group_column(
    cell_line_protein_df, cell_line_metadata_df
):
    with pytest.raises(ValueError, match="CellType"):
        by_number_of_values_per_group(
            cell_line_protein_df,
            cell_line_metadata_df,
            min_amount=1,
            group_column="CellType",
        )
