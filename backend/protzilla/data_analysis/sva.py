import numpy as np
from statsmodels.stats.multitest import fdrcorrection
from scipy.stats import f


def _apply_variance_filter(dat: np.ndarray, n: int) -> np.ndarray:
    """
    Filters data by variance keeping only the n variables with the most variance.

    :param dat: the data matrix with the variables in rows and samples in columns
    :param n: the number of most variable rows kept

    return: the filtered data matrix containing only the n most variable rows
    """
    num_features = dat.shape[0]
    if n < 100 or n > num_features:
        raise ValueError(
            f"The number of features used in the analysis must be between 100 and {num_features}"
        )
    tmpv = np.var(dat, axis=1, ddof=1)
    ind = np.argsort(-tmpv)[: n - 1]
    dat = dat[ind, :]
    return dat


def calculate_n_sv_be(
    dat: np.ndarray,
    mod: np.ndarray,
    variance_filter: int | None = None,
    B: int = 20,
    seed: int | None = None,
) -> int:
    """
    Calculates the optimal number of surrogate variables based on the algorithm implemented in the R package sva
    which implements SVA. One can find the original implementation here: https://rdrr.io/bioc/sva/src/R/num.sv.R
    This function builds on the approach by Buja and Eyuboglu 1992, there is another function to calculate the optimal
    number of surrogate variables with an approach by Leek.

    :param dat: the data matrix with the variables in rows and samples in columns
    :param mod: the model matrix being used to fit the data
    :param variance_filter: if not None, the number of most variable rows to apply sva on, the rest is filtered out
    :param seed: if not None, the seed for the permutation
    :param B: number of iterations of permuting the data

    :return: the number of surrogate variables to use for surrogate variable analysis (SVA)
    """
    if variance_filter:
        dat = _apply_variance_filter(dat=dat, n=variance_filter)

    n_rows, n_columns = dat.shape
    H = mod @ np.linalg.inv(mod.T @ mod) @ mod.T
    res = dat - (H @ dat.T).T
    # default for R for full_matrices is False, np default is True
    U, S, Vh = np.linalg.svd(res, full_matrices=False)
    ndf = int(min(n_rows, n_columns) - np.ceil(np.trace(H)))
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


def calculate_n_sv_leek(
    dat: np.ndarray, mod: np.ndarray, variance_filter: int | None = None
) -> int:
    """
    Calculates the optimal number of surrogate variables based on the algorithm implemented in the R package sva
    which implements SVA. One can find the original implementation here: https://rdrr.io/bioc/sva/src/R/num.sv.R
    This function builds on the approach by Leek, there is another function to calculate the optimal number of
    surrogate variables with an approach by Buja and Eyuboglu 1992.

    :param dat: the data matrix with the variables in rows and samples in columns
    :param mod: the model matrix being used to fit the data
    :param variance_filter: if not None, the number of most variable rows to apply sva on, the rest is filtered out

    :return: the number of surrogate variables
    """
    if variance_filter:
        dat = _apply_variance_filter(dat=dat, n=variance_filter)

    n_rows, n_columns = dat.shape
    a = np.linspace(0, 2, 100)
    n = np.floor(n_columns / 10)
    rhat = np.zeros((100, 10))
    P = np.eye(n_columns) - mod @ np.linalg.inv(mod.T @ mod) @ mod.T
    for j in range(1, 11):
        dats = dat[0 : int(j * n), :]
        eigenvalues, eigenvector = np.linalg.eigh(dats.T @ dats)
        sigbar = eigenvalues[n_columns - 1] / (j * n)
        R = dats @ P
        wm = (1 / (j * n)) * R.T @ R - P * sigbar
        eigenvalues, eigenvector = np.linalg.eigh(wm)
        thresholds = a * (j * n) ** (-1 / 3) * n_rows
        counts = np.sum(eigenvalues > thresholds[:, np.newaxis], axis=1)
        rhat[:, j - 1] = counts
    # default ddof for R is 1, for numpy it is 0
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
            "permutation based version by Buja and Eyuboglu 1992 instead."
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
    :param mod: the model matrix being used to fit the data
    :param mod0: the null model being compared when fitting the data

    :return: an array of f-statistic p-values for each row of dat
    """
    n_rows, n_columns = dat.shape
    df1 = mod.shape[1]
    df0 = mod0.shape[1]

    # calculate for biological signal
    beta, residuals, rank, s = np.linalg.lstsq(mod, dat.T, rcond=None)
    primary_variable_signal = mod @ beta
    resid = dat.T - primary_variable_signal
    rss1 = (resid * resid).sum(axis=0)

    # calculate for non-biological signal
    beta, residuals, rank, s = np.linalg.lstsq(mod0, dat.T, rcond=None)
    sv_signal = mod0 @ beta
    resid0 = dat.T - sv_signal
    rss0 = (resid0 * resid0).sum(axis=0)

    fstats = ((rss0 - rss1) / (df1 - df0)) / (rss1 / (n_columns - df1))
    p = f.sf(fstats, dfn=(df1 - df0), dfd=(n_columns - df1))
    return p


def irwsva(
    dat: np.ndarray,
    mod: np.ndarray,
    mod0: np.ndarray | None,
    n_surrogate_variables: int,
    B: int = 5,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    """
    Calculates the surrogate variables with the iteratively re-weighted least squares
    approach. The implementation is based on the algorithm implemented in the R package sva
    which implements SVA. One can find the original implementation here: https://rdrr.io/bioc/sva/src/R/irwsva.build.R

    :param dat: the data matrix with the variables in rows and samples in columns
    :param mod: the model matrix being used to fit the data
    :param mod0: the null model being compared when fitting the data
    :param n_surrogate_variables: the number of surrogate variables to calculate
    :param B: number of iterations for the algorithm to perform

    :return:
        sv: the surrogate variables in a matrix with the surrogate variables as columns and samples as rows
        pprob_gam: posterior probabilities for each feature for how it is affected by heterogeneity
        pprob_b: posterior probabilities for each feature for how it is affected by mod
        num_sv: the number of surrogate variables
    """
    if mod0 is None:
        mod0 = mod[:, 0:1]
    n_rows, n_columns = dat.shape
    # calculate residuals
    beta, residuals, rank, s = np.linalg.lstsq(mod, dat.T, rcond=None)
    primary_variable_signal = mod @ beta
    resid = dat.T - primary_variable_signal
    resid = resid.T

    eigenvalues, eigenvector = np.linalg.eigh(resid.T @ resid)
    # numpy returns the vector sorted form smallest to largest, while in R it is sorted from largest to smallest
    vv = eigenvector[:, ::-1]

    # unnecessary code in the original implementation (leaving it here for now)
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
        dats = dat * pprob[:, None]
        dats = dats - np.mean(dats, axis=1, keepdims=True)
        eigenvalues, eigenvector = np.linalg.eigh(dats.T @ dats)
        vv = eigenvector
    U, S, Vh = np.linalg.svd(dats, full_matrices=False)
    sv = Vh.T[:, 0:n_surrogate_variables]
    return sv, pprob_gam, pprob_b, n_surrogate_variables


def fsva(
    dbdat: np.ndarray,
    mod: np.ndarray,
    sv: np.ndarray,
    n_sv: int,
    pprob_gam: np.ndarray,
    pprob_b: np.ndarray,
    newdat: np.ndarray | None = None,
) -> tuple:
    """
    Performs frozen surrogate variable analysis as proposed in Parker, Corrada Bravo and Leek 2013.
    It uses the surrogate variables to remove batch effects from the training database (dbdat) and optionally
    from new data as well (newdat). The surrogate variables can be calculated by using iteratively re-weighted least squares
    approach introduced by Leek.
    This implementation only offers the exact method from the R code, the faster version in R uses an online approach to SVD
    which is less accurate.

    :param dbdat: the data used to find the surrogate variables with the variables in rows and samples in columns
    :param mod: the model matrix which was used to fit the data for the surrogate variable analysis
    :param sv: the surrogate variables from the surrogate variable analysis
    :param n_sv: number of surrogate variables from the surrogate variable analysis
    :param pprob_gam: posterior probabilities for each feature for how it is affected by heterogeneity from the surrogate variable analysis
    :param pprob_b: posterior probabilities for each feature for how it is affected by mod from the surrogate variable analysis

    :return: a tuple containing the following:
        db: the cleaned training data
        adjusted: the cleaned new data
        newV: the surrogate variables of the new data
    """
    ndb = dbdat.shape[1]
    nnew = newdat.shape[1] if newdat else 0
    nmod = mod.shape[1]
    ntot = ndb + nnew
    mod = np.hstack([mod, sv])
    gammahat = (dbdat @ mod @ np.linalg.inv(mod.T @ mod))[:, (nmod) : (nmod + n_sv)]
    db = dbdat - gammahat @ sv.T
    wts = ((1 - pprob_b) * pprob_gam)[:, None]
    newV = np.zeros((nnew, n_sv))
    for i in range(nnew):
        tmp = np.hstack([dbdat, newdat[:, i : i + 1]])
        tmpd = wts * tmp
        mean_centered_tmpd = tmpd - np.mean(tmpd, axis=1, keepdims=True)
        U, S, Vh = np.linalg.svd(mean_centered_tmpd, full_matrices=False)
        # we can get rid of the second for loop by using the fact that the sign of correlation
        # (cor() in the original R code) is the same as the sign of covariance which we calculate here.
        # For that we first need to mean center the two matrices
        v_mean_centered = Vh.T[:ndb, :n_sv] - np.mean(Vh.T[:ndb, :n_sv], axis=0)
        sv_mean_centered = sv[:ndb, :n_sv] - np.mean(sv[:ndb, :n_sv], axis=0)
        sgn = np.sign(np.sum(v_mean_centered * sv_mean_centered, axis=0))
        newV[i, :] = Vh.T[ndb, :n_sv] * sgn
    adjusted = newdat - gammahat @ newV.T

    return db, adjusted, newV
