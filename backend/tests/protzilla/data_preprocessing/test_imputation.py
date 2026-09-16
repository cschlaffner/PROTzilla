import inspect
import logging

import pytest

from backend.protzilla.constants.data_types import DataKey
from backend.protzilla.data_preprocessing.imputation import (
    by_knn,
    by_knn_plot,
    by_min_per_dataset,
    by_min_per_dataset_plot,
    by_min_per_protein,
    by_min_per_protein_plot,
    by_min_per_sample,
    by_min_per_sample_plot,
    by_normal_distribution_sampling,
    by_normal_distribution_sampling_plot,
    by_simple_imputer,
    by_simple_imputer_plot,
    np,
    number_of_imputed_values,
    pd,
)
from backend.protzilla.methods.data_preprocessing import (
    ImputationByNormalDistributionSampling,
)
from backend.tests.protzilla.data_preprocessing import test_plots_data_preprocessing


def protein_group_intensities(dataframe, protein_group_name):
    # small helper function for tests
    return dataframe[dataframe["Protein ID"] == protein_group_name]["Intensity"]


@pytest.fixture
def input_imputation_df():
    test_intensity_list = (
        ["Sample1", "Protein1", "Gene1", np.nan],
        ["Sample1", "Protein2", "Gene2", 20],
        ["Sample1", "Protein3", "Gene3", 10],
        ["Sample2", "Protein1", "Gene1", 1],
        ["Sample2", "Protein2", "Gene2", np.nan],
        ["Sample2", "Protein3", "Gene3", 2],
        ["Sample3", "Protein1", "Gene1", 100],
        ["Sample3", "Protein2", "Gene2", np.nan],
        ["Sample3", "Protein3", "Gene3", 80],
    )

    input_imputation_df = pd.DataFrame(
        data=test_intensity_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    return input_imputation_df


@pytest.fixture
def assertion_df_knn():
    assertion_list = (
        ["Sample1", "Protein1", "Gene1", 50.5],
        ["Sample1", "Protein2", "Gene2", 20],
        ["Sample1", "Protein3", "Gene3", 10],
        ["Sample2", "Protein1", "Gene1", 1.0],
        ["Sample2", "Protein2", "Gene2", 20],
        ["Sample2", "Protein3", "Gene3", 2],
        ["Sample3", "Protein1", "Gene1", 100],
        ["Sample3", "Protein2", "Gene2", 20],
        ["Sample3", "Protein3", "Gene3", 80],
    )
    assertion_df = pd.DataFrame(
        data=assertion_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )
    return assertion_df


@pytest.fixture
def assertion_df_min_value_per_df():
    assertion_list = (
        ["Sample1", "Protein1", "Gene1", 0.1],
        ["Sample1", "Protein2", "Gene2", 20],
        ["Sample1", "Protein3", "Gene3", 10],
        ["Sample2", "Protein1", "Gene1", 1],
        ["Sample2", "Protein2", "Gene2", 0.1],
        ["Sample2", "Protein3", "Gene3", 2],
        ["Sample3", "Protein1", "Gene1", 100],
        ["Sample3", "Protein2", "Gene2", 0.1],
        ["Sample3", "Protein3", "Gene3", 80],
    )
    assertion_df = pd.DataFrame(
        data=assertion_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )
    return assertion_df


@pytest.fixture
def assertion_df_min_value_per_sample():
    assertion_list = (
        ["Sample1", "Protein1", "Gene1", 2],
        ["Sample1", "Protein2", "Gene2", 20],
        ["Sample1", "Protein3", "Gene3", 10],
        ["Sample2", "Protein1", "Gene1", 1.0],
        ["Sample2", "Protein2", "Gene2", 0.2],
        ["Sample2", "Protein3", "Gene3", 2],
        ["Sample3", "Protein1", "Gene1", 100],
        ["Sample3", "Protein2", "Gene2", 16],
        ["Sample3", "Protein3", "Gene3", 80],
    )
    return pd.DataFrame(
        data=assertion_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )


@pytest.fixture
def assertion_df_min_value_per_protein():
    assertion_list = (
        ["Sample1", "Protein1", "Gene1", 1],
        ["Sample1", "Protein2", "Gene2", 20],
        ["Sample1", "Protein3", "Gene3", 10],
        ["Sample2", "Protein1", "Gene1", 1.0],
        ["Sample2", "Protein2", "Gene2", 20],
        ["Sample2", "Protein3", "Gene3", 2],
        ["Sample3", "Protein1", "Gene1", 100],
        ["Sample3", "Protein2", "Gene2", 20],
        ["Sample3", "Protein3", "Gene3", 80],
    )
    return pd.DataFrame(
        data=assertion_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )


@pytest.fixture
def assertion_df_mean_per_protein():
    assertion_list = (
        ["Sample1", "Protein1", "Gene1", 50.5],
        ["Sample1", "Protein2", "Gene2", 20],
        ["Sample1", "Protein3", "Gene3", 10],
        ["Sample2", "Protein1", "Gene1", 1.0],
        ["Sample2", "Protein2", "Gene2", 20],
        ["Sample2", "Protein3", "Gene3", 2],
        ["Sample3", "Protein1", "Gene1", 100],
        ["Sample3", "Protein2", "Gene2", 20],
        ["Sample3", "Protein3", "Gene3", 80],
    )
    return pd.DataFrame(
        data=assertion_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )


@pytest.mark.order(2)
@pytest.mark.dependency(depends=["test_build_box_hist_plot"])
def test_imputation_min_value_per_df(
    show_figures, input_imputation_df, assertion_df_min_value_per_df
):
    assertion_df = assertion_df_min_value_per_df

    # perform imputation on test data frame
    method_inputs = {
        DataKey.PROTEIN_DF: input_imputation_df,
        "shrinking_value": 0.1,
    }
    method_outputs = by_min_per_dataset(**method_inputs)

    fig1, fig2 = by_min_per_dataset_plot(
        input_imputation_df,
        method_outputs[DataKey.PROTEIN_DF],
        "Boxplot",
        "Bar chart",
        "Sample",
        "linear",
        True,
    )
    if show_figures:
        fig1.show()
        fig2.show()

    # test whether dataframes match
    result_df = method_outputs[DataKey.PROTEIN_DF]
    assert result_df.equals(
        assertion_df
    ), f"Imputation by min value per df does not match!\
             Imputation should be \
            {assertion_df} but is {result_df}"


@pytest.mark.order(2)
@pytest.mark.dependency(depends=["test_build_box_hist_plot"])
def test_imputation_min_value_per_sample(
    show_figures, input_imputation_df, assertion_df_min_value_per_sample
):
    assertion_df = assertion_df_min_value_per_sample

    # perform imputation on test data frame
    method_inputs = {
        DataKey.PROTEIN_DF: input_imputation_df,
        "shrinking_value": 0.2,
    }
    method_outputs = by_min_per_sample(**method_inputs)

    fig1, fig2 = by_min_per_sample_plot(
        input_imputation_df,
        method_outputs[DataKey.PROTEIN_DF],
        "Boxplot",
        "Bar chart",
        "Sample",
        "linear",
        True,
    )
    if show_figures:
        fig1.show()
        fig2.show()

    # test whether dataframes match
    result_df = method_outputs[DataKey.PROTEIN_DF]
    assert result_df.equals(
        assertion_df
    ), f"Imputation by min value per sample does not match!\
             Imputation should be \
            {assertion_df} but is {result_df}"


@pytest.mark.order(2)
@pytest.mark.dependency(depends=["test_build_box_hist_plot"])
def test_imputation_min_value_per_protein(
    show_figures, input_imputation_df, assertion_df_min_value_per_protein
):
    assertion_df = assertion_df_min_value_per_protein

    # perform imputation on test data frame
    method_inputs = {
        DataKey.PROTEIN_DF: input_imputation_df,
        "shrinking_value": 1.0,
    }
    method_outputs = by_min_per_protein(**method_inputs)

    fig1, fig2 = by_min_per_protein_plot(
        input_imputation_df,
        method_outputs[DataKey.PROTEIN_DF],
        "Boxplot",
        "Bar chart",
        "Sample",
        "linear",
        True,
    )
    if show_figures:
        fig1.show()
        fig2.show()

    # test whether dataframes match
    result_df = method_outputs[DataKey.PROTEIN_DF]
    assert result_df.equals(
        assertion_df
    ), f"Imputation by min value per protein does not match!\
             Imputation should be \
            {assertion_df} but is {result_df}"


@pytest.mark.order(2)
@pytest.mark.dependency(depends=["test_build_box_hist_plot"])
def test_imputation_mean_per_protein(
    show_figures, input_imputation_df, assertion_df_mean_per_protein
):
    assertion_df = assertion_df_mean_per_protein

    # perform imputation on test data frame
    method_inputs = {
        DataKey.PROTEIN_DF: input_imputation_df,
        "strategy": "mean",
    }
    method_outputs = by_simple_imputer(**method_inputs)

    fig1, fig2 = by_simple_imputer_plot(
        input_imputation_df,
        method_outputs[DataKey.PROTEIN_DF],
        "Boxplot",
        "Bar chart",
        "Sample",
        "linear",
        True,
    )
    if show_figures:
        fig1.show()
        fig2.show()

    # test whether dataframes match
    result_df = method_outputs[DataKey.PROTEIN_DF]
    assert result_df.equals(
        assertion_df
    ), f"Imputation by simple median imputation per protein does not match!\
             Imputation should be \
            {assertion_df} but is {result_df}"


@pytest.mark.order(2)
@pytest.mark.dependency(depends=["test_build_box_hist_plot"])
def test_imputation_knn(show_figures, input_imputation_df, assertion_df_knn):
    assertion_df = assertion_df_knn

    # perform imputation on test data frame
    method_inputs = {
        DataKey.PROTEIN_DF: input_imputation_df,
        "number_of_neighbours": 2,
    }
    method_outputs = by_knn(**method_inputs)

    fig1, fig2 = by_knn_plot(
        input_imputation_df,
        method_outputs[DataKey.PROTEIN_DF],
        "Boxplot",
        "Bar chart",
        "Sample",
        "linear",
        True,
    )
    if show_figures:
        fig1.show()
        fig2.show()

    # test whether dataframes match
    result_df = method_outputs[DataKey.PROTEIN_DF]
    assert result_df.equals(
        assertion_df
    ), f"Imputation by simple median imputation per protein does not match!\n\
             Imputation should be \n\
            {assertion_df} but is\n {result_df}"


@pytest.mark.order(2)
@pytest.mark.dependency(depends=["test_build_box_hist_plot"])
def test_imputation_normal_distribution_sampling(show_figures, input_imputation_df):
    # perform imputation on test data frame
    method_inputs_perProtein = {
        DataKey.PROTEIN_DF: input_imputation_df,
        "strategy": "perProtein",
        "down_shift": -10,
    }
    method_outputs_perProtein = by_normal_distribution_sampling(
        **method_inputs_perProtein
    )
    method_inputs_perDataset = {
        DataKey.PROTEIN_DF: input_imputation_df,
        "strategy": "perDataset",
        "down_shift": -10,
    }
    method_outputs_perDataset = by_normal_distribution_sampling(
        **method_inputs_perDataset
    )

    fig1, fig2 = by_normal_distribution_sampling_plot(
        input_imputation_df,
        method_outputs_perProtein[DataKey.PROTEIN_DF],
        "Boxplot",
        "Bar chart",
        "Sample",
        "linear",
        True,
    )
    if show_figures:
        fig1.show()
        fig2.show()

    result_df_perProtein = method_outputs_perProtein[DataKey.PROTEIN_DF]
    result_df_perDataset = method_outputs_perDataset[DataKey.PROTEIN_DF]
    assert (
        result_df_perProtein["Intensity"].min() >= 0
    ), f"Imputation by normal distribution sampling should not have negative values!"
    assert (
        result_df_perDataset["Intensity"].min() >= 0
    ), f"Imputation by normal distribution sampling should not have negative values!"

    assert (
        False == protein_group_intensities(result_df_perProtein, "Protein1").hasnans
    ) and (
        False == protein_group_intensities(result_df_perProtein, "Protein3").hasnans
    ), f"Imputation by normal distribution sampling should not have NaN values!"
    assert protein_group_intensities(
        result_df_perProtein, "Protein2"
    ).hasnans, f"This protein group should have NaN values! Not enough data points to sample from!"
    assert (
        False == result_df_perDataset["Intensity"].hasnans
    ), f"Imputation by normal distribution sampling per Dataset should not have NaN values!"


def test_number_of_imputed_values(input_imputation_df, assertion_df_knn):
    count = number_of_imputed_values(input_imputation_df, assertion_df_knn)
    assert (
        count == 3
    ), f"Wrong number of imputed samples\
               3 but is {count}"


@pytest.mark.order(1)
@pytest.mark.dependency()
def test_build_box_hist_plot(
    show_figures, input_imputation_df, assertion_df_knn, assertion_df_min_value_per_df
):
    test_plots_data_preprocessing.test_build_box_hist_plot(
        show_figures,
        input_imputation_df,
        assertion_df_knn,
        assertion_df_min_value_per_df,
    )


@pytest.fixture
def log_scale_imputation_df():
    # log2-scale, median-normalised data: contains negative values, so it cannot
    # be log-transformed again before sampling
    test_intensity_list = (
        ["Sample1", "Protein1", "Gene1", np.nan],
        ["Sample1", "Protein2", "Gene2", -1.0],
        ["Sample1", "Protein3", "Gene3", 0.5],
        ["Sample1", "Protein4", "Gene4", 2.0],
        ["Sample1", "Protein5", "Gene5", np.nan],
        ["Sample1", "Protein6", "Gene6", 3.5],
        ["Sample2", "Protein1", "Gene1", 1.0],
        ["Sample2", "Protein2", "Gene2", np.nan],
        ["Sample2", "Protein3", "Gene3", 2.5],
        ["Sample2", "Protein4", "Gene4", np.nan],
        ["Sample2", "Protein5", "Gene5", 4.0],
        ["Sample2", "Protein6", "Gene6", 5.0],
        ["Sample3", "Protein1", "Gene1", 0.0],
        ["Sample3", "Protein2", "Gene2", 1.5],
        ["Sample3", "Protein3", "Gene3", np.nan],
        ["Sample3", "Protein4", "Gene4", 2.5],
        ["Sample3", "Protein5", "Gene5", 3.0],
        ["Sample3", "Protein6", "Gene6", np.nan],
    )

    return pd.DataFrame(
        data=test_intensity_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )


def test_normal_distribution_sampling_per_sample_imputes_all_missing_values(
    input_imputation_df,
):
    method_outputs = by_normal_distribution_sampling(
        input_imputation_df,
        strategy="perSample",
        down_shift=-1.8,
        scaling_factor=0.3,
    )

    result_df = method_outputs[DataKey.PROTEIN_DF]
    assert (
        False == result_df["Intensity"].hasnans
    ), "Imputation per sample should fill every missing value"


def test_normal_distribution_sampling_per_sample_uses_statistics_of_that_sample(
    input_imputation_df,
):
    # a scaling factor of 0 removes the randomness, so the imputed value is
    # exactly the mean of the sampled distribution
    method_outputs = by_normal_distribution_sampling(
        input_imputation_df,
        strategy="perSample",
        down_shift=-1.8,
        scaling_factor=0,
    )

    result_df = method_outputs[DataKey.PROTEIN_DF]
    for sample in input_imputation_df["Sample"].unique():
        is_sample = input_imputation_df["Sample"] == sample
        observed = np.log10(input_imputation_df.loc[is_sample, "Intensity"].dropna())
        expected = 10 ** (observed.mean() - 1.8 * observed.std())

        was_missing = is_sample & input_imputation_df["Intensity"].isna()
        assert result_df.loc[was_missing, "Intensity"].tolist() == pytest.approx(
            [expected] * int(was_missing.sum())
        ), f"Imputed values of {sample} should be based on that sample's statistics"


def test_normal_distribution_sampling_per_sample_without_log_transform(
    log_scale_imputation_df,
):
    method_outputs = by_normal_distribution_sampling(
        log_scale_imputation_df,
        strategy="perSample",
        down_shift=-1.8,
        scaling_factor=0,
        log_transform=False,
    )

    result_df = method_outputs[DataKey.PROTEIN_DF]
    for sample in log_scale_imputation_df["Sample"].unique():
        is_sample = log_scale_imputation_df["Sample"] == sample
        observed = log_scale_imputation_df.loc[is_sample, "Intensity"].dropna()
        expected = observed.mean() - 1.8 * observed.std()

        was_missing = is_sample & log_scale_imputation_df["Intensity"].isna()
        assert result_df.loc[was_missing, "Intensity"].tolist() == pytest.approx(
            [expected] * int(was_missing.sum())
        ), f"Values of {sample} should be sampled on the scale of the input data"
        assert (
            expected < 0
        ), "This fixture is only meaningful if the downshifted mean is negative"


def test_normal_distribution_sampling_per_dataset_without_log_transform(
    log_scale_imputation_df,
):
    method_outputs = by_normal_distribution_sampling(
        log_scale_imputation_df,
        strategy="perDataset",
        down_shift=-1.8,
        scaling_factor=0,
        log_transform=False,
    )

    observed = log_scale_imputation_df["Intensity"].dropna()
    expected = observed.mean() - 1.8 * observed.std()
    assert expected < 0, "This fixture should produce a negative sampling mean"

    result_df = method_outputs[DataKey.PROTEIN_DF]
    was_missing = log_scale_imputation_df["Intensity"].isna()
    assert result_df.loc[was_missing, "Intensity"].tolist() == pytest.approx(
        [expected] * int(was_missing.sum())
    ), "Without a log transformation, imputed values should not be forced to be positive"


def test_normal_distribution_sampling_per_protein_without_log_transform(
    log_scale_imputation_df,
):
    method_outputs = by_normal_distribution_sampling(
        log_scale_imputation_df,
        strategy="perProtein",
        down_shift=-1.8,
        scaling_factor=0,
        log_transform=False,
    )

    result_df = method_outputs[DataKey.PROTEIN_DF]
    for protein in log_scale_imputation_df["Protein ID"].unique():
        is_protein = log_scale_imputation_df["Protein ID"] == protein
        observed = log_scale_imputation_df.loc[is_protein, "Intensity"].dropna()
        expected = observed.mean() - 1.8 * observed.std()

        was_missing = is_protein & log_scale_imputation_df["Intensity"].isna()
        actual = result_df.loc[result_df["Protein ID"] == protein, "Intensity"].tolist()
        imputed = [
            value for value, missing in zip(actual, was_missing[is_protein]) if missing
        ]
        assert imputed == pytest.approx(
            [expected] * len(imputed)
        ), f"Values of {protein} should be sampled on the scale of the input data"


def test_normal_distribution_sampling_with_the_same_seed_is_reproducible(
    input_imputation_df,
):
    method_inputs = {
        DataKey.PROTEIN_DF: input_imputation_df,
        "strategy": "perSample",
        "down_shift": -1.8,
        "scaling_factor": 0.3,
        "seed": 570,
    }
    first_run = by_normal_distribution_sampling(**method_inputs)
    second_run = by_normal_distribution_sampling(**method_inputs)

    assert first_run[DataKey.PROTEIN_DF].equals(
        second_run[DataKey.PROTEIN_DF]
    ), "Imputation with the same seed should produce the same values"


def test_normal_distribution_sampling_with_a_different_seed_differs(
    input_imputation_df,
):
    method_inputs = {
        DataKey.PROTEIN_DF: input_imputation_df,
        "strategy": "perSample",
        "down_shift": -1.8,
        "scaling_factor": 0.3,
    }
    first_run = by_normal_distribution_sampling(**method_inputs, seed=570)
    second_run = by_normal_distribution_sampling(**method_inputs, seed=571)

    assert not first_run[DataKey.PROTEIN_DF].equals(
        second_run[DataKey.PROTEIN_DF]
    ), "Imputation with a different seed should produce different values"


def test_normal_distribution_sampling_seed_does_not_affect_global_randomness(
    input_imputation_df,
):
    np.random.seed(42)
    expected_next_value = np.random.random()

    np.random.seed(42)
    by_normal_distribution_sampling(
        input_imputation_df,
        strategy="perSample",
        down_shift=-1.8,
        scaling_factor=0.3,
        seed=570,
    )

    assert (
        np.random.random() == expected_next_value
    ), "A seeded imputation should not consume or reset the global random state"


@pytest.fixture
def sparse_sample_imputation_df():
    test_intensity_list = (
        ["Sample1", "Protein1", "Gene1", 10],
        ["Sample1", "Protein2", "Gene2", 20],
        ["Sample1", "Protein3", "Gene3", np.nan],
        ["Sample2", "Protein1", "Gene1", 5],
        ["Sample2", "Protein2", "Gene2", np.nan],
        ["Sample2", "Protein3", "Gene3", np.nan],
    )

    return pd.DataFrame(
        data=test_intensity_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )


def test_normal_distribution_sampling_per_sample_skips_samples_with_too_few_values(
    sparse_sample_imputation_df,
):
    method_outputs = by_normal_distribution_sampling(
        sparse_sample_imputation_df,
        strategy="perSample",
        down_shift=-1.8,
        scaling_factor=0.3,
    )

    result_df = method_outputs[DataKey.PROTEIN_DF]
    sample1 = result_df[result_df["Sample"] == "Sample1"]["Intensity"]
    sample2 = result_df[result_df["Sample"] == "Sample2"]["Intensity"]

    assert False == sample1.hasnans, "Sample1 has enough measured values to be imputed"
    assert (
        sample2.isna().sum() == 2
    ), "Sample2 has only one measured value, so nothing should be sampled for it"
    assert any(
        message["level"] == logging.WARNING for message in method_outputs["messages"]
    ), "Remaining missing values should be reported as a warning"


def test_normal_distribution_sampling_skipped_sample_does_not_shift_other_samples(
    sparse_sample_imputation_df,
):
    # Sample2 cannot be imputed, so it should not consume any random values and
    # therefore not change what is drawn for the samples after it
    extra_sample = pd.DataFrame(
        data=(
            ["Sample3", "Protein1", "Gene1", 30],
            ["Sample3", "Protein2", "Gene2", 40],
            ["Sample3", "Protein3", "Gene3", np.nan],
        ),
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )
    with_sparse_sample = pd.concat(
        [sparse_sample_imputation_df, extra_sample], ignore_index=True
    )
    without_sparse_sample = with_sparse_sample[
        with_sparse_sample["Sample"] != "Sample2"
    ].reset_index(drop=True)

    method_inputs = {
        "strategy": "perSample",
        "down_shift": -1.8,
        "scaling_factor": 0.3,
        "seed": 570,
    }
    with_outputs = by_normal_distribution_sampling(with_sparse_sample, **method_inputs)[
        DataKey.PROTEIN_DF
    ]
    without_outputs = by_normal_distribution_sampling(
        without_sparse_sample, **method_inputs
    )[DataKey.PROTEIN_DF]

    assert with_outputs[with_outputs["Sample"] == "Sample3"][
        "Intensity"
    ].tolist() == pytest.approx(
        without_outputs[without_outputs["Sample"] == "Sample3"]["Intensity"].tolist()
    ), "A sample that cannot be imputed should not change the values of other samples"


EXPECTED_SUMMARY_COLUMNS = [
    "strategy",
    "group_type",
    "group",
    "n_observed",
    "n_missing",
    "n_imputed",
    "observed_mean",
    "observed_sd",
    "impute_mean",
    "impute_sd",
    "down_shift",
    "scaling_factor",
    "log_transform",
    "seed",
]


def test_normal_distribution_sampling_per_sample_summarises_every_sample(
    input_imputation_df,
):
    method_outputs = by_normal_distribution_sampling(
        input_imputation_df,
        strategy="perSample",
        down_shift=-1.8,
        scaling_factor=0.3,
        seed=570,
    )

    summary_df = method_outputs[DataKey.IMPUTATION_SUMMARY_DF]
    assert list(summary_df.columns) == EXPECTED_SUMMARY_COLUMNS
    assert summary_df["group"].tolist() == ["Sample1", "Sample2", "Sample3"]
    assert summary_df["group_type"].tolist() == ["Sample"] * 3
    assert summary_df["n_observed"].tolist() == [2, 2, 2]
    assert summary_df["n_imputed"].tolist() == [1, 1, 1]

    for _, row in summary_df.iterrows():
        is_sample = input_imputation_df["Sample"] == row["group"]
        observed = np.log10(input_imputation_df.loc[is_sample, "Intensity"].dropna())
        assert row["observed_mean"] == pytest.approx(observed.mean())
        assert row["observed_sd"] == pytest.approx(observed.std())
        assert row["impute_mean"] == pytest.approx(
            observed.mean() - 1.8 * observed.std()
        )
        assert row["impute_sd"] == pytest.approx(0.3 * observed.std())


def test_normal_distribution_sampling_summarises_a_skipped_sample(
    sparse_sample_imputation_df,
):
    method_outputs = by_normal_distribution_sampling(
        sparse_sample_imputation_df,
        strategy="perSample",
        down_shift=-1.8,
        scaling_factor=0.3,
    )

    summary_df = method_outputs[DataKey.IMPUTATION_SUMMARY_DF]
    skipped = summary_df[summary_df["group"] == "Sample2"].iloc[0]
    assert skipped["n_observed"] == 1
    assert skipped["n_missing"] == 2
    assert skipped["n_imputed"] == 0, "Nothing should be imputed for this sample"
    assert np.isnan(
        skipped["impute_mean"]
    ), "A skipped sample has no sampling distribution"


@pytest.mark.parametrize(
    "strategy,expected_group_type,expected_groups",
    [
        ("perProtein", "Protein ID", ["Protein1", "Protein2", "Protein3"]),
        ("perSample", "Sample", ["Sample1", "Sample2", "Sample3"]),
        ("perDataset", "Dataset", ["all"]),
    ],
)
def test_normal_distribution_sampling_summary_is_uniform_across_strategies(
    input_imputation_df, strategy, expected_group_type, expected_groups
):
    method_outputs = by_normal_distribution_sampling(
        input_imputation_df,
        strategy=strategy,
        down_shift=-1.8,
        scaling_factor=0.3,
        seed=570,
    )

    summary_df = method_outputs[DataKey.IMPUTATION_SUMMARY_DF]
    assert list(summary_df.columns) == EXPECTED_SUMMARY_COLUMNS
    assert summary_df["strategy"].tolist() == [strategy] * len(expected_groups)
    assert summary_df["group_type"].tolist() == [expected_group_type] * len(
        expected_groups
    )
    assert summary_df["group"].tolist() == expected_groups
    assert summary_df["down_shift"].tolist() == [-1.8] * len(expected_groups)
    assert summary_df["scaling_factor"].tolist() == [0.3] * len(expected_groups)
    assert summary_df["log_transform"].tolist() == [True] * len(expected_groups)
    assert summary_df["seed"].tolist() == [570] * len(expected_groups)


def test_imputation_by_normal_distribution_sampling_step_offers_the_new_parameters():
    step = ImputationByNormalDistributionSampling("teststep01_normal_distribution")

    field_names = {
        field.name for field in step.form.input_fields if hasattr(field, "name")
    }
    calculation_parameters = set(
        inspect.signature(by_normal_distribution_sampling).parameters
    )

    assert {"log_transform", "seed"} <= field_names
    assert {
        "strategy",
        "down_shift",
        "scaling_factor",
        "log_transform",
        "seed",
    } <= calculation_parameters
    assert field_names & calculation_parameters >= {
        "strategy",
        "down_shift",
        "scaling_factor",
        "log_transform",
        "seed",
    }, "Every parameter of the form has to be named like the calculation parameter"
    assert DataKey.IMPUTATION_SUMMARY_DF in step.output_keys


def test_imputation_by_normal_distribution_sampling_step_offers_the_per_sample_strategy():
    step = ImputationByNormalDistributionSampling("teststep01_normal_distribution")

    strategy_options = [option.value for option in step.form["strategy"].options]
    assert "perSample" in strategy_options
