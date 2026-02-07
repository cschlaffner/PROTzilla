from enum import Enum


class FeatureOrientationType(Enum):
    COLUMNS = "Columns (samples in rows, features in columns)"
    ROWS = "Rows (features in rows, samples in columns)"


class EmptyEnum(Enum):
    pass


class AggregationMethods(Enum):
    sum = "Sum"
    median = "Median"
    mean = "Mean"


rename_columns_csm_format = {
    "Crosslink Type": "Is_intra_crosslink",
    "PepSeq1": "Peptide1",
    "PepSeq2": "Peptide2",
    "LinkPos1": "CL_position1",
    "LinkPos2": "CL_position2",
    "PEP": "Q_value",
}

rename_columns_proteomediscoverer_xlinkx_format = {
    "Accession A": "Protein_id1",
    "Accession B": "Protein_id2",
    "Crosslink Type": "Is_intra_crosslink",
    "Sequence A": "Peptide1",
    "Sequence B": "Peptide2",
    "Q-value": "Q_value",
}

columns_in_crosslinking_df = [
    "Protein1",
    "Protein2",
    "Protein_id1",
    "Protein_id2",
    "Is_intra_crosslink",
    "Crosslinker",
    "Peptide1",
    "Peptide2",
    "CL_position1",
    "CL_position2",
    "Q_value",
]
