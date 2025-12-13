import pandas as pd

from backend.protzilla.data_preprocessing.plots import create_bar_plot, create_pie_plot

from backend.protzilla.utilities.utilities import default_intensity_column

from ..utilities.transform_dfs import long_to_wide


def by_samples_missing(
    protein_df: pd.DataFrame | None,
    peptide_df: pd.DataFrame | None,
    percentage: float = 0.5,
) -> dict:
    """
    This function filters proteins based on the amount of samples with nan values, if the percentage of nan values
    is below a threshold (percentage).

    :param protein_df: the protein dataframe that should be filtered
    :param peptide_df: the peptide dataframe that should be filtered in accordance to the intensity dataframe (optional)
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
    filtered_peptide_df = None
    if peptide_df is not None:
        filtered_peptide_df = peptide_df[
            (peptide_df["Protein ID"].isin(remaining_proteins_list))
        ]
    return dict(
        protein_df=filtered_df,
        peptide_df=filtered_peptide_df,
        filtered_proteins=filtered_proteins_list,
        remaining_proteins=remaining_proteins_list,
    )


def by_silac_ratios(
    protein_df: pd.DataFrame,
    peptide_df: pd.DataFrame | None,
    min_amount: int,
) -> dict:
    """
    This function filters proteins based on the amount of samples with unique SILAC ratios.

    :param protein_df: the protein dataframe that should be filtered
    :param peptide_df: the peptide dataframe that should be filtered in accordance to the intensity dataframe (optional)
    :param min_amount: defines the minimum amount of samples the protein has to have a unique intensity in (inclusive)
    :return: returns the filtered df as a Dataframe and a dict with a list of Protein IDs that were discarded
        and a list of Protein IDs that were kept
    """

    intensity_name = default_intensity_column(protein_df)
    unique_ratio_count = protein_df.groupby("Protein ID")[intensity_name].unique()
    remaining_proteins_list = unique_ratio_count[
        unique_ratio_count >= min_amount
    ].index.tolist()
    filtered_proteins_list = unique_ratio_count.drop(
        remaining_proteins_list
    ).index.tolist()
    filtered_df = protein_df[(protein_df["Protein ID"].isin(remaining_proteins_list))]
    filtered_peptide_df = None
    if peptide_df is not None:
        filtered_peptide_df = peptide_df[
            (peptide_df["Protein ID"].isin(remaining_proteins_list))
        ]
    return dict(
        protein_df=filtered_df,
        peptide_df=filtered_peptide_df,
        filtered_proteins=filtered_proteins_list,
        remaining_proteins=remaining_proteins_list,
    )


def by_samples_missing_plot(
    output_remaining_proteins, output_filtered_proteins, graph_type
):
    return _build_pie_bar_plot(
        output_remaining_proteins, output_filtered_proteins, graph_type
    )


def by_silac_ratios_plot(
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
