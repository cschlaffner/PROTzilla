import pandas as pd
from enum import Enum

from backend.protzilla.utilities.utilities import default_intensity_column


class AggregationMethod(Enum):
    sum = "sum"
    median = "median"
    mean = "mean"
    min = "min"
    max = "max"


def group_replicates(
    metadata_df: pd.DataFrame,
    protein_df: pd.DataFrame,
    aggregation_column: str,
    aggregation_method: str,
) -> dict:
    """
    This function groups replicate samples in the protein dataframe based on a specified
    metadata column and aggregates their intensity values using the provided aggregation method.

    :param metadata_df: the pandas dataframe containing metadata information
    :param protein_df: the pandas dataframe containing the protein information
    :param aggregation_column: the column in the metadata dataframe used to group samples
    :param aggregation_method: the method used to aggregate replicate intensities
                               ("sum", "mean", "median", "min", "max")
    :return: dict containing the protein dataframe with grouped and aggregated samples
    """
    # for each row in the protein_df add the value of the aggregation column of the metadata_df
    # we only keep rows that have a matching sample (MS run) in the metadata
    protein_df = pd.merge(
        protein_df,
        metadata_df[["Sample", aggregation_column]],
        left_on="Sample",
        right_on="Sample",
        how="inner",
    )
    # aggregate intensity values of the protein_df -> each combination of a protein id
    # and a specific value of the aggregation column is one group (= one row in the result)
    aggregation_method = AggregationMethod(aggregation_method)
    protein_df = protein_df.groupby(
        ["Protein ID", aggregation_column], as_index=False
    ).agg({default_intensity_column(protein_df): aggregation_method.value})
    # since there are different samples in each group we lost our "Sample" column
    # since some steps assume that there will be a "Sample" column, we rename the aggregation column
    protein_df.rename(columns={aggregation_column: "Sample"}, inplace=True)
    return dict(protein_df=protein_df)


def metadata_filter_by_samples(
    metadata_df: pd.DataFrame,
    protein_df: pd.DataFrame,
    sample_column: str,
) -> dict:
    """
    Filters the metadata_df such that it only includes info on samples also represented in the protein_df

    :param metadata_df: the pandas dataframe containing metadata information
    :param protein_df: the pandas dataframe containing the protein information
    :return: dict containing the filtered metadata dataframe
    """
    meta_filtered = metadata_df[metadata_df[sample_column].isin(protein_df["Sample"])]
    return dict(metadata_df=meta_filtered)
