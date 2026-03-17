import pandas as pd
from enum import Enum


class AggregationMethod(Enum):
    no_aggregation = "no aggregation"
    sum = "sum"
    median = "median"
    mean = "mean"

def metadata_adjustment(metadata_df: pd.DataFrame, protein_df: pd.DataFrame, aggregation_column: str, aggregation_method: str) -> dict:
    protein_df = pd.merge(
        protein_df,
        metadata_df["MS run", "Sample"],
        left_on="Sample",
        right_on="MS run",
        how="inner",
    )
    aggregation_method = AggregationMethod(aggregation_method)
    if aggregation_method.value != AggregationMethod.no_aggregation.value:
        protein_df = protein_df.groupby(
            ["Protein ID", aggregation_column], as_index=False
        ).agg(aggregation_method.value)
    return dict(protein_df=protein_df, metadata_df=metadata_df)