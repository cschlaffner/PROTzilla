from enum import StrEnum


ATOM_SITE_PREFIX = "_atom_site."


class ATOM_SITE_COLUMNS(StrEnum):
    """
    Enum containing all column names that should be present in
    the _atom_site. table for mmCIF files from PDB or AFDB
    """

    ID = f"{ATOM_SITE_PREFIX}id"
    TYPE_SYMBOL = f"{ATOM_SITE_PREFIX}type_symbol"
    LABEL_ATOM_ID = f"{ATOM_SITE_PREFIX}label_atom_id"
    LABEL_ALT_ID = f"{ATOM_SITE_PREFIX}label_alt_id"
    LABEL_COMP_ID = f"{ATOM_SITE_PREFIX}label_comp_id"
    LABEL_ASYM_ID = f"{ATOM_SITE_PREFIX}label_asym_id"
    LABEL_ENTITY_ID = f"{ATOM_SITE_PREFIX}label_entity_id"
    LABEL_SEQ_ID = f"{ATOM_SITE_PREFIX}label_seq_id"
    PDBX_PDB_INS_CODE = f"{ATOM_SITE_PREFIX}pdbx_PDB_ins_code"
    CARTN_X = f"{ATOM_SITE_PREFIX}Cartn_x"
    CARTN_Y = f"{ATOM_SITE_PREFIX}Cartn_y"
    CARTN_Z = f"{ATOM_SITE_PREFIX}Cartn_z"
    OCCUPANCY = f"{ATOM_SITE_PREFIX}occupancy"
    B_ISO_OR_EQUIV = f"{ATOM_SITE_PREFIX}B_iso_or_equiv"
    PDBX_FORMAL_CHARGE = f"{ATOM_SITE_PREFIX}pdbx_formal_charge"
    AUTH_SEQ_ID = f"{ATOM_SITE_PREFIX}auth_seq_id"
    AUTH_COMP_ID = f"{ATOM_SITE_PREFIX}auth_comp_id"
    AUTH_ASYM_ID = f"{ATOM_SITE_PREFIX}auth_asym_id"
    AUTH_ATOM_ID = f"{ATOM_SITE_PREFIX}auth_atom_id"
    PDBX_PDB_MODEL_NUM = f"{ATOM_SITE_PREFIX}pdbx_PDB_model_num"


ATOM_SITE_LABEL_COMP_ID = ATOM_SITE_COLUMNS.LABEL_COMP_ID

ATOM_SITE_COLUMNS_NUMERIC = [
    ATOM_SITE_COLUMNS.ID,
    ATOM_SITE_COLUMNS.LABEL_SEQ_ID,
    ATOM_SITE_COLUMNS.CARTN_X,
    ATOM_SITE_COLUMNS.CARTN_Y,
    ATOM_SITE_COLUMNS.CARTN_Z,
    ATOM_SITE_COLUMNS.OCCUPANCY,
    ATOM_SITE_COLUMNS.B_ISO_OR_EQUIV,
    ATOM_SITE_COLUMNS.AUTH_SEQ_ID,
]

CHEM_COMP_PREFIX = "_chem_comp."


class CHEM_COMP_COLUMNS(StrEnum):
    """
    Enum containing all column names that should be present in
    the _chem_comp. table for mmCIF files from PDB or AFDB
    """

    ID = f"{CHEM_COMP_PREFIX}id"
    TYPE = f"{CHEM_COMP_PREFIX}type"
    MON_NSTD_FLAG = f"{CHEM_COMP_PREFIX}mon_nstd_flag"
    NAME = f"{CHEM_COMP_PREFIX}name"
    PDBX_SYNONYMS = f"{CHEM_COMP_PREFIX}pdbx_synonyms"
    FORMULA = f"{CHEM_COMP_PREFIX}formula"
    FORMULA_WEIGHT = f"{CHEM_COMP_PREFIX}formula_weight"
