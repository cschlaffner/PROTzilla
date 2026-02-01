import logging

import numpy as np
import pandas as pd
from scipy import stats

from backend.protzilla.utilities import default_intensity_column, exists_message

from .differential_expression_helper import (
    INVALID_PROTEINGROUP_DATA_MSG,
    _map_log_base,
    apply_multiple_testing_correction,
)


def _is_valid(value):
    return value != 0 and not np.isnan(value)


def t_test(
    intensity_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    ttest_type: str,
    grouping: str,
    group1: str,
    group2: str,
    multiple_testing_correction_method: str,
    alpha: float,
    log_base: str = None,
    intensity_name: str = None,
    fc_zscore_filter: bool = False,
    fc_zscore_alpha: float = 0.05,
) -> dict:
    """
    A function to conduct a two sample t-test between groups defined in the
    clinical data. The t-test is conducted on the level of each protein.
    The p-values are corrected for multiple testing.
    :param ttest_type: the type of t-test to be used. Either "Student's t-Test" or "Welch's t-Test"
    :param intensity_df: the dataframe that should be tested in long format
    :param metadata_df: the dataframe that contains the clinical data
    :param grouping: the column name of the grouping variable in the metadata_df
    :param group1: the name of the first group for the t-test
    :param group2: the name of the second group for the t-test
    :param multiple_testing_correction_method: the method for multiple testing correction
    :param alpha: the p-value cut-off before multiple testing correction
    :param log_base: in case the data was previously log transformed this parameter contains the base as a string
    :param intensity_name: name of the column containing the protein group intensities
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

    assert grouping in metadata_df.columns
    messages = []
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

    intensity_df = pd.merge(
        left=intensity_df,
        right=metadata_df[["Sample", grouping]],
        on="Sample",
        copy=False,
    )

    intensity_name = default_intensity_column(intensity_df, intensity_name)

    log_base = _map_log_base(log_base)  # now log_base in [2, 10, None]

    proteins = intensity_df["Protein ID"].unique()
    p_values = []
    valid_protein_groups = []
    log2_fold_changes = []
    t_statistic = []
    fc_significance_df = pd.DataFrame(
        columns=["Protein ID", "fc_z_score", "fc_significance"]
    )
    for protein in proteins:
        protein_df = intensity_df[intensity_df["Protein ID"] == protein]
        group1_intensities = protein_df[protein_df[grouping] == group1][intensity_name]
        group2_intensities = protein_df[protein_df[grouping] == group2][intensity_name]

        group1_intensities = group1_intensities.dropna()
        group2_intensities = group2_intensities.dropna()
        if len(group1_intensities) < 2 or len(group2_intensities) < 2:
            if not exists_message(messages, INVALID_PROTEINGROUP_DATA_MSG):
                messages.append(INVALID_PROTEINGROUP_DATA_MSG)
            continue

        t, p = stats.ttest_ind(
            group1_intensities,
            group2_intensities,
            equal_var=(ttest_type == "Student's t-Test"),
        )

        if not np.isnan(p):
            if log_base:
                log2_fold_change = np.median(group2_intensities) - np.median(
                    group1_intensities
                )
            else:
                log2_fold_change = np.log2(
                    np.median(group2_intensities) / np.median(group1_intensities)
                )

            valid_protein_groups.append(protein)
            p_values.append(p)
            t_statistic.append(t)
            log2_fold_changes.append(log2_fold_change)
        elif not exists_message(messages, INVALID_PROTEINGROUP_DATA_MSG):
            messages.append(INVALID_PROTEINGROUP_DATA_MSG)
        else:
            # if the protein has a NaN value in a sample, we just skip it
            pass

    if len(valid_protein_groups) == 0:
        messages.append(
            {
                "level": logging.ERROR,
                "msg": "No valid protein groups found for t-test analysis.",
            }
        )
        return dict(
            differentially_expressed_proteins_df=pd.DataFrame(
                columns=intensity_df.columns.tolist()
                + ["corrected_p_value", "log2_fold_change", "t_statistic"]
            ),
            significant_proteins_df=pd.DataFrame(
                columns=intensity_df.columns.tolist()
                + ["corrected_p_value", "log2_fold_change", "t_statistic"]
            ),
            corrected_p_values_df=pd.DataFrame(
                columns=["Protein ID", "corrected_p_value"]
            ),
            t_statistic_df=pd.DataFrame(columns=["Protein ID", "t_statistic"]),
            log2_fold_change_df=pd.DataFrame(
                columns=["Protein ID", "log2_fold_change"]
            ),
            fc_significance_df=pd.DataFrame(
                columns=["Protein ID", "fc_z_score", "fc_significance"]
            ),
            corrected_alpha=alpha,
            fc_zscore_alpha=fc_zscore_alpha,
            fc_zscore_filter=fc_zscore_filter,
            messages=messages,
        )

    fc_mean = np.mean(log2_fold_changes)
    fc_std = np.std(log2_fold_changes)
    if fc_std == 0 or np.isnan(fc_std):
        z_scores = np.zeros(len(log2_fold_changes))
    else:
        z_scores = np.abs((np.array(log2_fold_changes) - fc_mean) / fc_std)
    fc_significance = 1 - stats.norm.cdf(z_scores)
    fc_significance_df = pd.DataFrame(
        list(zip(valid_protein_groups, z_scores, fc_significance)),
        columns=["Protein ID", "fc_z_score", "fc_significance"],
    )

    (corrected_p_values, corrected_alpha) = apply_multiple_testing_correction(
        p_values=p_values,
        method=multiple_testing_correction_method,
        alpha=alpha,
    )

    corrected_p_values_df = pd.DataFrame(
        list(zip(valid_protein_groups, corrected_p_values)),
        columns=["Protein ID", "corrected_p_value"],
    )
    log2_fold_change_df = pd.DataFrame(
        list(zip(valid_protein_groups, log2_fold_changes)),
        columns=["Protein ID", "log2_fold_change"],
    )
    t_statistic_df = pd.DataFrame(
        list(zip(valid_protein_groups, t_statistic)),
        columns=["Protein ID", "t_statistic"],
    )

    dataframes = [
        corrected_p_values_df,
        log2_fold_change_df,
        t_statistic_df,
        fc_significance_df,
    ]

    for df in dataframes:
        intensity_df = pd.merge(intensity_df, df, on="Protein ID", how="left")

    differentially_expressed_proteins_df = intensity_df.loc[
        intensity_df["Protein ID"].isin(valid_protein_groups)
    ]

    significant_proteins_df = differentially_expressed_proteins_df[
        differentially_expressed_proteins_df["corrected_p_value"] <= corrected_alpha
    ]
    if fc_zscore_filter and not fc_significance_df.empty:
        significant_proteins_df = significant_proteins_df[
            significant_proteins_df["fc_significance"] <= fc_zscore_alpha
        ]

    return dict(
        differentially_expressed_proteins_df=differentially_expressed_proteins_df,
        significant_proteins_df=significant_proteins_df,
        corrected_p_values_df=corrected_p_values_df,
        t_statistic_df=t_statistic_df,
        log2_fold_change_df=log2_fold_change_df,
        fc_significance_df=fc_significance_df,
        corrected_alpha=corrected_alpha,
        fc_zscore_alpha=fc_zscore_alpha,
        fc_zscore_filter=fc_zscore_filter,
        # filtered_proteins=filtered_proteins,
        messages=messages,
    )
