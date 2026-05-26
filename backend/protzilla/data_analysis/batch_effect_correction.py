from inmoose.pycombat import pycombat_norm
import pandas as pd
from backend.protzilla.utilities.utilities import default_intensity_column
from sklearn import linear_model
from backend.protzilla.utilities.transform_dfs import long_to_wide, wide_to_long
import numpy as np
from sklearn.decomposition import PCA


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
    # Turn the pycombat format into the long format
    intensity_df = pd.melt(
        pycombat_df.reset_index(),
        id_vars="Protein ID",
        var_name="Sample",
        value_name=intensity_name,
    )
    intensity_df.sort_values(
        by=["Sample", "Protein ID"],
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


def reconstruct_original_order(
    original_protein_df: pd.DataFrame, corrected_protein_df: pd.DataFrame
):
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


def turn_group_names_to_int(groups):
    group_names = {}
    y = []
    max = 0
    for group in groups:
        if group in group_names:
            y.append(group_names[group])
        else:
            group_names[group] = max
            y.append(max)
            max += 1
    return y


def get_training_data_and_target_values(
    protein_df: pd.DataFrame, metadata_df: pd.DataFrame
):
    X = long_to_wide(protein_df)
    groups = get_group_for_each_sample_in_order(
        transformed_protein_df=X, metadata_df=metadata_df
    )
    y = turn_group_names_to_int(groups)
    return X, np.array(y).reshape(-1, 1)


def sv_wide_to_long(
    wide_df: pd.DataFrame, original_long_df: pd.DataFrame, n_surrogate_variables: int
):
    # Read out info from original dataframe
    intensity_name = default_intensity_column(original_long_df)
    # Turn the wide format into the long format
    sv_names = []
    for i in range(n_surrogate_variables):
        sv_names.append(f"Surrogate Variable {i+1}")
    intensity_df = pd.melt(
        wide_df.reset_index(),
        id_vars=["Sample"] + sv_names,
        var_name="Protein ID",
        value_name=intensity_name,
    )
    intensity_df.sort_values(
        by=["Sample", "Protein ID"],
        ignore_index=True,
        inplace=True,
    )
    columns = ["Sample", "Protein ID", intensity_name] + sv_names
    intensity_df = intensity_df[columns]
    return intensity_df


def add_sv_columns_to_df(sv_columns: list, df: pd.DataFrame):
    for i in range(len(sv_columns)):
        df[f"Surrogate Variable {i+1}"] = sv_columns[i]
    return df


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


def sva_correction(
    protein_df: pd.DataFrame, metadata_df: pd.DataFrame, n_surrogate_variables
):
    # X has wide format and y is simply the label / primary variable
    wide_protein_df, groups = get_training_data_and_target_values(
        protein_df=protein_df, metadata_df=metadata_df
    )
    # first we take out the effect of the primary variable so we only have BE
    # and other unknown sources of variation in our values
    primary_variables_model = linear_model.LinearRegression()
    primary_variables_model.fit(groups, wide_protein_df)
    primary_variable_signal = primary_variables_model.predict(groups)
    cleaned_values = wide_protein_df - primary_variable_signal

    # Next, we need to perform SVD (in the original SVA, but we can use PCA as well)
    pca_model = PCA(n_components=n_surrogate_variables)
    sv = pca_model.fit_transform(cleaned_values)

    # Now, we add the surrogate variables to a df that also contains protein ids and samples
    sv_transposed = np.array(sv).T

    wide_surrogate_variable_df = add_sv_columns_to_df(sv_transposed, wide_protein_df)
    # this still contains the gene information after the wide_to_long transformation
    # (I should think about whether I want this)
    surrogate_variable_df = sv_wide_to_long(
        wide_surrogate_variable_df, protein_df, n_surrogate_variables
    )

    return {"protein_df": protein_df, "surrogate_variable_df": surrogate_variable_df}
