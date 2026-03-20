import logging
import os
from pathlib import Path

import pandas as pd
from pandas import DataFrame

from backend.protzilla.constants.paths import BACKEND_PATH
from backend.protzilla.utilities.utilities import random_string


def file_importer(file_path: Path) -> tuple[pd.DataFrame, str]:
    """
    Imports a file based on its file extension and returns a pandas DataFrame or None if the file format is not
    supported / the file doesn't exist.
    """
    try:
        if file_path.suffix == ".csv":
            meta_df = pd.read_csv(
                file_path,
                sep=",",
                low_memory=False,
                na_values=[""],
                keep_default_na=True,
                skipinitialspace=True,
            )
        elif file_path.suffix == ".xlsx":
            meta_df = pd.read_excel(file_path)
        elif file_path.suffix == ".psv":
            meta_df = pd.read_csv(file_path, sep="|", low_memory=False)
        elif file_path.suffix == ".tsv":
            meta_df = pd.read_csv(file_path, sep="\t", low_memory=False)
        elif file_path == "":
            return (
                pd.DataFrame(),
                "The file upload is empty. Please select a metadata file.",
            )
        else:
            return (
                pd.DataFrame(),
                "File format not supported. \
            Supported file formats are csv, xlsx, psv or tsv",
            )
        # If duplicates are not remove this could negatively impact downstream analysis, e.g. produces wrong p-values
        # in differential expression tests.
        meta_df = meta_df.drop_duplicates()
        if meta_df.empty:
            raise pd.errors.EmptyDataError
        msg = "Metadata file successfully imported."
        return meta_df, msg
    except pd.errors.EmptyDataError:
        msg = "The file is empty."
        return pd.DataFrame(), msg


def metadata_import_method(file_path: Path, feature_orientation: str) -> dict:
    """
        Imports a metadata file and returns the intensity dataframe and a dict with a message if the file import failed,
        and the metadata dataframe if the import was successful.

    returns: dict of DataFrame and other dict of metadata and messages
    """
    messages = []
    meta_df, msg = file_importer(file_path)
    if meta_df.empty:
        return dict(
            messages=[dict(level=logging.ERROR, msg=msg)],
        )
    # A lot of the code assumes that there is a column "Sample" in the metadata dataframe, so this assumption has to be
    # checked here.
    if "MS run" in meta_df.columns:
        meta_df.rename(columns={"MS run": "Sample"}, inplace=True)
    if "Sample" not in meta_df.columns:
        return {
            "messages": [
                {
                    "level": logging.ERROR,
                    "msg": "The metadata file must contain a column named 'Sample' that matches the sample names in "
                    "the intensity dataframe.",
                }
            ]
        }

    messages.append({"level": logging.INFO, "msg": msg})
    if meta_df.shape[1] > meta_df.shape[0]:
        messages.append(
            {
                "level": logging.INFO,
                "msg": "The imported dataframe indicates an incorrect orientation. Consider viewing the table to ensure the orientation is correct.",
            }
        )

    # always return metadata in the same orientation (features as columns)
    # as the dtype get lost when transposing, we save the df to disk after
    # changing the format and read it again as "Columns"-oriented
    if feature_orientation.startswith("Rows"):
        meta_df = meta_df.transpose()
        meta_df.reset_index(inplace=True)
        meta_df.rename(columns=meta_df.iloc[0], inplace=True)
        meta_df.drop(index=0, inplace=True)
        meta_df.index = meta_df.index - 1

        file_path = (
            BACKEND_PATH / f"protzilla/importing/conversion_tmp_{random_string()}.csv"
        )
        meta_df.to_csv(file_path, index=False)
        return metadata_import_method(file_path, "Columns")

    elif str(file_path).startswith(
        f"{BACKEND_PATH}/protzilla/importing/conversion_tmp_"
    ):
        os.remove(file_path)
    return dict(metadata_df=meta_df, messages=messages)


def metadata_column_assignment(
    metadata_df: pd.DataFrame,
    metadata_required_column: str = None,
    metadata_unknown_column: str = None,
):
    """
    This function renames a column in the metadata dataframe to the required column name.

    :param metadata_df: the metadata dataframe to be changed
    :type metadata_df: float
    :param metadata_required_column: the name of the column in the dataframe that is used for the metadata assignment
    :type metadata_df: str
    :param metadata_unknown_column: the name of the column in the metadata dataframe that is renamed to the
     required column name
    :type metadata_unknown_column: str
    :return: returns the unchanged dataframe and a dict with messages, potentially empty if no messages
    :rtype: dict of pd.Dataframe and dict of messages
    """

    # check if required column already in metadata, if so give error message
    if (
        metadata_required_column is None
        or metadata_unknown_column is None
        or metadata_unknown_column == ""
        or metadata_required_column == ""
    ):
        msg = f"You can proceed, as there is nothing that needs to be changed."
        return dict(
            metadata_df=metadata_df,
            messages=[dict(level=logging.INFO, msg=msg)],
        )

    if metadata_required_column in metadata_df.columns:
        msg = f"Metadata already contains column '{metadata_required_column}'. \
        Please rename the column or select another column."
        return dict(
            metadata_df=metadata_df,
            messages=[dict(level=logging.ERROR, msg=msg)],
        )
    # rename given in metadata_sample_column column to "Sample" if it is called otherwise
    renamed_metadata_df = metadata_df.rename(
        columns={metadata_unknown_column: metadata_required_column}
    )
    return dict(metadata_df=renamed_metadata_df, messages=dict())
