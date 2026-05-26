import gemmi
import pandas as pd
from enum import StrEnum

from backend.protzilla.constants.paths import PTM_PATH


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


class KnownPTM(StrEnum):
    """
    Enum holding all PTM pairings currently supported by the PTM insertion into cif files.
    Allows for construction via
        KnownPTM.from_strings("Acetylation", "Lysine")
    and path retrieval through .get_cif() on a constructed member
    """

    ACETYLATION_LYSINE = "Acetylation/Lysine"
    CITRULLINATION_ARGININE = "Citrullination/Arginine"
    METHYLATION_ARGININE = "Methylation/Arginine"
    METHYLATION_LYSINE = "Methylation/Lysine"
    PHOSPHORYLATION_SERINE = "Phosphorylation/Serine"
    PHOSPHORYLATION_THREONINE = "Phosphorylation/Threonine"
    PHOSPHORYLATION_TYROSINE = "Phosphorylation/Tyrosine"
    UBIQUITINATION_LYSINE = "Ubiquitination/Lysine"

    def get_cif(self) -> pd.DataFrame:
        """
        Retrieves the cif_df of the PTM
        """
        path = (PTM_PATH / self.value).with_suffix(".cif")

        doc = gemmi.cif.read_file(str(path))

        if len(doc) == 0:
            raise ValueError(f"No CIF blocks found in file: {path}")

        block = doc.sole_block()

        if ATOM_SITE_PREFIX not in block.get_mmcif_category_names():
            return pd.DataFrame()

        atom_site_table = block.find_mmcif_category(ATOM_SITE_PREFIX)

        atom_site_df = pd.DataFrame(
            list(atom_site_table),
            columns=list(atom_site_table.tags),
            dtype=pd.StringDtype(),
        )

        # convert to numeric dtype for numeric columns present in the dataframe
        present_numeric_columns = [
            column for column in ATOM_SITE_COLUMNS_NUMERIC if column in atom_site_table.tags
        ]
        atom_site_df[present_numeric_columns] = atom_site_df[present_numeric_columns].apply(
            pd.to_numeric, errors="coerce"
        )

        atom_site_df = atom_site_df.convert_dtypes()

        return atom_site_df

    @classmethod
    def from_strings(cls, modification: str, residue: str) -> "KnownPTM":
        """
        Factory method for known PTMs, by passing the modification and residue
        """
        try:
            return cls(f"{modification}/{residue}")
        except ValueError:
            raise ValueError(
                f"There is currently no PTM data for {modification} on {residue}"
            )
