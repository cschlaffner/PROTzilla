import pandas as pd
import pytest
from unittest.mock import patch
from unittest.mock import MagicMock


from backend.protzilla.data_analysis.crosslinking_validation import (
    validate_with_angstrom_deviation,
    get_distance_between_two_amino_acids_in_angstrom,
)
from protzilla.methods.data_analysis import CrossLinkingValidationWithAngstromDeviation


@patch(
    "backend.protzilla.data_analysis.crosslinking_validation.fetch_alphafold_protein_structure"
)
@pytest.mark.parametrize(
    "distance, expected",
    [
        (3.99, False),  # outside bounds
        (4.0, True),  # lower bound
        (6.0, True),  # upper bound
        (6.01, False),  # outside bounds
    ],
)
def test_validate_with_angstrom_deviation(mock_fetch, distance, expected):
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

    fasta_df = pd.DataFrame({"Protein Sequence": ["AB"]})

    mock_fetch.return_value = {"cif_df": cif_df, "sequence_df": fasta_df}

    # Fake Crosslink Data
    crosslinking_df = pd.DataFrame(
        {
            "Protein_id1": ["P12345"],
            "Protein_id2": ["P12345"],
            "Peptide1": ["A"],
            "Peptide2": ["B"],
            "CL_position_within_peptide1": [1],
            "CL_position_within_peptide2": [1],
            "Crosslinker": ["DSS"],
        }
    )

    crosslinker_information = {"DSS": [5.0, 1.0, 1.0]}  # Länge 5 Å ± 1 Å

    result = validate_with_angstrom_deviation(
        crosslinking_df,
        protein_to_validate="P12345",
        crosslinker_information=crosslinker_information,
    )

    df = result["crosslinking_result_df"]

    assert "alphafold_distance" in df.columns
    assert "valid_crosslink" in df.columns
    assert df.loc[0, "alphafold_distance"] == distance
    assert df.loc[0, "valid_crosslink"] is expected


def test_modify_form_creates_crosslinker_fields():
    crosslinking_df = pd.DataFrame({"Crosslinker": ["DSS", "BS3", "DSS"]})

    steps = MagicMock()
    steps.get_step_output.return_value = crosslinking_df

    run = MagicMock()
    run.steps = steps

    step = CrossLinkingValidationWithAngstromDeviation()
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
