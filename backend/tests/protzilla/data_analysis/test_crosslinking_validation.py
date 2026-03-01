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

    amino_acid_sequences_df = pd.DataFrame(
        {"Protein ID": ["P12345-1"], "Protein Sequence": ["AB"]}
    )

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
        structures_to_validate=["P12345"],
        crosslinker_information=crosslinker_information,
        amino_acid_sequences_df=amino_acid_sequences_df,
        cif_df=cif_df,
        is_multimer=False,
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
            "Protein_id1": ["P1"],
            "Protein_id2": ["P1"],
            "Peptide1": ["ABC"],
            "Peptide2": ["DEF"],
            "CL_position_within_peptide1": [1],
            "CL_position_within_peptide2": [2],
        }
    )

    amino_acid_sequences_df = pd.DataFrame(
        {"Protein ID": ["P1-1"], "Protein Sequence": ["XXABCYYYDEFZZ"]}
    )

    df, messages = add_positions_of_amino_acid_where_crosslinker_bound_to_df(
        df, amino_acid_sequences_df
    )

    assert messages == []

    assert df.loc[0, "crosslinker_position1"] == 2 + 1 + 1  # 1-based
    assert df.loc[0, "crosslinker_position2"] == 8 + 2 + 1  # 1-based

    assert str(df["crosslinker_position1"].dtype) == "Int64"
    assert str(df["crosslinker_position2"].dtype) == "Int64"


def test_add_crosslinker_positions_with_more_than_one_possible_position():
    df = pd.DataFrame(
        {
            "Protein_id1": ["P1"],
            "Protein_id2": ["P1"],
            "Peptide1": ["AA"],
            "Peptide2": ["BB"],
            "CL_position_within_peptide1": [0],
            "CL_position_within_peptide2": [0],
        }
    )

    amino_acid_sequences_df = pd.DataFrame(
        {"Protein ID": ["P1-1"], "Protein Sequence": ["AAXXAAZZBBYYBB"]}
    )

    df, messages = add_positions_of_amino_acid_where_crosslinker_bound_to_df(
        df, amino_acid_sequences_df
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
            "Protein_id1": ["P1"],
            "Protein_id2": ["P1"],
            "Peptide1": ["ABC"],
            "Peptide2": ["DEF"],
            "CL_position_within_peptide1": [0],
            "CL_position_within_peptide2": [0],
        }
    )

    amino_acid_sequences_df = pd.DataFrame(
        {"Protein ID": ["P1-1"], "Protein Sequence": ["XXXXXXXX"]}
    )

    df, messages = add_positions_of_amino_acid_where_crosslinker_bound_to_df(
        df, amino_acid_sequences_df
    )

    assert len(messages) == 1
    assert messages[0]["level"] == logging.WARNING
    assert "not found" in messages[0]["msg"]

    # row should be deleted
    assert df.empty


def test_add_crosslinker_positions_with_valid_and_invalid_rows_mixed():
    df = pd.DataFrame(
        {
            "Protein_id1": ["P1", "P1", "P1"],
            "Protein_id2": ["P1", "P1", "P1"],
            "Peptide1": ["ABC", "XXX", "ABC"],
            "Peptide2": ["DEF", "DEF", "YYY"],
            "CL_position_within_peptide1": [0, 0, 0],
            "CL_position_within_peptide2": [0, 0, 0],
        }
    )

    amino_acid_sequences_df = pd.DataFrame(
        {"Protein ID": ["P1-1"], "Protein Sequence": ["ABCDEF"]}
    )

    df, messages = add_positions_of_amino_acid_where_crosslinker_bound_to_df(
        df, amino_acid_sequences_df
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
            "Protein_id1": ["P1"],
            "Protein_id2": ["P1"],
            "Peptide1": ["AAA"],
            "Peptide2": ["B"],
            "CL_position_within_peptide1": [0],
            "CL_position_within_peptide2": [0],
        }
    )

    amino_acid_sequences_df = pd.DataFrame(
        {"Protein ID": ["P1-1"], "Protein Sequence": ["AAAAB"]}
    )

    df, messages = add_positions_of_amino_acid_where_crosslinker_bound_to_df(
        df, amino_acid_sequences_df
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


def test_validate_multimer_filters_only_pairs_within_structures_to_validate():
    rows = [
        ("P1-1", "ABCDE"),
        ("P2-1", "VWXYZ"),
        ("P3-1", "KLMNO"),
    ]
    sequences_df = pd.DataFrame(rows, columns=["Protein ID", "Protein Sequence"])

    crosslinking_df = pd.DataFrame(
        [
            # within set: P1-P2 (should be kept when validating ["P1","P2"])
            ("P1", "P2", "BC", "WX", 0, 0, "XL"),
            # within set: P2-P2
            ("P2", "P2", "WX", "WX", 0, 0, "XL"),
            # outside set: P1-P3 (should be filtered out)
            ("P1", "P3", "BC", "LM", 0, 0, "XL"),
        ],
        columns=[
            "Protein_id1",
            "Protein_id2",
            "Peptide1",
            "Peptide2",
            "CL_position_within_peptide1",
            "CL_position_within_peptide2",
            "Crosslinker",
        ],
    )

    cif_df = pd.DataFrame(
        {
            "_atom_site.label_atom_id": ["CA"] * 5,
            "_atom_site.label_seq_id": list(range(1, 6)),
            "_atom_site.Cartn_x": [float(i) for i in range(1, 6)],
            "_atom_site.Cartn_y": [0.0] * 5,
            "_atom_site.Cartn_z": [0.0] * 5,
        }
    )

    # Very permissive bounds: always valid as long as distance is defined.
    # Format is [length, upper_deviation, lower_deviation].
    crosslinker_information = {"XL": [0.0, 0.0, 0.0]}

    out = validate_with_angstrom_deviation(
        crosslinking_df=crosslinking_df,
        structures_to_validate=["P1", "P2"],
        crosslinker_information=crosslinker_information,
        cif_df=cif_df,
        amino_acid_sequences_df=sequences_df,
        is_multimer=True,
    )

    result_df = out["crosslinking_result_df"]
    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty

    # Only the first two rows should remain after filtering.
    assert len(result_df) == 2

    assert set(result_df["Protein_id1"].unique()).issubset({"P1", "P2"})
    assert set(result_df["Protein_id2"].unique()).issubset({"P1", "P2"})

    assert "alphafold_distance" in result_df.columns
    assert "valid_crosslink" in result_df.columns
    assert "crosslinker_position1" in result_df.columns
    assert "crosslinker_position2" in result_df.columns


def test_validate_multimer_no_links_between_structures_returns_empty_and_warning():
    sequences_df = pd.DataFrame(
        [
            ("P1-1", "ABCDE"),
            ("P2-1", "VWXYZ"),
            ("P3-1", "KLMNO"),
        ],
        columns=["Protein ID", "Protein Sequence"],
    )

    crosslinking_df = pd.DataFrame(
        [
            ("P1", "P3", "BC", "LM", 0, 0, "XL"),
            ("P3", "P2", "LM", "WX", 0, 0, "XL"),
        ],
        columns=[
            "Protein_id1",
            "Protein_id2",
            "Peptide1",
            "Peptide2",
            "CL_position_within_peptide1",
            "CL_position_within_peptide2",
            "Crosslinker",
        ],
    )

    cif_df = pd.DataFrame(
        {
            "_atom_site.label_atom_id": ["CA"] * 5,
            "_atom_site.label_seq_id": list(range(1, 6)),
            "_atom_site.Cartn_x": [float(i) for i in range(1, 6)],
            "_atom_site.Cartn_y": [0.0] * 5,
            "_atom_site.Cartn_z": [0.0] * 5,
        }
    )
    crosslinker_information = {"XL": [0.0, 0.0, 0.0]}

    out = validate_with_angstrom_deviation(
        crosslinking_df=crosslinking_df,
        structures_to_validate=["P1", "P2"],
        crosslinker_information=crosslinker_information,
        cif_df=cif_df,
        amino_acid_sequences_df=sequences_df,
        is_multimer=True,
    )

    result_df = out["crosslinking_result_df"]
    messages = out["messages"]

    assert isinstance(result_df, pd.DataFrame)
    assert result_df.empty

    assert isinstance(messages, list)
    assert len(messages) == 1
    assert messages[0].get("level") is not None
    assert "There are no cross links between the structures to validate." in messages[
        0
    ].get("msg", "")


def test_validate_multimer_duplicates_rows_for_multiple_peptide_matches_and_validates_all():
    # AB occurs twice in ABAB: at positions 1 and 3 (1-based).
    sequences_df = pd.DataFrame(
        [
            ("P1-1", "ABAB"),
            ("P2-1", "ABAB"),
        ],
        columns=["Protein ID", "Protein Sequence"],
    )

    crosslinking_df = pd.DataFrame(
        [
            ("P1", "P2", "AB", "AB", 0, 0, "XL"),
        ],
        columns=[
            "Protein_id1",
            "Protein_id2",
            "Peptide1",
            "Peptide2",
            "CL_position_within_peptide1",
            "CL_position_within_peptide2",
            "Crosslinker",
        ],
    )

    cif_df = cif_df = pd.DataFrame(
        {
            "_atom_site.label_atom_id": ["CA"] * 4,
            "_atom_site.label_seq_id": list(range(1, 5)),
            "_atom_site.Cartn_x": [float(i) for i in range(1, 5)],
            "_atom_site.Cartn_y": [0.0] * 4,
            "_atom_site.Cartn_z": [0.0] * 4,
        }
    )

    # Always-valid bounds so we focus on duplication and distance computation.
    crosslinker_information = {"XL": [0.0, 0.0, 0.0]}

    out = validate_with_angstrom_deviation(
        crosslinking_df=crosslinking_df,
        structures_to_validate=["P1", "P2"],
        crosslinker_information=crosslinker_information,
        cif_df=cif_df,
        amino_acid_sequences_df=sequences_df,
        is_multimer=True,
    )

    result_df = out["crosslinking_result_df"]
    messages = out["messages"]

    assert isinstance(result_df, pd.DataFrame)
    assert len(result_df) == 4

    # Crosslinker positions should cover the product of {1,3} x {1,3}.
    combos = set(
        zip(
            result_df["crosslinker_position1"].astype(int).tolist(),
            result_df["crosslinker_position2"].astype(int).tolist(),
        )
    )
    assert combos == {(1, 1), (1, 3), (3, 1), (3, 3)}

    # Distances in our 1D coordinate system are abs(pos2 - pos1).
    distances = sorted(result_df["alphafold_distance"].astype(float).tolist())
    assert distances == [0.0, 0.0, 2.0, 2.0]

    # With permissive bounds, all should be valid.
    assert result_df["valid_crosslink"].dropna().all()

    # Expect a duplication warning message.
    assert any(
        ("duplicated" in str(m.get("msg", "")).lower()) and (m.get("level") is not None)
        for m in messages
    )
