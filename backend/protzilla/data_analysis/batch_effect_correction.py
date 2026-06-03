from inmoose.pycombat import pycombat_norm
import pandas as pd
from backend.protzilla.utilities.utilities import default_intensity_column
from sklearn import linear_model
from backend.protzilla.utilities.transform_dfs import long_to_wide
import numpy as np
from sklearn.decomposition import PCA
from scipy.stats import f
from statsmodels.stats.multitest import fdrcorrection
from typing import Any
from backend.protzilla.constants.option_types import NumSVMethods


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
        :type protein_df: pd.DataFrame

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
        :type pycombat_df: pd.DataFrame
    :param original_protein_df: the original PROTzilla default formatted dataframe which we need to reintroduce
        the gene information
        :type original_protein_df: pd.DataFrame

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
    transformed_protein_df: pd.DataFrame, metadata_df: pd.DataFrame
) -> list:
    """
    Extracts the batch name for each sample in the transformed_protein_df.
    It preserves the order of the columns in the transformed_protein_df when returning the list of batch assignments.

    :param transformed_protein_df: the dataframe with the samples for which the function extracts the batch assignments
        :type transformed_protein_df: pd.DataFrame
    :param metadata_df: the dataframe that contains the metadata for the transformed_protein_df, including the batch assignments
        :type metadata_df: pd.DataFrame

    :return: returns a list with the batch assignments in the order of the samples in the transformed_protein_df
    """
    samples_in_order = transformed_protein_df.columns
    batches_in_order = []
    for sample in samples_in_order:
        batches_in_order.append(
            metadata_df[metadata_df["Sample"] == sample]["Batch"].iloc[0]
        )
    return batches_in_order


# <- SVA ->


def get_group_for_each_sample_in_order(
    transformed_protein_df: pd.DataFrame, metadata_df: pd.DataFrame
) -> list:
    """
    Extracts the group assignment for each sample in the transformed_protein_df.
    It preserves the order of the columns in the transformed_protein_df when returning the list of group assignments.

    :param transformed_protein_df: the dataframe with the samples for which the function extracts the group assignments
        :type transformed_protein_df: pd.DataFrame
    :param metadata_df: the dataframe that contains the metadata for the transformed_protein_df, including the group assignments
        :type metadata_df: pd.DataFrame

    :return: returns a list with the group assignments in the order of the samples in the transformed_protein_df
    """
    samples_in_order = transformed_protein_df.index
    groups_in_order = []
    for sample in samples_in_order:
        groups_in_order.append(
            metadata_df[metadata_df["Sample"] == sample]["Group"].iloc[0]
        )
    return groups_in_order


def turn_group_names_to_int(groups: list) -> list:
    """
    Receives a list of group names and assigns each unique group name a new integer needed for later processing.
    The order of the groups remains untouched.

    :param groups: a list of group assignments, e.g. ["AD", "AD", "CTR", "AD", "CTR", "AD"]
        :type groups: list

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


def get_training_data_and_target_values(
    protein_df: pd.DataFrame, metadata_df: pd.DataFrame
) -> tuple[pd.DataFrame | Any]:
    """
    Transforms PROTzilla default dataframes into formats which can be used to train a linear regression model on

    :param protein_df: the dataframe with the protein information in PROTzilla default format
    :param metadata_df: the dataframe containing the metadata for protein_df

    :return: returns a tuple of training data and target values for linear regression
    """
    X = long_to_wide(protein_df)
    groups = get_group_for_each_sample_in_order(
        transformed_protein_df=X, metadata_df=metadata_df
    )
    y = turn_group_names_to_int(groups)
    return X, np.array(y).reshape(-1, 1)


def sv_wide_to_long(
    wide_df: pd.DataFrame, original_long_df: pd.DataFrame, n_surrogate_variables: int
) -> pd.DataFrame:
    """
    Transforms a dataframe from a wide format containing surrogate variables into the PROTzilla default format
    where each combination of Sample and Protein ID are a row and the column names are "Sample", "Protein ID",
    "Gene", "_intensity_name_", "Surrogate Variable 1", "Surrogate Variable 2", ...

    :param wide_df: the dataframe that should be transformed into long format
        :type wide_df: pd.DataFrame
    :param original_protein_df: the original PROTzilla default formatted dataframe which we need to reintroduce
        the gene information
        :type original_protein_df: pd.DataFrame
    :param n_surrogate_variables: Number of surrogate variables
        :type n_surrogate_variables: int

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


def add_sv_columns_to_df(sv_columns: list, df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds surrogate variables as columns to the given dataframe. The given dataframe should be in wide format.

    :param sv_columns: a list of lists containing the surrogate variable for every sample
        :type list
    :param df: the wide format dataframe to which the surrogate variable columns should be added
        :type pd.DataFrame

    :return: the dataframe with the added columns
    """
    for i in range(len(sv_columns)):
        df[f"Surrogate Variable {i+1}"] = sv_columns[i]
    return df


def calculate_n_sv_be(
    wide_protein_df: pd.DataFrame, groups: list, seed: int | None = None, B: int = 20
) -> int:
    """
    Calculates the optimal number of surrogate variables based on the algorithm implemented in the R package sva
    which implements SVA. One can find the original implementation here: https://rdrr.io/bioc/sva/src/R/num.sv.R
    This function builds on the approach by Buja and Eyuboglu 1992, there is another function to calculate the optimal
    number of surrogate variables with an approach by Leek, which one can find below (calculate_n_sv_leek).

    :param wide_protein_df: the dataframe containing protein information in wide format
        type: pd.DataFrame
    :param groups: list containing the group assignments for the samples preserving their order
        type: list
    :param seed: the seed for the permutation
        type: int | None
    :param B: number of iterations to permute the data and test it against our real data

    :return: the number of surrogate variables
    """
    dat = (wide_protein_df.T).values
    mod = groups
    n_rows, n_columns = dat.shape
    H = mod @ np.linalg.inv(mod.T @ mod) @ mod.T
    res = dat - (H @ dat.T).T
    # default for R for full_matrices is False, np default is True
    U, S, Vh = np.linalg.svd(res, full_matrices=False)
    ndf = int(min(n_rows, n_columns) - np.trace(H))
    dstat = (S[:ndf] ** 2) / np.sum(S[:ndf] ** 2)
    dstat0 = np.zeros((int(B), ndf))
    if seed:
        random_state = np.random.RandomState(seed=seed)
    else:
        random_state = np.random.RandomState()
    for i in range(B):
        # R handles shuffling differently: it transposes the matrix and then performs the shuffling
        # therefore the original R implementation of num.sv performs the shuffling on the rows and then
        # transpose it back to columns, in Python we can directly do the shuffling along the columns
        res0 = np.apply_along_axis(random_state.permutation, axis=1, arr=res)
        res0 = res0 - (H @ res0.T).T
        U0, S0, Vh0 = np.linalg.svd(res0, full_matrices=False)
        dstat0[i, :] = (S0[:ndf] ** 2) / np.sum(S0[:ndf] ** 2)
    psv = np.ones(n_columns)
    for i in range(ndf):
        psv[i] = np.mean(dstat0[:, i] >= dstat[i])
    for i in range(1, ndf):
        psv[i] = max(psv[i - 1], psv[i])
    nsv = np.sum(psv <= 0.10)
    return int(nsv)


def calculate_n_sv_leek(wide_protein_df: pd.DataFrame, groups: list) -> int:
    """
    Calculates the optimal number of surrogate variables based on the algorithm implemented in the R package sva
    which implements SVA. One can find the original implementation here: https://rdrr.io/bioc/sva/src/R/num.sv.R
    This function builds on the approach by Leek, there is another function to calculate the optimal number of
    surrogate variables with an approach by Buja and Eyuboglu 1992, which one can find above (calculate_n_sv_be).

    :param wide_protein_df: the dataframe containing protein information in wide format
        type: pd.DataFrame
    :param groups: list containing the group assignments for the samples preserving their order
        type: list

    :return: the number of surrogate variables
    """
    dat = wide_protein_df.T
    mod = groups
    n_rows, n_columns = dat.shape
    a = np.linspace(0, 2, 100)
    n = np.floor(n_columns / 10)
    rhat = np.zeros((100, 10))
    P = np.eye(n_columns) - mod @ np.linalg.inv(mod.T @ mod) @ mod.T
    for j in range(1, 11):
        dats = dat.iloc[0 : int(j * n), :]
        eigenvalues, eigenvector = np.linalg.eigh(dats.T @ dats)
        sigbar = eigenvalues[n_columns - 1] / (j * n)
        R = dats @ P
        wm = (1 / (j * n)) * R.T @ R - P * sigbar
        eigenvalues, eigenvector = np.linalg.eigh(wm)
        thresholds = a * (j * n) ** (-1 / 3) * n_rows
        counts = np.sum(eigenvalues > thresholds[:, np.newaxis], axis=1)
        rhat[:, j - 1] = counts
    # ddof is necessary because numpy and R have different defaults on how to calculate variance
    ss = np.var(rhat, axis=1, ddof=1)
    bumpstart = np.argmax(ss > (2 * ss[0]))
    drop_condition = ss < (0.5 * ss[0])
    drop_condition[: bumpstart + 1] = False
    start = np.argmax(drop_condition)

    spike_condition = ss > ss[0]
    spike_condition[: start + 1] = False
    finish = np.argmax(spike_condition)

    if not finish:
        raise RuntimeError(
            "The Leek method fails because it cannot converge. The batch effects in your "
            "data are probably too subtle to detect by this method. Try to use the "
            "permutation based approach by Buja and Eyuboglu 1992 instead."
        )

    stable_estimates = rhat[start : finish + 1, 9]
    vals, counts = np.unique(stable_estimates, return_counts=True)
    n_sv = vals[np.argmax(counts)]
    return n_sv


def f_pvalue(dat: np.ndarray, mod: np.ndarray, mod0: np.ndarray) -> np.ndarray:
    """
    Calculates f-statistics for each row of the given data matrix and compares the nested models defined
    by the design matrices for the alternative (mod) and null cases (mod0) cases. The columns of mod0 should be
    a subset of the columns of mod. The function and its description is based on the helper function in the original
    R implementation and can be found here:
    https://rdrr.io/bioc/sva/man/f.pvalue.html (documentation)
    https://rdrr.io/bioc/sva/src/R/f.pvalue.R (R code)


    :param dat: the data matrix with the variables in rows and samples in columns
        type: np.ndarray
    :param mod: the model matrix being used to fit the data
        type: np.ndarray
    :param mod0: the null model being compared when fitting the data
        type: np.ndarray

    :return: an array of f-statistic p-values for each row of dat
    """
    n_rows, n_columns = dat.shape
    df1 = mod.shape[1]
    df0 = mod0.shape[1]

    # calculate for biological signal
    primary_variables_model = linear_model.LinearRegression()
    primary_variables_model.fit(mod, dat.T)
    primary_variable_signal = primary_variables_model.predict(mod)
    resid = dat.T - primary_variable_signal
    rss1 = (resid * resid).sum(axis=1)

    # calculate for non-biological signal
    sv_model = linear_model.LinearRegression()
    sv_model.fit(mod0, dat.T)
    sv_signal = sv_model.predict(mod0)
    resid0 = dat.T - sv_signal
    rss0 = (resid0 * resid0).sum(axis=1)

    fstats = ((rss0 - rss1) / (df1 - df0)) / (rss1 / (n_columns - df1))
    p = f.sf(fstats, dfn=(df1 - df0), dfd=(n_columns - df1))
    return p


def irwsva(
    wide_protein_df: pd.DataFrame, groups: list, n_surrogate_variables: int, B: int = 5
):
    """
    Calculates the surrogate variables with the iteratively re-weighted least squares
    approach. The implementation is based on the algorithm implemented in the R package sva
    which implements SVA. One can find the original implementation here: https://rdrr.io/bioc/sva/src/R/irwsva.build.R

    :param dat: the data matrix with the variables in rows and samples in columns
        type: np.ndarray
    :param mod: the model matrix being used to fit the data
        type: np.ndarray
    :param n_surrogate_variables: the number of surrogate variables to calculate
        type: int | None
    :param B: number of iterations for the algorithm to perform
        type: int

    :return: the surrogate variables in a matrix with the surrogate variables as columns and samples as rows
    """
    dat = (wide_protein_df.T).values
    mod0 = np.ones((len(groups), 1))
    mod = np.hstack([mod0, groups])
    n_rows, n_columns = dat.shape
    # first we take out the effect of the primary variable so we only have BE
    # and other unknown sources of variation in our values
    beta, residuals, rank, s = np.linalg.lstsq(mod, dat.T, rcond=None)
    primary_variable_signal = mod @ beta
    resid = dat.T - primary_variable_signal
    resid = resid.T

    eigenvalues, eigenvector = np.linalg.eigh(resid.T @ resid)
    vv = eigenvector

    # there is a lot of dead code in the original R code which I have copied here for now
    # to be able to map my code back
    ndf = n_columns - mod.shape[1]
    pprob = np.ones(n_rows)
    one = np.ones(n_columns)
    Id = np.eye(n_columns)
    df1 = mod.shape[1] + n_surrogate_variables
    df0 = mod0.shape[1] + n_surrogate_variables

    for i in range(B):
        mod_b = np.hstack([mod, vv[:, 0:n_surrogate_variables]])
        mod0_b = np.hstack([mod0, vv[:, 0:n_surrogate_variables]])
        ptmp = f_pvalue(dat, mod_b, mod0_b)
        pprob_b = 1 - fdrcorrection(ptmp)[1]

        mod_gam = np.hstack([mod0, vv[:, 0:n_surrogate_variables]])
        mod0_gam = np.hstack([mod0])
        ptmp = f_pvalue(dat, mod_gam, mod0_gam)
        pprob_gam = 1 - fdrcorrection(ptmp)[1]

        pprob = pprob_gam * (1 - pprob_b)
        dats = dat * pprob
        dats = dats - np.mean(dats, axis=0, keepdims=True)
        eigenvalues, eigenvector = np.linalg.eigh(dats.T @ dats)
        vv = eigenvector
    U, S, Vh = np.linalg.svd(dats, full_matrices=False)
    sv = Vh.T[:, 0:n_surrogate_variables]
    return sv


# <---- BECAs ---->


def combat_correction(
    protein_df: pd.DataFrame, metadata_df: pd.DataFrame
) -> dict[str, pd.DataFrame]:
    """
    Corrects the batch effects in the protein data with the batch effect correction algorithm ComBat.

    :param protein_df: the dataframe containing the protein data
        type: pd.DataFrame
    :param metadata_df: the dataframe containing the metadata for the protein data, the metadata should include the batch assignments

    return: a dictionary containing the corrected protein data
    """
    # TODO: What about parametric vs non-parametric
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
    protein_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    num_sv_method: str = NumSVMethods.be,
) -> dict[str, pd.DataFrame]:
    """
    Corrects the batch effects in the protein data with the batch effect correction algorithm SVA (Surrogate Variable Algorithm).

    :param protein_df: the dataframe containing the protein data
        type: pd.DataFrame
    :param metadata_df: the dataframe containing the metadata for the protein data, the metadata should include the batch assignments

    return: a dictionary containing the corrected protein data and a dataframe with the surrogate variables
    """
    wide_protein_df, groups = get_training_data_and_target_values(
        protein_df=protein_df, metadata_df=metadata_df
    )
    if num_sv_method == NumSVMethods.be.value:
        n_surrogate_variables = calculate_n_sv_be(wide_protein_df, groups)
    elif num_sv_method == NumSVMethods.leek.value:
        n_surrogate_variables = calculate_n_sv_leek(wide_protein_df, groups)
    else:
        raise ValueError(
            "No valid option to calculate the optimal number of surrogate variables selected."
        )

    sv = irwsva(
        wide_protein_df=wide_protein_df,
        groups=groups,
        n_surrogate_variables=n_surrogate_variables,
    )

    # Now, we add the surrogate variables to a df that also contains protein ids and samples
    sv_transposed = np.array(sv).T
    n_surrogate_variables = len(sv_transposed)

    wide_surrogate_variable_df = add_sv_columns_to_df(sv_transposed, wide_protein_df)
    # this still contains the gene information after the wide_to_long transformation
    # (I should think about whether I want this)
    surrogate_variable_df = sv_wide_to_long(
        wide_surrogate_variable_df, protein_df, n_surrogate_variables
    )

    # TODO: Correct the protein data!!
    return {"protein_df": protein_df, "surrogate_variable_df": surrogate_variable_df}


def loess_correction(protein_df: pd.DataFrame, metadata_df: pd.DataFrame):
    return {"protein_df": protein_df}
