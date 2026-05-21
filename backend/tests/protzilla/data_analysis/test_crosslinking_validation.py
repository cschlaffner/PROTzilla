import pandas as pd
from backend.protzilla.constants.option_types import CrosslinkingValidationCriterion
import pytest
import logging
from unittest.mock import patch, MagicMock
import plotly.graph_objects as go
from plotly.graph_objects import Figure
import pandas.testing as pdt
import numpy


from backend.protzilla.data_analysis.crosslinking_validation import (
    validate_with_angstrom_deviation,
    get_distance_between_two_amino_acids_in_angstrom,
    add_protein_crosslink_positions_to_df,
    diagrams_of_crosslinking_validation_data,
    expand_crosslinks_to_chain_combinations,
    get_chains,
)
from backend.protzilla.constants.colors import PLOT_PRIMARY_COLOR
from backend.protzilla.data_analysis.plots import (
    add_vertical_line_with_annotation_in_legend,
)
from backend.protzilla.form import Form

from backend.protzilla.methods.data_analysis import (
    CrosslinkingValidationWithAngstromDeviation,
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
def test_monomer_validation(distance, expected):
    crosslinker_information = {"DSS": [5.0, 1.0, 1.0]}  # Length 5 Å ± 1 Å

    # Fake AlphaFold Data with chain IDs
    cif_df = pd.DataFrame(
        {
            "_atom_site.label_atom_id": ["CA", "CA"],
            "_atom_site.label_asym_id": ["A", "A"],
            "_atom_site.label_seq_id": [1, 2],
            "_atom_site.Cartn_x": [0, distance],
            "_atom_site.Cartn_y": [0, 0],
            "_atom_site.Cartn_z": [0, 0],
            "_atom_site.auth_asym_id": ["A", "A"],
            "_atom_site.pdbx_sifts_xref_db_acc": ["P12345", "P12345"],
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

    structure_metadata_df = pd.DataFrame(
        {"entry_id": ["test"], "uniprot_accession": ["P12345"]}
    )

    valid_ids = {"P12345": ["P12345"]}
    structures_to_validate = ["P12345"]

    pae_df_noerror = pd.DataFrame(
        {
            "predicted_aligned_error": ["[[0, 0], [0, 0]]"],
            "max_predicted_aligned_error": [31.75],
        }
    )

    pae_matrix_noerror = numpy.array([[0, 0], [0, 0]])

    plddt_df_noerror = pd.DataFrame(
        {
            "residueNumber": [1, 2],
            "confidenceScore": [100, 100],
            "chainID": ["A", "A"],
            # confidenceCategory is not required
        }
    )

    result = validate_with_angstrom_deviation(
        crosslinking_df=crosslinking_df,
        structure_metadata_df=structure_metadata_df,
        crosslinker_information=crosslinker_information,
        cif_df=cif_df,
        amino_acid_sequences_df=amino_acid_sequences_df,
        valid_ids=valid_ids,
        id_column_name="_atom_site.pdbx_sifts_xref_db_acc",
        structures_to_validate=structures_to_validate,
        pae_matrix=pae_matrix_noerror,
        plddt_df=plddt_df_noerror,
        validation_criterion=CrosslinkingValidationCriterion.manual_bounds.value,
    )

    df: pd.DataFrame = result["crosslinking_result_df"]

    assert "alphafold_distance" in df.columns
    assert "valid_crosslink" in df.columns
    assert "link_type" in df.columns
    assert "Chain_id1" in df.columns
    assert "Chain_id2" in df.columns
    assert df.loc[0, "alphafold_distance"] == distance
    assert df.loc[0, "valid_crosslink"] == expected
    assert df.loc[0, "link_type"] == "intra"

    # Validation with PAE
    # TODO: Proper cases with error


def test_modify_form_creates_crosslinker_fields():
    crosslinking_df = pd.DataFrame({"Crosslinker": ["DSS", "BS3", "DSS"]})

    steps = MagicMock()
    steps.get_step_output.return_value = crosslinking_df

    run = MagicMock()
    run.steps = steps

    step = CrosslinkingValidationWithAngstromDeviation()
    step.form = step.create_form()

    step.input_source = MagicMock(return_value=("dummy_step", "dummy_handle"))

    step.modify_form(run)

    assert "DSS_length" in step.form
    assert "DSS_upper_accepted_deviation" in step.form
    assert "DSS_lower_accepted_deviation" in step.form

    assert "BS3_length" in step.form
    assert "BS3_upper_accepted_deviation" in step.form
    assert "BS3_lower_accepted_deviation" in step.form


def test_get_distance_between_two_amino_acids_in_angstrom():
    cif_df = pd.DataFrame(
        {
            "_atom_site.label_atom_id": ["CA", "CA"],
            "_atom_site.label_seq_id": [1, 2],
            "_atom_site.Cartn_x": [0, 3],
            "_atom_site.Cartn_y": [0, 4],
            "_atom_site.Cartn_z": [0, 0],
            "_atom_site.auth_asym_id": ["A", "A"],
        }
    )

    dist = get_distance_between_two_amino_acids_in_angstrom(
        1, 2, "A", "B", cif_df, chain_id1="A", chain_id2="A"
    )

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

    df, messages = add_protein_crosslink_positions_to_df(df, amino_acid_sequences_df)

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

    df, messages = add_protein_crosslink_positions_to_df(df, amino_acid_sequences_df)

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

    df, messages = add_protein_crosslink_positions_to_df(df, amino_acid_sequences_df)

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

    df, messages = add_protein_crosslink_positions_to_df(df, amino_acid_sequences_df)

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

    df, messages = add_protein_crosslink_positions_to_df(df, amino_acid_sequences_df)

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
            "_atom_site.auth_asym_id": ["A"] * 5,
            "_atom_site.label_entity_id": [1, 1, 2, 2, 3],
        }
    )

    # Very permissive bounds: always valid as long as distance is defined.
    # Format is [length, upper_deviation, lower_deviation].
    crosslinker_information = {"XL": [0.0, 0.0, 0.0]}
    valid_ids = {"P1": [1], "P2": [2]}
    structures_to_validate = ["P1", "P2"]

    structure_metadata_df = pd.DataFrame(
        {"entry_id": ["test"], "uniprot_ids": [["P1", "P2"]]}
    )

    out = validate_with_angstrom_deviation(
        crosslinking_df=crosslinking_df,
        structure_metadata_df=structure_metadata_df,
        crosslinker_information=crosslinker_information,
        cif_df=cif_df,
        amino_acid_sequences_df=sequences_df,
        valid_ids=valid_ids,
        id_column_name="_atom_site.label_entity_id",
        structures_to_validate=structures_to_validate,
        validation_criterion=CrosslinkingValidationCriterion.manual_bounds.value,
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
    assert "link_type" in result_df.columns
    assert "Chain_id1" in result_df.columns
    assert "Chain_id2" in result_df.columns


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
            "_atom_site.auth_asym_id": ["A"] * 5,
            "_atom_site.label_entity_id": [1, 1, 2, 3, 3],
        }
    )
    crosslinker_information = {"XL": [0.0, 0.0, 0.0]}
    valid_ids = {"P1": [1], "P2": [2]}
    structures_to_validate = ["P1", "P2"]

    structure_metadata_df = pd.DataFrame(
        {"entry_id": ["test"], "uniprot_ids": [["P1", "P2"]]}
    )

    out = validate_with_angstrom_deviation(
        crosslinking_df=crosslinking_df,
        structure_metadata_df=structure_metadata_df,
        crosslinker_information=crosslinker_information,
        cif_df=cif_df,
        amino_acid_sequences_df=sequences_df,
        valid_ids=valid_ids,
        id_column_name="_atom_site.label_entity_id",
        structures_to_validate=structures_to_validate,
        validation_criterion=CrosslinkingValidationCriterion.manual_bounds.value,
    )

    result_df = out["crosslinking_result_df"]
    messages = out["messages"]

    assert isinstance(result_df, pd.DataFrame)
    assert result_df.empty

    assert isinstance(messages, list)
    assert len(messages) >= 1
    assert messages[0].get("level") is not None
    assert "There are no crosslinks between the structures to validate." in messages[
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

    cif_df = pd.DataFrame(
        {
            "_atom_site.label_atom_id": ["CA"] * 8,
            "_atom_site.label_seq_id": [1, 2, 3, 4, 1, 2, 3, 4],
            "_atom_site.Cartn_x": [1.0, 2.0, 3.0, 4.0, 1.0, 2.0, 3.0, 4.0],
            "_atom_site.Cartn_y": [0.0] * 8,
            "_atom_site.Cartn_z": [0.0] * 8,
            "_atom_site.auth_asym_id": ["A", "A", "A", "A", "B", "B", "B", "B"],
            "_atom_site.label_entity_id": [1, 1, 1, 1, 2, 2, 2, 2],
        }
    )

    # Always-valid bounds so we focus on duplication and distance computation.
    crosslinker_information = {"XL": [0.0, 0.0, 0.0]}
    valid_ids = {"P1": [1], "P2": [2]}
    structures_to_validate = ["P1", "P2"]

    structure_metadata_df = pd.DataFrame(
        {"entry_id": ["test"], "uniprot_ids": [["P1", "P2"]]}
    )

    out = validate_with_angstrom_deviation(
        crosslinking_df=crosslinking_df,
        structure_metadata_df=structure_metadata_df,
        crosslinker_information=crosslinker_information,
        cif_df=cif_df,
        amino_acid_sequences_df=sequences_df,
        valid_ids=valid_ids,
        id_column_name="_atom_site.label_entity_id",
        structures_to_validate=structures_to_validate,
        validation_criterion=CrosslinkingValidationCriterion.manual_bounds.value,
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

    # Check link_type column
    assert "link_type" in result_df.columns
    assert result_df["link_type"].isin(["intra", "inter"]).all()
    # All links should be inter because they are between different chains
    assert all(result_df["link_type"] == "inter")

    # Expect a duplication warning message.
    assert any(
        ("duplicated" in str(m.get("msg", "")).lower()) and (m.get("level") is not None)
        for m in messages
    )


def test_add_vertical_line_with_annotation_in_legend_adds_line_and_legend():
    fig = go.Figure()
    add_vertical_line_with_annotation_in_legend(
        fig=fig, dash="dash", annotation="Test Line", x_value=5.0
    )

    # add_vline internally adds a shape to layout.shapes
    assert len(fig.layout.shapes) == 1
    vline = fig.layout.shapes[0]
    assert vline["x0"] == 5.0
    assert vline["line"]["dash"] == "dash"
    assert vline["line"]["color"] == PLOT_PRIMARY_COLOR

    # There should be 1 scatter trace for the legend
    assert len(fig.data) == 1
    trace = fig.data[0]
    assert trace.mode == "lines"
    assert trace.name == "Test Line"
    assert trace.line.dash == "dash"
    assert trace.line.color == PLOT_PRIMARY_COLOR
    assert trace.x == (None,)
    assert trace.y == (None,)


@pytest.fixture
def sample_crosslinking_df():
    return pd.DataFrame(
        {
            "Crosslinker": ["CL1", "CL1", "CL2", "CL2"],
            "alphafold_distance": [10.0, 12.0, 8.0, 9.0],
            "valid_crosslink": [True, False, True, False],
            "link_type": ["intra", "intra", "inter", "inter"],
        }
    )


@pytest.fixture
def sample_crosslinker_info():
    return {
        "CL1": [11.0, 2.0, 0.0],  # [length, upper_deviation, lower_deviation]
        "CL2": [9.0, 0.0, 1.0],
    }


@patch("backend.protzilla.data_analysis.crosslinking_validation.create_histograms")
@patch("backend.protzilla.data_analysis.crosslinking_validation.create_bar_plot")
@patch(
    "backend.protzilla.data_analysis.crosslinking_validation.add_vertical_line_with_annotation_in_legend"
)
def test_diagrams_of_crosslinking_validation_data_with_drawing_all_vertical_lines(
    mock_add_vline,
    mock_create_bar,
    mock_create_hist,
    sample_crosslinking_df,
    sample_crosslinker_info,
):
    validated_df = sample_crosslinking_df.copy()

    hist_mock = Figure()
    mock_create_hist.return_value = hist_mock
    bar_mock = Figure()
    mock_create_bar.return_value = bar_mock

    figures = diagrams_of_crosslinking_validation_data(
        validated_df=validated_df,
        structures_to_validate=["P12345"],
        crosslinker_information=sample_crosslinker_info,
    )

    # 2 histograms per crosslinker + 1 bar plot
    assert len(figures) == 5
    assert all(isinstance(f, Figure) for f in figures)

    assert (
        mock_add_vline.call_count == 8
    )  # for both crosslinkers: 1 call for crosslinker length for each histogram and 1 call for bound on deviation for each histogram

    # Check that create_histograms was called 2 times (1 per crosslinker)
    assert mock_create_hist.call_count == 2

    # Check that create_bar_plot was called once
    mock_create_bar.assert_called_once()


@pytest.fixture
def sample_crosslinking_df_with_no_std():
    return pd.DataFrame(
        {
            "Crosslinker": ["CL1", "CL1", "CL2", "CL2"],
            "alphafold_distance": [10.5, 10.5, 10.5, 10.5],
            "valid_crosslink": [True, False, True, False],
            "link_type": ["intra", "intra", "inter", "inter"],
        }
    )


@pytest.fixture
def sample_crosslinker_info_matching_sample_crosslinking_df_with_no_std():
    return {
        "CL1": [10.5, 1.0, 1.0],  # [length, upper_deviation, lower_deviation]
        "CL2": [10.5, 0.5, 0.3],
    }


@patch("backend.protzilla.data_analysis.crosslinking_validation.create_histograms")
@patch("backend.protzilla.data_analysis.crosslinking_validation.create_bar_plot")
@patch(
    "backend.protzilla.data_analysis.crosslinking_validation.add_vertical_line_with_annotation_in_legend"
)
def test_diagrams_of_crosslinking_validation_data_without_drawing_all_vertical_lines(
    mock_add_vline,
    mock_create_bar,
    mock_create_hist,
    sample_crosslinking_df_with_no_std,
    sample_crosslinker_info_matching_sample_crosslinking_df_with_no_std,
):
    validated_df = sample_crosslinking_df_with_no_std.copy()

    hist_mock = Figure()
    mock_create_hist.return_value = hist_mock
    bar_mock = Figure()
    mock_create_bar.return_value = bar_mock

    figures = diagrams_of_crosslinking_validation_data(
        validated_df=validated_df,
        structures_to_validate=["P12345"],
        crosslinker_information=sample_crosslinker_info_matching_sample_crosslinking_df_with_no_std,
    )

    # 2 histograms per crosslinker + 1 bar plot
    assert len(figures) == 5
    assert all(isinstance(f, Figure) for f in figures)

    # CL1: all 3 lines are drawn for both histograms, CL2: only crosslinker_length ist drawn for both histograms,
    # the bounds are only drawn for the histogram that is not limited to the range of +- 2 standard deviations
    assert mock_add_vline.call_count == 10

    # Check that create_histograms was called 2 times (1 per crosslinker)
    assert mock_create_hist.call_count == 2

    # Check that create_bar_plot was called once
    mock_create_bar.assert_called_once()


@pytest.fixture
def sample_crosslinker_info_with_one_crosslinker():
    return {
        "CL1": [11.0, 2.0, 1.0],  # [length, upper_deviation, lower_deviation]
    }


@pytest.fixture
def sample_crosslinking_df_with_one_crosslinker():
    return pd.DataFrame(
        {
            "Crosslinker": ["CL1", "CL1", "CL1", "CL1"],
            "alphafold_distance": [10.0, 12.0, 8.0, 9.0],
            "valid_crosslink": [True, False, True, False],
            "link_type": ["intra", "intra", "inter", "inter"],
        }
    )


def test_diagrams_calls_with_correct_parameters(
    sample_crosslinking_df_with_one_crosslinker,
    sample_crosslinker_info_with_one_crosslinker,
):
    with patch(
        "backend.protzilla.data_analysis.crosslinking_validation.create_histograms"
    ) as mock_hist, patch(
        "backend.protzilla.data_analysis.crosslinking_validation.add_vertical_line_with_annotation_in_legend"
    ) as mock_vline, patch(
        "backend.protzilla.data_analysis.crosslinking_validation.create_bar_plot"
    ) as mock_bar:

        mock_hist.return_value = Figure()
        mock_bar.return_value = "bar_fig"

        figures = diagrams_of_crosslinking_validation_data(
            validated_df=sample_crosslinking_df_with_one_crosslinker,
            structures_to_validate=["P12345"],
            crosslinker_information=sample_crosslinker_info_with_one_crosslinker,
        )

        # There should be 1 histogram calls: 1 per crosslinker
        assert mock_hist.call_count == 1

        # Check histogram call parameters for crosslinker ±2 std
        hist_call = mock_hist.call_args_list[0].kwargs
        assert hist_call["name_a"] == "Predictions matching CLs (intra: 1, inter: 1)"
        assert (
            hist_call["name_b"] == "Predictions not matching CLs (intra: 1, inter: 1)"
        )
        assert (
            hist_call["heading"]
            == "Predicted distances for P12345 with crosslinker CL1, mean +/- 2 σ"
        )
        assert hist_call["relevant_column_a"] == "alphafold_distance"
        assert hist_call["relevant_column_b"] == "alphafold_distance"
        assert hist_call["one_bin_per_int"] == True

        mean_predicted_lengths = sample_crosslinking_df_with_one_crosslinker[
            "alphafold_distance"
        ].mean()
        standard_deviation_predicted_lengths = (
            sample_crosslinking_df_with_one_crosslinker["alphafold_distance"].std()
        )
        mean_plus_minus_two_std_range = (
            max(0, mean_predicted_lengths - 2 * standard_deviation_predicted_lengths),
            mean_predicted_lengths + 2 * standard_deviation_predicted_lengths,
        )
        assert hist_call["min_value"] == mean_plus_minus_two_std_range[0]
        assert hist_call["max_value"] == mean_plus_minus_two_std_range[1]

        valid_crosslinks = sample_crosslinking_df_with_one_crosslinker.loc[
            sample_crosslinking_df_with_one_crosslinker["valid_crosslink"] == True,
            "alphafold_distance",
        ]
        invalid_crosslinks = sample_crosslinking_df_with_one_crosslinker.loc[
            sample_crosslinking_df_with_one_crosslinker["valid_crosslink"] == False,
            "alphafold_distance",
        ]
        dataframe_a = pd.DataFrame({"alphafold_distance": valid_crosslinks})
        dataframe_b = pd.DataFrame({"alphafold_distance": invalid_crosslinks})
        pdt.assert_frame_equal(hist_call["dataframe_a"], dataframe_a)
        pdt.assert_frame_equal(hist_call["dataframe_b"], dataframe_b)

        call_args_list = [call.kwargs for call in mock_vline.call_args_list]
        assert any(
            call["annotation"] == "CL1 length: 11.0Å" and call["x_value"] == 11.0
            for call in call_args_list
        )

        mock_bar.assert_called_once()


def test_validate_multimer_with_invalid_crosslinks():
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

    cif_df = pd.DataFrame(
        {
            "_atom_site.label_atom_id": ["CA"] * 4,
            "_atom_site.label_seq_id": [1, 2, 3, 4],
            "_atom_site.Cartn_x": [1.0, 2.0, 3.0, 4.0],
            "_atom_site.Cartn_y": [0.0, 0.0, 0.0, 0.0],
            "_atom_site.Cartn_z": [0.0, 0.0, 0.0, 0.0],
            "_atom_site.auth_asym_id": ["A"] * 4,
            "_atom_site.label_entity_id": [1, 1, 2, 2],
        }
    )

    # length = 1.5, upper_dev = 0.6, lower_dev = 0.6.
    # Distances will be [0.0, 0.0, 2.0, 2.0] -> two valid (2.0) and two invalid (0.0).
    crosslinker_information = {"XL": [1.5, 0.6, 0.6]}
    valid_ids = {"P1": [1], "P2": [2]}
    structures_to_validate = ["P1", "P2"]

    structure_metadata_df = pd.DataFrame(
        {"entry_id": ["test"], "uniprot_ids": [["P1", "P2"]]}
    )

    out = validate_with_angstrom_deviation(
        crosslinking_df=crosslinking_df,
        structure_metadata_df=structure_metadata_df,
        crosslinker_information=crosslinker_information,
        cif_df=cif_df,
        amino_acid_sequences_df=sequences_df,
        valid_ids=valid_ids,
        id_column_name="_atom_site.label_entity_id",
        structures_to_validate=structures_to_validate,
        validation_criterion=CrosslinkingValidationCriterion.manual_bounds.value,
    )

    result_df = out["crosslinking_result_df"]
    assert isinstance(result_df, pd.DataFrame)
    assert len(result_df) == 4

    distances = sorted(result_df["alphafold_distance"].astype(float).tolist())
    assert distances == [0.0, 0.0, 2.0, 2.0]

    valid_counts = result_df["valid_crosslink"].value_counts()
    assert valid_counts.get(True, 0) == 2
    assert valid_counts.get(False, 0) == 2

    valid_distances = sorted(
        result_df.loc[result_df["valid_crosslink"] == True, "alphafold_distance"]
        .astype(float)
        .tolist()
    )
    assert valid_distances == [2.0, 2.0]
    assert "link_type" in result_df.columns


def test_get_chains():
    """Test that get_chains extracts chain IDs correctly from CIF data."""
    cif_df = pd.DataFrame(
        {
            "_atom_site.label_seq_id": [1, 2, 3, 4, 5],
            "_atom_site.auth_asym_id": ["A", "A", "B", "B", "B"],
            "_atom_site.label_entity_id": [1, 1, 2, 2, 2],
        }
    )

    valid_ids = {"P1": [1], "P2": [2]}

    chains_p1 = get_chains(
        cif_df=cif_df,
        valid_ids=valid_ids,
        protein_id="P1",
        id_column_name="_atom_site.label_entity_id",
    )

    chains_p2 = get_chains(
        cif_df=cif_df,
        valid_ids=valid_ids,
        protein_id="P2",
        id_column_name="_atom_site.label_entity_id",
    )

    assert set(chains_p1) == {"A"}
    assert set(chains_p2) == {"B"}


def test_expand_crosslinks_to_chain_combinations_homodimer():
    """Test expanding crosslinks for homodimer (same protein twice)."""
    crosslinking_df = pd.DataFrame(
        [
            ("P1", "P1", "AB", "CD", 0, 0, "XL"),
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

    chains_per_protein = {"P1": {"A": None, "B": None}}

    expanded_df = expand_crosslinks_to_chain_combinations(
        crosslinking_df, chains_per_protein
    )

    # For homodimer with 2 chains: combinations with replacement should give us:
    # (A,A), (A,B), (B,B) = 3 combinations
    assert len(expanded_df) == 3
    assert "Chain_id1" in expanded_df.columns
    assert "Chain_id2" in expanded_df.columns

    chain_combos = set(
        zip(expanded_df["Chain_id1"].tolist(), expanded_df["Chain_id2"].tolist())
    )
    assert chain_combos == {("A", "A"), ("A", "B"), ("B", "B")}


def test_expand_crosslinks_to_chain_combinations_heterodimer():
    """Test expanding crosslinks for heterodimer (different proteins)."""
    crosslinking_df = pd.DataFrame(
        [
            ("P1", "P2", "AB", "CD", 0, 0, "XL"),
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

    chains_per_protein = {"P1": {"A": None}, "P2": {"C": None, "D": None}}

    expanded_df = expand_crosslinks_to_chain_combinations(
        crosslinking_df, chains_per_protein
    )

    # For heterodimer: product of {A} x {C, D} = 2 combinations
    assert len(expanded_df) == 2

    chain_combos = set(
        zip(expanded_df["Chain_id1"].tolist(), expanded_df["Chain_id2"].tolist())
    )
    assert chain_combos == {("A", "C"), ("A", "D")}


def test_validate_multimer_same_protein_different_chains_intra_vs_inter():
    """Test that intra/inter link_type is determined by chain ID, not protein ID."""
    sequences_df = pd.DataFrame(
        [
            ("P1-1", "ABCD"),
        ],
        columns=["Protein ID", "Protein Sequence"],
    )

    # Single protein P1 with two copies in multimer (P1 appears twice as different chains)
    crosslinking_df = pd.DataFrame(
        [
            ("P1", "P1", "AB", "AB", 0, 0, "XL"),
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
            "_atom_site.label_atom_id": ["CA"] * 8,
            "_atom_site.label_seq_id": [1, 2, 3, 4, 1, 2, 3, 4],
            "_atom_site.Cartn_x": [1.0, 2.0, 3.0, 4.0, 1.0, 2.0, 3.0, 4.0],
            "_atom_site.Cartn_y": [0.0] * 8,
            "_atom_site.Cartn_z": [0.0] * 8,
            "_atom_site.auth_asym_id": ["A", "A", "A", "A", "B", "B", "B", "B"],
            "_atom_site.label_entity_id": [1, 1, 1, 1, 1, 1, 1, 1],
        }
    )

    structure_metadata_df = pd.DataFrame(
        {
            "entry_id": ["test"],
            "uniprot_ids": ["ABCD"],
        }
    )

    crosslinker_information = {"XL": [0.0, 0.0, 0.0]}
    valid_ids = {"P1": [1]}  # One protein ID, but present in chains A and B
    structures_to_validate = ["P1"]

    out = validate_with_angstrom_deviation(
        crosslinking_df=crosslinking_df,
        crosslinker_information=crosslinker_information,
        structure_metadata_df=structure_metadata_df,
        cif_df=cif_df,
        amino_acid_sequences_df=sequences_df,
        valid_ids=valid_ids,
        id_column_name="_atom_site.label_entity_id",
        structures_to_validate=structures_to_validate,
        validation_criterion=CrosslinkingValidationCriterion.manual_bounds.value,
    )

    result_df = out["crosslinking_result_df"]

    # Should have 3 combinations: (A,A), (A,B), (B,B)
    assert len(result_df) == 3

    # Check link types based on chain IDs
    intra_links = result_df[result_df["link_type"] == "intra"]
    inter_links = result_df[result_df["link_type"] == "inter"]

    # (A,A) and (B,B) should be intra (same chain)
    assert len(intra_links) == 2
    # (A,B) should be inter (different chains)
    assert len(inter_links) == 1

    # Verify the specific chain combinations
    intra_combos = set(
        zip(intra_links["Chain_id1"].tolist(), intra_links["Chain_id2"].tolist())
    )
    assert intra_combos == {("A", "A"), ("B", "B")}

    inter_combos = set(
        zip(inter_links["Chain_id1"].tolist(), inter_links["Chain_id2"].tolist())
    )
    assert inter_combos == {("A", "B")}
