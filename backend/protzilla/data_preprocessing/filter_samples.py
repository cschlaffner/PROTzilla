import pandas as pd

from backend.protzilla.data_preprocessing.plots import create_bar_plot, create_pie_plot
from backend.protzilla.utilities.utilities import default_intensity_column


def by_protein_intensity_sum(
    protein_df: pd.DataFrame,
    deviation_threshold: float,
) -> dict:
    """
    This function filters samples based on the sum of the protein intensities.

    :param protein_df: the intensity dataframe that should be filtered
    :param deviation_threshold: defining the maximally allowed deviation from the median (in standard deviations)
        to keep a sample
    :return: the filtered df as a Dataframe and a dict with a list of Sample IDs that have been filtered
    """
    intensity_name = default_intensity_column(protein_df)
    sample_protein_sum = protein_df.groupby("Sample")[intensity_name].sum()

    median = sample_protein_sum.median()
    sd = sample_protein_sum.std()

    filtered_samples_list = sample_protein_sum[
        ~sample_protein_sum.between(
            (median - deviation_threshold * sd),
            (median + deviation_threshold * sd),
        )
    ].index.tolist()

    filtered_df = protein_df[~(protein_df["Sample"].isin(filtered_samples_list))]

    return dict(
        protein_df=filtered_df,
        filtered_samples=filtered_samples_list,
    )


def by_protein_count(
    protein_df: pd.DataFrame,
    deviation_threshold: float,
) -> dict:
    """
    This function filters samples based on their deviation of amount of proteins with a non-nan value from
    the median across all samples.

    :param protein_df: the intensity dataframe that should be filtered
    :param deviation_threshold: float, defining the allowed deviation (in standard deviations) from the median number
        of non-nan values to keep a sample
    :return: the filtered df as a Dataframe and a dict with a list of Sample IDs that have been filtered
    """
    intensity_name = default_intensity_column(protein_df)
    sample_protein_count = (
        protein_df[~protein_df[intensity_name].isnull()]
        .groupby("Sample")["Protein ID"]
        .nunique()
    )

    median = sample_protein_count.median()
    sd = sample_protein_count.std()

    filtered_samples_list = sample_protein_count[
        ~sample_protein_count.between(
            (median - deviation_threshold * sd),
            (median + deviation_threshold * sd),
        )
    ].index.tolist()

    filtered_df = protein_df[~(protein_df["Sample"].isin(filtered_samples_list))]

    return dict(
        protein_df=filtered_df,
        filtered_samples=filtered_samples_list,
    )


def by_proteins_missing(
    protein_df: pd.DataFrame,
    percentage: float,
) -> dict:
    """
    This function filters samples based on the amount of proteins with nan values, if the percentage of nan values
    is below a threshold (percentage).

    :param protein_df: the intensity dataframe that should be filtered
    :param percentage: ranging from 0 to 1. Defining the relative share of proteins that were detected in the
        sample in inorder to be kept.
    :return: the filtered df as a Dataframe and a dict with a list of Sample IDs that have been filtered
    """

    intensity_name = default_intensity_column(protein_df)
    total_protein_count = protein_df["Protein ID"].nunique()
    sample_protein_count = (
        protein_df[~protein_df[intensity_name].isnull()]
        .groupby("Sample")["Protein ID"]
        .nunique()
        .reindex(protein_df["Sample"].unique(), fill_value=0)
    )
    filtered_samples_list = sample_protein_count[
        ~sample_protein_count.ge(total_protein_count * percentage)
    ].index.tolist()

    filtered_df = protein_df[~(protein_df["Sample"].isin(filtered_samples_list))]

    return dict(
        protein_df=filtered_df,
        filtered_samples=filtered_samples_list,
    )


def by_class_in_metadata(
    protein_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    class_column: str,
    classes_names: list[str],
) -> dict:
    """
        This function filters samples based on a user specified class, e.g. filter out a batch.

        :param protein_df: the intensity dataframe that should be filtered
        :param metadata_df: the dataframe that contains the metadata needed for filtering the intensity frame
        :param class_column: the kind of class that should be filtered for (e.g Batch or Group)
        :param classes_names: the specific classes that should be filtered out (e.g. Batch_A, or faulty_batch)
    a
        :return: the filtered df as a Dataframe and a dict with a list of Sample IDs that have been filtered
    """
    filtered_samples_list = metadata_df[
        metadata_df[class_column].astype(str).isin(classes_names)
    ]["Sample"].tolist()
    filtered_df = protein_df[~(protein_df["Sample"].isin(filtered_samples_list))]
    return dict(
        protein_df=filtered_df,
        filtered_samples=filtered_samples_list,
    )


def by_protein_intensity_sum_plot(
    output_protein_df, output_filtered_samples, graph_type
):
    return _build_pie_bar_plot(output_protein_df, output_filtered_samples, graph_type)


def by_proteins_missing_plot(output_protein_df, output_filtered_samples, graph_type):
    return _build_pie_bar_plot(output_protein_df, output_filtered_samples, graph_type)


def by_protein_count_plot(output_protein_df, output_filtered_samples, graph_type):
    return _build_pie_bar_plot(output_protein_df, output_filtered_samples, graph_type)


def by_class_in_metadata_plot(output_protein_df, output_filtered_samples, graph_type):
    return _build_pie_bar_plot(output_protein_df, output_filtered_samples, graph_type)


def _build_pie_bar_plot(result_df, filtered_sampels, graph_type):
    if graph_type == "Pie chart":
        fig = create_pie_plot(
            values_of_sectors=[
                len(result_df["Sample"].unique()),
                len(filtered_sampels),
            ],
            names_of_sectors=["Samples kept", "Samples filtered"],
            heading="Number of Filtered Samples",
        )
    if graph_type == "Bar chart":
        fig = create_bar_plot(
            values_of_sectors=[
                len(result_df["Sample"].unique()),
                len(filtered_sampels),
            ],
            names_of_sectors=["Samples kept", "Samples filtered"],
            heading="Number of Filtered Samples",
            y_title="Number of Samples",
        )
    return [fig]
