from enum import StrEnum


class MAX_QUANT_PEPTIDE_COLUMNS(StrEnum):
    """
    Enum containing column names expected in raw MQ peptide.txt files
    """

    LEADING_RAZOR_PROTEIN = "Leading razor protein"
    SEQUENCE = "Sequence"
    MISSED_CLEAVAGES = "Missed cleavages"
    PEP = "PEP"


class PEPTIDE_DF_COLUMNS(StrEnum):
    """
    Enum containing column names expected in a peptide_df after import
    """

    SEQUENCE = "Sequence"
    MISSED_CLEAVAGES = "Missed cleavages"
    PEP = "PEP"
    # During the peptide import, Leading razor protein is renamed to Protein ID
    PROTEIN_ID = "Protein ID"


class MAX_QUANT_EVIDENCE_COLUMNS(StrEnum):
    """
    Enum containing column names expected in raw MQ evidence.txt files
    """

    LEADING_RAZOR_PROTEIN = "Leading razor protein"
    SEQUENCE = "Sequence"
    MISSED_CLEAVAGES = "Missed cleavages"
    PEP = "PEP"
    MODIFICATIONS = "Modifications"
    MODIFIED_SEQUENCE = "Modified sequence"
    EXPERIMENT = "Experiment"
    RAW_FILE = "Raw file"


class PSM_DF_COLUMNS(StrEnum):
    """
    Enum containing column names expected in a psm_df after import
    """

    SEQUENCE = "Sequence"
    MISSED_CLEAVAGES = "Missed cleavages"
    PEP = "PEP"
    MODIFICATIONS = "Modifications"
    MODIFIED_SEQUENCE = "Modified sequence"
    RAW_FILE = "Raw file"
    # During the evidence import, Leading razor protein is renamed to Protein ID
    PROTEIN_ID = "Protein ID"
    SAMPLE = "Sample"


class MODIFICATION_COLUMNS(StrEnum):
    """
    Enum containing all column names expected in a modification_df
    """

    PROTEIN_ID = "Protein ID"
    MODIFICATION = "Modification"
    PROTEIN_LOCATION = "Protein Location"
    RESIDUE = "Residue"
