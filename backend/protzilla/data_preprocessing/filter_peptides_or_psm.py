import pandas as pd
from plotly.graph_objs import Figure

from backend.protzilla.data_preprocessing.plots import create_bar_plot, create_pie_plot


def by_pep_value(
    peptide_or_psm_df: pd.DataFrame, threshold: float
) -> (pd.DataFrame, list):
    """
    This function filters out all peptides/psm with a PEP value (assigned to all samples
    together for each peptide) below a certain threshold.

    :param protein_df: ms-dataframe, piped through so next methods get proper input
    :param peptide_or_psm_df: the pandas dataframe containing the peptide/psm information
    :param threshold: peptides/psm with a PEP-value below this threshold will be filtered out

    :return: peptide_or_psm_df without the peptides below the threshold and of a list with
    filtered-out peptides (Sequences)
    """

    filtered = peptide_or_psm_df[peptide_or_psm_df["PEP"] < threshold]
    peptide_or_psm_df.drop(filtered.index, inplace=True)
    peptide_or_psm_df.reset_index(drop=True, inplace=True)
    filtered.reset_index(drop=True, inplace=True)
    filtered_peptides_or_psm_list = filtered["Sequence"].unique().tolist()

    return peptide_or_psm_df, filtered_peptides_or_psm_list


def filter_peptides_by_pep_value(peptide_df: pd.DataFrame, threshold: float) -> dict:
    peptide_df, filtered_peptides_list = by_pep_value(peptide_df, threshold)
    return dict(
        peptide_df=peptide_df,
        filtered_peptides=filtered_peptides_list,
    )


def filter_psm_by_pep_value(psm_df: pd.DataFrame, threshold: float) -> dict:
    psm_df, filtered_psm_list = by_pep_value(psm_df, threshold)
    return dict(
        peptide_df=psm_df,
        filtered_peptides=filtered_psm_list,
    )


def by_pep_value_plot(
    output_peptide_or_psm_df, output_filtered_peptides_or_psm, graph_type
):
    value_dict = dict(
        values_of_sectors=[
            len(output_peptide_or_psm_df),
            len(output_filtered_peptides_or_psm),
        ],
        names_of_sectors=["Samples kept", "Samples filtered"],
        heading="Number of Filtered Samples",
    )

    if graph_type == "Pie chart":
        fig = create_pie_plot(**value_dict)
    elif graph_type == "Bar chart":
        fig = create_bar_plot(**value_dict)
    return [fig]


def filter_peptides_by_pep_value_plot(
    output_peptide_df, output_filtered_peptides, graph_type
):
    return by_pep_value_plot(output_peptide_df, output_filtered_peptides, graph_type)


def filter_psm_by_pep_value_plot(output_psm_df, output_filtered_psm, graph_type):
    return by_pep_value_plot(output_psm_df, output_filtered_psm, graph_type)


def by_existing_proteins(
    peptide_or_psm_df: pd.DataFrame, protein_df: pd.DataFrame
) -> pd.DataFrame:
    """
    This function filters a peptide or psm dataframe so that only peptides or psm remain whose
    Protein ID exists in the provided protein dataframe.
    :param peptide_or_psm_df: the pandas dataframe containing the peptide or psm information
    :param protein_df: the pandas dataframe containing the protein information
    :return: the input dataframe filtered to peptides/psm whose Protein ID exists in the protein dataframe
    """
    filtered_peptide_df = peptide_or_psm_df[
        (peptide_or_psm_df["Protein ID"].isin(protein_df["Protein ID"]))
    ]
    return filtered_peptide_df


def filter_peptides_by_existing_proteins(
    peptide_df: pd.DataFrame, protein_df: pd.DataFrame
) -> dict:
    return dict(peptide_df=by_existing_proteins(peptide_df, protein_df))


def filter_psm_by_existing_proteins(
    psm_df: pd.DataFrame, protein_df: pd.DataFrame
) -> dict:
    return dict(peptide_df=by_existing_proteins(psm_df, protein_df))


def by_existing_samples(
    peptide_or_psm_df: pd.DataFrame, protein_df: pd.DataFrame
) -> pd.DataFrame:
    """
    This function filters the peptide or psm dataframe so that only peptides or psm remain whose
    sample exists in the provided protein dataframe.

    :param peptide_or_psm_df: the pandas dataframe containing the peptide or psm information
    :param protein_df: the pandas dataframe containing the protein information
    :return: the input dataframe filtered to peptides/psm whose sample exists in the protein dataframe
    """
    filtered_peptide_df = peptide_or_psm_df[
        peptide_or_psm_df["Sample"].isin(protein_df["Sample"])
    ]
    return filtered_peptide_df


def filter_peptides_by_existing_samples(
    peptide_df: pd.DataFrame, protein_df: pd.DataFrame
) -> dict:
    return dict(
        peptide_df=by_existing_samples(peptide_df, protein_df),
    )


def filter_psm_by_existing_samples(
    psm_df: pd.DataFrame, protein_df: pd.DataFrame
) -> dict:
    return dict(
        peptide_df=by_existing_samples(psm_df, protein_df),
    )


def filtering_pie_plot(
    peptide_or_psm_df: pd.DataFrame, output_peptide_or_psm_df: pd.DataFrame
) -> list[Figure]:
    fig = create_pie_plot(
        values_of_sectors=[
            len(output_peptide_or_psm_df),
            len(peptide_or_psm_df) - len(output_peptide_or_psm_df),
        ],
        names_of_sectors=["Peptides kept", "Peptides filtered"],
        heading="Number of Filtered Peptides",
    )
    return [fig]


def peptide_filtering_pie_plot(
    peptide_df: pd.DataFrame, output_peptide_df: pd.DataFrame
) -> list[Figure]:
    return filtering_pie_plot(peptide_df, output_peptide_df)


def psm_filtering_pie_plot(
    psm_df: pd.DataFrame, output_psm_df: pd.DataFrame
) -> list[Figure]:
    return filtering_pie_plot(psm_df, output_psm_df)
