import numpy as np
import pandas as pd
import re

from backend.protzilla.utilities.transform_dfs import long_to_wide
from backend.protzilla.data_analysis.amino_acid_spheres import (
    find_ptm_amino_acid_sphere_collisions,
)
from backend.protzilla.steps import OutputItem, OutputType


def ptms_per_sample(psm_df: pd.DataFrame) -> dict:
    """
    This function calculates the amount of every PTMs per sample.

    :param psm_df: the pandas dataframe containing the peptide information

    :return: dict containing a dataframe one row per sample and one column per PTM that occurs in the peptide_df,
    with the cells containing the amount of the PTM in the sample
    """

    modification_df = aggregate_ptms(psm_df, ["Sample"])

    modification_df["Total Amount of Peptides"] = (
        psm_df.groupby("Sample").size().reset_index()[0]
    )

    return dict(ptm_df=modification_df)


def ptms_per_protein_and_sample(psm_df: pd.DataFrame) -> dict:
    """
    This function calculates the amount of every PTM per sample and protein.

    :param psm_df: the pandas dataframe containing the peptide information

    :return: dict containing a dataframe one row per sample and one column per protein,
    with the cells containing a list of PTMs that occur in the peptide_df for the protein and sample and
    their amount in the protein and sample
    """

    modification_df = aggregate_ptms(psm_df, ["Sample", "Protein ID"])

    modi = modification_df.drop(["Sample", "Protein ID"], axis=1).apply(
        lambda x: ("(" + x.astype(str) + ") " + x.name + ", ")
    )

    for column, data in modi.items():
        modi[column] = np.where(modification_df[column] > 0, modi[column], "")

    modification_df["Modifications"] = modi.apply("".join, axis=1)
    modification_df = modification_df[["Sample", "Protein ID", "Modifications"]]

    modification_df = (
        long_to_wide(modification_df, "Modifications").fillna("").reset_index()
    )

    return dict(ptm_df=modification_df)


def aggregate_ptms(psm_df: pd.DataFrame, group_by: list[str]):

    modification_df = pd.concat(
        [psm_df[group_by], (psm_df["Modifications"].str.get_dummies(sep=","))],
        axis=1,
    )

    for column, data in modification_df.items():
        amount, name = from_string(column)
        if amount > 1:
            modification_df[column] = modification_df[column].multiply(amount)
            modification_df = modification_df.rename(columns={column: name})

    modification_df = modification_df.groupby(group_by).sum()

    modification_df = modification_df.groupby(modification_df.columns, axis=1).sum()

    modification_df = modification_df.reset_index()

    return modification_df


def from_string(mod_string: str) -> tuple[int, str]:
    """
    This function extracts the amount and name of a modification from its listing in the evidence file.

    :param mod_string: a string containing the amount and name of the modification

    :return: tuple containing the amount and name of the modification
    """

    re_search = re.search(r"\d+", mod_string)
    amount = int(re_search.group()) if re_search else 1
    name = re.search(r"\D+", mod_string).group()
    name = name[1:] if name[0] == " " else name

    return amount, name


def ptm_validation(
    cif_df: pd.DataFrame,
    structure_metadata_df: pd.DataFrame,
    ignored_neighbors: int = 0,
):
    ignored_neighbors = int(ignored_neighbors)
    collisions = find_ptm_amino_acid_sphere_collisions(
        cif_df, ignored_neighbors=ignored_neighbors
    )
    collision_columns = [
        "ptm_name",
        "ptm_chain",
        "ptm_position",
        "amino_acid_chain",
        "amino_acid_position",
    ]
    collision_rows = [
        {
            "ptm_name": collision["ptm_name"],
            "ptm_chain": collision["chain"],
            "ptm_position": collision["position"],
            "amino_acid_chain": amino_acid["chain"],
            "amino_acid_position": amino_acid["position"],
        }
        for collision in collisions
        for amino_acid in collision["collisions"]
    ]
    data_for_visualization = {
        "structure_entry_id": structure_metadata_df["entry_id"].iloc[0],
        "cif_df": cif_df,
        "include_ptm_spheres": True,
        "ignored_neighbors": ignored_neighbors,
    }
    return {
        "ptm_collisions_df": pd.DataFrame(collision_rows, columns=collision_columns),
        "visualization": OutputItem(
            output_type=OutputType.VISUALIZATION, value=data_for_visualization
        ),
    }
