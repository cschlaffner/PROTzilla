from curses import meta

from inmoose.pycombat import pycombat_norm
import pandas as pd
from backend.protzilla.utilities.utilities import default_intensity_column
from sklearn import linear_model
from backend.protzilla.utilities.transform_dfs import long_to_wide


# <---- helper functions ---->
def long_to_pycombat_df(
    protein_df: pd.DataFrame, value_name: str | None = None
) -> pd.DataFrame:
    """
    This function transforms a dataframe into a format that can be passed into the combat function.
    ComBat expects the dataframe to have Samples as columns and the Protein IDs as rows.
    Therefore, each Protein ID gets one row with all observations in the different samples as columns.

    :param protein_df: the dataframe that should be transformed into
        long format
        :type protein_df: pd.DataFrame

    :return: returns dataframe in a format suitable for use for the combat method from pycombat
    """
    values_name = (
        default_intensity_column(protein_df) if value_name is None else value_name
    )
    return pd.pivot(
        protein_df, index="Protein ID", columns="Sample", values=values_name
    )


def pycombat_df_to_long(pycombat_df: pd.DataFrame, original_protein_df: pd.DataFrame):
    # Read out info from original dataframe
    intensity_name = default_intensity_column(original_protein_df)
    gene_info = original_protein_df["Gene"]
    # Turn the wide format into the long format
    intensity_df = pd.melt(
        pycombat_df.reset_index(),
        id_vars="Protein ID",
        var_name="Sample",
        value_name=intensity_name,
    )
    intensity_df.sort_values(
        by=["Protein ID", "Sample"],
        ignore_index=True,
        inplace=True,
    )
    intensity_df.insert(2, "Gene", gene_info)

    return intensity_df


def get_batch_for_each_sample_in_order(
    transformed_protein_df: pd.DataFrame, metadata_df: pd.DataFrame
):
    samples_in_order = transformed_protein_df.columns
    batches_in_order = []
    for sample in samples_in_order:
        batches_in_order.append(
            metadata_df[metadata_df["Sample"] == sample]["Batch"].iloc[0]
        )
    return batches_in_order

def reconstruct_original_order(original_protein_df: pd.DataFrame, corrected_protein_df: pd.DataFrame):
    pass

def get_group_for_each_sample_in_order(
    transformed_protein_df: pd.DataFrame, metadata_df: pd.DataFrame
):
    samples_in_order = transformed_protein_df.index
    groups_in_order = []
    for sample in samples_in_order:
        groups_in_order.append(
            metadata_df[metadata_df["Sample"] == sample]["Group"].iloc[0]
        )
    return groups_in_order


def get_training_data_and_target_values(
    protein_df: pd.DataFrame, metadata_df: pd.DataFrame
):
    X = long_to_wide(protein_df)
    y = get_group_for_each_sample_in_order(
        transformed_protein_df=X, metadata_df=metadata_df
    )
    return X, y


# <---- BECAs ---->


def combat_correction(protein_df: pd.DataFrame, metadata_df: pd.DataFrame):
    transformed_protein_df = long_to_pycombat_df(protein_df=protein_df)
    batches_in_order = get_batch_for_each_sample_in_order(
        transformed_protein_df=transformed_protein_df, metadata_df=metadata_df
    )
    batch_corrected_protein_df = pycombat_norm(transformed_protein_df, batches_in_order)
    batch_corrected_protein_df = pycombat_df_to_long(
        batch_corrected_protein_df, protein_df
    )
    return {"protein_df": batch_corrected_protein_df}


def sva_correction(protein_df: pd.DataFrame, metadata_df: pd.DataFrame):
    X, y = get_training_data_and_target_values(
        protein_df=protein_df, metadata_df=metadata_df
    )
    return {"protein_df": protein_df}
