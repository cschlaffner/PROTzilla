import numpy as np
import pandas as pd

from backend.protzilla.constants.option_types import LogTransformationBaseType
from backend.protzilla.data_preprocessing.plots import (
    create_box_plots,
    create_histograms,
)
from backend.protzilla.utilities.utilities import default_intensity_column


# --8<-- [start:by_inversion]
def by_inversion(
    protein_df: pd.DataFrame, peptide_df: pd.DataFrame | None = None
) -> dict:
    """
    This function inverts the intensity column of a dataframe (1/n).
    Especially useful for H/L <-> L/H ratio transformations.

    :param protein_df: a protein data frame in long format
    :type protein_df: pd.DataFrame
    :param peptide_df: a peptide data frame, that is to be transformed the same way as the protein data frame

    :return: returns a dict containing the transformed dataframes for "protein_df" and "peptide_df" respectively
    :rtype: dict[str, pd.DataFrame | None]
    """
    protein_intensity_name = default_intensity_column(protein_df)
    peptide_intensity_name = (
        default_intensity_column(peptide_df) if peptide_df is not None else None
    )

    transformed_df = protein_df.copy()
    transformed_df[protein_intensity_name] = 1 / transformed_df[protein_intensity_name]
    if np.isinf(transformed_df[protein_intensity_name]).any():
        raise ValueError("Division by zero when inverting values.")

    transformed_peptide_df = peptide_df.copy() if peptide_df is not None else None
    if transformed_peptide_df is not None:
        transformed_peptide_df[peptide_intensity_name] = (
            1 / transformed_peptide_df[peptide_intensity_name]
        )
        if np.isinf(transformed_peptide_df[peptide_intensity_name]).any():
            raise ValueError("Division by zero when inverting values.")

    return dict(protein_df=transformed_df, peptide_df=transformed_peptide_df)


# --8<-- [end:by_inversion]


# --8<-- [start:by_log]
def by_log(
    protein_df: pd.DataFrame,
    peptide_df: pd.DataFrame | None = None,
    log_base: LogTransformationBaseType = LogTransformationBaseType.LOG10,
) -> dict:
    """
    This function log-transforms intensity
    DataFrames. Supports log-transformation to the base
    of 2 or 10.

    :param protein_df: a protein data frame in long format
    :type protein_df: pd.DataFrame
    :param peptide_df: a peptide data frame, that is to be transformed the same way as the protein data frame
    :param log_base: String of the used log method "log10" (base 10)
        or "log2" (base 2). Default: "log10"
    :type log_base: str

    :return: returns a dict containing the transformed dataframes for "protein_df" and "peptide_df" respectively
    :rtype: dict[str, pd.DataFrame | None]
    """
    try:
        log_base = LogTransformationBaseType(log_base)
    except ValueError:
        raise ValueError("Unknown log_base. Known log methods are 'log2' and 'log10'.")
    intensity_name = default_intensity_column(protein_df)
    peptide_intensity_name = (
        default_intensity_column(peptide_df) if peptide_df is not None else None
    )
    transformed_df = protein_df.copy()
    transformed_peptide_df = peptide_df.copy() if peptide_df is not None else None

    # TODO 41 drop data when intensity is 0 and return them in dict
    log_method = np.log2 if log_base == LogTransformationBaseType.LOG2 else np.log10
    transformed_df[intensity_name] = log_method(transformed_df[intensity_name])
    if transformed_peptide_df is not None:
        transformed_peptide_df[peptide_intensity_name] = log_method(
            transformed_peptide_df[peptide_intensity_name]
        )
    return dict(protein_df=transformed_df, peptide_df=transformed_peptide_df)


# --8<-- [end:by_log]


def by_log_plot(
    protein_df, output_protein_df, graph_type, group_by, show_outliers=True
):
    if graph_type == "Boxplot":
        fig = create_box_plots(
            dataframe_a=protein_df,
            dataframe_b=output_protein_df,
            name_a="Before Transformation",
            name_b="After Transformation",
            heading="Distribution of Protein Intensities",
            group_by=group_by,
            y_title="Intensity",
            show_outliers=show_outliers,
        )
    if graph_type == "Histogram":
        fig = create_histograms(
            dataframe_a=protein_df,
            dataframe_b=output_protein_df,
            name_a="Before Transformation",
            name_b="After Transformation",
            heading="Distribution of Protein Intensities",
            x_title="Protein Intensities",
            y_title="Frequency of Protein Intensities",
        )
    return [fig]
