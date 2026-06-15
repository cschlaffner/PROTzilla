import logging

import numpy as np
import pandas as pd
import pytest
from scipy import stats

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
from backend.protzilla.data_analysis.differential_expression_t_test import (
    get_z_score_based_fold_change_significance,
    vectorized_t_test,
)
from backend.tests.paths import TEST_AML_DATA_PATH


@pytest.fixture
def z_score_significance_data():
    # The data within the dataset stems directly form the supplementary material of the original AML paper
    fold_changes_z_score_df = pd.read_csv(
        TEST_AML_DATA_PATH / "fold_changes_zscores.csv"
    )
    return fold_changes_z_score_df


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


def test_z_score_significance_calculation(z_score_significance_data):
    _, z_score_significance = get_z_score_based_fold_change_significance(
        z_score_significance_data["fold_change"]
    )
    expected_z_score_significance = z_score_significance_data["z_score_significance"]
    # Our calcluation doesn't match the reported numbers perfectly. However, this is probably due to internal things
    # that are out of our control (rounding errors, implementations that differ between programming languaes, etc.)
    pd.testing.assert_series_equal(
        pd.Series(z_score_significance),
        expected_z_score_significance,
        check_names=False,
        check_exact=False,
        atol=1e-4,
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
        fc_zscore_alpha=0.08,
    )

    # Fold-change Z-score filter should keep only Protein1 (The others will be dropped because fc_significance is
    # too high)
    fc_significance = current_out["fc_significance_df"]
    assert not fc_significance.empty
    assert (
        round(
            fc_significance.loc[fc_significance["Protein ID"] == "Protein1"][
                "fc_significance"
            ].iloc[0],
            2,
        )
        == 0.08
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
    )

    assert not out[DataKey.CORRECTED_P_VALUES_DF].empty
    assert out[DataKey.CORRECTED_P_VALUES_DF]["Protein ID"].tolist() == ["Protein1"]
    assert (
        round(out[DataKey.CORRECTED_P_VALUES_DF]["corrected_p_value"].iloc[0], 4)
        == 0.0513
    )
    assert (
        round(out[DataKey.LOG2_FOLD_CHANGE_DF]["log2_fold_change"].iloc[0], 2) == -0.44
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


# --- vectorized_t_test unit tests ---


def _group_stats(data):
    """Return (counts, means, vars) for a list of values as float scalars."""
    a = np.array(data, dtype=float)
    return float(len(a)), float(np.mean(a)), float(np.var(a, ddof=1))


def test_vectorized_t_test_student_matches_scipy():
    group1_data = [18.0, 20.0, 22.0]
    group2_data = [8.0, 10.0, 12.0]
    group1_counts, group1_means, group1_vars = _group_stats(group1_data)
    group2_counts, group2_means, group2_vars = _group_stats(group2_data)

    t_statistics, p_values = vectorized_t_test(
        np.array([group1_counts]),
        np.array([group2_counts]),
        np.array([group1_means]),
        np.array([group2_means]),
        np.array([group1_vars]),
        np.array([group2_vars]),
        "Student's t-Test",
    )

    expected_t, expected_p = stats.ttest_ind(group1_data, group2_data, equal_var=True)
    assert round(float(t_statistics[0]), 6) == round(expected_t, 6)
    assert round(float(p_values[0]), 6) == round(expected_p, 6)


def test_vectorized_t_test_welch_matches_scipy():
    group1_data = [18.0, 20.0, 22.0]
    group2_data = [8.0, 10.0, 12.0]
    group1_counts, group1_means, group1_vars = _group_stats(group1_data)
    group2_counts, group2_means, group2_vars = _group_stats(group2_data)

    t_statistics, p_values = vectorized_t_test(
        np.array([group1_counts]),
        np.array([group2_counts]),
        np.array([group1_means]),
        np.array([group2_means]),
        np.array([group1_vars]),
        np.array([group2_vars]),
        "Welch's t-Test",
    )

    expected_t, expected_p = stats.ttest_ind(group1_data, group2_data, equal_var=False)
    assert round(float(t_statistics[0]), 6) == round(expected_t, 6)
    assert round(float(p_values[0]), 6) == round(expected_p, 6)


def test_vectorized_t_test_multiple_proteins():
    proteins = [
        ([18.0, 20.0, 22.0], [8.0, 10.0, 12.0]),
        ([1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]),
        ([100.0, 200.0, 150.0], [99.0, 198.0, 152.0]),
    ]
    group1_counts_list, group2_counts_list = [], []
    group1_means_list, group2_means_list = [], []
    group1_vars_list, group2_vars_list = [], []
    expected_t_student, expected_p_student = [], []
    expected_t_welch, expected_p_welch = [], []

    for group1_data, group2_data in proteins:
        group1_counts, group1_means, group1_vars = _group_stats(group1_data)
        group2_counts, group2_means, group2_vars = _group_stats(group2_data)
        group1_counts_list.append(group1_counts)
        group2_counts_list.append(group2_counts)
        group1_means_list.append(group1_means)
        group2_means_list.append(group2_means)
        group1_vars_list.append(group1_vars)
        group2_vars_list.append(group2_vars)
        et, ep = stats.ttest_ind(group1_data, group2_data, equal_var=True)
        expected_t_student.append(et)
        expected_p_student.append(ep)
        et, ep = stats.ttest_ind(group1_data, group2_data, equal_var=False)
        expected_t_welch.append(et)
        expected_p_welch.append(ep)

    t_student, p_student = vectorized_t_test(
        np.array(group1_counts_list),
        np.array(group2_counts_list),
        np.array(group1_means_list),
        np.array(group2_means_list),
        np.array(group1_vars_list),
        np.array(group2_vars_list),
        "Student's t-Test",
    )
    t_welch, p_welch = vectorized_t_test(
        np.array(group1_counts_list),
        np.array(group2_counts_list),
        np.array(group1_means_list),
        np.array(group2_means_list),
        np.array(group1_vars_list),
        np.array(group2_vars_list),
        "Welch's t-Test",
    )

    for i in range(len(proteins)):
        assert round(float(t_student[i]), 6) == round(expected_t_student[i], 6)
        assert round(float(p_student[i]), 6) == round(expected_p_student[i], 6)
        assert round(float(t_welch[i]), 6) == round(expected_t_welch[i], 6)
        assert round(float(p_welch[i]), 6) == round(expected_p_welch[i], 6)


def test_vectorized_t_test_identical_means():
    # When means are equal the t-statistic must be 0 and p-value 1.0
    group1_counts, group1_means, group1_vars = 5.0, 3.0, 2.0
    group2_counts, group2_means, group2_vars = 5.0, 3.0, 2.0

    for ttest_type in ["Student's t-Test", "Welch's t-Test"]:
        t_statistics, p_values = vectorized_t_test(
            np.array([group1_counts]),
            np.array([group2_counts]),
            np.array([group1_means]),
            np.array([group2_means]),
            np.array([group1_vars]),
            np.array([group2_vars]),
            ttest_type,
        )
        assert float(t_statistics[0]) == 0.0
        assert round(float(p_values[0]), 10) == 1.0


def test_vectorized_t_test_t_statistic_sign():
    # group1 > group2 → positive t; group1 < group2 → negative t
    group1_counts, group2_counts = 5.0, 5.0
    group1_vars, group2_vars = 1.0, 1.0

    t_pos, _ = vectorized_t_test(
        np.array([group1_counts]),
        np.array([group2_counts]),
        np.array([10.0]),
        np.array([5.0]),
        np.array([group1_vars]),
        np.array([group2_vars]),
        "Student's t-Test",
    )
    t_neg, _ = vectorized_t_test(
        np.array([group1_counts]),
        np.array([group2_counts]),
        np.array([5.0]),
        np.array([10.0]),
        np.array([group1_vars]),
        np.array([group2_vars]),
        "Student's t-Test",
    )
    assert float(t_pos[0]) > 0
    assert float(t_neg[0]) < 0
    assert round(float(t_pos[0]), 10) == round(-float(t_neg[0]), 10)


def test_vectorized_t_test_zero_variance_same_mean_produces_nan():
    # Both groups are constant and equal → se=0, t=0/0=NaN, p=NaN
    group1_counts, group1_means, group1_vars = 5.0, 3.0, 0.0
    group2_counts, group2_means, group2_vars = 5.0, 3.0, 0.0

    for ttest_type in ["Student's t-Test", "Welch's t-Test"]:
        t_statistics, p_values = vectorized_t_test(
            np.array([group1_counts]),
            np.array([group2_counts]),
            np.array([group1_means]),
            np.array([group2_means]),
            np.array([group1_vars]),
            np.array([group2_vars]),
            ttest_type,
        )
        assert np.isnan(float(t_statistics[0]))
        assert np.isnan(float(p_values[0]))


def test_vectorized_t_test_zero_variance_different_mean_produces_inf_t():
    # Both groups are constant but different means → se=0, t=±inf, p=0
    group1_counts, group1_means, group1_vars = 5.0, 3.0, 0.0
    group2_counts, group2_means, group2_vars = 5.0, 7.0, 0.0

    for ttest_type in ["Student's t-Test", "Welch's t-Test"]:
        t_statistics, p_values = vectorized_t_test(
            np.array([group1_counts]),
            np.array([group2_counts]),
            np.array([group1_means]),
            np.array([group2_means]),
            np.array([group1_vars]),
            np.array([group2_vars]),
            ttest_type,
        )
        assert np.isinf(float(t_statistics[0]))
        assert float(p_values[0]) == 0.0


def test_vectorized_t_test_unequal_sample_sizes():
    group1_data = [1.0, 2.0, 3.0, 4.0, 5.0]
    group2_data = [6.0, 7.0, 8.0]
    group1_counts, group1_means, group1_vars = _group_stats(group1_data)
    group2_counts, group2_means, group2_vars = _group_stats(group2_data)

    for ttest_type, equal_var in [
        ("Student's t-Test", True),
        ("Welch's t-Test", False),
    ]:
        t_statistics, p_values = vectorized_t_test(
            np.array([group1_counts]),
            np.array([group2_counts]),
            np.array([group1_means]),
            np.array([group2_means]),
            np.array([group1_vars]),
            np.array([group2_vars]),
            ttest_type,
        )
        expected_t, expected_p = stats.ttest_ind(
            group1_data, group2_data, equal_var=equal_var
        )
        assert round(float(t_statistics[0]), 6) == round(expected_t, 6)
        assert round(float(p_values[0]), 6) == round(expected_p, 6)


def test_vectorized_t_test_unequal_variances_gives_different_results():
    # Welch's and Student's should diverge when variances differ substantially
    group1_data = [1.0, 1.1, 0.9, 1.0, 1.05]
    group2_data = [10.0, 1.0, 50.0, 2.0, 30.0]
    group1_counts, group1_means, group1_vars = _group_stats(group1_data)
    group2_counts, group2_means, group2_vars = _group_stats(group2_data)

    _, p_student = vectorized_t_test(
        np.array([group1_counts]),
        np.array([group2_counts]),
        np.array([group1_means]),
        np.array([group2_means]),
        np.array([group1_vars]),
        np.array([group2_vars]),
        "Student's t-Test",
    )
    _, p_welch = vectorized_t_test(
        np.array([group1_counts]),
        np.array([group2_counts]),
        np.array([group1_means]),
        np.array([group2_means]),
        np.array([group1_vars]),
        np.array([group2_vars]),
        "Welch's t-Test",
    )
    assert float(p_student[0]) != float(p_welch[0])


def test_vectorized_t_test_nan_variance_propagates():
    # var=NaN (e.g. n=1, undefined sample variance) → t and p should both be NaN
    group1_counts, group1_means, group1_vars = 1.0, 5.0, float("nan")
    group2_counts, group2_means, group2_vars = 5.0, 3.0, 1.0

    for ttest_type in ["Student's t-Test", "Welch's t-Test"]:
        t_statistics, p_values = vectorized_t_test(
            np.array([group1_counts]),
            np.array([group2_counts]),
            np.array([group1_means]),
            np.array([group2_means]),
            np.array([group1_vars]),
            np.array([group2_vars]),
            ttest_type,
        )
        assert np.isnan(float(t_statistics[0]))
        assert np.isnan(float(p_values[0]))


def test_vectorized_t_test_highly_significant():
    # Very separated groups with low variance → p-value should be very small
    group1_data = [1.0, 1.1, 0.9, 1.0, 1.05, 0.95]
    group2_data = [1000.0, 1001.0, 999.5, 1000.5, 1000.2, 999.8]
    group1_counts, group1_means, group1_vars = _group_stats(group1_data)
    group2_counts, group2_means, group2_vars = _group_stats(group2_data)

    for ttest_type in ["Student's t-Test", "Welch's t-Test"]:
        _, p_values = vectorized_t_test(
            np.array([group1_counts]),
            np.array([group2_counts]),
            np.array([group1_means]),
            np.array([group2_means]),
            np.array([group1_vars]),
            np.array([group2_vars]),
            ttest_type,
        )
        assert float(p_values[0]) < 1e-10
