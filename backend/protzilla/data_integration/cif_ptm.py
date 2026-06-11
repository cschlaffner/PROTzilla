import logging
import re
from typing import cast

import pandas as pd
import gemmi

from backend.protzilla.data_analysis.crosslinking_validation import (
    _get_structure_entry_id,
)
from backend.protzilla.constants.cif_columns import (
    ATOM_SITE_COLUMNS,
    ATOM_SITE_COLUMNS_NUMERIC,
    BACKBONE_ATOMS,
    CHEM_COMP_BOOLEAN_COLUMNS,
    ATOM_SITE_TO_CHEM_COMP,
    CHEM_COMP_ATOM_COLUMNS,
    CHEM_COMP_ATOM_PREFIX,
    CHEM_COMP_COLUMNS,
    CIF_BOOL_MAP,
    KnownPTM,
)
from backend.protzilla.constants.data_types import DataKey
from backend.protzilla.constants.peptide_columns import (
    MODIFICATION_COLUMNS,
    PSM_DF_COLUMNS,
)
from backend.protzilla.data_analysis.crosslinking_validation import (
    get_residue_positions_in_protein,
    get_protein_sequence_from_df,
)
from backend.protzilla.steps import OutputItem, OutputType
from backend.protzilla.utilities.ptm_helpers import (
    clean_mod_list_of_numbers,
    extract_mods,
)


def parse_protein_ids(structure_metadata_df: pd.DataFrame) -> list[str]:
    """
    Parses a structure_metadata_df and returns a list of protein IDs
    """
    MONOMER_ID_COLUMN_NAME = "uniprot_accession"
    MULTIMER_ID_COLUMN_NAME = "uniprot_ids"

    is_monomer = MONOMER_ID_COLUMN_NAME in structure_metadata_df.columns

    ids: list[str] = (
        [structure_metadata_df.iloc[0][MONOMER_ID_COLUMN_NAME]]
        if is_monomer
        else re.findall(
            r"'(.+?)'",
            structure_metadata_df.reset_index(drop=True).loc[
                0, MULTIMER_ID_COLUMN_NAME
            ],
        )
    )

    return ids


def evidence_to_modifications(
    psm_df: pd.DataFrame, protein_sequences: dict[str, str]
) -> pd.DataFrame:
    """
    Parses a psm_df and returns a df containing all detected modifications
    """

    # filter evidence

    psm_df = psm_df[  # pyright: ignore[reportUnknownMemberType, reportAssignmentType]
        # only consider evidence rows with modifications
        (psm_df[PSM_DF_COLUMNS.MODIFICATIONS] != "Unmodified")
        #  and the protein ids from the metadata
        & (psm_df[PSM_DF_COLUMNS.PROTEIN_ID].isin(protein_sequences.keys()))
    ][
        # and ignore duplicates between different samples
        [
            PSM_DF_COLUMNS.SEQUENCE,
            PSM_DF_COLUMNS.MODIFICATIONS,
            PSM_DF_COLUMNS.MODIFIED_SEQUENCE,
            PSM_DF_COLUMNS.PROTEIN_ID,
        ]
    ].drop_duplicates(
        ignore_index=True
    )

    if psm_df.empty:
        return pd.DataFrame()

    # Create long dataframe with modification, location, residue from wide psm_df with modifications

    psm_df["mod_tuple"] = psm_df.apply(
        lambda row: [
            (
                mod,
                residue,
                # caution: position within protein is 1-indexed
                protein_location,
            )
            for mod, mod_locations in extract_mods(
                row[PSM_DF_COLUMNS.MODIFIED_SEQUENCE],
                clean_mod_list_of_numbers(row[PSM_DF_COLUMNS.MODIFICATIONS].split(",")),
            ).items()
            for peptide_location, residue in mod_locations
            for protein_location in get_residue_positions_in_protein(
                row[PSM_DF_COLUMNS.SEQUENCE],
                protein_sequences[row[PSM_DF_COLUMNS.PROTEIN_ID]],
                peptide_location - 1,
            )
        ],
        axis=1,
    )

    # turn each element of the list in the "mod_tuple" column into a new row
    modification_df = psm_df.explode("mod_tuple")

    # split the tuples into separate columns
    modification_df[
        [
            MODIFICATION_COLUMNS.MODIFICATION,
            MODIFICATION_COLUMNS.RESIDUE,
            MODIFICATION_COLUMNS.PROTEIN_LOCATION,
        ]
    ] = pd.DataFrame(modification_df["mod_tuple"].tolist(), index=modification_df.index)

    # only keep unique entries in respect to their protein ID/location combination
    modification_df = modification_df[
        [
            MODIFICATION_COLUMNS.PROTEIN_ID,
            MODIFICATION_COLUMNS.PROTEIN_LOCATION,
            MODIFICATION_COLUMNS.MODIFICATION,
            MODIFICATION_COLUMNS.RESIDUE,
        ]
    ].drop_duplicates(ignore_index=True)

    return modification_df


def _superpose_backbone_df(old_df: pd.DataFrame, new_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aligns the modified residue atoms onto the non-modified atoms' backbone
    """

    old_backbone = old_df[old_df[ATOM_SITE_COLUMNS.LABEL_ATOM_ID].isin(BACKBONE_ATOMS)]
    new_backbone = new_df[new_df[ATOM_SITE_COLUMNS.LABEL_ATOM_ID].isin(BACKBONE_ATOMS)]

    # Match backbone atoms by name
    merged = new_backbone.merge(
        old_backbone[
            [
                ATOM_SITE_COLUMNS.LABEL_ATOM_ID,
                ATOM_SITE_COLUMNS.CARTN_X,
                ATOM_SITE_COLUMNS.CARTN_Y,
                ATOM_SITE_COLUMNS.CARTN_Z,
            ]
        ],
        on=ATOM_SITE_COLUMNS.LABEL_ATOM_ID,
        suffixes=("_new", "_old"),
    )

    if len(merged) < 3:
        raise ValueError(
            f"Need ≥3 backbone atoms for superposition, found {len(merged)}"
        )

    # gemmi superposition
    old_pos = [
        gemmi.Position(
            row[ATOM_SITE_COLUMNS.CARTN_X + "_old"],
            row[ATOM_SITE_COLUMNS.CARTN_Y + "_old"],
            row[ATOM_SITE_COLUMNS.CARTN_Z + "_old"],
        )
        for _, row in merged.iterrows()
    ]
    new_pos = [
        gemmi.Position(
            row[ATOM_SITE_COLUMNS.CARTN_X + "_new"],
            row[ATOM_SITE_COLUMNS.CARTN_Y + "_new"],
            row[ATOM_SITE_COLUMNS.CARTN_Z + "_new"],
        )
        for _, row in merged.iterrows()
    ]

    transform = gemmi.superpose_positions(old_pos, new_pos).transform

    # Apply transform to all atoms in new residue
    for idx in new_df.index:
        pos = gemmi.Position(
            float(new_df.at[idx, ATOM_SITE_COLUMNS.CARTN_X]),
            float(new_df.at[idx, ATOM_SITE_COLUMNS.CARTN_Y]),
            float(new_df.at[idx, ATOM_SITE_COLUMNS.CARTN_Z]),
        )
        transformed = transform.apply(pos)
        new_df.at[idx, ATOM_SITE_COLUMNS.CARTN_X] = transformed.x
        new_df.at[idx, ATOM_SITE_COLUMNS.CARTN_Y] = transformed.y
        new_df.at[idx, ATOM_SITE_COLUMNS.CARTN_Z] = transformed.z

    return new_df


def load_ptm_df(ptm: KnownPTM) -> pd.DataFrame:
    """
    Load the cif file describing the PTM and return a cif_df containing only this residue
    """
    cif_path = ptm.get_cif_path()
    doc = gemmi.cif.read_file(str(cif_path))
    block = doc.sole_block()

    cat = block.find_mmcif_category(CHEM_COMP_ATOM_PREFIX)
    chem_comp_df = pd.DataFrame(
        list(cat),
        columns=list(cat.tags),
        dtype=pd.StringDtype(),
    )

    comp_id = block.find_value(CHEM_COMP_COLUMNS.ID)

    atom_site_df = pd.DataFrame(dtype=pd.StringDtype())

    # rename the columns according to the mapping between
    # the tables' labels
    for atom_col, chem_comp_col in ATOM_SITE_TO_CHEM_COMP.items():
        if chem_comp_col in CHEM_COMP_BOOLEAN_COLUMNS:
            # convert to native bool values
            atom_site_df[atom_col] = (
                chem_comp_df[chem_comp_col].map(CIF_BOOL_MAP).astype("boolean")
            )
        else:
            atom_site_df[atom_col] = chem_comp_df[chem_comp_col]

    atom_site_df[ATOM_SITE_COLUMNS.GROUP_PDB] = "HETATM"

    atom_site_df[ATOM_SITE_COLUMNS.LABEL_COMP_ID] = comp_id
    atom_site_df[ATOM_SITE_COLUMNS.AUTH_COMP_ID] = comp_id
    atom_site_df[ATOM_SITE_COLUMNS.LABEL_ALT_ID] = "."
    atom_site_df[ATOM_SITE_COLUMNS.OCCUPANCY] = 1.0
    atom_site_df[ATOM_SITE_COLUMNS.B_ISO_OR_EQUIV] = pd.NA
    atom_site_df[CHEM_COMP_COLUMNS.MON_NSTD_FLAG] = False

    # required column for deciding what to keep in the calling context
    atom_site_df["_leaving_flag"] = chem_comp_df[CHEM_COMP_ATOM_COLUMNS.LEAVING_FLAG]

    # convert numeric columns
    numeric = [c for c in ATOM_SITE_COLUMNS_NUMERIC if c in atom_site_df.columns]
    atom_site_df[numeric] = atom_site_df[numeric].apply(pd.to_numeric, errors="coerce")

    return atom_site_df.convert_dtypes()


def replace_residue_with_ptm(
    cif_df: pd.DataFrame, index: int, ptm: KnownPTM, entity_id: int
) -> pd.DataFrame:
    """
    Replaces the residue at a specific location with a modified residue

    :param cif_df: The cif_df to modify
    :param index: The 1-based index in the protein of the resiude to change
    :param ptm: The KnownPTM member whose structure will replace the old residue
    :returns: The modified cif_df
    """

    # select the correct index of the correct entity
    residue_mask = (cif_df[ATOM_SITE_COLUMNS.AUTH_SEQ_ID] == index) & (
        cif_df[ATOM_SITE_COLUMNS.LABEL_ENTITY_ID] == entity_id
    )
    old_residue_df = cif_df[residue_mask].reset_index(drop=True)
    unchanged_rows = cif_df[~residue_mask]
    cut_idx = residue_mask.to_numpy().nonzero()[0][0]

    modified_residue_df = load_ptm_df(ptm)

    # Depending on whether the residue is at either terminal of the chain,
    # we want to keep the terminal atoms that are only present at the N- and C-terminal
    old_atom_names = set(old_residue_df[ATOM_SITE_COLUMNS.LABEL_ATOM_ID])
    is_leaving = modified_residue_df["_leaving_flag"] == True
    is_in_old = modified_residue_df[ATOM_SITE_COLUMNS.LABEL_ATOM_ID].isin(
        old_atom_names
    )
    modified_residue_df = modified_residue_df[~is_leaving | is_in_old]

    # Align on backbone
    modified_residue_df = _superpose_backbone_df(old_residue_df, modified_residue_df)

    # Keep non-changing columns the same
    for col in [
        ATOM_SITE_COLUMNS.AUTH_SEQ_ID,
        ATOM_SITE_COLUMNS.LABEL_SEQ_ID,
        ATOM_SITE_COLUMNS.LABEL_ASYM_ID,
        ATOM_SITE_COLUMNS.AUTH_ASYM_ID,
        ATOM_SITE_COLUMNS.LABEL_ENTITY_ID,
        ATOM_SITE_COLUMNS.PDBX_PDB_INS_CODE,
        ATOM_SITE_COLUMNS.PDBX_PDB_MODEL_NUM,
    ]:
        if col in old_residue_df.columns:
            modified_residue_df[col] = old_residue_df[col].iloc[0]

    # Reindex to match original columns
    modified_residue_df = modified_residue_df.reindex(columns=cif_df.columns)

    # Stitch the rows back together
    result = pd.concat(
        [
            unchanged_rows.iloc[:cut_idx],
            modified_residue_df,
            unchanged_rows.iloc[cut_idx:],
        ],
        ignore_index=True,
    )

    result[ATOM_SITE_COLUMNS.ID] = range(1, len(result) + 1)

    return result


def add_ptms_from_evidence_to_cif(
    structure_metadata_df: pd.DataFrame,
    cif_df: pd.DataFrame,
    psm_df: pd.DataFrame,
    amino_acid_sequences_df: pd.DataFrame,
    selected_ptm_names: list[str],
) -> dict[str, pd.DataFrame | OutputItem | list[dict[str, str | int]]]:
    """
    Integrates PTMs from peptide-spectrum match (PSM) evidence into a CIF model

    Parses modification evidence, maps each modification to its location
    within the protein loads the corresponding modified residue, and replaces
    the appropriate amino acid in the ``cif_df``.
    """

    if not selected_ptm_names:
        return {
            "messages": [
                {
                    "level": logging.ERROR,
                    "msg": "At least one type of PTM has to be selected",
                }
            ]
        }

    # convert PTMs from names to enum members
    selected_ptms = {KnownPTM[name] for name in selected_ptm_names}

    # parse protein id(s) from structure metadata
    ids = parse_protein_ids(structure_metadata_df)

    if not ids:
        return {
            "messages": [
                {
                    "level": logging.ERROR,
                    "msg": "There were no protein IDs in the supplied structure_metadata_df",
                }
            ]
        }

    protein_sequences = {
        protein_id: get_protein_sequence_from_df(amino_acid_sequences_df, protein_id)
        for protein_id in ids
    }

    # Map protein IDs to their label_entity_id in the cif_df
    # order corresponds to the order in the fasta
    protein_to_entity: dict[str, int] = {}
    for i, protein_id in enumerate(amino_acid_sequences_df["Protein ID"]):
        # normalize without isoform suffix
        protein_id = re.match(r"(\w+)-\d+", protein_id).group(1)
        protein_to_entity[protein_id] = i + 1

    modification_df = evidence_to_modifications(psm_df, protein_sequences)

    unknown_ptms = set[tuple[str, str]]()
    modification_counter = 0
    for _, row in modification_df.iterrows():
        protein_id, location, modification, residue = row
        entity_id = protein_to_entity[protein_id]
        try:
            ptm = KnownPTM.from_strings(modification, residue)
        except ValueError:
            unknown_ptms.add((modification, residue))
            continue
        if ptm in selected_ptms:
            cif_df = replace_residue_with_ptm(cif_df, location, ptm, entity_id)
            modification_counter += 1

    data_for_visualization = {
        "structure_entry_id": _get_structure_entry_id(structure_metadata_df),
        DataKey.CIF_DF: cif_df,
    }

    messages = [
        {
            "level": logging.INFO,
            "msg": f"{modification_counter} PTMs have been inserted into the cif_df",
        },
    ]
    if unknown_ptms:
        messages.append(
            {
                "level": logging.WARNING,
                "msg": f"The following unknown PTMs were encountered:\n{', '.join(f'{mod} on {res}' for mod, res in unknown_ptms)}",
            }
        )

    return {
        DataKey.MODIFICATION_DF.value: modification_df,
        DataKey.CIF_DF.value: cif_df,
        "visualization": OutputItem(OutputType.VISUALIZATION, data_for_visualization),
        "messages": messages,
    }
