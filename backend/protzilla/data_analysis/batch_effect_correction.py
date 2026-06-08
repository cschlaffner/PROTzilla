from inmoose.pycombat import pycombat_norm
import pandas as pd
from backend.protzilla.utilities.utilities import default_intensity_column
from backend.protzilla.utilities.transform_dfs import long_to_wide
import numpy as np
from backend.protzilla.constants.option_types import NumSVMethods
from backend.protzilla.data_analysis.sva import (
    calculate_n_sv_be,
    calculate_n_sv_leek,
    irwsva,
)
from utilities.utilities import collect_col_for_sample_in_order

# <---- helper functions ---->


# <- ComBat ->
def long_to_pycombat_df(
    protein_df: pd.DataFrame, value_name: str | None = None
) -> pd.DataFrame:
    """
    Transforms a dataframe into a format that can be passed into the combat function.
    ComBat expects the dataframe to have Samples as columns and the Protein IDs as rows.
    Therefore, each Protein ID gets one row with all observations in the different samples as columns.

    :param protein_df: the dataframe that should be transformed into the format suitable for pyCombat

    :return: returns dataframe in a format suitable for use for the combat method from pycombat
    """
    values_name = (
        default_intensity_column(protein_df) if value_name is None else value_name
    )
    return pd.pivot(
        protein_df, index="Protein ID", columns="Sample", values=values_name
    )


def pycombat_df_to_long(
    pycombat_df: pd.DataFrame, original_protein_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Transforms a dataframe from a format suitable for pyCombat (Samples as columns and
    Protein IDs as rows) into the PROTzilla default format where each combination of Sample and Protein ID
    are a row and the column names are "Sample", "Protein ID", "Gene", "_intensity_name_".

    :param pycombat_df: the dataframe that should be transformed into long format
    :param original_protein_df: the original PROTzilla default formatted dataframe which we need to reintroduce
        the gene information

    :return: returns dataframe in the default PROTzilla format
    """
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
    transformed_protein_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    batch_column: str,
) -> list:
    # TODO: for now it is replaced by utility function, but test whether bugs are introduced
    """
    Extracts the batch name for each sample in the transformed_protein_df.
    It preserves the order of the columns in the transformed_protein_df when returning the list of batch assignments.

    :param transformed_protein_df: the dataframe with the samples for which the function extracts the batch assignments
    :param metadata_df: the dataframe that contains the metadata for the transformed_protein_df, including the batch assignments
    :param batch_column: the name of the batch column in metadata

    :return: returns a list with the batch assignments in the order of the samples in the transformed_protein_df
    """
    samples_in_order = transformed_protein_df.columns
    batches_in_order = []
    for sample in samples_in_order:
        batches_in_order.append(
            metadata_df[metadata_df["Sample"] == sample][batch_column].iloc[0]
        )
    return batches_in_order


# <- SVA ->


def turn_group_names_to_int(groups: list) -> list:
    """
    Receives a list of group names and assigns each unique group name a new integer needed for later processing.
    The order of the groups remains untouched.

    :param groups: a list of group assignments, e.g. ["AD", "AD", "CTR", "AD", "CTR", "AD"]

    :return: returns a list with the group assignments in the order of the samples in the transformed_protein_df,
        e.g. [0, 0, 1, 0, 1, 0]
    """
    group_names = {}
    groups_as_integer = []
    max = 0
    for group in groups:
        if group in group_names:
            groups_as_integer.append(group_names[group])
        else:
            group_names[group] = max
            groups_as_integer.append(max)
            max += 1
    return groups_as_integer


# currently unused
# could be useful if we want the surrogate variables listed for each protein even though they are only for each sample
def sv_wide_to_long(
    wide_df: pd.DataFrame, original_long_df: pd.DataFrame, n_surrogate_variables: int
) -> pd.DataFrame:
    """
    Transforms a dataframe from a wide format containing surrogate variables into the PROTzilla default format
    where each combination of Sample and Protein ID are a row and the column names are "Sample", "Protein ID",
    "Gene", "_intensity_name_", "Surrogate Variable 1", "Surrogate Variable 2", ...

    :param wide_df: the dataframe that should be transformed into long format
    :param original_protein_df: the original PROTzilla default formatted dataframe which we need to reintroduce
        the gene information
    :param n_surrogate_variables: Number of surrogate variables

    :return: returns dataframe in the default PROTzilla format with a added surrogate variables columns
    """
    # Read out info from original dataframe
    intensity_name = default_intensity_column(original_long_df)
    # Collect surrogate variable column names
    sv_names = []
    for i in range(n_surrogate_variables):
        sv_names.append(f"Surrogate Variable {i+1}")
    # Turn the wide format into the long format
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
    # sort the columns
    columns = ["Sample", "Protein ID", intensity_name] + sv_names
    intensity_df = intensity_df[columns]
    return intensity_df


def create_sv_dataframe(sv_columns: list, samples_in_order: list[str]) -> pd.DataFrame:
    """
    Creates a surrogate variables dataframe with only Sample and their surrogate variables as columns.

    :param sv_columns: a list of lists containing the surrogate variable for every sample
    :param samples_in_order: samples in order of the surrogate variables

    :return: the surrogate variables dataframe
    """
    sv_names = []
    df = pd.DataFrame()
    for i in range(len(sv_columns)):
        # sv_name = f"Surrogate Variable {i+1}"
        sv_name = f"SV{i+1}"
        sv_names.append(sv_name)
        df[sv_name] = sv_columns[i]
    df["Sample"] = samples_in_order
    df = df[["Sample"] + sv_names]
    return df


# <--LOESS-->


def filter_samples_based_on_group(
    wide_protein_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    group_column: str,
    qc_group_names: list[str],
) -> list:
    """
    Removes all samples from the protein dataframe that are not in one of the specified quality control groups.

    :param wide_protein_df: the dataframe in wide format (with samples as rows) which is to be filtered
    :param metadata_df: the dataframe that contains the metadata for the wide_protein_df, including the group assignments
    :param group_column: the name of the column that specifies the group in the metadata
    :param qc_group_names: list of all group names that should be treated as quality control groups for the LOESS correction

    :return: returns the filtered wide_protein_df which only contains the samples which belong to one of the specified quality control groups
    """
    samples_in_order = wide_protein_df.index
    groups_in_order = []

    for sample in samples_in_order:
        groups_in_order.append(
            metadata_df[metadata_df["Sample"] == sample][group_column].iloc[0]
        )

    filter_samples = []
    for i in range(len(samples_in_order)):
        if groups_in_order[i] not in qc_group_names:
            filter_samples.append(samples_in_order[i])

    return wide_protein_df.drop(index=filter_samples)


def get_batch_protein_dfs(
    wide_protein_df: pd.DataFrame, metadata_df: pd.DataFrame, batch_column: str
) -> list[pd.DataFrame]:
    batches = (
        get_batch_for_each_sample_in_order(
            transformed_protein_df=wide_protein_df,
            metadata_df=metadata_df,
            batch_column=batch_column,
        )
    ).unique()

    return batches


# <---- BECAs ---->


def combat_correction(
    protein_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    par_prior: bool,
    batch_column: str,
) -> dict[str, pd.DataFrame]:
    """
    Corrects the batch effects in the protein data with the batch effect correction algorithm ComBat.

    :param protein_df: the dataframe containing the protein data
    :param metadata_df: the dataframe containing the metadata for the protein data, the metadata should include the batch assignments
    :param par_prior: whether to perform parametric ComBat or nonparametric ComBat
    :param batch_column: the name of the batch column in metadata

    return: a dictionary containing the corrected protein data
    """
    transformed_protein_df = long_to_pycombat_df(protein_df=protein_df)
    batches_in_order = collect_col_for_sample_in_order(
        wide_protein_df=transformed_protein_df.T, metadata_df=metadata_df
    )
    batch_corrected_protein_df = pycombat_norm(
        transformed_protein_df, batches_in_order, par_prior=par_prior
    )
    batch_corrected_protein_df = pycombat_df_to_long(
        batch_corrected_protein_df, protein_df
    )
    return {"protein_df": batch_corrected_protein_df}


def sva_correction(
    protein_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    num_sv_method: str,
    group_column: str,
    seed: int,
) -> dict[str, pd.DataFrame]:
    """
    Corrects the batch effects in the protein data with the batch effect correction algorithm SVA (Surrogate Variable Algorithm).

    :param protein_df: the dataframe containing the protein data
    :param metadata_df: the dataframe containing the metadata for the protein data, the metadata should include the batch assignments
    :param num_sv_method: name of the method how to calculate the number of surrogate variables. Can be either the permutation based method
        for or the asymptotic method by Leek.
    :param group_column: the name of the column that specifies the group in the metadata
    :param seed: Seed for the permutation in the permutation-based calculation of the number of surrogate variables.
        If seed is -1, it means there is no seed (seed=None).

    return: a dictionary containing the corrected protein data and a dataframe with the surrogate variables
    """

    wide_protein_df = long_to_wide(protein_df)
    groups = collect_col_for_sample_in_order(
        wide_protein_df=wide_protein_df,
        metadata_df=metadata_df,
        group_column=group_column,
    )
    groups_int = np.array(turn_group_names_to_int(groups)).reshape(-1, 1)

    dat = (wide_protein_df.T).values
    mod0 = np.ones((len(groups_int), 1))
    mod = np.hstack([mod0, groups_int])

    if num_sv_method == NumSVMethods.be.value:
        if seed == -1:
            seed = None
        n_surrogate_variables = calculate_n_sv_be(dat=dat, mod=mod, seed=seed)
    elif num_sv_method == NumSVMethods.leek.value:
        n_surrogate_variables = calculate_n_sv_leek(dat=dat, mod=mod)
    else:
        raise ValueError(
            "No valid option to calculate the optimal number of surrogate variables selected."
        )

    sv = irwsva(
        dat=dat,
        mod=mod,
        mod0=None,
        n_surrogate_variables=n_surrogate_variables,
    )
    # turn sv to column
    sv_transposed = np.array(sv).T
    # create sv dataframe
    samples_in_order = wide_protein_df.index
    sv_df = create_sv_dataframe(sv_transposed, samples_in_order)

    # TODO: Correct the protein data!!
    return {"protein_df": protein_df, "surrogate_variable_df": sv_df}


def loess_correction(
    protein_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    group_column: str,
    qc_group_names: list[str],
    order: list[str],
    batch_column: str,
) -> dict[str, pd.DataFrame]:
    # TODO: doc string
    wide_protein_df = long_to_wide(protein_df)
    filtered_wide_protein_df = filter_samples_based_on_group(
        wide_protein_df=wide_protein_df,
        metadata_df=metadata_df,
        group_column=group_column,
        qc_group_names=qc_group_names,
    )
    qc_samples = filtered_wide_protein_df.index
    qc_samples_in_order = sorted(qc_samples, key=order.index)
    qc_sample_values = filtered_wide_protein_df.loc[qc_samples_in_order]

    all_samples = wide_protein_df.index
    all_samples_in_order = sorted(all_samples, key=order.index)
    all_sample_values = filtered_wide_protein_df.loc[all_samples_in_order]

    return {"protein_df": protein_df}
