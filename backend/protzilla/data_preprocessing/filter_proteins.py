import pandas as pd

from backend.protzilla.constants.option_types import GroupValueRequirement
from backend.protzilla.data_preprocessing.plots import create_bar_plot, create_pie_plot
from backend.protzilla.utilities.transform_dfs import long_to_wide
from backend.protzilla.utilities.utilities import default_intensity_column


# --8<-- [start:by_samples_missing]
def by_samples_missing(
    protein_df: pd.DataFrame | None,
    percentage: float = 0.5,
) -> dict:
    """
    This function filters proteins based on the amount of samples with nan values, if the percentage of nan values
    is below a threshold (percentage).

    :param protein_df: the protein dataframe that should be filtered
    :param percentage: ranging from 0 to 1. Defining the relative share of samples the proteins need to be present in,
        in order for the protein to be kept.
    :return: returns the filtered df as a Dataframe and a dict with a list of Protein IDs that were discarded
        and a list of Protein IDs that were kept
    """
    filter_threshold: int = percentage * len(protein_df.Sample.unique())
    transformed_df = long_to_wide(protein_df)

    remaining_proteins_list = transformed_df.dropna(
        axis=1, thresh=filter_threshold
    ).columns.tolist()
    filtered_proteins_list = (
        transformed_df.drop(remaining_proteins_list, axis=1).columns.unique().tolist()
    )
    filtered_df = protein_df[(protein_df["Protein ID"].isin(remaining_proteins_list))]
    return dict(
        protein_df=filtered_df,
        filtered_proteins=filtered_proteins_list,
        remaining_proteins=remaining_proteins_list,
    )


# --8<-- [end:by_samples_missing]


# --8<-- [start:by_number_of_values_per_group]
def by_number_of_values_per_group(
    protein_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    min_amount: int = 1,
    group_column: str = "Group",
    mode: str = GroupValueRequirement.EVERY_GROUP,
) -> dict:
    """
    This function filters proteins based on the amount of samples with non-missing values per group. Depending on the
    selected mode, a protein is kept if it reaches the minimum amount in every group or in at least one group.

    :param protein_df: the protein dataframe that should be filtered
    :param metadata_df: the metadata dataframe from which to take group labels
    :param min_amount: defines the minimum amount of samples the protein has to have a non-missing intensity in
        (inclusive)
    :param group_column: the column of the metadata dataframe that holds the group labels
    :param mode: whether the minimum amount has to be reached in every group or in at least one group
    :return: returns the filtered df as a Dataframe and a dict with a list of Protein IDs that were discarded
        and a list of Protein IDs that were kept
    """
    if group_column not in metadata_df.columns:
        raise ValueError(
            f"The column {group_column} does not exist in the metadata. "
            f"Available columns are: {', '.join(map(str, metadata_df.columns))}"
        )

    intensity_name = default_intensity_column(protein_df)
    labeled_df = pd.merge(
        protein_df, metadata_df[["Sample", group_column]], on="Sample", how="left"
    )
    non_missing_df = labeled_df[labeled_df[intensity_name].notna()]

    # groups without any value, proteins without any value and proteins that only occur in samples
    # missing from the metadata are dropped by the groupby, so the counts are reindexed onto all
    # proteins and groups to count them as zero instead of losing them silently
    all_proteins = pd.Index(protein_df["Protein ID"].unique()).sort_values()
    all_groups = labeled_df[group_column].dropna().unique()
    values_per_group = (
        non_missing_df.groupby(["Protein ID", group_column])[intensity_name]
        .size()
        .unstack(fill_value=0)
        .reindex(columns=all_groups, fill_value=0)
        .reindex(index=all_proteins, fill_value=0)
    )

    if mode == GroupValueRequirement.AT_LEAST_ONE_GROUP:
        values_per_protein = values_per_group.max(axis=1)
    else:
        values_per_protein = values_per_group.min(axis=1)

    remaining_proteins_list = values_per_protein[
        values_per_protein >= min_amount
    ].index.tolist()
    filtered_proteins_list = values_per_protein.drop(
        remaining_proteins_list
    ).index.tolist()
    filtered_df = protein_df[(protein_df["Protein ID"].isin(remaining_proteins_list))]
    return dict(
        protein_df=filtered_df,
        filtered_proteins=filtered_proteins_list,
        remaining_proteins=remaining_proteins_list,
    )


# --8<-- [end:by_number_of_values_per_group]


# --8<-- [start:by_protein_ids]
def by_protein_ids(protein_df: pd.DataFrame, protein_ids: list[str]) -> dict:
    filtered_df = protein_df[(protein_df["Protein ID"].isin(protein_ids))]
    return dict(protein_df=filtered_df)


# --8<-- [end:by_protein_ids]


# --8<-- [start:keep_n_most_significant_proteins]
def keep_n_most_significant_proteins(
    number_of_proteins_to_keep: int, differentially_expressed_proteins_df: pd.DataFrame
) -> dict:
    """
    This function filters the differentially expressed proteins dataframe to keep only the specified number of
    most significant proteins based on the corrected p-value (-> smaller p-value = more significant). Duplicate protein IDs are removed.

    :param number_of_proteins_to_keep: the number of proteins to retain
    :param differentially_expressed_proteins_df: the dataframe containing differentially expressed proteins with
        corrected p-values (smaller p-value = more significant)
    :return: returns a dict containing the filtered dataframe with the most significant proteins
    """
    filtered_df = (
        differentially_expressed_proteins_df.sort_values(
            "corrected_p_value"
        )  # sort ascending
        .drop_duplicates("Protein ID")  # remove protein_id duplicates
        .head(
            number_of_proteins_to_keep
        )  # keep the n proteins with the smallest p_value
    )
    return dict(differentially_expressed_proteins_df=filtered_df)


# --8<-- [end:keep_n_most_significant_proteins]


def by_samples_missing_plot(
    output_remaining_proteins, output_filtered_proteins, graph_type
):
    return _build_pie_bar_plot(
        output_remaining_proteins, output_filtered_proteins, graph_type
    )


def by_number_of_values_per_group_plot(
    output_remaining_proteins, output_filtered_proteins, graph_type
):
    return _build_pie_bar_plot(
        output_remaining_proteins, output_filtered_proteins, graph_type
    )


def _build_pie_bar_plot(
    output_remaining_proteins, output_filtered_proteins, graph_type
):
    if graph_type == "Pie chart":
        fig = create_pie_plot(
            values_of_sectors=[
                len(output_remaining_proteins),
                len(output_filtered_proteins),
            ],
            names_of_sectors=["Proteins kept", "Proteins filtered"],
            heading="Number of Filtered Proteins",
        )
    elif graph_type == "Bar chart":
        fig = create_bar_plot(
            values_of_sectors=[
                len(output_remaining_proteins),
                len(output_filtered_proteins),
            ],
            names_of_sectors=["Proteins kept", "Proteins filtered"],
            heading="Number of Filtered Proteins",
            y_title="Number of Proteins",
        )
    return [fig]
