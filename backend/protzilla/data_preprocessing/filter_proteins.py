import pandas as pd

from backend.protzilla.data_preprocessing.plots import create_bar_plot, create_pie_plot
from backend.protzilla.utilities.utilities import default_intensity_column

from backend.protzilla.utilities.transform_dfs import long_to_wide


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


def by_number_of_values_per_group(
    protein_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    min_amount: int = 1,
) -> dict:
    """
    This function filters proteins based on the amount of samples with unique values per group. Only proteins with
    at least the specified amount of samples in each group are kept.

    :param protein_df: the protein dataframe that should be filtered
    :param metadata_df: the metadata dataframe from which to take group labels
    :param min_amount: defines the minimum amount of samples the protein has to have a unique intensity in (inclusive)
    :return: returns the filtered df as a Dataframe and a dict with a list of Protein IDs that were discarded
        and a list of Protein IDs that were kept
    """

    intensity_name = default_intensity_column(protein_df)
    labeled_df = pd.merge(protein_df, metadata_df, on="Sample", how="left")
    unique_ratio_count = (
        labeled_df.groupby(["Protein ID", "Group"])[intensity_name]
        .nunique()
        .groupby("Protein ID")
        .min()
    )
    remaining_proteins_list = unique_ratio_count[
        unique_ratio_count >= min_amount
    ].index.tolist()
    filtered_proteins_list = unique_ratio_count.drop(
        remaining_proteins_list
    ).index.tolist()
    filtered_df = protein_df[(protein_df["Protein ID"].isin(remaining_proteins_list))]
    return dict(
        protein_df=filtered_df,
        filtered_proteins=filtered_proteins_list,
        remaining_proteins=remaining_proteins_list,
    )


def by_protein_ids(protein_df: pd.DataFrame, protein_ids: list[str]) -> dict:
    filtered_df = protein_df[(protein_df["Protein ID"].isin(protein_ids))]
    return dict(protein_df=filtered_df)


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
