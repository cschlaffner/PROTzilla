import logging

import numpy as np
import pandas as pd
import pytest

from backend.protzilla.constants.data_types import DataKey
from backend.protzilla.data_analysis.differential_expression import (
    anova,
    linear_model,
    t_test,
    mann_whitney_test_on_intensity_data,
    mann_whitney_test_on_ptm_data,
    kruskal_wallis_test_on_intensity_data,
    kruskal_wallis_test_on_ptm_data,
)
from backend.protzilla.data_analysis.plots import create_volcano_plot


@pytest.fixture
def diff_expr_test_data():
    test_intensity_list = (
        ["Sample1", "Protein1", "Gene1", 20],
        ["Sample1", "Protein2", "Gene1", 16],
        ["Sample1", "Protein3", "Gene1", 1],
        ["Sample1", "Protein4", "Gene1", 14],
        ["Sample2", "Protein1", "Gene1", 20],
        ["Sample2", "Protein2", "Gene1", 15],
        ["Sample2", "Protein3", "Gene1", 2],
        ["Sample2", "Protein4", "Gene1", 15],
        ["Sample3", "Protein1", "Gene1", 22],
        ["Sample3", "Protein2", "Gene1", 14],
        ["Sample3", "Protein3", "Gene1", 3],
        ["Sample3", "Protein4", "Gene1", 16],
        ["Sample4", "Protein1", "Gene1", 8],
        ["Sample4", "Protein2", "Gene1", 15],
        ["Sample4", "Protein3", "Gene1", 1],
        ["Sample4", "Protein4", "Gene1", 9],
        ["Sample5", "Protein1", "Gene1", 10],
        ["Sample5", "Protein2", "Gene1", 14],
        ["Sample5", "Protein3", "Gene1", 2],
        ["Sample5", "Protein4", "Gene1", 10],
        ["Sample6", "Protein1", "Gene1", 12],
        ["Sample6", "Protein2", "Gene1", 13],
        ["Sample6", "Protein3", "Gene1", 3],
        ["Sample6", "Protein4", "Gene1", 11],
        ["Sample7", "Protein1", "Gene1", 12],
        ["Sample7", "Protein2", "Gene1", 13],
        ["Sample7", "Protein3", "Gene1", 3],
        ["Sample7", "Protein4", "Gene1", 11],
    )

    test_protein_df = pd.DataFrame(
        data=test_intensity_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    test_metadata_list = (
        ["Sample1", "Group1"],
        ["Sample2", "Group1"],
        ["Sample3", "Group1"],
        ["Sample4", "Group2"],
        ["Sample5", "Group2"],
        ["Sample6", "Group2"],
        ["Sample7", "Group3"],
    )

    test_metadata_df = pd.DataFrame(
        data=test_metadata_list,
        columns=["Sample", "Group"],
    )
    return test_protein_df, test_metadata_df


def test_differential_expression_linear_model(
    diff_expr_test_data,
    show_figures,
):
    test_protein_df, test_metadata_df = diff_expr_test_data
    test_alpha = 0.05
    test_fc_threshold = 0

    current_input = dict(
        protein_df=test_protein_df,
        metadata_df=test_metadata_df,
        grouping="Group",
        group1="Group1",
        group2="Group2",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
        log_base="log2",
    )
    current_out = linear_model(**current_input)

    fig = create_volcano_plot(
        corrected_p_values_df=current_out[DataKey.CORRECTED_P_VALUES_DF],
        log2_fold_change_df=current_out[DataKey.LOG2_FOLD_CHANGE_DF],
        alpha=current_out["corrected_alpha"],
        group1=current_input["group1"],
        group2=current_input["group2"],
        fc_threshold=test_fc_threshold,
    )

    if show_figures:
        fig.show()

    corrected_p_values = [0.0053, 0.3838, 1.0, 0.0072]
    log2_fc = [-10.1926, -1.0, 0.0, -5.0]
    differentially_expressed_proteins = ["Protein1", "Protein2", "Protein3", "Protein4"]

    p_values_rounded = [
        round(x, 4)
        for x in current_out[DataKey.CORRECTED_P_VALUES_DF]["corrected_p_value"]
    ]
    log2fc_rounded = [
        round(x, 4)
        for x in current_out[DataKey.LOG2_FOLD_CHANGE_DF]["log2_fold_change"]
    ]

    assert p_values_rounded == corrected_p_values
    assert log2fc_rounded == log2_fc
    assert (
        list(
            current_out[DataKey.DIFFERENTIALLY_EXPRESSED_PROTEINS_DF][
                "Protein ID"
            ].unique()
        )
        == differentially_expressed_proteins
    )
    assert current_out["corrected_alpha"] == test_alpha


def test_differential_expression_student_t_test(diff_expr_test_data, show_figures):
    test_protein_df, test_metadata_df = diff_expr_test_data
    test_alpha = 0.05
    test_fc_threshold = 0.9

    current_input = dict(
        protein_df=test_protein_df,
        metadata_df=test_metadata_df,
        ttest_type="Student's t-Test",
        grouping="Group",
        group1="Group1",
        group2="Group2",
        log_base="None",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
    )
    current_out = t_test(**current_input)

    fig = create_volcano_plot(
        current_out[DataKey.CORRECTED_P_VALUES_DF],
        current_out[DataKey.LOG2_FOLD_CHANGE_DF],
        test_fc_threshold,
        current_out["corrected_alpha"].value,
        current_input["group1"],
        current_input["group2"],
    )
    if show_figures:
        fig.show()

    corrected_p_values = [0.0053, 0.3838, 1.0, 0.0072]
    differentially_expressed_proteins = [
        "Protein1",
        "Protein2",
        "Protein3",
        "Protein4",
    ]
    significant_proteins = ["Protein1", "Protein4"]

    p_values_rounded = [
        round(x, 4)
        for x in current_out[DataKey.CORRECTED_P_VALUES_DF]["corrected_p_value"]
    ]
    log2fc_rounded = [
        round(x, 4)
        for x in current_out[DataKey.LOG2_FOLD_CHANGE_DF]["log2_fold_change"]
    ]

    assert p_values_rounded == corrected_p_values
    assert (
        list(
            current_out[DataKey.DIFFERENTIALLY_EXPRESSED_PROTEINS_DF][
                "Protein ID"
            ].unique()
        )
        == differentially_expressed_proteins
    )
    assert current_out["corrected_alpha"].value == test_alpha
    assert (
        list(current_out[DataKey.SIGNIFICANT_PROTEINS_DF]["Protein ID"].unique())
        == significant_proteins
    )


def test_differential_expression_welch_t_test(diff_expr_test_data, show_figures):
    test_protein_df, test_metadata_df = diff_expr_test_data
    test_alpha = 0.05
    test_fc_threshold = 0.9

    current_input = dict(
        protein_df=test_protein_df,
        metadata_df=test_metadata_df,
        ttest_type="Welch's t-Test",
        grouping="Group",
        group1="Group1",
        group2="Group2",
        log_base="None",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
    )
    current_out = t_test(**current_input)

    fig = create_volcano_plot(
        current_out[DataKey.CORRECTED_P_VALUES_DF],
        current_out[DataKey.LOG2_FOLD_CHANGE_DF],
        test_fc_threshold,
        current_out["corrected_alpha"].value,
        current_input["group1"],
        current_input["group2"],
    )
    if show_figures:
        fig.show()

    corrected_p_values = [0.0072, 0.3838, 1.0, 0.0072]
    differentially_expressed_proteins = [
        "Protein1",
        "Protein2",
        "Protein3",
        "Protein4",
    ]
    significant_proteins = ["Protein1", "Protein4"]

    p_values_rounded = [
        round(x, 4)
        for x in current_out[DataKey.CORRECTED_P_VALUES_DF]["corrected_p_value"]
    ]
    log2fc_rounded = [
        round(x, 4)
        for x in current_out[DataKey.LOG2_FOLD_CHANGE_DF]["log2_fold_change"]
    ]

    assert p_values_rounded == corrected_p_values
    assert (
        list(
            current_out[DataKey.DIFFERENTIALLY_EXPRESSED_PROTEINS_DF][
                "Protein ID"
            ].unique()
        )
        == differentially_expressed_proteins
    )
    assert current_out["corrected_alpha"].value == test_alpha
    assert (
        list(current_out[DataKey.SIGNIFICANT_PROTEINS_DF]["Protein ID"].unique())
        == significant_proteins
    )


def test_differential_expression_t_test_with_fc_zscore_filter(diff_expr_test_data):
    test_intensity_df, test_metadata_df = diff_expr_test_data
    test_alpha = 0.05

    current_out = t_test(
        protein_df=test_intensity_df,
        metadata_df=test_metadata_df,
        ttest_type="Welch's t-Test",
        grouping="Group",
        group1="Group1",
        group2="Group2",
        log_base="None",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
        fc_zscore_filter=True,
        fc_zscore_alpha=0.25,
    )

    # Fold-change Z-score filter should keep only Protein1 (Protein4 drops because fc_significance is too high)
    fc_significance = current_out["fc_significance_df"]
    assert not fc_significance.empty
    assert (
        round(
            fc_significance.loc[fc_significance["Protein ID"] == "Protein1"][
                "fc_significance"
            ].iloc[0],
            2,
        )
        == 0.07
    )
    assert list(
        current_out[DataKey.SIGNIFICANT_PROTEINS_DF]["Protein ID"].unique()
    ) == ["Protein1"]


def test_differential_expression_t_test_types(diff_expr_test_data, show_figures):
    test_protein_df, test_metadata_df = diff_expr_test_data
    test_alpha = 0.05

    # Run Student's t-test
    student_out = t_test(
        protein_df=test_protein_df,
        metadata_df=test_metadata_df,
        ttest_type="Student's t-Test",
        grouping="Group",
        group1="Group1",
        group2="Group2",
        log_base="None",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
    )

    # Run Welch's t-test
    welch_out = t_test(
        protein_df=test_protein_df,
        metadata_df=test_metadata_df,
        ttest_type="Welch's t-Test",
        grouping="Group",
        group1="Group1",
        group2="Group2",
        log_base="None",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
    )

    # Check if the p-values are different
    assert not np.array_equal(
        student_out[DataKey.CORRECTED_P_VALUES_DF]["corrected_p_value"],
        welch_out[DataKey.CORRECTED_P_VALUES_DF]["corrected_p_value"],
    )


def test_differential_expression_t_test_with_log_data(show_figures):
    test_intensity_list = (
        ["Sample1", "Protein1", "Gene1"],
        ["Sample1", "Protein2", "Gene1"],
        ["Sample2", "Protein1", "Gene1"],
        ["Sample2", "Protein2", "Gene1"],
        ["Sample3", "Protein1", "Gene1"],
        ["Sample3", "Protein2", "Gene1"],
        ["Sample4", "Protein1", "Gene1"],
        ["Sample4", "Protein2", "Gene1"],
        ["Sample5", "Protein1", "Gene1"],
        ["Sample5", "Protein2", "Gene1"],
        ["Sample6", "Protein1", "Gene1"],
        ["Sample6", "Protein2", "Gene1"],
    )
    intensities = np.log2([18, 16, 20, 15, 22, 14, 8, 15, 10, 14, 12, 13])
    test_protein_df = pd.DataFrame(
        data=test_intensity_list,
        columns=["Sample", "Protein ID", "Gene"],
    )

    test_protein_df["Intensity"] = intensities

    test_metadata_list = (
        ["Sample1", "Group1"],
        ["Sample2", "Group1"],
        ["Sample3", "Group1"],
        ["Sample4", "Group2"],
        ["Sample5", "Group2"],
        ["Sample6", "Group2"],
        ["Sample7", "Group3"],
    )

    test_metadata_df = pd.DataFrame(
        data=test_metadata_list,
        columns=["Sample", "Group"],
    )

    test_alpha = 0.05

    current_out = t_test(
        protein_df=test_protein_df,
        metadata_df=test_metadata_df,
        ttest_type="Student's t-Test",
        grouping="Group",
        group1="Group1",
        group2="Group2",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
        log_base="log2",
    )

    log2_fc = [-1, -0.1]
    # because of the longer fc calculation the comparison does not work as accurately as on paper (inaccuracy due to multiple float operations)
    log2fc_rounded = [
        round(x, 1)
        for x in current_out[DataKey.LOG2_FOLD_CHANGE_DF]["log2_fold_change"]
    ]

    assert log2fc_rounded == log2_fc


def test_differential_expression_t_test_with_silac_ratios():
    """
    SILAC ratio data contains NaN values in both groups.
    nan_policy='omit' tells scipy to drop NaN before the t-test, yielding a valid p-value.

    Group1 ratios: [1.2, NaN, 1.1]  →  omit NaN for t-test: [1.2, 1.1]
    Group2 ratios: [0.8, 0.9, NaN]  →  omit NaN for t-test: [0.8, 0.9]

    NOTE: Fold change uses np.median() (not np.nanmedian()), so NaN in either group
    causes the fold change itself to be NaN. Only the p-value is reliable here.
    """
    silac_ratio_df = pd.DataFrame(
        data=[
            ["Sample1", "Protein1", "Gene1", 1.2],
            ["Sample2", "Protein1", "Gene1", np.nan],
            ["Sample3", "Protein1", "Gene1", 1.1],
            ["Sample4", "Protein1", "Gene1", 0.8],
            ["Sample5", "Protein1", "Gene1", 0.9],
            ["Sample6", "Protein1", "Gene1", np.nan],
        ],
        columns=["Sample", "Protein ID", "Gene", "Ratio H/L"],
    )

    metadata_df = pd.DataFrame(
        data=[
            ["Sample1", "Group1"],
            ["Sample2", "Group1"],
            ["Sample3", "Group1"],
            ["Sample4", "Group2"],
            ["Sample5", "Group2"],
            ["Sample6", "Group2"],
        ],
        columns=["Sample", "Group"],
    )

    out = t_test(
        protein_df=silac_ratio_df,
        metadata_df=metadata_df,
        ttest_type="Welch's t-Test",
        grouping="Group",
        group1="Group1",
        group2="Group2",
        log_base="None",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=0.05,
        nan_policy="omit",
    )

    # Protein1 IS included because scipy returned a valid p-value after omitting NaN.
    assert not out[DataKey.CORRECTED_P_VALUES_DF].empty
    assert out[DataKey.CORRECTED_P_VALUES_DF]["Protein ID"].tolist() == ["Protein1"]
    assert (
        round(out[DataKey.CORRECTED_P_VALUES_DF]["corrected_p_value"].iloc[0], 4)
        == 0.0513
    )
    # Fold change is NaN because np.median([1.2, NaN, 1.1]) = NaN (not nanmedian).
    assert np.isnan(out[DataKey.LOG2_FOLD_CHANGE_DF]["log2_fold_change"].iloc[0])


@pytest.fixture
def nan_intensity_data():
    """Intensity data where one sample per group contains a NaN value."""
    protein_df = pd.DataFrame(
        data=[
            ["Sample1", "Protein1", "Gene1", 18.0],
            ["Sample2", "Protein1", "Gene1", np.nan],
            ["Sample3", "Protein1", "Gene1", 22.0],
            ["Sample4", "Protein1", "Gene1", 8.0],
            ["Sample5", "Protein1", "Gene1", 10.0],
            ["Sample6", "Protein1", "Gene1", 12.0],
        ],
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )
    metadata_df = pd.DataFrame(
        data=[
            ["Sample1", "Group1"],
            ["Sample2", "Group1"],
            ["Sample3", "Group1"],
            ["Sample4", "Group2"],
            ["Sample5", "Group2"],
            ["Sample6", "Group2"],
        ],
        columns=["Sample", "Group"],
    )
    return protein_df, metadata_df


@pytest.fixture
def nan_intensity_data_insufficient_after_omit():
    """
    Intensity data where each group has exactly 2 samples, one of which is NaN.

    After nan_policy='omit' drops the NaN, each group is left with only 1 valid
    sample — insufficient for a two-sample t-test. scipy returns NaN for both
    t-statistic and p-value in this degenerate case.

        Group1: [18.0, NaN]  →  after omit: [18.0]  (1 sample, variance undefined)
        Group2: [8.0,  NaN]  →  after omit: [8.0]   (1 sample, variance undefined)
    """
    protein_df = pd.DataFrame(
        data=[
            ["Sample1", "Protein1", "Gene1", 18.0],
            ["Sample2", "Protein1", "Gene1", np.nan],
            ["Sample3", "Protein1", "Gene1", 8.0],
            ["Sample4", "Protein1", "Gene1", np.nan],
        ],
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )
    metadata_df = pd.DataFrame(
        data=[
            ["Sample1", "Group1"],
            ["Sample2", "Group1"],
            ["Sample3", "Group2"],
            ["Sample4", "Group2"],
        ],
        columns=["Sample", "Group"],
    )
    return protein_df, metadata_df


def test_t_test_nan_policy_omit_raises_nan_when_too_few_samples_remain(
    nan_intensity_data_insufficient_after_omit,
):
    """
    nan_policy='omit' with only 2 samples per group where 1 is NaN:
    after omission only 1 valid sample remains per group, which is insufficient
    for a t-test. scipy returns NaN for the p-value, so the protein is excluded
    and the function signals the problem via INVALID_PROTEINGROUP_DATA_MSG.

        Group1: [18.0, NaN]  →  after omit: [18.0]  →  p = NaN  →  protein excluded
        Group2: [8.0,  NaN]  →  after omit: [8.0]
    """
    protein_df, metadata_df = nan_intensity_data_insufficient_after_omit

    out = t_test(
        protein_df=protein_df,
        metadata_df=metadata_df,
        ttest_type="Welch's t-Test",
        grouping="Group",
        group1="Group1",
        group2="Group2",
        log_base="None",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=0.05,
        nan_policy="omit",
    )

    # No valid p-value could be computed → protein is excluded from all result dataframes.
    assert out[DataKey.CORRECTED_P_VALUES_DF].empty
    assert out[DataKey.LOG2_FOLD_CHANGE_DF].empty

    # The function should report that insufficient data was found.
    from backend.protzilla.data_analysis.differential_expression_helper import (
        INVALID_PROTEINGROUP_DATA_MSG,
    )

    assert any(message == INVALID_PROTEINGROUP_DATA_MSG for message in out["messages"])


def test_t_test_nan_policy_omit_skips_nan_samples_and_computes_result(
    nan_intensity_data,
):
    """
    nan_policy='omit': NaN samples are silently dropped before the t-test runs,
    so scipy returns a valid p-value and the protein is kept in the results.

    Data layout (nan_intensity_data fixture):
        Group1: [18.0, NaN, 22.0]  →  after omitting NaN: [18.0, 22.0]  →  valid p-value
        Group2: [8.0, 10.0, 12.0]  →  no NaNs

    NOTE: The fold change is computed with np.median() (not np.nanmedian()), so a NaN
    in the raw group data causes the fold change to be NaN even under 'omit' policy.
    This is a known limitation of the current implementation.
    """
    protein_df, metadata_df = nan_intensity_data
    common_kwargs = dict(
        protein_df=protein_df,
        metadata_df=metadata_df,
        grouping="Group",
        group1="Group1",
        group2="Group2",
        log_base="None",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=0.05,
        nan_policy="omit",
    )

    for ttest_type in ["Welch's t-Test", "Student's t-Test"]:
        out = t_test(ttest_type=ttest_type, **common_kwargs)
        # The protein IS included because scipy found a valid p-value after omitting NaN.
        assert not out[
            DataKey.CORRECTED_P_VALUES_DF
        ].empty, f"ttest_type={ttest_type}: Protein1 should be included after NaN samples are omitted"
        assert out[DataKey.CORRECTED_P_VALUES_DF]["Protein ID"].tolist() == ["Protein1"]
        # Fold change is NaN because np.median([18.0, NaN, 22.0]) = NaN (not nanmedian).
        assert np.isnan(
            out[DataKey.LOG2_FOLD_CHANGE_DF]["log2_fold_change"].iloc[0]
        ), f"ttest_type={ttest_type}: expected NaN fold change (median does not skip NaN)"


def test_t_test_nan_policy_propagate_excludes_protein_with_any_nan(nan_intensity_data):
    """
    nan_policy='propagate': a NaN anywhere in a group causes the t-test to return NaN
    for that protein. The protein is then excluded from the output entirely.

    Data layout (nan_intensity_data fixture):
        Group1: [18.0, NaN, 22.0]  →  one NaN → t-test returns p = NaN → Protein1 excluded
        Group2: [8.0, 10.0, 12.0]  →  (no NaNs, but NaN from Group1 already propagated)

    Expected: corrected_p_values_df is empty because no protein produced a valid p-value.
    """
    protein_df, metadata_df = nan_intensity_data

    out = t_test(
        protein_df=protein_df,
        metadata_df=metadata_df,
        ttest_type="Welch's t-Test",
        grouping="Group",
        group1="Group1",
        group2="Group2",
        log_base="None",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=0.05,
        nan_policy="propagate",
    )

    assert out[
        DataKey.CORRECTED_P_VALUES_DF
    ].empty, "Protein1 should be excluded because the NaN in Group1 propagated to the p-value"


def test_t_test_nan_policy_raise_errors_when_nan_is_present(nan_intensity_data):
    """
    nan_policy='raise': a ValueError is raised immediately when any NaN value is
    detected in the input data. Use this policy to treat NaN as a hard error that
    must be resolved before running the analysis.

    Data layout (nan_intensity_data fixture):
        Group1: [18.0, NaN, 22.0]  →  NaN is present → ValueError is raised
    """
    protein_df, metadata_df = nan_intensity_data

    with pytest.raises(ValueError):
        t_test(
            protein_df=protein_df,
            metadata_df=metadata_df,
            ttest_type="Welch's t-Test",
            grouping="Group",
            group1="Group1",
            group2="Group2",
            log_base="None",
            multiple_testing_correction_method="Benjamini-Hochberg",
            alpha=0.05,
            nan_policy="raise",
        )


def test_differential_expression_anova(show_figures):
    test_intensity_list = (
        ["Sample1", "Protein1", "Gene1", 18],
        ["Sample1", "Protein2", "Gene1", 16],
        ["Sample1", "Protein3", "Gene1", 1],
        ["Sample2", "Protein1", "Gene1", 20],
        ["Sample2", "Protein2", "Gene1", 15],
        ["Sample2", "Protein3", "Gene1", 2],
        ["Sample3", "Protein1", "Gene1", 22],
        ["Sample3", "Protein2", "Gene1", 14],
        ["Sample3", "Protein3", "Gene1", 3],
        ["Sample4", "Protein1", "Gene1", 8],
        ["Sample4", "Protein2", "Gene1", 2],
        ["Sample4", "Protein3", "Gene1", 1],
        ["Sample5", "Protein1", "Gene1", 10],
        ["Sample5", "Protein2", "Gene1", 5],
        ["Sample5", "Protein3", "Gene1", 2],
        ["Sample6", "Protein1", "Gene1", 12],
        ["Sample6", "Protein2", "Gene1", 4],
        ["Sample6", "Protein3", "Gene1", 3],
    )

    test_protein_df = pd.DataFrame(
        data=test_intensity_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    test_metadata_list = (
        ["Sample1", "Group1"],
        ["Sample2", "Group1"],
        ["Sample3", "Group1"],
        ["Sample4", "Group2"],
        ["Sample5", "Group2"],
        ["Sample6", "Group2"],
    )

    test_metadata_df = pd.DataFrame(
        data=test_metadata_list,
        columns=["Sample", "Group"],
    )

    output_dict = anova(
        protein_df=test_protein_df,
        metadata_df=test_metadata_df,
        grouping="Group",
        selected_groups=test_metadata_df["Group"].unique().tolist(),
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=0.05,
    )
    corrected_p_values_df = output_dict[DataKey.CORRECTED_P_VALUES_DF]

    p_values_rounded = [round(x, 4) for x in corrected_p_values_df["corrected_p_value"]]
    assertion_p_values = [
        0.0054,
        0.0013,
        1.0000,
    ]

    assert assertion_p_values == p_values_rounded


def test_differential_expression_mann_whitney_on_intensity(
    diff_expr_test_data,
    show_figures,
):
    test_protein_df, test_metadata_df = diff_expr_test_data
    test_alpha = 0.05

    current_input = dict(
        protein_df=test_protein_df,
        metadata_df=test_metadata_df,
        grouping="Group",
        group1="Group1",
        group2="Group2",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
        log_base="log2",
        p_value_calculation_method="auto",
    )
    current_out = mann_whitney_test_on_intensity_data(**current_input)

    fig = create_volcano_plot(
        corrected_p_values_df=current_out[DataKey.CORRECTED_P_VALUES_DF],
        log2_fold_change_df=current_out[DataKey.LOG2_FOLD_CHANGE_DF],
        alpha=current_out["corrected_alpha"],
        group1=current_input["group1"],
        group2=current_input["group2"],
        fc_threshold=0,
    )

    if show_figures:
        fig.show()

    expected_corrected_p_values = [0.2, 0.4916, 1.0, 0.2]
    expected_u_statistics = [9.0, 7.0, 4.5, 9.0]
    expected_log2_fc = [-10.1926, -1.0, 0.0, -5.0]
    expected_differentially_expressed_proteins = [
        "Protein1",
        "Protein2",
        "Protein3",
        "Protein4",
    ]

    p_values_rounded = [
        round(x, 4)
        for x in current_out[DataKey.CORRECTED_P_VALUES_DF]["corrected_p_value"]
    ]
    u_statistics = current_out["u_statistic_df"]["u_statistic"]
    log2fc_rounded = [
        round(x, 4)
        for x in current_out[DataKey.LOG2_FOLD_CHANGE_DF]["log2_fold_change"]
    ]

    assert p_values_rounded == expected_corrected_p_values
    assert all(u_statistics == expected_u_statistics)
    assert log2fc_rounded == expected_log2_fc
    assert (
        list(
            current_out[DataKey.DIFFERENTIALLY_EXPRESSED_PROTEINS_DF][
                "Protein ID"
            ].unique()
        )
        == expected_differentially_expressed_proteins
    )
    assert current_out["corrected_alpha"] == test_alpha


def test_differential_expression_kruskal_wallis_on_intensity_three_groups(
    diff_expr_test_data,
    show_figures,
):
    test_protein_df, test_metadata_df = diff_expr_test_data
    test_alpha = 0.05

    current_input = dict(
        protein_df=test_protein_df,
        metadata_df=test_metadata_df,
        grouping="Group",
        selected_groups=["Group1", "Group2", "Group3"],
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
    )
    current_out = kruskal_wallis_test_on_intensity_data(**current_input)

    expected_corrected_p_values = [0.175, 0.33, 0.5712, 0.175]

    expected_h_statistics = [4.963, 2.7925, 1.12, 4.8727]
    expected_differentially_expressed_proteins = [
        "Protein1",
        "Protein2",
        "Protein3",
        "Protein4",
    ]

    p_values_rounded = [
        round(x, 4)
        for x in current_out[DataKey.CORRECTED_P_VALUES_DF]["corrected_p_value"]
    ]
    h_statistics_rounded = [
        round(x, 4) for x in current_out["h_statistic_df"]["h_statistic"]
    ]

    assert p_values_rounded == expected_corrected_p_values
    assert h_statistics_rounded == expected_h_statistics
    assert (
        list(
            current_out[DataKey.DIFFERENTIALLY_EXPRESSED_PROTEINS_DF][
                "Protein ID"
            ].unique()
        )
        == expected_differentially_expressed_proteins
    )
    assert current_out["corrected_alpha"] == test_alpha


def test_differential_expression_kruskal_wallis_on_intensity_group_handling(
    diff_expr_test_data,
    show_figures,
):
    test_protein_df, test_metadata_df = diff_expr_test_data
    test_alpha = 0.05

    current_input = dict(
        protein_df=test_protein_df,
        metadata_df=test_metadata_df,
        grouping="Group",
        selected_groups=["Group1", "wrong_group"],
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
    )
    current_out = kruskal_wallis_test_on_intensity_data(**current_input)

    assert "messages" in current_out
    assert any(
        message["level"] == logging.WARNING
        and "Group 'wrong_group' were not found in metadata" in message["msg"]
        for message in current_out["messages"]
    )
    assert any(
        message["level"] == logging.WARNING
        and "Auto-selected the groups 'Group1', 'Group2', 'Group3'" in message["msg"]
        for message in current_out["messages"]
    )

    expected_corrected_p_values = [0.175, 0.33, 0.5712, 0.175]
    p_values_rounded = [
        round(x, 4)
        for x in current_out[DataKey.CORRECTED_P_VALUES_DF]["corrected_p_value"]
    ]
    assert p_values_rounded == expected_corrected_p_values


def test_kruskal_wallis_too_few_groups(diff_expr_test_data):
    test_intensity_df, _ = diff_expr_test_data
    test_metadata_df = pd.DataFrame(
        data=(
            ["Sample7", "Group3"],
            ["Sample8", "Group4"],
            ["Sample9", "Group5"],
        ),
        columns=["Sample", "Group"],
    )

    test_alpha = 0.05

    current_input = dict(
        protein_df=test_intensity_df,
        metadata_df=test_metadata_df,
        grouping="Group",
        selected_groups=["wrong_group1", "wrong_group2"],
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
    )
    with pytest.raises(
        ValueError,
        match="At least two groups from the metadata must also be present in the data for differential expression analysis.",
    ):
        _ = kruskal_wallis_test_on_intensity_data(**current_input)


def test_kruskal_wallis_invalid_groups_selected(diff_expr_test_data):
    test_intensity_df, test_metadata_df = diff_expr_test_data
    additional_metadata = pd.DataFrame(
        data=(
            ["Sample8", "Group4"],
            ["Sample9", "Group5"],
        ),
        columns=["Sample", "Group"],
    )
    test_metadata_df = pd.concat(
        [test_metadata_df, additional_metadata], ignore_index=True
    )

    test_alpha = 0.05

    current_input = dict(
        protein_df=test_intensity_df,
        metadata_df=test_metadata_df,
        grouping="Group",
        selected_groups=["Group1", "Group2", "Group4", "Group5"],
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
    )
    current_out = kruskal_wallis_test_on_intensity_data(**current_input)

    assert "messages" in current_out and len(current_out["messages"]) == 1
    first_message = current_out["messages"][0]
    assert (
        first_message["level"] == logging.WARNING
        and first_message["msg"]
        == "Groups 'Group4', 'Group5' were not found in the data and thus removed."
    )

    current_input = dict(
        protein_df=test_intensity_df,
        metadata_df=test_metadata_df,
        grouping="Group",
        selected_groups=["Group4", "Group5"],
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
    )
    current_out = kruskal_wallis_test_on_intensity_data(**current_input)

    assert "messages" in current_out and len(current_out["messages"]) == 2
    sorted_messages = sorted(current_out["messages"], key=lambda x: x["msg"])
    assert (
        sorted_messages[0]["level"] == logging.WARNING
        and "Auto-selected the groups 'Group1', 'Group2', 'Group3'"
        in sorted_messages[0]["msg"]
    )
    assert (
        sorted_messages[1]["level"] == logging.WARNING
        and "Groups 'Group4', 'Group5' were not found in the data and thus removed."
        in sorted_messages[1]["msg"]
    )


@pytest.fixture
def ptm_test_data():
    test_amount_list = (
        ["Sample1", 1, 1, 10, 1, 100, 100],
        ["Sample2", 2, 2, 10, 1, 100, 100],
        ["Sample3", 3, 3, 10, 1, 100, 100],
        ["Sample4", 4, 4, 10, 1, 100, 100],
        ["Sample5", 5, 5, 10, 1, 100, 100],
        ["Sample6", 6, 3, 11, 111, 100, 100],
        ["Sample7", 7, 4, 12, 222, 100, 100],
        ["Sample8", 8, 5, 13, 333, 100, 100],
        ["Sample9", 9, 6, 14, 444, 100, 100],
        ["Sample10", 10, 7, 15, 555, 100, 100],
        ["Sample11", 11, 5, 16, 1111, 100, 100],
        ["Sample12", 12, 6, 17, 2222, 100, 100],
        ["Sample13", 13, 7, 18, 3333, 100, 100],
        ["Sample14", 14, 8, 19, 4444, 100, 100],
        ["Sample15", 15, 9, 20, 5555, 100, 100],
    )
    test_amount_df = pd.DataFrame(
        data=test_amount_list,
        columns=[
            "Sample",
            "Oxidation",
            "Acetyl",
            "GlyGly",
            "Phospho",
            "Unmodified",
            "Total Amount of Peptides",
        ],
    )

    test_metadata_list = (
        ["Sample1", "Group1"],
        ["Sample2", "Group1"],
        ["Sample3", "Group1"],
        ["Sample4", "Group1"],
        ["Sample5", "Group1"],
        ["Sample6", "Group2"],
        ["Sample7", "Group2"],
        ["Sample8", "Group2"],
        ["Sample9", "Group2"],
        ["Sample10", "Group2"],
        ["Sample11", "Group3"],
        ["Sample12", "Group3"],
        ["Sample13", "Group3"],
        ["Sample14", "Group3"],
        ["Sample15", "Group3"],
    )
    test_metadata_df = pd.DataFrame(
        data=test_metadata_list,
        columns=["Sample", "Group"],
    )

    return test_amount_df, test_metadata_df


def test_differential_expression_mann_whitney_on_ptm(
    ptm_test_data,
    show_figures,
):
    test_amount_df, test_metadata_df = ptm_test_data
    test_alpha = 0.05

    current_input = dict(
        ptm_df=test_amount_df,
        metadata_df=test_metadata_df,
        grouping="Group",
        group1="Group1",
        group2="Group2",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
        p_value_calculation_method="auto",
    )
    current_out = mann_whitney_test_on_ptm_data(**current_input)

    expected_corrected_p_values = [0.0132, 0.1423, 0.0132, 0.0132, 1.00000]
    expected_u_statistics = [0.0, 4.5, 0.0, 0.0, 12.5]
    expected_log2_fc = [1.415, 0.737, 0.3785, 8.3794, 0.0]

    expected_significant_ptms = ["Oxidation", "GlyGly", "Phospho"]

    p_values_rounded = [
        round(x, 4)
        for x in current_out[DataKey.CORRECTED_P_VALUES_DF]["corrected_p_value"]
    ]
    u_statistics = current_out["u_statistic_df"]["u_statistic"]
    log2_fc_rounded = [
        round(x, 4)
        for x in current_out[DataKey.LOG2_FOLD_CHANGE_DF]["log2_fold_change"]
    ]

    assert p_values_rounded == expected_corrected_p_values
    assert all(u_statistics == expected_u_statistics)
    assert log2_fc_rounded == expected_log2_fc
    assert (
        list(current_out["significant_ptm_df"]["PTM"].unique())
        == expected_significant_ptms
    )
    assert current_out["corrected_alpha"] == test_alpha


def test_differential_expression_kruskal_wallis_on_ptm(
    ptm_test_data,
    show_figures,
):
    test_amount_df, test_metadata_df = ptm_test_data
    test_alpha = 0.05

    current_input = dict(
        ptm_df=test_amount_df,
        metadata_df=test_metadata_df,
        grouping="Group",
        selected_groups=["Group1", "Group2", "Group3"],
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=test_alpha,
    )
    current_out = kruskal_wallis_test_on_ptm_data(**current_input)

    expected_corrected_p_values = [0.0026, 0.0173, 0.0026, 0.0026]
    expected_h_statistics = [12.5, 8.1159, 12.963, 12.963]
    expected_significant_ptms = ["Oxidation", "Acetyl", "GlyGly", "Phospho"]

    p_values_rounded = [
        round(x, 4)
        for x in current_out[DataKey.CORRECTED_P_VALUES_DF]["corrected_p_value"]
    ]
    h_statistics_rounded = [
        round(x, 4) for x in current_out["h_statistic_df"]["h_statistic"]
    ]

    assert p_values_rounded == expected_corrected_p_values
    assert h_statistics_rounded == expected_h_statistics
    assert (
        list(current_out["significant_ptm_df"]["PTM"].unique())
        == expected_significant_ptms
    )
    assert current_out["corrected_alpha"] == test_alpha


def test_differential_expression_t_test_empty_p_values():
    """Test that t-test handles empty p-values correctly when all proteins are invalid."""
    test_intensity_df = pd.DataFrame(
        data=[
            ["Sample1", "Protein1", "Gene1", np.nan],
            ["Sample2", "Protein1", "Gene1", np.nan],
            ["Sample3", "Protein1", "Gene1", np.nan],
            ["Sample4", "Protein1", "Gene1", np.nan],
        ],
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    test_metadata_df = pd.DataFrame(
        data=[
            ["Sample1", "Group1"],
            ["Sample2", "Group1"],
            ["Sample3", "Group2"],
            ["Sample4", "Group2"],
        ],
        columns=["Sample", "Group"],
    )

    # nan_policy="propagate": all intensities are NaN → every protein's p-value is NaN
    # → no valid protein groups → function returns empty dataframes + error message.
    # (nan_policy="raise" would crash immediately; "omit" would leave empty groups → same NaN result)
    current_out = t_test(
        protein_df=test_intensity_df,
        metadata_df=test_metadata_df,
        ttest_type="Welch's t-Test",
        grouping="Group",
        group1="Group1",
        group2="Group2",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=0.05,
        log_base="None",
        nan_policy="propagate",
    )

    # Check that all dataframes are empty but with correct columns
    assert current_out[DataKey.DIFFERENTIALLY_EXPRESSED_PROTEINS_DF].empty
    assert current_out[DataKey.SIGNIFICANT_PROTEINS_DF].empty
    assert current_out[DataKey.CORRECTED_P_VALUES_DF].empty
    assert current_out["t_statistic_df"].empty
    assert current_out[DataKey.LOG2_FOLD_CHANGE_DF].empty
    assert current_out["corrected_alpha"] == 0.05

    # Check that an error message was generated
    assert any(
        message["level"] == logging.ERROR
        and "No valid protein groups found for t-test analysis" in message["msg"]
        for message in current_out["messages"]
    )


def test_differential_expression_anova_empty_p_values():
    """Test that ANOVA handles empty p-values correctly when all proteins are invalid."""
    test_intensity_df = pd.DataFrame(
        data=[
            ["Sample1", "Protein1", "Gene1", 10],
            ["Sample2", "Protein1", "Gene1", 10],
            ["Sample3", "Protein1", "Gene1", 10],
            ["Sample4", "Protein1", "Gene1", 10],
        ],
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    test_metadata_df = pd.DataFrame(
        data=[
            ["Sample1", "Group1"],
            ["Sample2", "Group1"],
            ["Sample3", "Group2"],
            ["Sample4", "Group2"],
        ],
        columns=["Sample", "Group"],
    )

    current_out = anova(
        protein_df=test_intensity_df,
        metadata_df=test_metadata_df,
        grouping="Group",
        selected_groups=["Group1", "Group2"],
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=0.05,
    )

    # Check that all dataframes are empty but with correct columns
    assert current_out[DataKey.DIFFERENTIALLY_EXPRESSED_PROTEINS_DF].empty
    assert current_out[DataKey.SIGNIFICANT_PROTEINS_DF].empty
    assert current_out[DataKey.CORRECTED_P_VALUES_DF].empty
    assert current_out["corrected_alpha"] == 0.05
    assert current_out["filtered_proteins"] == []

    # Check that an error message was generated
    assert any(
        message["level"] == logging.ERROR
        and "No valid protein groups found for ANOVA analysis" in message["msg"]
        for message in current_out["messages"]
    )


def test_differential_expression_linear_model_empty_p_values():
    """Test that linear model handles empty p-values correctly when all proteins are invalid."""
    test_intensity_df = pd.DataFrame(
        data=[
            ["Sample1", "Protein1", "Gene1", np.nan],
            ["Sample2", "Protein1", "Gene1", np.nan],
            ["Sample3", "Protein1", "Gene1", np.nan],
            ["Sample4", "Protein1", "Gene1", np.nan],
        ],
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    test_metadata_df = pd.DataFrame(
        data=[
            ["Sample1", "Group1"],
            ["Sample2", "Group1"],
            ["Sample3", "Group2"],
            ["Sample4", "Group2"],
        ],
        columns=["Sample", "Group"],
    )

    current_out = linear_model(
        protein_df=test_intensity_df,
        metadata_df=test_metadata_df,
        grouping="Group",
        group1="Group1",
        group2="Group2",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=0.05,
        log_base="None",
    )

    # Check that all dataframes are empty but with correct columns
    assert current_out[DataKey.DIFFERENTIALLY_EXPRESSED_PROTEINS_DF].empty
    assert current_out[DataKey.SIGNIFICANT_PROTEINS_DF].empty
    assert current_out[DataKey.CORRECTED_P_VALUES_DF].empty
    assert current_out[DataKey.LOG2_FOLD_CHANGE_DF].empty
    assert current_out["corrected_alpha"] == 0.05
    assert current_out["filtered_proteins"] == ["Protein1"]

    # Check that an error message was generated
    assert any(
        message["level"] == logging.ERROR
        and "No valid protein groups found for linear model analysis" in message["msg"]
        for message in current_out["messages"]
    )


def test_differential_expression_mann_whitney_empty_p_values():
    """Test that Mann-Whitney U test handles empty p-values correctly when all proteins are invalid."""
    test_intensity_df = pd.DataFrame(
        data=[
            ["Sample1", "Protein1", "Gene1", np.nan],
            ["Sample2", "Protein1", "Gene1", np.nan],
            ["Sample3", "Protein1", "Gene1", np.nan],
            ["Sample4", "Protein1", "Gene1", np.nan],
        ],
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    test_metadata_df = pd.DataFrame(
        data=[
            ["Sample1", "Group1"],
            ["Sample2", "Group1"],
            ["Sample3", "Group2"],
            ["Sample4", "Group2"],
        ],
        columns=["Sample", "Group"],
    )

    current_out = mann_whitney_test_on_intensity_data(
        protein_df=test_intensity_df,
        metadata_df=test_metadata_df,
        grouping="Group",
        group1="Group1",
        group2="Group2",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=0.05,
        log_base="None",
    )

    # Check that all dataframes are empty but with correct columns
    assert current_out[DataKey.DIFFERENTIALLY_EXPRESSED_PROTEINS_DF].empty
    assert current_out[DataKey.SIGNIFICANT_PROTEINS_DF].empty
    assert current_out[DataKey.CORRECTED_P_VALUES_DF].empty
    assert current_out["u_statistic_df"].empty
    assert current_out[DataKey.LOG2_FOLD_CHANGE_DF].empty
    assert current_out["corrected_alpha"] == 0.05

    # Check that an error message was generated
    assert any(
        message["level"] == logging.ERROR
        and "No valid protein ids found for Mann-Whitney U test analysis"
        in message["msg"]
        for message in current_out["messages"]
    )


def test_differential_expression_mann_whitney_on_ptm_empty_p_values():
    """Test that Mann-Whitney U test on PTM data handles empty p-values correctly."""
    test_ptm_df = pd.DataFrame(
        data=[
            ["Sample1", np.nan, 100],
            ["Sample2", np.nan, 100],
            ["Sample3", np.nan, 100],
            ["Sample4", np.nan, 100],
        ],
        columns=["Sample", "Phospho", "Total Amount of Peptides"],
    )

    test_metadata_df = pd.DataFrame(
        data=[
            ["Sample1", "Group1"],
            ["Sample2", "Group1"],
            ["Sample3", "Group2"],
            ["Sample4", "Group2"],
        ],
        columns=["Sample", "Group"],
    )

    current_out = mann_whitney_test_on_ptm_data(
        ptm_df=test_ptm_df,
        metadata_df=test_metadata_df,
        grouping="Group",
        group1="Group1",
        group2="Group2",
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=0.05,
    )

    # Check that all dataframes are empty but with correct columns
    assert current_out[DataKey.DIFFERENTIALLY_EXPRESSED_PTM_DF].empty
    assert current_out["significant_ptm_df"].empty
    assert current_out[DataKey.CORRECTED_P_VALUES_DF].empty
    assert current_out["u_statistic_df"].empty
    assert current_out[DataKey.LOG2_FOLD_CHANGE_DF].empty
    assert current_out["corrected_alpha"] == 0.05

    # Check that an error message was generated
    assert any(
        message["level"] == logging.ERROR
        and "No valid ptms found for Mann-Whitney U test analysis" in message["msg"]
        for message in current_out["messages"]
    )


def test_differential_expression_kruskal_wallis_empty_p_values():
    """Test that Kruskal-Wallis test handles empty p-values correctly when all proteins are invalid."""
    test_intensity_df = pd.DataFrame(
        data=[
            ["Sample1", "Protein1", "Gene1", 10],
            ["Sample2", "Protein1", "Gene1", 10],
            ["Sample3", "Protein1", "Gene1", 10],
            ["Sample4", "Protein1", "Gene1", 10],
        ],
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    test_metadata_df = pd.DataFrame(
        data=[
            ["Sample1", "Group1"],
            ["Sample2", "Group1"],
            ["Sample3", "Group2"],
            ["Sample4", "Group2"],
        ],
        columns=["Sample", "Group"],
    )

    current_out = kruskal_wallis_test_on_intensity_data(
        protein_df=test_intensity_df,
        metadata_df=test_metadata_df,
        grouping="Group",
        selected_groups=["Group1", "Group2"],
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=0.05,
    )

    # Check that all dataframes are empty but with correct columns
    assert current_out[DataKey.DIFFERENTIALLY_EXPRESSED_PROTEINS_DF].empty
    assert current_out[DataKey.SIGNIFICANT_PROTEINS_DF].empty
    assert current_out[DataKey.CORRECTED_P_VALUES_DF].empty
    assert current_out["h_statistic_df"].empty
    assert current_out["corrected_alpha"] == 0.05

    # Check that an error message was generated
    assert any(
        message["level"] == logging.ERROR
        and "No valid protein ids found for Kruskal-Wallis test analysis"
        in message["msg"]
        for message in current_out["messages"]
    )


def test_differential_expression_kruskal_wallis_on_ptm_empty_p_values():
    """Test that Kruskal-Wallis test on PTM data handles empty p-values correctly."""
    test_ptm_df = pd.DataFrame(
        data=[
            ["Sample1", 10, 100],
            ["Sample2", 10, 100],
            ["Sample3", 10, 100],
            ["Sample4", 10, 100],
        ],
        columns=["Sample", "Phospho", "Total Amount of Peptides"],
    )

    test_metadata_df = pd.DataFrame(
        data=[
            ["Sample1", "Group1"],
            ["Sample2", "Group1"],
            ["Sample3", "Group2"],
            ["Sample4", "Group2"],
        ],
        columns=["Sample", "Group"],
    )

    current_out = kruskal_wallis_test_on_ptm_data(
        ptm_df=test_ptm_df,
        metadata_df=test_metadata_df,
        grouping="Group",
        selected_groups=["Group1", "Group2"],
        multiple_testing_correction_method="Benjamini-Hochberg",
        alpha=0.05,
    )

    # Check that all dataframes are empty but with correct columns
    assert current_out[DataKey.DIFFERENTIALLY_EXPRESSED_PTM_DF].empty
    assert current_out["significant_ptm_df"].empty
    assert current_out[DataKey.CORRECTED_P_VALUES_DF].empty
    assert current_out["h_statistic_df"].empty
    assert current_out["corrected_alpha"] == 0.05

    # Check that an error message was generated
    assert any(
        message["level"] == logging.ERROR
        and "No valid ptms found for Kruskal-Wallis test analysis" in message["msg"]
        for message in current_out["messages"]
    )
