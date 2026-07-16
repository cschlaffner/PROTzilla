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
    "LinkPos1": "CL_position_within_peptide1",
    "LinkPos2": "CL_position_within_peptide2",
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
    "CL_position_within_peptide1",
    "CL_position_within_peptide2",
    "Q_value",
]

column_aliases = {
    "Protein1": [
        "protein1",
        "Protein A",
        "Gene Name A",
        "Gene names A",
        "Alpha Gene Name",
    ],
    "Protein2": [
        "protein2",
        "Protein B",
        "Gene Name B",
        "Gene names B",
        "Beta Gene Name",
    ],
    "Protein_id1": [
        "protein_id1",
        "protein_id_a",
        "ProteinId1",
        "Alpha Protein Id",
        "Accession A",
        "AccessionA",
        "Protein Accession A",
        "Protein Accessions A",
    ],
    "Protein_id2": [
        "protein_id2",
        "protein_id_b",
        "ProteinId2",
        "Beta Protein Id",
        "Accession B",
        "AccessionB",
        "Protein Accession B",
        "Protein Accessions B",
    ],
    "Is_intra_crosslink": [
        "Crosslink Type",
        "XL_type",
        "Link-Type",
        "LinkType",
        "Link type",
        "XFDR.is_intraprotein",
    ],
    "Crosslinker": ["xl_mod"],
    "Peptide1": [
        "Sequence A",
        "SequenceA",
        "Peptide A",
        "peptide_a",
        "peptide1",
        "Alpha peptide",
        "CleanPep 1",
        "PepSeq1",
        "alpha_sequence",
    ],
    "Peptide2": [
        "Sequence B",
        "SequenceB",
        "Peptide B",
        "peptide_b",
        "peptide2",
        "Beta peptide",
        "CleanPep 2",
        "PepSeq2",
        "beta_sequence",
    ],
    "CL_position_within_peptide1": [
        "Crosslinker Position A",
        "xl_a",
        "AlphaPos",
        "LinkPos1",
        "xl_pos1",
    ],
    "CL_position_within_peptide2": [
        "Crosslinker Position B",
        "xl_b",
        "BetaPos",
        "LinkPos2",
        "xl_pos2",
    ],
    "Q_value": [
        "Q-value",
        "Qvalue",
    ],
}

rename_columns_universal_format = {
    alias: target for target, aliases in column_aliases.items() for alias in aliases
}
