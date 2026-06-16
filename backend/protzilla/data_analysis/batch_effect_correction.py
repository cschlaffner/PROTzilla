from inmoose.pycombat import pycombat_norm
import pandas as pd
from joblib import Parallel, delayed

from backend.protzilla.utilities.utilities import (
    default_intensity_column,
    collect_col_for_sample_in_order,
)
from backend.protzilla.utilities.transform_dfs import long_to_wide, wide_to_long
import numpy as np
from backend.protzilla.constants.option_types import NumSVMethods
from backend.protzilla.data_analysis.sva import (
    calculate_n_sv_be,
    calculate_n_sv_leek,
    irwsva,
    fsva,
)
from backend.protzilla.data_analysis.loess import correct_intra_batch_with_loess

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


def filter_samples_based_on_col(
    wide_protein_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    column_name: str,
    filter_names: list[str],
) -> list:
    """
    Removes all samples from the protein dataframe that are not one of the specified assignments for the specific column.

    :param wide_protein_df: the dataframe in wide format (with samples as rows) which is to be filtered
    :param metadata_df: the dataframe that contains the metadata for the wide_protein_df, including the group assignments
    :param column_name: the name of the column that specifies the assignment in the metadata (usually group or batch)
    :param filter_names: list of all assignment names that should be included in the returned filtered protein df

    :return: returns the filtered wide_protein_df which only contains the samples which belong to one of the specified assignments
        of the specified column
    """
    samples_in_order = wide_protein_df.index
    assignment_in_order = []

    for sample in samples_in_order:
        assignment_in_order.append(
            metadata_df[metadata_df["Sample"] == sample][column_name].iloc[0]
        )

    filter_samples = []
    for i in range(len(samples_in_order)):
        if assignment_in_order[i] not in filter_names:
            filter_samples.append(samples_in_order[i])

    return wide_protein_df.drop(index=filter_samples)


def _process_single_batch(
    batch: str,
    wide_protein_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    batch_column: str,
    group_column: str,
    qc_group_names: list[str],
    order_dict: dict,
) -> dict:
    """
    Corrects signal drift within a single batch with the LOESS method.

    :param batch: name of the batch
    :param wide_protein_df: the dataframe that contains the protein data in wide format
    :param metadata_df: the dataframe that contains the metadata for the wide_protein_df, including order, batch and group assignment
    :param batch_column: the name of the column that specifies the batch assignment in the metadata
    :param group_column: the name of the column that specifies the group assignment in the metadata
    :param qc_group_names: list of all group names that specify the quality control samples used to fit the LOESS curve
    :param order_dict: dictionary that maps each sample name to the order number e.g. {Sample1: 0, QC_Sample1: 1, Sample2: 2, ...}

    :return: dictionary with the adjusted batch specific protein dataframe and, if there are any, messages
    """

    filtered_batch_wide_protein_df = filter_samples_based_on_col(
        wide_protein_df=wide_protein_df,
        metadata_df=metadata_df,
        column_name=batch_column,
        filter_names=[batch],
    )
    filtered_batch_sample_wide_protein_df = filter_samples_based_on_col(
        wide_protein_df=filtered_batch_wide_protein_df,
        metadata_df=metadata_df,
        column_name=group_column,
        filter_names=qc_group_names,
    )

    qc_samples = filtered_batch_sample_wide_protein_df.index
    qc_samples_in_order = sorted(qc_samples, key=lambda x: order_dict.get(x))
    qc_sample_values = filtered_batch_sample_wide_protein_df.loc[qc_samples_in_order]

    all_samples = filtered_batch_wide_protein_df.index
    all_samples_in_order = sorted(all_samples, key=lambda x: order_dict.get(x))
    all_samples_values = filtered_batch_wide_protein_df.loc[all_samples_in_order]

    X_qc = np.array([order_dict[s] for s in qc_samples_in_order]).reshape(-1, 1)
    X_all = np.array([order_dict[s] for s in all_samples_in_order]).reshape(-1, 1)

    return correct_intra_batch_with_loess(
        batch_wide_protein_df=filtered_batch_wide_protein_df,
        qc_samples_in_order=X_qc,
        qc_samples_values=qc_sample_values,
        all_samples_in_order=X_all,
        all_samples_values=all_samples_values,
    )


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
        wide_protein_df=transformed_protein_df.T,
        metadata_df=metadata_df,
        col_name=batch_column,
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
        col_name=group_column,
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

    sv, pprob_gam, pprob_b, num_sv = irwsva(
        dat=dat,
        mod=mod,
        mod0=None,
        n_surrogate_variables=n_surrogate_variables,
    )
    (
        cleaned_dat,
        _adjusted,
        _new_sv,
    ) = fsva(
        dbdat=dat, mod=mod, sv=sv, n_sv=num_sv, pprob_gam=pprob_gam, pprob_b=pprob_gam
    )
    cleaned_wide_protein_df = pd.DataFrame(
        cleaned_dat.T, index=wide_protein_df.index, columns=wide_protein_df.columns
    )
    cleaned_protein_df = wide_to_long(cleaned_wide_protein_df, protein_df)
    # turn sv to column
    sv_transposed = np.array(sv).T
    # create sv dataframe
    samples_in_order = wide_protein_df.index
    sv_df = create_sv_dataframe(sv_transposed, samples_in_order)

    return {"protein_df": cleaned_protein_df, "surrogate_variable_df": sv_df}


def loess_correction(
    protein_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    group_column: str,
    qc_group_names: list[str],
    batch_column: str,
    order_column: str,
) -> dict:
    """
    Corrects the batch effects in the protein data with the batch effect correction algorithm LOESS. This correction corrects the signal drift
    within the batches. For distinct batch effect correction one should refer to ComBat or SVA.

    :param protein_df: the dataframe containing the protein data
    :param metadata_df: the dataframe containing the metadata for the protein data, the metadata should include the batch assignments, group assignments
        and the order of the samples
    :param group_column: the name of the column that specifies the group in the metadata
    :param qc_group_names: the list of group names that should be taken as quality control group
    :param batch_column: the name of the column that specifies the batch in the metadata
    :param order_column: the name of the column that specifies the order in the metadata

    return: a dictionary containing the corrected protein data and, if there any, messages
    """
    wide_protein_df = long_to_wide(protein_df)

    metadata_df.sort_values(
        by=[order_column],
        ignore_index=True,
        inplace=True,
    )

    batches = metadata_df[batch_column].unique()

    order = metadata_df["Sample"].tolist()
    order_dict = {sample: i for i, sample in enumerate(order)}

    results = Parallel(n_jobs=-1, verbose=10)(
        delayed(_process_single_batch)(
            batch,
            wide_protein_df,
            metadata_df,
            batch_column,
            group_column,
            qc_group_names,
            order_dict,
        )
        for batch in batches
    )

    messages = []

    # Reassemble the dataframe from the parallel results
    for batch_result in results:
        wide_protein_df.update(batch_result["protein_df"])
        if batch_result["messages"]:
            messages.extend(batch_result["messages"])

    protein_df = wide_to_long(wide_df=wide_protein_df, original_long_df=protein_df)

    return {"protein_df": protein_df, "messages": messages}
