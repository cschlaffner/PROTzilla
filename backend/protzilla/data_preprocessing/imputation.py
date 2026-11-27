import logging

import numpy as np
import pandas as pd
from plotly.graph_objs import Figure
from sklearn.impute import KNNImputer, SimpleImputer

from backend.protzilla.constants.option_types import (
    ImputationByNormalDistributionSamplingStrategyType,
    SimpleImputerStrategyType,
)
from backend.protzilla.data_preprocessing.plots import (
    create_bar_plot,
    create_box_plots,
    create_histograms,
    create_pie_plot,
)
from backend.protzilla.utilities.transform_dfs import long_to_wide, wide_to_long
from backend.protzilla.utilities.utilities import default_intensity_column


def flag_invalid_values(df: pd.DataFrame, messages: list) -> dict:
    """
    A function to check if there are any NaN values in the dataframe.
    Also checks if some Protein groups have completely identical values for each sample.
    If so, add a warning to the messages list.
    :param df: the dataframe that should be checked
    :param messages: a list to which warning messages will be appended
    :return: a dictionary containing the dataframe and the updated messages list
    """
    if df.isnull().values.any():
        columns_with_nan = df.columns[df.isna().any()].tolist()
        try:
            columns_with_nan.remove("Gene")
        except ValueError:
            pass

        if len(columns_with_nan) > 0:
            messages.append(
                {
                    "level": logging.WARNING,
                    "msg": f"Some NaN values remain in {columns_with_nan} of the imputed dataframe, indicating an unfiltered dataset and / or insufficient data. "
                    "Possible solutions to this include adding a filtering step before this imputation step in the preprocessing section to your workflow, "
                    "or using a different imputation method.",
                }
            )

    # Group by 'Protein ID' and check if all values in each group are identical
    identical_values_warning_given = False
    for protein_id, group in df.groupby("Protein ID"):
        if group.nunique().nunique() == 1 and not identical_values_warning_given:
            messages.append(
                {
                    "level": logging.WARNING,
                    "msg": f"Some Protein groups have completely identical values for each sample.",
                }
            )
            identical_values_warning_given = True

    return dict(protein_df=df, messages=messages)


# --8<-- [start:by_knn]
def by_knn(protein_df: pd.DataFrame, number_of_neighbours: int = 5) -> dict:
    """
    A function to perform value imputation based on KNN
    (k-nearest neighbors). Imputes missing values for each
    sample based on intensity-wise similar samples.
    Two samples are close if the features that neither is
    missing are close.
    CAVE: Proteins that have NaN in all samples will be
    filtered out if not previously filtered out!

    Implements an instance of the sklearn.impute KNNImputer
    class.
    https://scikit-learn.org/stable/modules/generated/sklearn.impute.KNNImputer.html

    :param protein_df: the dataframe that should be filtered in
        long format
    :type protein_df: pandas DataFrame
    :param number_of_neighbours: number of neighbouring samples used for
        imputation. Default: 5
    :type number_of_neighbours: int
    :return: returns an imputed dataframe in typical protzilla long format
        and a list of messages
    :rtype: pd.DataFrame
    """

    transformed_df = long_to_wide(protein_df)
    transformed_df.dropna(axis=1, how="all", inplace=True)
    index = transformed_df.index
    columns = transformed_df.columns

    imputer = KNNImputer(n_neighbors=number_of_neighbours)
    transformed_df = imputer.fit_transform(transformed_df)
    transformed_df = pd.DataFrame(transformed_df, columns=columns, index=index)

    # Turn the wide format into the long format
    imputed_df = wide_to_long(transformed_df, protein_df)

    return flag_invalid_values(imputed_df, [])


# --8<-- [end:by_knn]


# --8<-- [start:by_simple_imputer]
def by_simple_imputer(
    protein_df: pd.DataFrame,
    strategy: str = "mean",
) -> dict:
    """
    A function to perform protein-wise imputations
    on your dataframe. Imputes missing values for each protein
    taking into account data from each protein.

    Imputation methods include imputation by mean, median and
    mode. Implements the sklearn.SimpleImputer class.
    https://scikit-learn.org/stable/modules/generated/sklearn.impute.SimpleImputer.html
    CAVE: If there are no intensities for a protein,
    no data will be imputed. This function automatically filters
    out such proteins from the DataFrame beforehand.

    :param protein_df: the dataframe that should be filtered in
        long format
    :param strategy: Defines the imputation strategy. Can be "mean",
        "median" or "most_frequent" (for mode).

    :return: returns an imputed dataframe in typical protzilla long format
        a list of messages
    """
    assert strategy in {item.value for item in SimpleImputerStrategyType}
    transformed_df = long_to_wide(protein_df)
    transformed_df.dropna(axis=1, how="all", inplace=True)

    index = transformed_df.index
    columns = transformed_df.columns

    imputer = SimpleImputer(missing_values=np.nan, strategy=strategy)
    transformed_df = imputer.fit_transform(transformed_df)
    transformed_df = pd.DataFrame(transformed_df, columns=columns, index=index)

    # Turn the wide format into the long format
    imputed_df = wide_to_long(transformed_df, protein_df)
    return flag_invalid_values(imputed_df, [])


# --8<-- [end:by_simple_imputer]


# --8<-- [start:by_min_per_sample]
def by_min_per_sample(
    protein_df: pd.DataFrame,
    shrinking_value: float = 1,
) -> dict:
    """
    A function to perform  minimal value imputation on the level
    of samples of your dataframe. Imputes missing values for each
    protein taking into account data from each sample.

    Sets missing intensity values to the smallest measured value
    for each sample. The user can also assign a shrinking factor to
    take a fraction of that minimum value for imputation.
    CAVE: Data for samples without any intensity values will not
    be filtered out and NaN values could remain in the dataframe.
    If not wanted, make sure to filter 0 intensity samples in the
    filtering step.

    :param protein_df: the dataframe that should be filtered in
        long format
    :param shrinking_value: a factor to alter the minimum value
        used for imputation. With a shrinking factor of 0.1 for
        example, a tenth of the minimum value found will be used for
        imputation. Default: 1 (no shrinking)

    :return: returns an imputed dataframe in typical protzilla long format
        a list of messages
    """
    protein_df_copy = protein_df.copy(deep=True)
    intensity_name = default_intensity_column(protein_df_copy)
    samples = protein_df_copy["Sample"].unique().tolist()
    for sample in samples:
        location = protein_df_copy[intensity_name].loc[
            protein_df_copy["Sample"] == sample,
        ]
        if location.isnull().all():
            continue
        else:
            location.fillna(location.min() * shrinking_value, inplace=True)
            protein_df_copy[intensity_name].update(location)
    return flag_invalid_values(protein_df_copy, [])


# --8<-- [end:by_min_per_sample]


# --8<-- [start:by_min_per_protein]
def by_min_per_protein(
    protein_df: pd.DataFrame,
    shrinking_value: float = 1,
) -> dict:
    """
    A function to impute missing values for each protein
    by taking into account data from each protein.
    Sets missing value to the smallest measured value for each
    protein column. The user can also assign a shrinking factor to
    take a fraction of that minimum value for imputation.
    CAVE: All proteins without any values will be filtered out.

    :param protein_df: the dataframe that should be filtered in
        long format
    :param shrinking_value: a factor to alter the minimum value
        used for imputation. With a shrinking factor of 0.1 for
        example, a tenth of the minimum value found will be used for
        imputation. Default: 1 (no shrinking)

    :return: returns an imputed dataframe in typical protzilla long format
        a list of messages
    """
    transformed_df = long_to_wide(protein_df)
    transformed_df.dropna(axis=1, how="all", inplace=True)
    columns = transformed_df.columns

    # Iterate over proteins to impute minimal value
    for column in columns:
        transformed_df[column].fillna(
            transformed_df[column].min() * shrinking_value, inplace=True
        )
    # this implementation seems to work with all protein columns that
    # contain data if used with 0 intensity protein filtering
    # it would work perfectly
    # CAVE: By use of the shrinking value all NaN's are turned to 0
    # - we thus decided to filter them out beforehand.

    # Turn the wide format into the long format
    imputed_df = wide_to_long(transformed_df, protein_df)

    return flag_invalid_values(imputed_df, [])


# --8<-- [end:by_min_per_protein]


# --8<-- [start:by_min_per_dataset]
def by_min_per_dataset(
    protein_df: pd.DataFrame,
    shrinking_value: float = 1,
) -> dict:
    """
    A function to impute missing values for each protein
    by taking into account data from the entire dataframe.
    Sets missing value to the smallest measured value in
    the dataframe. The user can also assign a shrinking factor to
    take a fraction of that minimum value for imputation.

    :param protein_df: the dataframe that should be filtered in
        long format
    :param shrinking_value: a factor to alter the minimum value
        used for imputation. With a shrinking factor of 0.1 for
        example, a tenth of the minimum value found will be used for
        imputation. Default: 1 (no shrinking)

    :return: returns an imputed dataframe in typical protzilla long format
        a list of messages
    """
    protein_df_copy = protein_df.copy(deep=True)
    intensity_name = default_intensity_column(protein_df_copy)
    protein_df_copy[intensity_name].fillna(
        protein_df_copy[intensity_name].min() * shrinking_value,
        inplace=True,
    )
    return flag_invalid_values(protein_df_copy, [])


# --8<-- [end:by_min_per_dataset]


# --8<-- [start:by_normal_distribution_sampling]
SUMMARY_COLUMNS = [
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


def _observed_values(values: pd.Series, log_transform: bool) -> pd.Series:
    """
    Returns the measured values of a group on the scale that is sampled on.

    :param values: the values of a group, missing values included
    :param log_transform: whether the values are log10-transformed before sampling
    :return: the measured values, log10-transformed if requested
    """
    observed = values.dropna()
    return np.log10(observed) if log_transform else observed


def _sampling_parameters(
    observed: pd.Series,
    down_shift: float,
    scaling_factor: float,
    force_positive: bool = False,
) -> tuple[float, float]:
    """
    Calculates mean and standard deviation of the normal distribution that is sampled
    for a group, by shifting and scaling the statistics of its measured values.

    :param observed: the measured values of the group, on the scale that is sampled on
    :param down_shift: how many standard deviations the mean of the distribution is
        shifted by
    :param scaling_factor: the factor the standard deviation of the distribution is
        scaled by
    :param force_positive: whether the mean is kept on the positive side of the log10
        scale, only meaningful in combination with log_transform
    :return: the mean and the standard deviation of the distribution to sample
    """
    sampling_mean = observed.mean() + down_shift * observed.std()
    sampling_std = observed.std() * scaling_factor
    if force_positive:
        sampling_mean = max(0, sampling_mean)

    return sampling_mean, sampling_std


def _sampled_imputation_values(
    sampling_mean: float,
    sampling_std: float,
    number_of_values: int,
    log_transform: bool,
    rng: np.random.Generator,
    force_positive: bool = False,
) -> np.ndarray:
    """
    Draws values from the normal distribution that was defined for a group.

    :param sampling_mean: the mean of the distribution to sample
    :param sampling_std: the standard deviation of the distribution to sample
    :param number_of_values: the number of values to draw
    :param log_transform: whether the drawn values are transformed back from log10 scale
    :param rng: the random number generator the values are drawn from
    :param force_positive: whether the drawn values are kept on the positive side of the
        log10 scale, only meaningful in combination with log_transform
    :return: the values to impute
    """
    values = rng.normal(
        loc=sampling_mean,
        scale=sampling_std,
        size=number_of_values,
    )
    if force_positive:
        values = abs(values)

    return 10**values if log_transform else values


def _summary_row(
    group_type: str,
    group: str,
    observed: pd.Series,
    number_of_nans: int,
    number_of_imputed: int,
    sampling_mean: float,
    sampling_std: float,
    parameters: dict,
) -> dict:
    """
    Describes how one group was imputed, so that the sampled distributions can be
    inspected after the calculation.

    :param group_type: what the groups of the chosen strategy are, e.g. "Sample"
    :param group: the name of the group, e.g. the name of a sample
    :param observed: the measured values of the group, on the scale that is sampled on
    :param number_of_nans: how many values of the group were missing
    :param number_of_imputed: how many values of the group were imputed, which is 0 if
        the group did not offer enough data to sample from
    :param sampling_mean: the mean of the sampled distribution, NaN if nothing was
        imputed
    :param sampling_std: the standard deviation of the sampled distribution, NaN if
        nothing was imputed
    :param parameters: the user-defined parameters shared by all groups
    :return: one row of the imputation summary
    """
    return {
        "strategy": parameters["strategy"],
        "group_type": group_type,
        "group": group,
        "n_observed": len(observed),
        "n_missing": int(number_of_nans),
        "n_imputed": int(number_of_imputed),
        "observed_mean": observed.mean() if len(observed) > 0 else np.nan,
        "observed_sd": observed.std() if len(observed) > 1 else np.nan,
        "impute_mean": sampling_mean,
        "impute_sd": sampling_std,
        "down_shift": parameters["down_shift"],
        "scaling_factor": parameters["scaling_factor"],
        "log_transform": parameters["log_transform"],
        "seed": parameters["seed"],
    }


def by_normal_distribution_sampling(
    protein_df: pd.DataFrame,
    strategy: str = "perProtein",
    down_shift: float = 0,
    scaling_factor: float = 1,
    log_transform: bool = True,
    seed: int = -1,
) -> dict:
    """
    A function to perform imputation via sampling of a normal distribution
    defined by the existing datapoints and user-defined parameters for down-
    shifting and scaling. Imputes missing values for each protein, for each sample
    or for the whole dataset. By default the data is log-transformed before sampling
    from the normal distribution and transformed back afterwards, meaning only
    values > 0 are imputed. Data that is already on a log scale, and therefore may
    contain negative values, should be imputed with log_transform disabled.
    Will not impute if insufficient data is available for sampling.

    :param protein_df: the dataframe that should be filtered in
    long format
    :param strategy: which strategy to use for definition of the normal
    distribution to be sampled. Can be "perProtein", "perSample" or "perDataset"
    :param down_shift: a factor defining how many dataset standard deviations
    to shift the mean of the normal distribution used for imputation.
    Default: 0 (no shift)
    :param scaling_factor: a factor determining how the variance of the normal
    distribution used for imputation is scaled compared to dataset.
    Default: 1 (no scaling)
    :param log_transform: whether the intensities are log10-transformed before sampling
    and transformed back afterwards. Disable this for data that is already on a log
    scale. Default: True
    :param seed: the seed of the random number generator, which makes the imputation
    reproducible. A negative seed draws different values on every calculation.
    Default: -1 (not seeded)
    :return: returns an imputed dataframe in typical protzilla long format, a summary
    of the sampled distributions and a list of messages
    """
    assert strategy in {
        item.value for item in ImputationByNormalDistributionSamplingStrategyType
    }

    # a local generator keeps the global random state of other steps untouched
    rng = np.random.default_rng(seed) if seed >= 0 else np.random
    parameters = dict(
        strategy=strategy,
        down_shift=down_shift,
        scaling_factor=scaling_factor,
        log_transform=log_transform,
        seed=seed,
    )
    summary_rows = []

    if strategy == ImputationByNormalDistributionSamplingStrategyType.PER_PROTEIN.value:
        transformed_df = long_to_wide(protein_df)
        # iterate over all protein groups
        for protein_grp in transformed_df.columns:
            number_of_nans = transformed_df[protein_grp].isnull().sum()

            location_of_nans = transformed_df[protein_grp].isnull()
            indices_of_nans = location_of_nans[location_of_nans].index
            observed = _observed_values(transformed_df[protein_grp], log_transform)

            if number_of_nans > len(transformed_df[protein_grp]) - 2:
                summary_rows.append(
                    _summary_row(
                        "Protein ID",
                        protein_grp,
                        observed,
                        number_of_nans,
                        0,
                        np.nan,
                        np.nan,
                        parameters,
                    )
                )
                continue

            sampling_mean, sampling_std = _sampling_parameters(
                observed, down_shift, scaling_factor
            )
            transformed_df.loc[indices_of_nans, protein_grp] = (
                _sampled_imputation_values(
                    sampling_mean,
                    sampling_std,
                    number_of_nans,
                    log_transform,
                    rng,
                )
            )
            summary_rows.append(
                _summary_row(
                    "Protein ID",
                    protein_grp,
                    observed,
                    number_of_nans,
                    number_of_nans,
                    sampling_mean,
                    sampling_std,
                    parameters,
                )
            )

        imputed_df = wide_to_long(transformed_df, protein_df)

    elif (
        strategy == ImputationByNormalDistributionSamplingStrategyType.PER_SAMPLE.value
    ):
        # determine column for protein intensities
        intensity_type = default_intensity_column(protein_df)
        imputed_df = protein_df.copy()

        # iterate over all samples
        for sample in imputed_df["Sample"].unique():
            values = imputed_df.loc[imputed_df["Sample"] == sample, intensity_type]
            location_of_nans = values.isnull()
            indices_of_nans = location_of_nans[location_of_nans].index
            number_of_nans = len(indices_of_nans)
            observed = _observed_values(values, log_transform)

            # a sample without at least two measured values offers no standard
            # deviation to sample from, so it is left untouched
            if number_of_nans == 0 or len(observed) < 2:
                summary_rows.append(
                    _summary_row(
                        "Sample",
                        sample,
                        observed,
                        number_of_nans,
                        0,
                        np.nan,
                        np.nan,
                        parameters,
                    )
                )
                continue

            sampling_mean, sampling_std = _sampling_parameters(
                observed, down_shift, scaling_factor
            )
            imputed_df.loc[indices_of_nans, intensity_type] = (
                _sampled_imputation_values(
                    sampling_mean,
                    sampling_std,
                    number_of_nans,
                    log_transform,
                    rng,
                )
            )
            summary_rows.append(
                _summary_row(
                    "Sample",
                    sample,
                    observed,
                    number_of_nans,
                    number_of_nans,
                    sampling_mean,
                    sampling_std,
                    parameters,
                )
            )

    else:
        # determine column for protein intensities
        intensity_type = default_intensity_column(protein_df)
        imputed_df = protein_df.copy()

        number_of_nans = imputed_df[intensity_type].isnull().sum()
        assert number_of_nans <= len(imputed_df[intensity_type]) - 2

        location_of_nans = imputed_df[intensity_type].isnull()
        indices_of_nans = location_of_nans[location_of_nans].index
        observed = _observed_values(imputed_df[intensity_type], log_transform)

        # the original behaviour keeps dataset-wide imputed intensities positive,
        # which is only meaningful on the log10 scale
        sampling_mean, sampling_std = _sampling_parameters(
            observed, down_shift, scaling_factor, force_positive=log_transform
        )
        imputed_df.loc[indices_of_nans, intensity_type] = _sampled_imputation_values(
            sampling_mean,
            sampling_std,
            number_of_nans,
            log_transform,
            rng,
            force_positive=log_transform,
        )
        summary_rows.append(
            _summary_row(
                "Dataset",
                "all",
                observed,
                number_of_nans,
                number_of_nans,
                sampling_mean,
                sampling_std,
                parameters,
            )
        )

    outputs = flag_invalid_values(imputed_df, [])
    outputs["imputation_summary_df"] = pd.DataFrame(
        summary_rows, columns=SUMMARY_COLUMNS
    )
    return outputs


# --8<-- [end:by_normal_distribution_sampling]


def by_knn_plot(
    protein_df,
    output_protein_df,
    graph_type,
    graph_type_quantities,
    group_by,
    visual_transformation,
    show_outliers=True,
):
    return _build_box_hist_plot(
        protein_df,
        output_protein_df,
        graph_type,
        graph_type_quantities,
        group_by,
        visual_transformation,
        show_outliers,
    )


def by_normal_distribution_sampling_plot(
    protein_df,
    output_protein_df,
    graph_type,
    graph_type_quantities,
    group_by,
    visual_transformation,
    show_outliers=True,
):
    return _build_box_hist_plot(
        protein_df,
        output_protein_df,
        graph_type,
        graph_type_quantities,
        group_by,
        visual_transformation,
        show_outliers,
    )


def by_simple_imputer_plot(
    protein_df,
    output_protein_df,
    graph_type,
    graph_type_quantities,
    group_by,
    visual_transformation,
    show_outliers=True,
):
    return _build_box_hist_plot(
        protein_df,
        output_protein_df,
        graph_type,
        graph_type_quantities,
        group_by,
        visual_transformation,
        show_outliers,
    )


def by_min_per_sample_plot(
    protein_df,
    output_protein_df,
    graph_type,
    graph_type_quantities,
    group_by,
    visual_transformation,
    show_outliers=True,
):
    return _build_box_hist_plot(
        protein_df,
        output_protein_df,
        graph_type,
        graph_type_quantities,
        group_by,
        visual_transformation,
        show_outliers,
    )


def by_min_per_protein_plot(
    protein_df,
    output_protein_df,
    graph_type,
    graph_type_quantities,
    group_by,
    visual_transformation,
    show_outliers=True,
):
    return _build_box_hist_plot(
        protein_df,
        output_protein_df,
        graph_type,
        graph_type_quantities,
        group_by,
        visual_transformation,
        show_outliers,
    )


def by_min_per_dataset_plot(
    protein_df,
    output_protein_df,
    graph_type,
    graph_type_quantities,
    group_by,
    visual_transformation,
    show_outliers=True,
):
    return _build_box_hist_plot(
        protein_df,
        output_protein_df,
        graph_type,
        graph_type_quantities,
        group_by,
        visual_transformation,
        show_outliers,
    )


def number_of_imputed_values(input_df, result_df):
    return abs(result_df.isnull().sum().sum() - input_df.isnull().sum().sum())


def _build_box_hist_plot(
    df: pd.DataFrame,
    result_df: pd.DataFrame,
    graph_type: str = "Boxplot",
    graph_type_quantities: str = "Pie chart",
    group_by: str = "None",
    visual_transformation: str = "linear",
    show_outliers=True,
) -> list[Figure]:
    """
    This function creates two visualisations:

    1. graph visualising the distributional
    differences between the protein intensities prior to
    and after imputation. Default is set to display a grouped
    graph (see group_by parameter).

    2. a graph summarising the amount of
    filtered proteins.
    """

    intensity_name_df = df.columns[3]
    intensity_name_result_df = result_df.columns[3]

    imputed_df = result_df.copy()

    imputed_df[intensity_name_result_df] = list(
        map(
            lambda x, y: y if np.isnan(x) else np.nan,
            df[intensity_name_df],
            result_df[intensity_name_result_df],
        )
    )

    if graph_type == "Boxplot":
        fig1 = create_box_plots(
            dataframe_a=df,
            dataframe_b=imputed_df,
            name_a="Original Values",
            name_b="Imputed Values",
            heading="Distribution of Protein Intensities",
            group_by=group_by,
            visual_transformation=visual_transformation,
            y_title="Intensity",
            show_outliers=show_outliers,
        )
    elif graph_type == "Histogram":
        fig1 = create_histograms(
            dataframe_a=df,
            dataframe_b=imputed_df,
            name_a="Original Values",
            name_b="Imputed Values",
            heading="Distribution of Protein Intensities",
            visual_transformation=visual_transformation,
            overlay=True,
            x_title="Protein Intensities",
            y_title="Frequency of Protein Intensities",
        )

    values_of_sectors = [
        abs(len(df)),
        number_of_imputed_values(df, result_df),
    ]
    if graph_type_quantities == "Bar chart":
        fig2 = create_bar_plot(
            names_of_sectors=["Non-imputed values", "Imputed values"],
            values_of_sectors=values_of_sectors,
            heading="Number of Imputed Values",
            y_title="Number of Values",
        )
    elif graph_type_quantities == "Pie chart":
        fig2 = create_pie_plot(
            names_of_sectors=["Non-imputed values", "Imputed values"],
            values_of_sectors=values_of_sectors,
            heading="Number of Imputed Values",
        )
    return [fig1, fig2]
