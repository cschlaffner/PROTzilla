import logging

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

from backend.protzilla.data_preprocessing.plots import (
    create_box_plots,
    create_histograms,
)
from backend.protzilla.utilities.utilities import default_intensity_column


def by_z_score(protein_df: pd.DataFrame) -> dict:
    """
    A function to run the sklearn StandardScaler class on your dataframe.
    Normalises the data on the level of each sample.
    Scales the data to zero mean and unit variance. This is often also
    called z-score normalisation/transformation.

    :param protein_df: the dataframe that should be filtered in
        long format
    :type protein_df: pd.DataFrame

    :return: returns a scaled dataframe in typical protzilla long format and an empty
        dictionary
    :rtype: Tuple[pandas DataFrame, dict]
    """

    # Suppress SettingWithCopyWarning:
    # It gets raised because of reassignment of values to a subset of a df
    # The alternative - making an explicit copy - could use more memory
    # https://realpython.com/pandas-settingwithcopywarning/
    pd.set_option("mode.chained_assignment", None)

    intensity_name = default_intensity_column(protein_df)
    scaled_df = pd.DataFrame()
    samples = protein_df["Sample"].unique().tolist()

    for sample in samples:
        df_sample = protein_df.loc[protein_df["Sample"] == sample,]
        scaler = StandardScaler().fit(df_sample[[intensity_name]])
        df_sample[f"Normalised {intensity_name}"] = scaler.transform(
            df_sample[[intensity_name]]
        )
        df_sample.drop(axis=1, labels=[intensity_name], inplace=True)
        scaled_df = pd.concat([scaled_df, df_sample], ignore_index=True)

    pd.reset_option("mode.chained_assignment")
    return dict(protein_df=scaled_df)


def by_median(
    protein_df: pd.DataFrame,
    log: bool,
    percentile=0.5,  # quartile, default is median
) -> dict:
    """
    A function to perform a quartile/percentile normalisation on your
    dataframe. Normalises the data on the level of each sample.
    Divides each intensity by the chosen intensity quartile of the
    respective sample. By default, the median (50%-quartile) is used.

    :param protein_df: the dataframe that should be filtered in
        long format
    :type protein_df: pandas DataFrame
    :param log: whether the data was log transformed before the normalisation or not
    :type log: bool
    :param percentile: the chosen quartile of the sample intensities for
        normalisation
    :type percentile: float

    :return: returns a scaled dataframe in typical protzilla long format
        and a dict, containing all zeroed samples due to quantile being 0
    :rtype: Tuple[pandas DataFrame, dict]
    """

    # Suppress SettingWithCopyWarning:
    # It gets raised because of reassignment of values to a subset of a df
    # The alternative - making an explicit copy - could use more memory
    # https://realpython.com/pandas-settingwithcopywarning/
    pd.set_option("mode.chained_assignment", None)

    assert 0 <= percentile <= 1

    intensity_name = default_intensity_column(protein_df)
    scaled_df = pd.DataFrame()
    samples = protein_df["Sample"].unique().tolist()
    zeroed_samples = []

    if log:
        valid_mask = np.isfinite(protein_df[intensity_name])
        valid_data = protein_df.loc[valid_mask, intensity_name]
        global_median = valid_data.median()

    for sample in samples:
        df_sample = protein_df.loc[protein_df["Sample"] == sample,]
        quantile = df_sample[intensity_name].quantile(q=percentile)

        if log:
            if np.isfinite(quantile):
                # without adding the global median our data would be zero centered and therefore one half would be
                # negative which can lead to problems later down the workflow
                df_sample[f"Normalised {intensity_name}"] = (
                    df_sample[intensity_name] - quantile + global_median
                )
            else:
                df_sample[f"Normalised {intensity_name}"] = 0
                zeroed_samples.append(sample)
        else:
            if quantile != 0:
                df_sample[f"Normalised {intensity_name}"] = df_sample[
                    intensity_name
                ].div(quantile)
            else:
                df_sample[f"Normalised {intensity_name}"] = 0
                zeroed_samples.append(sample)
        df_sample.drop(axis=1, labels=[intensity_name], inplace=True)
        scaled_df = pd.concat([scaled_df, df_sample], ignore_index=True)

    pd.reset_option("mode.chained_assignment")

    output = dict(protein_df=scaled_df, zeroed_samples=zeroed_samples)

    if zeroed_samples != []:
        output["messages"] = dict(
            level=logging.WARNING,
            msg=f"Samples {zeroed_samples} have median zero - we recommend adapting your filtering strategy or using a higher quantile for normalisation",
        )
    return output


def by_totalsum(protein_df: pd.DataFrame) -> dict:
    """
    A function to perform normalisation using the total sum
    of sample intensities on your dataframe.
    Normalises the data on the level of each sample.
    Divides each intensity by the total sum of sample intensities.

    :param protein_df: the dataframe that should be filtered in
        long format
    :type protein_df: pandas DataFrame

    :return: returns a scaled dataframe in typical protzilla long format
        and a dict, containing all zeroed samples due to sum being 0
    :rtype: Tuple[pandas DataFrame, dict]
    """

    # Suppress SettingWithCopyWarning:
    # It gets raised because of reassignment of values to a subset of a df
    # The alternative - making an explicit copy - could use more memory
    # https://realpython.com/pandas-settingwithcopywarning/
    pd.set_option("mode.chained_assignment", None)

    intensity_name = default_intensity_column(protein_df)
    scaled_df = pd.DataFrame()
    samples = protein_df["Sample"].unique().tolist()
    zeroed_samples = []

    for sample in samples:
        df_sample = protein_df.loc[protein_df["Sample"] == sample,]
        totalsum = df_sample[intensity_name].sum()

        if totalsum != 0:
            df_sample[f"Normalised {intensity_name}"] = df_sample[intensity_name].div(
                totalsum
            )
        else:
            df_sample[f"Normalised {intensity_name}"] = 0
            zeroed_samples.append(sample)

        df_sample.drop(axis=1, labels=[intensity_name], inplace=True)

        scaled_df = pd.concat([scaled_df, df_sample], ignore_index=True)

    pd.reset_option("mode.chained_assignment")
    output = dict(protein_df=scaled_df, zeroed_samples=zeroed_samples)
    if zeroed_samples != []:
        output["messages"] = dict(
            level=logging.WARNING,
            msg=f"Samples {zeroed_samples} have a sum of zero - try using other filtering strategies such as filtering non- or low intensity samples.",
        )
    return output


def by_width_adjustment(protein_df: pd.DataFrame) -> dict:
    """
    The first, second and third quartiles (q_1, q_2, q_3) are calculated
    per sample. The second quartile (median) is subtracted to center the
    distribution, then the data are rescaled asymmetrically towards the
    median upper/lower quartile width across samples. Positive values are
    multiplied by (median(q3 - q2) / (q3 - q2)_sample) and negative values
    by (median(q2 - q1) / (q2 - q1)_sample).

    :param protein_df: the dataframe that should be normalised in
        long format
    :type protein_df: pandas DataFrame

    :return: returns a scaled dataframe in typical protzilla long format;
        on failure (zero quartile width) returns None and an error message
    :rtype: dict with protein_df (pd.DataFrame | None) and optional messages
    """

    # Suppress SettingWithCopyWarning:
    # It gets raised because of reassignment of values to a subset of a df
    # The alternative - making an explicit copy - could use more memory
    # https://realpython.com/pandas-settingwithcopywarning/
    pd.set_option("mode.chained_assignment", None)

    intensity_name = default_intensity_column(protein_df)
    samples = protein_df["Sample"].unique().tolist()
    sample_quartiles = {}
    upper_widths = []
    lower_widths = []

    for sample in samples:
        sample_series = pd.to_numeric(
            protein_df.loc[protein_df["Sample"] == sample, intensity_name],
            errors="coerce",
        )

        if sample_series.isna().all():
            raise ValueError(
                f"Width adjustment normalisation failed because all intensity values in sample {sample} \
                are non-numeric."
            )
        q1 = sample_series.quantile(0.25)
        q2 = sample_series.quantile(0.5)
        q3 = sample_series.quantile(0.75)
        upper_width = q3 - q2
        lower_width = q2 - q1

        if upper_width == 0 or lower_width == 0:
            if upper_width > 0:
                upper_widths.append(upper_width)
            if lower_width > 0:
                lower_widths.append(lower_width)
        else:
            upper_widths.append(upper_width)
            lower_widths.append(lower_width)

        sample_quartiles[sample] = dict(
            q2=q2, upper_width=upper_width, lower_width=lower_width
        )

    target_upper_width = pd.Series(upper_widths).median() if upper_widths else 0
    target_lower_width = pd.Series(lower_widths).median() if lower_widths else 0

    if target_upper_width == 0 or target_lower_width == 0:
        msg = "Width adjustment normalisation failed because no sample had a non-zero quartile width."
        return dict(
            protein_df=None,
            messages=[dict(level=logging.ERROR, msg=msg)],
        )

    scaled_df = pd.DataFrame()
    for sample in samples:
        sample_df = protein_df.loc[protein_df["Sample"] == sample].copy()
        centered = pd.to_numeric(sample_df[intensity_name], errors="coerce") - (
            sample_quartiles[sample]["q2"]
        )

        scale_upper = (
            target_upper_width / sample_quartiles[sample]["upper_width"]
            if sample_quartiles[sample]["upper_width"] > 0
            else 1
        )
        scale_lower = (
            target_lower_width / sample_quartiles[sample]["lower_width"]
            if sample_quartiles[sample]["lower_width"] > 0
            else 1
        )

        scaled = centered.copy()
        scaled_mask = centered > 0
        scaled.loc[scaled_mask] = centered.loc[scaled_mask] * scale_upper
        scaled.loc[~scaled_mask] = centered.loc[~scaled_mask] * scale_lower

        sample_df[f"Normalised {intensity_name}"] = scaled
        sample_df.drop(axis=1, labels=[intensity_name], inplace=True)
        scaled_df = pd.concat([scaled_df, sample_df], ignore_index=True)

    result_df = scaled_df.sort_values(
        by=["Sample", "Protein ID"], inplace=False, ignore_index=True
    )

    pd.reset_option("mode.chained_assignment")
    return dict(protein_df=result_df)


def by_reference_protein(
    protein_df: pd.DataFrame,
    reference_protein: str,
) -> dict:
    """
    A function to perform protein-intensity normalisation in reference
    to a selected protein on your dataframe.
    Normalises the data on the level of each sample.
    Divides each intensity by the intensity of the chosen reference
    protein in each sample. Samples where this value is zero will be
    removed and returned separately.

    :param protein_df: the dataframe that should be filtered in
        long format
    :type protein_df: pandas DataFrame
    :param reference_protein: Protein ID of the protein to normalise by
        type reference_protein_id: str
    :return: returns a scaled dataframe in typical protzilla long format
        and dict with a list of the indices of the dropped samples
    :rtype: Tuple[pandas DataFrame, dict]
    """
    scaled_df = pd.DataFrame()
    dropped_samples = []
    intensity_name = default_intensity_column(protein_df)
    protein_groups = protein_df["Protein ID"].unique().tolist()
    for group in protein_groups:
        if reference_protein in group.split(";"):
            reference_protein_group = group
            break
    else:
        raise ValueError(f"The protein with ID {reference_protein} was not found")

    samples = protein_df["Sample"].unique().tolist()
    for sample in samples:
        df_sample = protein_df.loc[protein_df["Sample"] == sample]

        reference_intensity = df_sample.loc[
            df_sample["Protein ID"].values == reference_protein_group,
            intensity_name,
        ].values[0]
        if not (reference_intensity > 0):
            dropped_samples.append(sample)
            continue

        df_sample.loc[:, f"Normalised {intensity_name}"] = df_sample.loc[
            :, intensity_name
        ].div(reference_intensity)
        df_sample.drop(axis=1, labels=[intensity_name], inplace=True)

        scaled_df = pd.concat([scaled_df, df_sample], ignore_index=True)

    return dict(protein_df=scaled_df, dropped_samples=dropped_samples)


def by_z_score_plot(
    protein_df,
    output_protein_df,
    graph_type,
    group_by,
    visual_transformation,
    show_outliers=True,
):
    return _build_box_hist_plot(
        protein_df,
        output_protein_df,
        graph_type,
        group_by,
        visual_transformation,
        show_outliers,
    )


def by_median_plot(
    protein_df,
    output_protein_df,
    graph_type,
    group_by,
    visual_transformation,
    show_outliers=True,
):
    return _build_box_hist_plot(
        protein_df,
        output_protein_df,
        graph_type,
        group_by,
        visual_transformation,
        show_outliers,
    )


def by_totalsum_plot(
    protein_df,
    output_protein_df,
    graph_type,
    group_by,
    visual_transformation,
    show_outliers=True,
):
    return _build_box_hist_plot(
        protein_df,
        output_protein_df,
        graph_type,
        group_by,
        visual_transformation,
        show_outliers,
    )


def by_reference_protein_plot(
    protein_df,
    output_protein_df,
    graph_type,
    group_by,
    visual_transformation,
    show_outliers=True,
):
    return _build_box_hist_plot(
        protein_df,
        output_protein_df,
        graph_type,
        group_by,
        visual_transformation,
        show_outliers,
    )


def by_width_adjustment_plot(
    protein_df,
    output_protein_df,
    graph_type,
    group_by,
    visual_transformation,
    show_outliers=True,
):
    return _build_box_hist_plot(
        protein_df,
        output_protein_df,
        graph_type,
        group_by,
        visual_transformation,
        show_outliers,
    )


def _build_box_hist_plot(
    df, result_df, graph_type, group_by, visual_transformation, show_outliers=True
):
    if graph_type == "Boxplot":
        fig = create_box_plots(
            dataframe_a=df,
            dataframe_b=result_df,
            name_a="Before Normalisation",
            name_b="After Normalisation",
            heading="Distribution of Protein Intensities",
            x_title="",
            y_title="Intensity",
            group_by=group_by,
            visual_transformation=visual_transformation,
            show_outliers=show_outliers,
        )
    if graph_type == "Histogram":
        fig = create_histograms(
            dataframe_a=df,
            dataframe_b=result_df,
            name_a="Before Normalisation",
            name_b="After Normalisation",
            heading="Distribution of Protein Intensities",
            x_title="Protein Intensities",
            y_title="Frequency of Protein Intensities",
            visual_transformation=visual_transformation,
        )
    return [fig]
