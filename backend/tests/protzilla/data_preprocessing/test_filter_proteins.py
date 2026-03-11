import numpy as np
import pandas as pd
import pytest

from backend.protzilla.constants.data_types import DataKey
from backend.protzilla.data_preprocessing.filter_proteins import (
    by_samples_missing,
    by_samples_missing_plot,
    by_number_of_values_per_group,
    by_number_of_values_per_group_plot,
)
from backend.protzilla.data_preprocessing.peptide_filter import by_existing_proteins
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

    peptide_filtering_output = by_existing_proteins(
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

    peptide_filtering_output = by_existing_proteins(
        peptides_df, method_output["protein_df"]
    )

    assert_peptide_filtering_matches_protein_filtering(
        method_output[DataKey.PROTEIN_DF],
        peptides_df,
        peptide_filtering_output[DataKey.PEPTIDE_DF],
        "Protein ID",
    )
