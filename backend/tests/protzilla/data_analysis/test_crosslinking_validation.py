import pandas as pd
import pytest
import logging
from unittest.mock import patch, MagicMock
import plotly.graph_objects as go
from plotly.graph_objects import Figure
import pandas.testing as pdt


from backend.protzilla.data_analysis.crosslinking_validation import (
    validate_with_angstrom_deviation,
    get_distance_between_two_amino_acids_in_angstrom,
    add_positions_of_amino_acid_where_crosslinker_bound_to_df,
    diagrams_of_crosslinking_validation_data,
)
from protzilla.data_analysis.plots import add_vertical_line_with_annotation_in_legend
from protzilla.methods.data_analysis import CrossLinkingValidationWithAngstromDeviation


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

    amino_acid_sequence_df = pd.DataFrame({"Protein Sequence": ["AB"]})

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
        protein_to_validate="P12345",
        crosslinker_information=crosslinker_information,
        amino_acid_sequence_df=amino_acid_sequence_df,
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
    assert vline["line"]["color"] == "blue"

    # There should be 1 scatter trace for the legend
    assert len(fig.data) == 1
    trace = fig.data[0]
    assert trace.mode == "lines"
    assert trace.name == "Test Line"
    assert trace.line.dash == "dash"
    assert trace.line.color == "blue"
    assert trace.x == (None,)
    assert trace.y == (None,)


def test_add_vertical_line_with_annotation_in_legend_adds_line_and_legend_multiple_calls():
    fig = go.Figure()
    add_vertical_line_with_annotation_in_legend(
        fig=fig, dash="dash", annotation="Line 1", x_value=1.0
    )
    add_vertical_line_with_annotation_in_legend(
        fig=fig, dash="dot", annotation="Line 2", x_value=2.0, color="green"
    )

    # Check layout.shapes -> add_vline internally adds a shape to layout.shapes
    assert len(fig.layout.shapes) == 2
    vlines_x = [shape.x0 for shape in fig.layout.shapes]
    assert vlines_x == [1.0, 2.0]
    vlines_colors = [shape["line"]["color"] for shape in fig.layout.shapes]
    assert vlines_colors == ["blue", "green"]
    vlines_dashes = [shape["line"]["dash"] for shape in fig.layout.shapes]
    assert vlines_dashes == ["dash", "dot"]

    # Check legend traces
    assert len(fig.data) == 2
    names = [trace.name for trace in fig.data]
    colors = [trace.line.color for trace in fig.data]
    dashes = [trace.line.dash for trace in fig.data]
    x_values = [trace.x for trace in fig.data]
    y_values = [trace.y for trace in fig.data]
    assert names == ["Line 1", "Line 2"]
    assert colors == ["blue", "green"]
    assert dashes == ["dash", "dot"]
    assert x_values == [(None,), (None,)]
    assert y_values == [(None,), (None,)]


@pytest.fixture
def sample_crosslinking_df():
    return pd.DataFrame(
        {
            "Crosslinker": ["CL1", "CL1", "CL2", "CL2"],
            "alphafold_distance": [10.0, 12.0, 8.0, 9.0],
            "valid_crosslink": [True, False, True, False],
            "Is_intra_crosslink": [True, False, True, False],
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
@patch(
    "backend.protzilla.data_analysis.crosslinking_validation.validate_with_angstrom_deviation"
)
def test_diagrams_of_crosslinking_validation_data_with_drawing_all_vertical_lines(
    mock_validate,
    mock_add_vline,
    mock_create_bar,
    mock_create_hist,
    sample_crosslinking_df,
    sample_crosslinker_info,
):
    validated_df = sample_crosslinking_df.copy()
    mock_validate.return_value = {"crosslinking_result_df": validated_df}

    hist_mock = Figure()
    mock_create_hist.return_value = hist_mock
    bar_mock = Figure()
    mock_create_bar.return_value = bar_mock

    figures = diagrams_of_crosslinking_validation_data(
        crosslinking_df=sample_crosslinking_df,
        protein_to_validate="P12345",
        crosslinker_information=sample_crosslinker_info,
    )

    # 2 histograms per crosslinker + 1 bar plot
    assert len(figures) == 5
    assert all(isinstance(f, Figure) for f in figures)

    mock_validate.assert_called_once_with(
        sample_crosslinking_df, "P12345", sample_crosslinker_info
    )

    assert (
        mock_add_vline.call_count == 8
    )  # for both crosslinkers: 1 call for crosslinker length for each histogram and 1 call for bound on deviation for each histogram

    # Check that create_histograms was called 4 times (2 per crosslinker)
    assert mock_create_hist.call_count == 4

    # Check that create_bar_plot was called once
    mock_create_bar.assert_called_once()


@pytest.fixture
def sample_crosslinking_df_with_no_std():
    return pd.DataFrame(
        {
            "Crosslinker": ["CL1", "CL1", "CL2", "CL2"],
            "alphafold_distance": [10.5, 10.5, 10.5, 10.5],
            "valid_crosslink": [True, False, True, False],
            "Is_intra_crosslink": [True, False, True, False],
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
@patch(
    "backend.protzilla.data_analysis.crosslinking_validation.validate_with_angstrom_deviation"
)
def test_diagrams_of_crosslinking_validation_data_without_drawing_all_vertical_lines(
    mock_validate,
    mock_add_vline,
    mock_create_bar,
    mock_create_hist,
    sample_crosslinking_df_with_no_std,
    sample_crosslinker_info_matching_sample_crosslinking_df_with_no_std,
):
    validated_df = sample_crosslinking_df_with_no_std.copy()
    mock_validate.return_value = {"crosslinking_result_df": validated_df}

    hist_mock = Figure()
    mock_create_hist.return_value = hist_mock
    bar_mock = Figure()
    mock_create_bar.return_value = bar_mock

    figures = diagrams_of_crosslinking_validation_data(
        crosslinking_df=sample_crosslinking_df_with_no_std,
        protein_to_validate="P12345",
        crosslinker_information=sample_crosslinker_info_matching_sample_crosslinking_df_with_no_std,
    )

    # 2 histograms per crosslinker + 1 bar plot
    assert len(figures) == 5
    assert all(isinstance(f, Figure) for f in figures)

    # CL1: all 3 lines are drawn for both histograms, CL2: only crosslinker_length ist drawn for both histograms,
    # the bounds are only drawn for the histogram that is not limited to the range of +- 2 standard deviations
    assert mock_add_vline.call_count == 10

    # Check that create_histograms was called 4 times (2 per crosslinker)
    assert mock_create_hist.call_count == 4

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
            "Is_intra_crosslink": [True, False, True, False],
        }
    )


def test_diagrams_calls_with_correct_parameters(
    sample_crosslinking_df_with_one_crosslinker,
    sample_crosslinker_info_with_one_crosslinker,
):
    with patch(
        "backend.protzilla.data_analysis.crosslinking_validation.validate_with_angstrom_deviation"
    ) as mock_validate, patch(
        "backend.protzilla.data_analysis.crosslinking_validation.create_histograms"
    ) as mock_hist, patch(
        "backend.protzilla.data_analysis.crosslinking_validation.add_vertical_line_with_annotation_in_legend"
    ) as mock_vline, patch(
        "backend.protzilla.data_analysis.crosslinking_validation.create_bar_plot"
    ) as mock_bar:

        mock_validate.return_value = {
            "crosslinking_result_df": sample_crosslinking_df_with_one_crosslinker
        }

        mock_hist.side_effect = lambda **kwargs: f"hist_{kwargs['heading']}"
        mock_bar.return_value = "bar_fig"

        figures = diagrams_of_crosslinking_validation_data(
            crosslinking_df=sample_crosslinking_df_with_one_crosslinker,
            protein_to_validate="P12345",
            crosslinker_information=sample_crosslinker_info_with_one_crosslinker,
        )

        mock_validate.assert_called_once_with(
            sample_crosslinking_df_with_one_crosslinker,
            "P12345",
            sample_crosslinker_info_with_one_crosslinker,
        )

        # There should be 2 histogram calls: 2 per crosslinker
        assert mock_hist.call_count == 2

        # Check histogram call parameters for crosslinker full-range
        first_hist_call = mock_hist.call_args_list[0].kwargs
        assert first_hist_call["name_a"] == "Valid Crosslinks"
        assert first_hist_call["name_b"] == "Invalid Crosslinks"
        assert first_hist_call["heading"] == "Predicted distances for P12345"
        assert first_hist_call["relevant_column_a"] == "alphafold_distance"
        assert first_hist_call["relevant_column_b"] == "alphafold_distance"
        assert first_hist_call["one_bin_per_int"] == True

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
        pdt.assert_frame_equal(first_hist_call["dataframe_a"], dataframe_a)
        pdt.assert_frame_equal(first_hist_call["dataframe_b"], dataframe_b)

        # Check histogram call parameters for crosslinker ±2 std
        second_hist_call = mock_hist.call_args_list[1].kwargs
        assert "mean +- 2 standard deviations" in second_hist_call["heading"]
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
        assert second_hist_call["min_value"] == mean_plus_minus_two_std_range[0]
        assert second_hist_call["max_value"] == mean_plus_minus_two_std_range[1]

        call_args_list = [call.kwargs for call in mock_vline.call_args_list]
        assert any(
            call["annotation"] == "CL1 length" and call["x_value"] == 11.0
            for call in call_args_list
        )

        mock_bar.assert_called_once()

        expected_figures = [
            "hist_Predicted distances for P12345, mean +- 2 standard deviations",
            "hist_Predicted distances for P12345",
            "bar_fig",
        ]
        assert figures == expected_figures
