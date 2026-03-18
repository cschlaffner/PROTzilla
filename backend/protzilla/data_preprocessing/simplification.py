import pandas as pd
from enum import Enum

from protzilla.utilities.utilities import default_intensity_column


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
    protein_df = pd.merge(
        protein_df,
        metadata_df[["Sample", aggregation_column]],
        left_on="Sample",
        right_on="Sample",
        how="inner",
    )
    aggregation_method = AggregationMethod(aggregation_method)
    protein_df = protein_df.groupby(
        ["Protein ID", aggregation_column], as_index=False
    ).agg({default_intensity_column(protein_df): aggregation_method.value})
    protein_df.rename(columns={aggregation_column: "Sample"}, inplace=True)
    return dict(protein_df=protein_df, metadata_df=metadata_df)
