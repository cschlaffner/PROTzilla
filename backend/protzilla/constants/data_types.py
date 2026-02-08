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


class Connection(TypedDict):
    """
    Type for connections in the node viewer
    """

    source: str
    sourceHandle: DataKeys
    target: str
    targetHandle: DataKeys
    key: str
    id: str
