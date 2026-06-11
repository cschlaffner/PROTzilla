import pandas as pd

from enum import Enum, StrEnum
from pathlib import Path

from typing_extensions import override

from backend.protzilla.constants.paths import PTM_PATH
from backend.protzilla.form import Option


ATOM_SITE_PREFIX = "_atom_site."


class ATOM_SITE_COLUMNS(StrEnum):
    """
    Enum containing all column names that should be present in
    the _atom_site. table for mmCIF files from PDB or AFDB
    """

    GROUP_PDB = f"{ATOM_SITE_PREFIX}group_PDB"
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


ATOM_SITE_COLUMNS_NUMERIC = [
    ATOM_SITE_COLUMNS.ID,
    ATOM_SITE_COLUMNS.LABEL_ENTITY_ID,
    ATOM_SITE_COLUMNS.LABEL_SEQ_ID,
    ATOM_SITE_COLUMNS.CARTN_X,
    ATOM_SITE_COLUMNS.CARTN_Y,
    ATOM_SITE_COLUMNS.CARTN_Z,
    ATOM_SITE_COLUMNS.OCCUPANCY,
    ATOM_SITE_COLUMNS.B_ISO_OR_EQUIV,
    ATOM_SITE_COLUMNS.AUTH_SEQ_ID,
]

CHEM_COMP_PREFIX = "_chem_comp."

# convert flags to native booleans
CIF_BOOL_MAP = {"y": True, "n": False, ".": pd.NA}


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


BACKBONE_ATOMS = ["N", "CA", "C", "O"]

CHEM_COMP_ATOM_PREFIX = "_chem_comp_atom."


class CHEM_COMP_ATOM_COLUMNS(StrEnum):
    """
    Enum containing all column names expected in the _chem_comp_atom. table
    in the cif files describing modified residues
    """

    COMP_ID = f"{CHEM_COMP_ATOM_PREFIX}comp_id"
    ATOM_ID = f"{CHEM_COMP_ATOM_PREFIX}atom_id"
    ALT_ATOM_ID = f"{CHEM_COMP_ATOM_PREFIX}alt_atom_id"
    TYPE_SYMBOL = f"{CHEM_COMP_ATOM_PREFIX}type_symbol"
    CHARGE = f"{CHEM_COMP_ATOM_PREFIX}charge"
    MODEL_CARTN_X = f"{CHEM_COMP_ATOM_PREFIX}model_Cartn_x"
    MODEL_CARTN_Y = f"{CHEM_COMP_ATOM_PREFIX}model_Cartn_y"
    MODEL_CARTN_Z = f"{CHEM_COMP_ATOM_PREFIX}model_Cartn_z"
    IDEAL_CARTN_X = f"{CHEM_COMP_ATOM_PREFIX}pdbx_model_Cartn_x_ideal"
    IDEAL_CARTN_Y = f"{CHEM_COMP_ATOM_PREFIX}pdbx_model_Cartn_y_ideal"
    IDEAL_CARTN_Z = f"{CHEM_COMP_ATOM_PREFIX}pdbx_model_Cartn_z_ideal"
    LEAVING_FLAG = f"{CHEM_COMP_ATOM_PREFIX}pdbx_leaving_atom_flag"
    BACKBONE_FLAG = f"{CHEM_COMP_ATOM_PREFIX}pdbx_backbone_atom_flag"


# convert column name from chem_comp_atom columns to atom_site columns
ATOM_SITE_TO_CHEM_COMP = {
    ATOM_SITE_COLUMNS.LABEL_ATOM_ID: CHEM_COMP_ATOM_COLUMNS.ATOM_ID,
    ATOM_SITE_COLUMNS.AUTH_ATOM_ID: CHEM_COMP_ATOM_COLUMNS.ATOM_ID,
    ATOM_SITE_COLUMNS.TYPE_SYMBOL: CHEM_COMP_ATOM_COLUMNS.TYPE_SYMBOL,
    ATOM_SITE_COLUMNS.PDBX_FORMAL_CHARGE: CHEM_COMP_ATOM_COLUMNS.CHARGE,
    ATOM_SITE_COLUMNS.CARTN_X: CHEM_COMP_ATOM_COLUMNS.IDEAL_CARTN_X,
    ATOM_SITE_COLUMNS.CARTN_Y: CHEM_COMP_ATOM_COLUMNS.IDEAL_CARTN_Y,
    ATOM_SITE_COLUMNS.CARTN_Z: CHEM_COMP_ATOM_COLUMNS.IDEAL_CARTN_Z,
}

CHEM_COMP_BOOLEAN_COLUMNS = {
    CHEM_COMP_ATOM_COLUMNS.LEAVING_FLAG,
    CHEM_COMP_ATOM_COLUMNS.BACKBONE_FLAG,
}


class Modification(StrEnum):
    Acetylation = "Acetyl"
    Citrullination = "Deamidation"
    Ubiquitination = "GlyGly"
    Methylation = "Methyl"
    Phosphorylation = "Phospho"


class Residue(StrEnum):
    Lysine = "K"
    Arginine = "R"
    Serine = "S"
    Threonine = "T"
    Tyrosine = "Y"


class KnownPTM(Enum):
    """
    Enum holding all PTM pairings currently supported by the PTM insertion into cif files.
    Allows for construction via
        KnownPTM.from_strings("Acetylation", "Lysine")
    and path retrieval through .get_cif_path() on a constructed member
    """

    ACETYLATION_LYSINE = (Modification.Acetylation, Residue.Lysine)
    CITRULLINATION_ARGININE = (Modification.Citrullination, Residue.Arginine)
    METHYLATION_ARGININE = (Modification.Methylation, Residue.Arginine)
    METHYLATION_LYSINE = (Modification.Methylation, Residue.Lysine)
    PHOSPHORYLATION_SERINE = (Modification.Phosphorylation, Residue.Serine)
    PHOSPHORYLATION_THREONINE = (Modification.Phosphorylation, Residue.Threonine)
    PHOSPHORYLATION_TYROSINE = (Modification.Phosphorylation, Residue.Tyrosine)
    UBIQUITINATION_LYSINE = (Modification.Ubiquitination, Residue.Lysine)

    @property
    def modification(self) -> Modification:
        return self.value[0]

    @property
    def residue(self) -> Residue:
        return self.value[1]

    @override
    def __str__(self) -> str:
        return f"{self.modification.name} on {self.residue.name}"

    @classmethod
    def to_options(cls) -> list[Option]:
        return [Option(member.name, str(member)) for member in cls]

    def get_cif_path(self) -> Path:
        """
        Retrieves the cif path of the PTM
        """
        mod, res = self.value
        path = (PTM_PATH / mod.name / res.name).with_suffix(".cif")
        return path

    @classmethod
    def from_strings(cls, modification: str, residue: str) -> "KnownPTM":
        """
        Factory method for known PTMs, by passing the modification and residue
        """
        try:
            return cls((Modification(modification), Residue(residue)))
        except ValueError:
            raise ValueError(
                f"There is currently no PTM data for {modification} on {residue}"
            )
