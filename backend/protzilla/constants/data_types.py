import pandas as pd
from enum import StrEnum
from typing import NewType, TypedDict
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier


class DataKey(StrEnum):
    DEBUG = "debug_data"
    PROTEIN_DF = "protein_df"
    PEPTIDE_DF = "peptide_df"
    PSM_DF = "psm_df"  # psm = peptide spectrum match
    METADATA_DF = "metadata_df"
    STRUCTURE_METADATA_DF = "structure_metadata_df"
    FASTA_DF = "fasta_df"
    SIGNIFICANT_PROTEINS_DF = "significant_proteins_df"
    PTM_DF = "ptm_df"
    DIFFERENTIALLY_EXPRESSED_PROTEINS_DF = "differentially_expressed_proteins_df"
    DIFFERENTIALLY_EXPRESSED_PTM_DF = "differentially_expressed_ptm_df"
    CORRECTED_P_VALUES_DF = "corrected_p_values_df"
    LOG2_FOLD_CHANGE_DF = "log2_fold_change_df"
    ENRICHMENT_DF = "enrichment_df"
    GENE_MAPPING_DF = "gene_mapping_df"
    CIF_DF = "cif_df"
    AMINO_ACID_SEQUENCES_DF = "amino_acid_sequences_df"
    PAE_MATRIX = "pae_matrix"  # pae = predicted aligned error
    PLDDT_DF = "plddt_df"  # plddt = predicted local distance difference test
    CROSSLINKING_DF = "crosslinking_df"
    CONFIDENCE_DF = "confidence_df"
    FULL_DATA_DF = "full_data_df"
    JOB_REQUEST_DF = "job_request_df"
    CORRELATION_MATRIX_DF = "correlation_matrix_df"
    DISTANCE_MATRIX_DF = "distance_matrix_df"
    CLUSTER_LABELS_DF = "cluster_labels_df"
    DBCV_SCORES_DF = "dbcv_scores_df"
    SILHOUETTE_SCORES_DF = "silhouette_scores_df"


ProteinDf = NewType("ProteinDf", pd.DataFrame)
PeptideDf = NewType("PeptideDf", pd.DataFrame)
MetadataDf = NewType("MetadataDf", pd.DataFrame)

StepID = NewType("StepID", str)

ClassificationType = SVC | RandomForestClassifier


class Connection(TypedDict):
    """
    Type for connections in the node viewer
    """

    source: StepID
    sourceHandle: DataKey
    target: StepID
    targetHandle: DataKey
    key: str
    id: str


def parse_connection(
    connection: Connection,
) -> tuple[StepID, DataKey, StepID, DataKey]:
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
