import pandas as pd
import pytest
import logging
from unittest.mock import MagicMock


from backend.protzilla.data_analysis.crosslinking_validation import (
    validate_with_angstrom_deviation,
    get_distance_between_two_amino_acids_in_angstrom,
    add_positions_of_amino_acid_where_crosslinker_bound_to_df,
)
from protzilla.methods.data_analysis import CrosslinkingValidationWithAngstromDeviation


@pytest.mark.parametrize(
    "distance, expected",
    [
        (3.99, False),  # outside bounds
        (4.0, True),  # lower bound
        (6.0, True),  # upper bound
        (6.01, False),  # outside bounds
    ],
)
def test_validate_with_angstrom_deviation(distance, expected):
    # Fake AlphaFold Data
    cif_df = pd.DataFrame(
        {
            "_atom_site.label_atom_id": ["CA", "CA"],
            "_atom_site.label_seq_id": [1, 2],
            "_atom_site.Cartn_x": [0, distance],
            "_atom_site.Cartn_y": [0, 0],
            "_atom_site.Cartn_z": [0, 0],
        }
    )

    amino_acid_sequences_df = pd.DataFrame({"Protein Sequence": ["AB"]})

    # Fake Crosslink Data
    crosslinking_df = pd.DataFrame(
        {
            "Protein_id1": ["P12345"],
            "Protein_id2": ["P12345"],
            "Peptide1": ["A"],
            "Peptide2": ["B"],
            "CL_position_within_peptide1": [0],
            "CL_position_within_peptide2": [0],
            "Crosslinker": ["DSS"],
        }
    )

    crosslinker_information = {"DSS": [5.0, 1.0, 1.0]}  # Länge 5 Å ± 1 Å

    result = validate_with_angstrom_deviation(
        crosslinking_df,
        structure_to_validate="P12345",
        crosslinker_information=crosslinker_information,
        amino_acid_sequences_df=amino_acid_sequences_df,
        cif_df=cif_df,
    )

    df = result["crosslinking_result_df"]

    assert "alphafold_distance" in df.columns
    assert "valid_crosslink" in df.columns
    assert df.loc[0, "alphafold_distance"] == distance
    assert df.loc[0, "valid_crosslink"] == expected


def test_modify_form_creates_crosslinker_fields():
    crosslinking_df = pd.DataFrame({"Crosslinker": ["DSS", "BS3", "DSS"]})

    steps = MagicMock()
    steps.get_step_output.return_value = crosslinking_df

    run = MagicMock()
    run.steps = steps

    step = CrosslinkingValidationWithAngstromDeviation()
    form = step.create_form()

    step.modify_form(form, run)

    assert "DSS_length" in form
    assert "DSS_upper_accepted_deviation" in form
    assert "DSS_lower_accepted_deviation" in form

    assert "BS3_length" in form
    assert "BS3_upper_accepted_deviation" in form
    assert "BS3_lower_accepted_deviation" in form


def test_get_distance_between_two_amino_acids_in_angstrom():
    cif_df = pd.DataFrame(
        {
            "_atom_site.label_atom_id": ["CA", "CA"],
            "_atom_site.label_seq_id": [1, 2],
            "_atom_site.Cartn_x": [0, 3],
            "_atom_site.Cartn_y": [0, 4],
            "_atom_site.Cartn_z": [0, 0],
        }
    )

    dist = get_distance_between_two_amino_acids_in_angstrom(1, 2, "A", "B", cif_df)

    assert dist == 5.0


def test_add_crosslinker_positions_with_exactly_one_possible_position():
    df = pd.DataFrame(
        {
            "Peptide1": ["ABC"],
            "Peptide2": ["DEF"],
            "CL_position_within_peptide1": [1],
            "CL_position_within_peptide2": [2],
        }
    )

    protein_sequence = "XXABCYYYDEFZZ"

    df, messages = add_positions_of_amino_acid_where_crosslinker_bound_to_df(
        df, protein_sequence
    )

    assert messages == []

    assert df.loc[0, "crosslinker_position1"] == 2 + 1 + 1  # 1-based
    assert df.loc[0, "crosslinker_position2"] == 8 + 2 + 1  # 1-based

    assert str(df["crosslinker_position1"].dtype) == "Int64"
    assert str(df["crosslinker_position2"].dtype) == "Int64"


def test_add_crosslinker_positions_with_more_than_one_possible_position():
    df = pd.DataFrame(
        {
            "Peptide1": ["AA"],
            "Peptide2": ["BB"],
            "CL_position_within_peptide1": [0],
            "CL_position_within_peptide2": [0],
        }
    )

    protein_sequence = "AAXXAAZZBBYYBB"

    df, messages = add_positions_of_amino_acid_where_crosslinker_bound_to_df(
        df, protein_sequence
    )

    # 2 AA matches × 2 BB matches = 4 combinations
    assert len(df) == 4

    # One warning about duplication
    assert len(messages) == 1
    assert messages[0]["level"] == logging.WARNING
    assert "duplicated" in messages[0]["msg"]

    # All rows should have valid positions
    assert df["crosslinker_position1"].notna().all()
    assert df["crosslinker_position2"].notna().all()


def test_add_crosslinker_positions_but_one_peptide_not_found_deletes_row():
    df = pd.DataFrame(
        {
            "Peptide1": ["ABC"],
            "Peptide2": ["DEF"],
            "CL_position_within_peptide1": [0],
            "CL_position_within_peptide2": [0],
        }
    )

    protein_sequence = "XXXXXXXX"

    df, messages = add_positions_of_amino_acid_where_crosslinker_bound_to_df(
        df, protein_sequence
    )

    assert len(messages) == 1
    assert messages[0]["level"] == logging.WARNING
    assert "not found" in messages[0]["msg"]

    # row should be deleted
    assert df.empty


def test_add_crosslinker_positions_with_valid_and_invalid_rows_mixed():
    df = pd.DataFrame(
        {
            "Peptide1": ["ABC", "XXX", "ABC"],
            "Peptide2": ["DEF", "DEF", "YYY"],
            "CL_position_within_peptide1": [0, 0, 0],
            "CL_position_within_peptide2": [0, 0, 0],
        }
    )

    protein_sequence = "ABCDEF"

    df, messages = add_positions_of_amino_acid_where_crosslinker_bound_to_df(
        df, protein_sequence
    )

    assert len(messages) == 2
    assert messages[0]["level"] == logging.WARNING

    # First row valid
    assert df.loc[0, "crosslinker_position1"] == 1
    assert df.loc[0, "crosslinker_position2"] == 4

    # Second and third row invalid -> df should only have one row
    assert len(df) == 1


def test_add_crosslinker_positions_with_overlapping_peptide_matches():
    df = pd.DataFrame(
        {
            "Peptide1": ["AAA"],
            "Peptide2": ["B"],
            "CL_position_within_peptide1": [0],
            "CL_position_within_peptide2": [0],
        }
    )

    protein_sequence = "AAAAB"

    df, messages = add_positions_of_amino_acid_where_crosslinker_bound_to_df(
        df, protein_sequence
    )

    # AAA -> positions 0, 1
    # B -> position 4
    # => 2 * 1 = 2 combinations
    assert len(df) == 2

    # One warning about duplication
    assert len(messages) == 1
    assert messages[0]["level"] == logging.WARNING
    assert "duplicated" in messages[0]["msg"]

    observed_positions = set(
        zip(
            df["crosslinker_position1"].astype(int),
            df["crosslinker_position2"].astype(int),
        )
    )

    expected_positions = {(1, 5), (2, 5)}

    assert observed_positions == expected_positions
