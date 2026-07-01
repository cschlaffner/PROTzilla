import pandas as pd
from backend.protzilla.utilities.transform_dfs import long_to_wide


def transform_to_wide(protein_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms protein df into wide format for csv download.
    The index is reset to have the samples as rows with the samples names included. Otherwise, the sample names would be lost.

    :param protein_df: the dataframe containing protein data to be transformed

    :return: a protein dataframe in wide format
    """
    wide_protein_df = long_to_wide(protein_df)
    return {"debug_data": wide_protein_df.reset_index()}
