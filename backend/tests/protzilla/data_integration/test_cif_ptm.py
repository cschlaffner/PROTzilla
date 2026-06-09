import gemmi
import logging
import pandas as pd
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from backend.protzilla.constants.cif_columns import (
    ATOM_SITE_COLUMNS,
    ATOM_SITE_COLUMNS_NUMERIC,
    BACKBONE_ATOMS,
    CHEM_COMP_ATOM_COLUMNS,
    CHEM_COMP_ATOM_PREFIX,
    CHEM_COMP_BOOLEAN_COLUMNS,
    ATOM_SITE_TO_CHEM_COMP,
    CHEM_COMP_COLUMNS,
    CIF_BOOL_MAP,
    KnownPTM,
    Modification,
)
from backend.protzilla.constants.data_types import DataKey
from backend.protzilla.constants.peptide_columns import (
    MODIFICATION_COLUMNS,
    PSM_DF_COLUMNS,
)
from backend.protzilla.data_integration.cif_ptm import (
    _superpose_backbone_df,
    add_ptms_from_evidence_to_cif,
    evidence_to_modifications,
    load_ptm_df,
    parse_protein_ids,
    replace_residue_with_ptm,
)
from backend.protzilla.constants import paths


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_cif_df(rows: list[dict]) -> pd.DataFrame:
    """Build a minimal cif_df from a list of row dicts."""
    records = []
    for r in rows:
        records.append(
            {
                ATOM_SITE_COLUMNS.ID: r.get("atom_id"),
                ATOM_SITE_COLUMNS.TYPE_SYMBOL: r.get("type_symbol"),
                ATOM_SITE_COLUMNS.LABEL_ATOM_ID: r.get("label_atom_id"),
                ATOM_SITE_COLUMNS.LABEL_ALT_ID: ".",
                ATOM_SITE_COLUMNS.LABEL_COMP_ID: r.get("label_comp_id"),
                ATOM_SITE_COLUMNS.AUTH_COMP_ID: r.get("label_comp_id"),
                ATOM_SITE_COLUMNS.LABEL_ASYM_ID: "A",
                ATOM_SITE_COLUMNS.AUTH_ASYM_ID: "A",
                ATOM_SITE_COLUMNS.LABEL_ENTITY_ID: r.get("label_entity_id", 1),
                ATOM_SITE_COLUMNS.LABEL_SEQ_ID: r.get("auth_seq_id"),
                ATOM_SITE_COLUMNS.AUTH_SEQ_ID: r.get("auth_seq_id"),
                ATOM_SITE_COLUMNS.PDBX_PDB_INS_CODE: "",
                ATOM_SITE_COLUMNS.CARTN_X: r.get("cartn_x", 0.0),
                ATOM_SITE_COLUMNS.CARTN_Y: r.get("cartn_y", 0.0),
                ATOM_SITE_COLUMNS.CARTN_Z: r.get("cartn_z", 0.0),
                ATOM_SITE_COLUMNS.OCCUPANCY: 1.0,
                ATOM_SITE_COLUMNS.B_ISO_OR_EQUIV: pd.NA,
                ATOM_SITE_COLUMNS.GROUP_PDB: "ATOM",
                ATOM_SITE_COLUMNS.PDBX_FORMAL_CHARGE: r.get("charge", 0),
                ATOM_SITE_COLUMNS.PDBX_PDB_MODEL_NUM: "1",
            }
        )
    df = pd.DataFrame(records)

    # Convert numeric columns to numeric dtype (matches real cif_df)
    numeric = [c for c in ATOM_SITE_COLUMNS_NUMERIC if c in df.columns]
    df[numeric] = df[numeric].apply(pd.to_numeric, errors="coerce")
    return df.convert_dtypes()


def _make_ptm_cif_df(
    rows: list[dict], leaving_flags: list[bool] | None = None
) -> pd.DataFrame:
    """Build a minimal PTM cif_df (as returned by load_ptm_df).

    Includes the internal _leaving_flag column as boolean.
    """
    records = []
    for i, r in enumerate(rows):
        records.append(
            {
                ATOM_SITE_COLUMNS.TYPE_SYMBOL: r.get("type_symbol"),
                ATOM_SITE_COLUMNS.LABEL_ATOM_ID: r.get("label_atom_id"),
                ATOM_SITE_COLUMNS.LABEL_ALT_ID: ".",
                ATOM_SITE_COLUMNS.LABEL_COMP_ID: r.get("label_comp_id"),
                ATOM_SITE_COLUMNS.AUTH_COMP_ID: r.get("label_comp_id"),
                ATOM_SITE_COLUMNS.GROUP_PDB: "HETATM",
                ATOM_SITE_COLUMNS.PDBX_FORMAL_CHARGE: r.get("charge", 0),
                ATOM_SITE_COLUMNS.CARTN_X: r.get("cartn_x", 0.0),
                ATOM_SITE_COLUMNS.CARTN_Y: r.get("cartn_y", 0.0),
                ATOM_SITE_COLUMNS.CARTN_Z: r.get("cartn_z", 0.0),
                ATOM_SITE_COLUMNS.OCCUPANCY: 1.0,
                ATOM_SITE_COLUMNS.B_ISO_OR_EQUIV: pd.NA,
                "_leaving_flag": leaving_flags[i] if leaving_flags else False,
            }
        )
    df = pd.DataFrame(records)

    # Convert numeric columns
    numeric = [c for c in ATOM_SITE_COLUMNS_NUMERIC if c in df.columns]
    df[numeric] = df[numeric].apply(pd.to_numeric, errors="coerce")
    return df.convert_dtypes()


# ---------------------------------------------------------------------------
# KnownPTM enum tests
# ---------------------------------------------------------------------------


class TestKnownPTM:
    def test_known_ptm_members_exist(self):
        assert KnownPTM.ACETYLATION_LYSINE is not None
        assert KnownPTM.PHOSPHORYLATION_SERINE is not None

    def test_known_ptm_from_strings_valid(self):
        ptm = KnownPTM.from_strings("Acetyl", "K")
        assert ptm == KnownPTM.ACETYLATION_LYSINE

    def test_known_ptm_from_strings_invalid(self):
        with pytest.raises(ValueError):
            KnownPTM.from_strings("Nonexistent", "K")

    def test_known_ptm_cif_path(self):
        ptm = KnownPTM.ACETYLATION_LYSINE
        result = ptm.get_cif_path()
        assert result.name == "Lysine.cif"
        # Parent directory should reference the modification type
        assert "Acetyl" in str(result) or "Acetylation" in str(result)

    def test_known_ptm_reconstructible_from_name(self):
        """Enum should be reconstructible from its .name string for frontend round-tripping."""
        ptm = KnownPTM.ACETYLATION_LYSINE
        reconstructed = KnownPTM[ptm.name]
        assert reconstructed is ptm

    def test_modification_enum_values(self):
        assert Modification.Acetylation.value == "Acetyl"
        assert Modification.Phosphorylation.value == "Phospho"


# ---------------------------------------------------------------------------
# parse_protein_ids tests
# ---------------------------------------------------------------------------


class TestParseProteinIDs:
    def test_monomer(self):
        metadata_df = pd.DataFrame([{"uniprot_accession": "P12345"}])
        assert parse_protein_ids(metadata_df) == ["P12345"]

    def test_multimer(self):
        metadata_df = pd.DataFrame([{"uniprot_ids": "['P1', 'P2']"}])
        assert parse_protein_ids(metadata_df) == ["P1", "P2"]

    def test_multimer_single(self):
        metadata_df = pd.DataFrame([{"uniprot_ids": "['P1']"}])
        assert parse_protein_ids(metadata_df) == ["P1"]


# ---------------------------------------------------------------------------
# _superpose_backbone_df tests
# ---------------------------------------------------------------------------


class TestSuperposeBackbone:
    def test_superpose_backbone_df_preserves_backbone(self):
        """After superposition, backbone atoms of the new residue should
        align with the old residue's backbone atoms."""
        # Consistent backbone geometry: atoms along x-axis with O offset in y
        old_df = _make_cif_df(
            [
                {
                    "atom_id": 1,
                    "type_symbol": "N",
                    "label_atom_id": "N",
                    "label_comp_id": "SER",
                    "auth_seq_id": 5,
                    "label_entity_id": 1,
                    "cartn_x": 10.0,
                    "cartn_y": 20.0,
                    "cartn_z": 30.0,
                },
                {
                    "atom_id": 2,
                    "type_symbol": "C",
                    "label_atom_id": "CA",
                    "label_comp_id": "SER",
                    "auth_seq_id": 5,
                    "label_entity_id": 1,
                    "cartn_x": 11.0,
                    "cartn_y": 20.0,
                    "cartn_z": 30.0,
                },
                {
                    "atom_id": 3,
                    "type_symbol": "C",
                    "label_atom_id": "C",
                    "label_comp_id": "SER",
                    "auth_seq_id": 5,
                    "label_entity_id": 1,
                    "cartn_x": 12.0,
                    "cartn_y": 20.0,
                    "cartn_z": 30.0,
                },
                {
                    "atom_id": 4,
                    "type_symbol": "O",
                    "label_atom_id": "O",
                    "label_comp_id": "SER",
                    "auth_seq_id": 5,
                    "label_entity_id": 1,
                    "cartn_x": 12.5,
                    "cartn_y": 21.0,
                    "cartn_z": 30.0,
                },
            ]
        )

        # New residue: same backbone geometry, just translated to origin
        new_df = _make_cif_df(
            [
                {
                    "atom_id": 1,
                    "type_symbol": "N",
                    "label_atom_id": "N",
                    "label_comp_id": "SEP",
                    "auth_seq_id": 5,
                    "label_entity_id": 1,
                    "cartn_x": 0.0,
                    "cartn_y": 0.0,
                    "cartn_z": 0.0,
                },
                {
                    "atom_id": 2,
                    "type_symbol": "C",
                    "label_atom_id": "CA",
                    "label_comp_id": "SEP",
                    "auth_seq_id": 5,
                    "label_entity_id": 1,
                    "cartn_x": 1.0,
                    "cartn_y": 0.0,
                    "cartn_z": 0.0,
                },
                {
                    "atom_id": 3,
                    "type_symbol": "C",
                    "label_atom_id": "C",
                    "label_comp_id": "SEP",
                    "auth_seq_id": 5,
                    "label_entity_id": 1,
                    "cartn_x": 2.0,
                    "cartn_y": 0.0,
                    "cartn_z": 0.0,
                },
                {
                    "atom_id": 4,
                    "type_symbol": "O",
                    "label_atom_id": "O",
                    "label_comp_id": "SEP",
                    "auth_seq_id": 5,
                    "label_entity_id": 1,
                    "cartn_x": 2.5,
                    "cartn_y": 1.0,
                    "cartn_z": 0.0,
                },
                {
                    "atom_id": 5,
                    "type_symbol": "P",
                    "label_atom_id": "P",
                    "label_comp_id": "SEP",
                    "auth_seq_id": 5,
                    "label_entity_id": 1,
                    "cartn_x": -1.0,
                    "cartn_y": 0.0,
                    "cartn_z": 0.0,
                },
            ]
        )

        result = _superpose_backbone_df(old_df, new_df)

        # Backbone atoms should now be close to old positions
        for backbone_atom in ["N", "CA", "C", "O"]:
            old_row = old_df[
                old_df[ATOM_SITE_COLUMNS.LABEL_ATOM_ID] == backbone_atom
            ].iloc[0]
            new_row = result[
                result[ATOM_SITE_COLUMNS.LABEL_ATOM_ID] == backbone_atom
            ].iloc[0]
            for coord in [
                ATOM_SITE_COLUMNS.CARTN_X,
                ATOM_SITE_COLUMNS.CARTN_Y,
                ATOM_SITE_COLUMNS.CARTN_Z,
            ]:
                assert abs(float(new_row[coord]) - float(old_row[coord])) < 1e-3

    def test_superpose_backbone_df_insufficient_atoms(self):
        """Should raise ValueError with < 3 backbone atoms."""
        old_df = _make_cif_df(
            [
                {
                    "atom_id": 1,
                    "type_symbol": "N",
                    "label_atom_id": "N",
                    "label_comp_id": "SER",
                    "auth_seq_id": 5,
                    "label_entity_id": 1,
                    "cartn_x": 0.0,
                    "cartn_y": 0.0,
                    "cartn_z": 0.0,
                },
                {
                    "atom_id": 2,
                    "type_symbol": "C",
                    "label_atom_id": "CA",
                    "label_comp_id": "SER",
                    "auth_seq_id": 5,
                    "label_entity_id": 1,
                    "cartn_x": 1.0,
                    "cartn_y": 0.0,
                    "cartn_z": 0.0,
                },
            ]
        )
        new_df = _make_cif_df(
            [
                {
                    "atom_id": 1,
                    "type_symbol": "N",
                    "label_atom_id": "N",
                    "label_comp_id": "SEP",
                    "auth_seq_id": 5,
                    "label_entity_id": 1,
                    "cartn_x": 0.0,
                    "cartn_y": 0.0,
                    "cartn_z": 0.0,
                },
            ]
        )

        with pytest.raises(ValueError, match="Need ≥3 backbone atoms"):
            _superpose_backbone_df(old_df, new_df)


# ---------------------------------------------------------------------------
# replace_residue_with_ptm tests
# ---------------------------------------------------------------------------


class TestReplaceResidueWithPTM:
    @pytest.fixture
    def _mock_load_ptm_df(self):
        """Mock load_ptm_df to return a phosphoserine-like residue."""
        ptm_df = _make_ptm_cif_df(
            [
                {
                    "type_symbol": "N",
                    "label_atom_id": "N",
                    "label_comp_id": "SEP",
                    "cartn_x": 0.0,
                    "cartn_y": 0.0,
                    "cartn_z": 0.0,
                },
                {
                    "type_symbol": "C",
                    "label_atom_id": "CA",
                    "label_comp_id": "SEP",
                    "cartn_x": 1.0,
                    "cartn_y": 0.0,
                    "cartn_z": 0.0,
                },
                {
                    "type_symbol": "C",
                    "label_atom_id": "C",
                    "label_comp_id": "SEP",
                    "cartn_x": 2.0,
                    "cartn_y": 0.0,
                    "cartn_z": 0.0,
                },
                {
                    "type_symbol": "O",
                    "label_atom_id": "O",
                    "label_comp_id": "SEP",
                    "cartn_x": 2.5,
                    "cartn_y": 1.0,
                    "cartn_z": 0.0,
                },
                {
                    "type_symbol": "C",
                    "label_atom_id": "CB",
                    "label_comp_id": "SEP",
                    "cartn_x": 0.5,
                    "cartn_y": -1.0,
                    "cartn_z": 0.0,
                },
                {
                    "type_symbol": "P",
                    "label_atom_id": "P",
                    "label_comp_id": "SEP",
                    "cartn_x": -1.0,
                    "cartn_y": -1.0,
                    "cartn_z": 0.0,
                },
            ],
            leaving_flags=[False, False, False, False, False, False],
        )
        return ptm_df

    def test_replace_residue_with_ptm_mid_chain(self, _mock_load_ptm_df):
        """Replacing a mid-chain residue should swap atoms and keep neighbours."""
        cif_df = _make_cif_df(
            [
                # Residue 4 (before target)
                {
                    "atom_id": 1,
                    "type_symbol": "N",
                    "label_atom_id": "N",
                    "label_comp_id": "ALA",
                    "auth_seq_id": 4,
                    "label_entity_id": 1,
                    "cartn_x": 7.0,
                    "cartn_y": 20.0,
                    "cartn_z": 30.0,
                },
                # Residue 5 (target) — consistent backbone geometry
                {
                    "atom_id": 2,
                    "type_symbol": "N",
                    "label_atom_id": "N",
                    "label_comp_id": "SER",
                    "auth_seq_id": 5,
                    "label_entity_id": 1,
                    "cartn_x": 10.0,
                    "cartn_y": 20.0,
                    "cartn_z": 30.0,
                },
                {
                    "atom_id": 3,
                    "type_symbol": "C",
                    "label_atom_id": "CA",
                    "label_comp_id": "SER",
                    "auth_seq_id": 5,
                    "label_entity_id": 1,
                    "cartn_x": 11.0,
                    "cartn_y": 20.0,
                    "cartn_z": 30.0,
                },
                {
                    "atom_id": 4,
                    "type_symbol": "C",
                    "label_atom_id": "C",
                    "label_comp_id": "SER",
                    "auth_seq_id": 5,
                    "label_entity_id": 1,
                    "cartn_x": 12.0,
                    "cartn_y": 20.0,
                    "cartn_z": 30.0,
                },
                {
                    "atom_id": 5,
                    "type_symbol": "O",
                    "label_atom_id": "O",
                    "label_comp_id": "SER",
                    "auth_seq_id": 5,
                    "label_entity_id": 1,
                    "cartn_x": 12.5,
                    "cartn_y": 21.0,
                    "cartn_z": 30.0,
                },
                {
                    "atom_id": 6,
                    "type_symbol": "C",
                    "label_atom_id": "CB",
                    "label_comp_id": "SER",
                    "auth_seq_id": 5,
                    "label_entity_id": 1,
                    "cartn_x": 10.5,
                    "cartn_y": 19.0,
                    "cartn_z": 30.0,
                },
                # Residue 6 (after target)
                {
                    "atom_id": 7,
                    "type_symbol": "N",
                    "label_atom_id": "N",
                    "label_comp_id": "GLY",
                    "auth_seq_id": 6,
                    "label_entity_id": 1,
                    "cartn_x": 13.0,
                    "cartn_y": 20.0,
                    "cartn_z": 30.0,
                },
            ]
        )

        with patch(
            "backend.protzilla.data_integration.cif_ptm.load_ptm_df",
            return_value=_mock_load_ptm_df,
        ):
            result = replace_residue_with_ptm(
                cif_df, 5, KnownPTM.PHOSPHORYLATION_SERINE, entity_id=1
            )

        # Unchanged residues should still be present
        assert 4 in result[ATOM_SITE_COLUMNS.AUTH_SEQ_ID].tolist()
        assert 6 in result[ATOM_SITE_COLUMNS.AUTH_SEQ_ID].tolist()

        # Atom IDs should be sequential
        assert result[ATOM_SITE_COLUMNS.ID].tolist() == list(range(1, len(result) + 1))

        # Modified residue should have HETATM group
        modified_rows = result[result[ATOM_SITE_COLUMNS.AUTH_SEQ_ID] == 5]
        assert all(modified_rows[ATOM_SITE_COLUMNS.GROUP_PDB] == "HETATM")

        # Modified residue should have SEP as comp_id
        assert all(modified_rows[ATOM_SITE_COLUMNS.LABEL_COMP_ID] == "SEP")

    def test_replace_residue_with_ptm_c_terminal(self, _mock_load_ptm_df):
        """Replacing a C-terminal residue should keep terminal atoms."""
        cif_df = _make_cif_df(
            [
                # Residue 4 (before target)
                {
                    "atom_id": 1,
                    "type_symbol": "N",
                    "label_atom_id": "N",
                    "label_comp_id": "ALA",
                    "auth_seq_id": 4,
                    "label_entity_id": 1,
                    "cartn_x": 7.0,
                    "cartn_y": 20.0,
                    "cartn_z": 30.0,
                },
                # Residue 5 (C-terminal target) — consistent backbone geometry
                {
                    "atom_id": 2,
                    "type_symbol": "N",
                    "label_atom_id": "N",
                    "label_comp_id": "SER",
                    "auth_seq_id": 5,
                    "label_entity_id": 1,
                    "cartn_x": 10.0,
                    "cartn_y": 20.0,
                    "cartn_z": 30.0,
                },
                {
                    "atom_id": 3,
                    "type_symbol": "C",
                    "label_atom_id": "CA",
                    "label_comp_id": "SER",
                    "auth_seq_id": 5,
                    "label_entity_id": 1,
                    "cartn_x": 11.0,
                    "cartn_y": 20.0,
                    "cartn_z": 30.0,
                },
                {
                    "atom_id": 4,
                    "type_symbol": "C",
                    "label_atom_id": "C",
                    "label_comp_id": "SER",
                    "auth_seq_id": 5,
                    "label_entity_id": 1,
                    "cartn_x": 12.0,
                    "cartn_y": 20.0,
                    "cartn_z": 30.0,
                },
                {
                    "atom_id": 5,
                    "type_symbol": "O",
                    "label_atom_id": "O",
                    "label_comp_id": "SER",
                    "auth_seq_id": 5,
                    "label_entity_id": 1,
                    "cartn_x": 12.5,
                    "cartn_y": 21.0,
                    "cartn_z": 30.0,
                },
                {
                    "atom_id": 6,
                    "type_symbol": "C",
                    "label_atom_id": "CB",
                    "label_comp_id": "SER",
                    "auth_seq_id": 5,
                    "label_entity_id": 1,
                    "cartn_x": 10.5,
                    "cartn_y": 19.0,
                    "cartn_z": 30.0,
                },
            ]
        )

        with patch(
            "backend.protzilla.data_integration.cif_ptm.load_ptm_df",
            return_value=_mock_load_ptm_df,
        ):
            result = replace_residue_with_ptm(
                cif_df, 5, KnownPTM.PHOSPHORYLATION_SERINE, entity_id=1
            )

        # Atom IDs should be sequential
        assert result[ATOM_SITE_COLUMNS.ID].tolist() == list(range(1, len(result) + 1))

        # Modified residue should have SEP comp_id
        modified_rows = result[result[ATOM_SITE_COLUMNS.AUTH_SEQ_ID] == 5]
        assert all(modified_rows[ATOM_SITE_COLUMNS.LABEL_COMP_ID] == "SEP")

    def test_replace_residue_with_ptm_entity_scoping(self, _mock_load_ptm_df):
        """Only the residue in the specified entity should be replaced."""
        cif_df = _make_cif_df(
            [
                # Entity 1, residue 5 — consistent backbone geometry
                {
                    "atom_id": 1,
                    "type_symbol": "N",
                    "label_atom_id": "N",
                    "label_comp_id": "SER",
                    "auth_seq_id": 5,
                    "label_entity_id": 1,
                    "cartn_x": 10.0,
                    "cartn_y": 20.0,
                    "cartn_z": 30.0,
                },
                {
                    "atom_id": 2,
                    "type_symbol": "C",
                    "label_atom_id": "CA",
                    "label_comp_id": "SER",
                    "auth_seq_id": 5,
                    "label_entity_id": 1,
                    "cartn_x": 11.0,
                    "cartn_y": 20.0,
                    "cartn_z": 30.0,
                },
                {
                    "atom_id": 3,
                    "type_symbol": "C",
                    "label_atom_id": "C",
                    "label_comp_id": "SER",
                    "auth_seq_id": 5,
                    "label_entity_id": 1,
                    "cartn_x": 12.0,
                    "cartn_y": 20.0,
                    "cartn_z": 30.0,
                },
                {
                    "atom_id": 4,
                    "type_symbol": "O",
                    "label_atom_id": "O",
                    "label_comp_id": "SER",
                    "auth_seq_id": 5,
                    "label_entity_id": 1,
                    "cartn_x": 12.5,
                    "cartn_y": 21.0,
                    "cartn_z": 30.0,
                },
                # Entity 2, same seq_id 5 — consistent backbone geometry, should NOT be replaced
                {
                    "atom_id": 5,
                    "type_symbol": "N",
                    "label_atom_id": "N",
                    "label_comp_id": "SER",
                    "auth_seq_id": 5,
                    "label_entity_id": 2,
                    "cartn_x": 50.0,
                    "cartn_y": 60.0,
                    "cartn_z": 70.0,
                },
                {
                    "atom_id": 6,
                    "type_symbol": "C",
                    "label_atom_id": "CA",
                    "label_comp_id": "SER",
                    "auth_seq_id": 5,
                    "label_entity_id": 2,
                    "cartn_x": 51.0,
                    "cartn_y": 60.0,
                    "cartn_z": 70.0,
                },
                {
                    "atom_id": 7,
                    "type_symbol": "C",
                    "label_atom_id": "C",
                    "label_comp_id": "SER",
                    "auth_seq_id": 5,
                    "label_entity_id": 2,
                    "cartn_x": 52.0,
                    "cartn_y": 60.0,
                    "cartn_z": 70.0,
                },
                {
                    "atom_id": 8,
                    "type_symbol": "O",
                    "label_atom_id": "O",
                    "label_comp_id": "SER",
                    "auth_seq_id": 5,
                    "label_entity_id": 2,
                    "cartn_x": 52.5,
                    "cartn_y": 61.0,
                    "cartn_z": 70.0,
                },
            ]
        )

        with patch(
            "backend.protzilla.data_integration.cif_ptm.load_ptm_df",
            return_value=_mock_load_ptm_df,
        ):
            result = replace_residue_with_ptm(
                cif_df, 5, KnownPTM.PHOSPHORYLATION_SERINE, entity_id=1
            )

        # Entity 2 residue should be unchanged
        entity2_rows = result[result[ATOM_SITE_COLUMNS.LABEL_ENTITY_ID] == 2]
        assert len(entity2_rows) == 4
        assert all(entity2_rows[ATOM_SITE_COLUMNS.LABEL_COMP_ID] == "SER")
        assert all(entity2_rows[ATOM_SITE_COLUMNS.GROUP_PDB] == "ATOM")

        # Entity 1 residue should be modified
        entity1_modified = result[
            (result[ATOM_SITE_COLUMNS.LABEL_ENTITY_ID] == 1)
            & (result[ATOM_SITE_COLUMNS.AUTH_SEQ_ID] == 5)
        ]
        assert all(entity1_modified[ATOM_SITE_COLUMNS.LABEL_COMP_ID] == "SEP")
        assert all(entity1_modified[ATOM_SITE_COLUMNS.GROUP_PDB] == "HETATM")


# ---------------------------------------------------------------------------
# evidence_to_modifications tests
# ---------------------------------------------------------------------------


class TestEvidenceToModifications:
    def test_evidence_to_modifications_extracts_ptms(self):
        protein_sequences = {"P1": "MSERK"}

        psm_df = pd.DataFrame(
            [
                {
                    PSM_DF_COLUMNS.SEQUENCE: "SERK",
                    PSM_DF_COLUMNS.MODIFICATIONS: "Phospho (S)",
                    PSM_DF_COLUMNS.MODIFIED_SEQUENCE: "_(Phospho (S))SERK_",
                    PSM_DF_COLUMNS.PROTEIN_ID: "P1",
                }
            ]
        )

        result = evidence_to_modifications(psm_df, protein_sequences)

        assert not result.empty
        assert MODIFICATION_COLUMNS.MODIFICATION in result.columns
        assert MODIFICATION_COLUMNS.PROTEIN_LOCATION in result.columns

    def test_evidence_to_modifications_filters_unmodified(self):
        protein_sequences = {"P1": "AAAAK"}

        # Include at least one modified row so the DataFrame isn't empty
        # after filtering (empty DF apply fails with column assignment)
        psm_df = pd.DataFrame(
            [
                {
                    PSM_DF_COLUMNS.SEQUENCE: "AAAK",
                    PSM_DF_COLUMNS.MODIFICATIONS: "Acetyl (K)",
                    PSM_DF_COLUMNS.MODIFIED_SEQUENCE: "_(Acetyl (K))AAAK_",
                    PSM_DF_COLUMNS.PROTEIN_ID: "P1",
                },
                {
                    PSM_DF_COLUMNS.SEQUENCE: "AAAAK",
                    PSM_DF_COLUMNS.MODIFICATIONS: "Unmodified",
                    PSM_DF_COLUMNS.MODIFIED_SEQUENCE: "AAAAK",
                    PSM_DF_COLUMNS.PROTEIN_ID: "P1",
                },
            ]
        )

        result = evidence_to_modifications(psm_df, protein_sequences)
        # Unmodified rows should be filtered out, only the acetylation remains
        assert len(result) == 1
        assert result.iloc[0][MODIFICATION_COLUMNS.MODIFICATION] == "Acetyl"


# ---------------------------------------------------------------------------
# add_ptms_from_evidence_to_cif tests
# ---------------------------------------------------------------------------


class TestAddPTMsFromEvidence:
    def test_add_ptms_from_evidence_no_selected_ptms(self):
        """Should return error message when no PTMs are selected."""
        metadata_df = pd.DataFrame([{"uniprot_accession": "P1"}])
        cif_df = _make_cif_df(
            [
                {
                    "atom_id": 1,
                    "type_symbol": "N",
                    "label_atom_id": "N",
                    "label_comp_id": "ALA",
                    "auth_seq_id": 1,
                    "label_entity_id": 1,
                    "cartn_x": 0.0,
                    "cartn_y": 0.0,
                    "cartn_z": 0.0,
                },
            ]
        )
        psm_df = pd.DataFrame()
        amino_acid_sequences_df = pd.DataFrame(
            {"Protein Sequence": ["AAAA"]},
            index=["P1"],
        )

        result = add_ptms_from_evidence_to_cif(
            metadata_df,
            cif_df,
            psm_df,
            amino_acid_sequences_df,
            selected_ptm_names=[],
        )

        assert "messages" in result
        assert any(m["level"] == logging.ERROR for m in result["messages"])

    def test_add_ptms_from_evidence_no_protein_ids(self):
        """Should return error message when no protein IDs found."""
        metadata_df = pd.DataFrame([{"uniprot_ids": ""}])
        cif_df = _make_cif_df(
            [
                {
                    "atom_id": 1,
                    "type_symbol": "N",
                    "label_atom_id": "N",
                    "label_comp_id": "ALA",
                    "auth_seq_id": 1,
                    "label_entity_id": 1,
                    "cartn_x": 0.0,
                    "cartn_y": 0.0,
                    "cartn_z": 0.0,
                },
            ]
        )
        psm_df = pd.DataFrame()
        amino_acid_sequences_df = pd.DataFrame(
            {"Protein Sequence": ["AAAA"]},
            index=["P1"],
        )

        result = add_ptms_from_evidence_to_cif(
            metadata_df,
            cif_df,
            psm_df,
            amino_acid_sequences_df,
            selected_ptm_names=["ACETYLATION_LYSINE"],
        )

        assert "messages" in result
        assert any(m["level"] == logging.ERROR for m in result["messages"])
