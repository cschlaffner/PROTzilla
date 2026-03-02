from dataclasses import dataclass
import pandas as pd
from enum import StrEnum
from typing import NewType, TypedDict


class DataKeys(StrEnum):
    PROTEIN_DF = "protein_df"
    PEPTIDE_DF = "peptide_df"
    METADATA_DF = "metadata_df"
    FASTA_DF = "fasta_df"
    SIGNIFICANT_PROTEINS_DF = "significant_proteins_df"
    PTM_DF = "ptm_df"


ProteinDf = NewType("ProteinDf", pd.DataFrame)
PeptideDf = NewType("PeptideDf", pd.DataFrame)
MetadataDf = NewType("MetadataDf", pd.DataFrame)

StepID = NewType("StepID", str)


class OutputLocator(TypedDict):
    step_id: StepID
    key: DataKeys


class Connection(TypedDict):
    """
    Type for connections in the node viewer
    """

    source: StepID
    sourceHandle: DataKeys
    target: StepID
    targetHandle: DataKeys
    key: str
    id: str


def parse_connection(
    connection: Connection,
) -> tuple[StepID, DataKeys, StepID, DataKeys]:
    try:
        return (
            connection["source"],
            connection["sourceHandle"],
            connection["target"],
            connection["targetHandle"],
        )
    except KeyError as e:
        raise KeyError(
            "The supplied connection parameter does not adhere to the specification. Expected keys are source, sourceHandle, target and targetHandle"
        ) from e
