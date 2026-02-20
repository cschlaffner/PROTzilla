from dataclasses import dataclass
import pandas as pd
from enum import Enum
from typing import NewType, TypedDict

class DataKeys(str, Enum):
    PROTEIN_DF = "protein_df"
    PEPTIDE_DF = "peptide_df"
    METADATA_DF = "metadata_df"
    FASTA_DF = "fasta_df"


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

