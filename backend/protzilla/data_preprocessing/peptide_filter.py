import pandas as pd
from plotly.graph_objs import Figure

from backend.protzilla.data_preprocessing.plots import create_bar_plot, create_pie_plot


def by_pep_value(peptide_df: pd.DataFrame, threshold: float) -> dict:
    """
    This function filters out all peptides with a PEP value (assigned to all samples
    together for each peptide) below a certain threshold.

    :param protein_df: ms-dataframe, piped through so next methods get proper input
    :type protein_df: pd.Dataframe
    :param peptide_df: the pandas dataframe containing the peptide information
    :type peptide_df: pd.Dataframe
    :param threshold: peptides with a PEP-value below this threshold will be filtered
        out
    :type threshold: float

    :return: dict of intensity-df, piped through, and of peptide_df without the peptides
        below the threshold and of a list with filtered-out peptides (Sequences)
    :rtype: Tuple[pd.Dataframe, dict(pd.Dataframe, list)]
    """

    filtered_peptides = peptide_df[peptide_df["PEP"] < threshold]
    peptide_df.drop(filtered_peptides.index, inplace=True)
    peptide_df.reset_index(drop=True, inplace=True)
    filtered_peptides.reset_index(drop=True, inplace=True)
    filtered_peptides_list = filtered_peptides["Sequence"].unique().tolist()

    return dict(
        peptide_df=peptide_df,
        filtered_peptides=filtered_peptides_list,
    )


def by_pep_value_plot(output_peptide_df, output_filtered_peptides, graph_type):
    value_dict = dict(
        values_of_sectors=[
            len(output_peptide_df),
            len(output_filtered_peptides),
        ],
        names_of_sectors=["Samples kept", "Samples filtered"],
        heading="Number of Filtered Samples",
    )

    if graph_type == "Pie chart":
        fig = create_pie_plot(**value_dict)
    elif graph_type == "Bar chart":
        fig = create_bar_plot(**value_dict)
    return [fig]


def by_existing_proteins(peptide_df: pd.DataFrame, protein_df: pd.DataFrame) -> dict:
    """
    This function filters the peptide dataframe so that only peptides remain whose
    Protein ID exists in the provided protein dataframe.
    :param peptide_df: the pandas dataframe containing the peptide information
    :param protein_df: the pandas dataframe containing the protein information
    :return: dict containing the peptide dataframe filtered to peptides whose
            Protein ID exists in the protein dataframe
    """
    filtered_peptide_df = peptide_df[
        (peptide_df["Protein ID"].isin(protein_df["Protein ID"]))
    ]
    return dict(
        peptide_df=filtered_peptide_df,
    )


def by_existing_samples(peptide_df: pd.DataFrame, protein_df: pd.DataFrame) -> dict:
    """
    This function filters the peptide dataframe so that only peptides remain whose
    Sample exists in the provided protein dataframe.

    :param peptide_df: the pandas dataframe containing the peptide information
    :param protein_df: the pandas dataframe containing the protein information
    :return: dict containing the peptide dataframe filtered to peptides whose
            Sample exists in the protein dataframe
    """
    filtered_peptide_df = peptide_df[peptide_df["Sample"].isin(protein_df["Sample"])]
    return dict(
        peptide_df=filtered_peptide_df,
    )


def peptide_filtering_pie_plot(
    peptide_df: pd.DataFrame, output_peptide_df: pd.DataFrame
) -> list[Figure]:
    fig = create_pie_plot(
        values_of_sectors=[
            len(output_peptide_df),
            len(peptide_df) - len(output_peptide_df),
        ],
        names_of_sectors=["Peptides kept", "Peptides filtered"],
        heading="Number of Filtered Peptides",
    )
    return [fig]
