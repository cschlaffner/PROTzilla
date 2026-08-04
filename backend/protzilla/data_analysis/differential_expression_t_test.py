import logging

import numpy as np
import pandas as pd
from scipy import stats

from backend.protzilla.constants.option_types import (
    CORRECTED_P_VALUES_COLUMNS,
    FC_SIGNIFICANCE_COLUMNS,
    LOG2_FOLD_CHANGE_COLUMNS,
    T_STATISTIC_COLUMNS,
    LogBaseWithNoneType,
)
from backend.protzilla.steps import OutputItem, OutputType
from backend.protzilla.utilities.utilities import (
    default_intensity_column,
    exists_message,
)

from .differential_expression_helper import (
    INVALID_PROTEINGROUP_DATA_MSG,
    _map_log_base,
    apply_multiple_testing_correction,
)


def get_z_score_based_fold_change_significance(
    fold_changes: pd.Series,
) -> tuple[pd.Series, pd.Series]:
    # Reimplementation of the fold-change Z-score significance as described in
    # https://pubs.acs.org/doi/10.1021/pr1009977
    median = np.median(fold_changes)
    sd_lower = median - np.percentile(fold_changes, 15.87)
    sd_upper = np.percentile(fold_changes, 84.13) - median

    def calc_z_score(ratio):
        if ratio > median:
            return (ratio - median) / sd_upper
        else:
            return (median - ratio) / sd_lower

    z_scores = fold_changes.apply(calc_z_score)
    z_score_p_value = 1 - stats.norm.cdf(z_scores)

    return z_scores, z_score_p_value


def vectorized_t_test(
    group1_counts,
    group2_counts,
    group1_means,
    group2_means,
    group1_vars,
    group2_vars,
    ttest_type,
):
    """
    Compute two-sample t-tests for multiple protein groups simultaneously.

    Implements both Student's (equal-variance, pooled) and Welch's
    (unequal-variance, Welch-Satterthwaite df) variants. All array arguments
    must be 1-D arrays of equal length where each element corresponds to one
    protein group. The implementation is equivalent to calling
    ``scipy.stats.ttest_ind`` per protein but avoids the Python-level loop and is much faster
    because all operations are vectorized.

    :param group1_counts: per-protein observation counts for group 1 (float array, ddof excluded)
    :param group2_counts: per-protein observation counts for group 2 (float array, ddof excluded)
    :param group1_means: per-protein sample means for group 1
    :param group2_means: per-protein sample means for group 2
    :param group1_vars: per-protein sample variances (ddof=1) for group 1
    :param group2_vars: per-protein sample variances (ddof=1) for group 2
    :param ttest_type: "Student's t-Test" for equal-variance, any other value for Welch's t-Test
    :return: tuple of (t_statistics, p_values) — two-tailed p-values from the t-distribution
    """
    if ttest_type == "Student's t-Test":
        # Pooled variance: weighted average of both sample variances, weights = (n - 1)
        pooled_vars = (
            (group1_counts - 1) * group1_vars + (group2_counts - 1) * group2_vars
        ) / (group1_counts + group2_counts - 2)
        # SE of the difference of means under the equal-variance assumption
        standard_errors = np.sqrt(
            pooled_vars * (1.0 / group1_counts + 1.0 / group2_counts)
        )
        # df = total observations minus one per group
        degrees_of_freedom = group1_counts + group2_counts - 2
    else:
        # s²/n terms used throughout the Welch formulas
        group1_var_count_ratios = group1_vars / group1_counts
        group2_var_count_ratios = group2_vars / group2_counts
        # SE of the difference of means without assuming equal variances
        standard_errors = np.sqrt(group1_var_count_ratios + group2_var_count_ratios)
        # Welch-Satterthwaite df: (s1²/n1 + s2²/n2)² / ((s1²/n1)²/(n1-1) + (s2²/n2)²/(n2-1))
        with np.errstate(divide="ignore", invalid="ignore"):
            degrees_of_freedom = (
                group1_var_count_ratios + group2_var_count_ratios
            ) ** 2 / (
                group1_var_count_ratios**2 / (group1_counts - 1)
                + group2_var_count_ratios**2 / (group2_counts - 1)
            )
        # When both variances are 0 the Satterthwaite formula is 0/0=NaN.
        # Equal variances (both zero) is the equal-variance case, so fall back to Student's df.
        student_degrees_of_freedom = group1_counts + group2_counts - 2
        degrees_of_freedom = np.where(
            np.isnan(degrees_of_freedom),
            student_degrees_of_freedom,
            degrees_of_freedom,
        )

    with np.errstate(divide="ignore", invalid="ignore"):
        # t = (mean1 - mean2) / SE; two-tailed p from the survival function of |t|
        t_statistics = (group1_means - group2_means) / standard_errors
        p_values = 2 * stats.t.sf(np.abs(t_statistics), degrees_of_freedom)
    return t_statistics, p_values


# --8<-- [start:t_test]
def t_test(
    protein_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    ttest_type: str,
    grouping: str,
    group1: str,
    group2: str,
    multiple_testing_correction_method: str,
    alpha: float,
    log_base: LogBaseWithNoneType = LogBaseWithNoneType.NONE,
    fc_zscore_filter: bool = False,
    fc_zscore_alpha: float = 0.05,
) -> dict:
    """
    A function to conduct a two sample t-test between groups defined in the
    clinical data. The t-test is conducted on the level of each protein.
    The p-values are corrected for multiple testing.
    :param protein_df: the dataframe that should be tested in long format
    :param metadata_df: the dataframe that contains the clinical data
    :param ttest_type: the type of t-test to be used. Either "Student's t-Test" or "Welch's t-Test"
    :param grouping: the column name of the grouping variable in the metadata_df
    :param group1: the name of the first group for the t-test
    :param group2: the name of the second group for the t-test
    :param multiple_testing_correction_method: the method for multiple testing correction
    :param alpha: the p-value cut-off before multiple testing correction
    :param log_base: in case the data was previously log transformed this parameter contains the base as a string
    :param fc_zscore_filter: whether to apply a fold-change Z-score significance filter in addition to the p-value
    :param fc_zscore_alpha: the p-value cutoff (tail probability) for the fold-change Z-score significance

    :return: a dict containing
        - a df differentially_expressed_proteins_df in typical protzilla long format containing the t-test results
        - a df significant_proteins_df, containing the proteins that are significant after multiple testing correction
        - a df corrected_p_values, containing the p_values after application of multiple testing correction,
        - a df log2_fold_change, containing the log2 fold changes per protein,
        - a df t_statistic_df, containing the t-statistic per protein,
        - a df fc_significance_df, containing the fold-change z-scores and their tail probabilities,
        - a float corrected_alpha, containing the alpha value after application of multiple testing correction (depending on the selected multiple testing correction method corrected_alpha may be equal to alpha),
        - a list messages, containing messages for the user
    """

    def empty_result(messages):
        return dict(
            differentially_expressed_proteins_df=pd.DataFrame(
                columns=protein_df.columns.tolist()
                + ["corrected_p_value", "log2_fold_change", "t_statistic"]
            ),
            significant_proteins_df=pd.DataFrame(
                columns=protein_df.columns.tolist()
                + ["corrected_p_value", "log2_fold_change", "t_statistic"]
            ),
            corrected_p_values_df=pd.DataFrame(columns=CORRECTED_P_VALUES_COLUMNS),
            t_statistic_df=pd.DataFrame(columns=T_STATISTIC_COLUMNS),
            log2_fold_change_df=pd.DataFrame(columns=LOG2_FOLD_CHANGE_COLUMNS),
            fc_significance_df=pd.DataFrame(columns=FC_SIGNIFICANCE_COLUMNS),
            corrected_alpha=alpha,
            messages=messages,
        )

    assert grouping in metadata_df.columns
    messages = []

    if ttest_type not in ["Student's t-Test", "Welch's t-Test"]:
        messages.append(
            {
                "level": logging.WARNING,
                "msg": """t-Test type must be either "Student's t-Test" or "Welch's t-Test".""",
            }
        )
        return empty_result(messages)

    # User input handling
    unique_groups = metadata_df[grouping].unique()
    # Check if group1 is in unique_groups, if not assign the first unique group
    if group1 not in unique_groups:
        group1 = unique_groups[0]
        messages.append(
            {
                "level": logging.WARNING,
                "msg": f"Group 1 was invalid. Auto-selected {group1} as group1.",
            }
        )

    # Check if group2 is in unique_groups and not the same as group1, if not assign the next unique group
    if group2 not in unique_groups or group1 == group2:
        for group in unique_groups:
            if group != group1:
                group2 = group
                break
        messages.append(
            {
                "level": logging.WARNING,
                "msg": f"Group 2 was invalid. Auto-selected {group2} as group 2.",
            }
        )

    protein_df = pd.merge(
        left=protein_df,
        right=metadata_df[["Sample", grouping]],
        on="Sample",
        copy=False,
    )

    intensity_name = default_intensity_column(protein_df)

    log_base = _map_log_base(log_base)  # now log_base in [2, 10, None]

    protein_df["id"] = protein_df.groupby(["Protein ID", grouping]).cumcount()

    protein_df_wide = protein_df.dropna(subset=[intensity_name]).pivot(
        index=["Protein ID", "id"], columns=grouping, values=intensity_name
    )

    if group1 not in protein_df_wide.columns or group2 not in protein_df_wide.columns:
        messages.append(
            {
                "level": logging.ERROR,
                "msg": "No valid protein groups found for t-test analysis.",
            }
        )
        return empty_result(messages)

    grouped_dfs = protein_df_wide.groupby("Protein ID")
    statistics_group1 = grouped_dfs[group1].agg(
        n="count", mean="mean", var="var", median="median"
    )
    statistics_group2 = grouped_dfs[group2].agg(
        n="count", mean="mean", var="var", median="median"
    )

    valid_mask = (statistics_group1["n"] >= 2) & (statistics_group2["n"] >= 2)
    if (~valid_mask).any() and not exists_message(
        messages, INVALID_PROTEINGROUP_DATA_MSG
    ):
        messages.append(INVALID_PROTEINGROUP_DATA_MSG)

    valid_statistics_group1 = statistics_group1[valid_mask]
    valid_statistics_group2 = statistics_group2[valid_mask]

    # Statistics grouped by protein
    group1_counts = valid_statistics_group1["n"].to_numpy(dtype=float)
    group2_counts = valid_statistics_group2["n"].to_numpy(dtype=float)
    group1_means = valid_statistics_group1["mean"].to_numpy()
    group2_means = valid_statistics_group2["mean"].to_numpy()
    group1_vars = valid_statistics_group1["var"].to_numpy()
    group2_vars = valid_statistics_group2["var"].to_numpy()
    group1_medians = valid_statistics_group1["median"].to_numpy()
    group2_medians = valid_statistics_group2["median"].to_numpy()

    t_statistics, p_values = vectorized_t_test(
        group1_counts,
        group2_counts,
        group1_means,
        group2_means,
        group1_vars,
        group2_vars,
        ttest_type,
    )

    if log_base:
        fc_arr = (group2_medians - group1_medians) * np.log2(log_base)
    else:
        with np.errstate(divide="ignore", invalid="ignore"):
            fc_arr = np.log2(group2_medians / group1_medians)

    ttest_results = pd.DataFrame(
        {
            "Protein ID": valid_statistics_group1.index,
            "n1": group1_counts.astype(int),
            "n2": group2_counts.astype(int),
            "t_statistic": t_statistics,
            "p_value": p_values,
            "log2_fold_change": fc_arr,
        }
    ).dropna(subset=["p_value"])

    if len(ttest_results) == 0:
        messages.append(
            {
                "level": logging.ERROR,
                "msg": "No valid protein groups found for t-test analysis.",
            }
        )
        return empty_result(messages)

    ttest_results["fc_z_score"], ttest_results["fc_significance"] = (
        get_z_score_based_fold_change_significance(ttest_results["log2_fold_change"])
    )

    ttest_results["corrected_p_value"], corrected_alpha = (
        apply_multiple_testing_correction(
            p_values=ttest_results["p_value"],
            method=multiple_testing_correction_method,
            alpha=alpha,
        )
    )

    differentially_expressed_proteins_df = pd.merge(
        ttest_results, protein_df, on="Protein ID", how="left"
    )

    # Drop unused columns and reorder for backwards compatibility
    differentially_expressed_proteins_df = differentially_expressed_proteins_df[
        [
            "Sample",
            "Protein ID",
            "Gene",
            default_intensity_column(differentially_expressed_proteins_df),
            "Group",
            "corrected_p_value",
            "log2_fold_change",
            "t_statistic",
            "fc_z_score",
            "fc_significance",
        ]
    ]

    significant_proteins_df = differentially_expressed_proteins_df.query(
        "corrected_p_value <= @corrected_alpha"
    )

    if fc_zscore_filter:
        significant_proteins_df = significant_proteins_df.query(
            "fc_significance <= @fc_zscore_alpha"
        )

    return dict(
        differentially_expressed_proteins_df=differentially_expressed_proteins_df,
        significant_proteins_df=significant_proteins_df,
        corrected_p_values_df=ttest_results[CORRECTED_P_VALUES_COLUMNS],
        t_statistic_df=ttest_results[T_STATISTIC_COLUMNS],
        log2_fold_change_df=ttest_results[LOG2_FOLD_CHANGE_COLUMNS],
        fc_significance_df=ttest_results[FC_SIGNIFICANCE_COLUMNS],
        corrected_alpha=OutputItem(
            output_type=OutputType.FLOAT,
            value=float(corrected_alpha),
        ),
        messages=messages,
    )
# --8<-- [end:t_test]
