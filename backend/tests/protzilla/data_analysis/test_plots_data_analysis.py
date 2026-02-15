import numpy as np
import pytest

from backend.protzilla.data_analysis.plots import *
from backend.tests.protzilla.data_analysis.test_clustering import *
from backend.protzilla.data_preprocessing.plots import create_histograms


@pytest.fixture
def wide_2d_df():
    return pd.DataFrame(
        np.array(
            [
                [4, 10],
                [8, 2],
                [2, 7],
                [13, 5],
            ]
        ),
        columns=["Protein1", "Protein2"],
        index=["Sample1", "Sample2", "Sample3", "Sample4"],
    )


@pytest.fixture
def wide_3d_df():
    return pd.DataFrame(
        np.array(
            [
                [4, 10, 3],
                [8, 2, 4],
                [2, 7, 1],
                [13, 5, 7],
            ]
        ),
        columns=["Protein1", "Protein2", "Protein3"],
        index=["Sample1", "Sample2", "Sample3", "Sample4"],
    )


@pytest.fixture
def wide_4d_df():
    return pd.DataFrame(
        np.array(
            [
                [4, 10, 3, 2],
                [8, 2, 4, 7],
                [2, 7, 1, 4],
                [13, 5, 7, 1],
            ]
        ),
        columns=["Protein1", "Protein2", "Protein3", "Protein4"],
        index=["Sample1", "Sample2", "Sample3", "Sample4"],
    )


@pytest.fixture
def color_df():
    return pd.DataFrame(
        np.array(
            [
                ["Color1"],
                ["Color2"],
                ["Color1"],
                ["Color1"],
            ]
        ),
        columns=["Color"],
        index=["Sample1", "Sample2", "Sample3", "Sample4"],
    )


@pytest.fixture
def metadata_df():
    return pd.DataFrame(
        np.array(
            [
                ["Sample1", "Group1"],
                ["Sample2", "Group2"],
                ["Sample3", "Group1"],
                ["Sample4", "Group1"],
            ]
        ),
        columns=["Sample", "Group"],
    )


def test_scatter_plot_2d(show_figures, wide_2d_df, color_df):
    outputs = scatter_plot(wide_2d_df, color_df)
    assert "plots" in outputs
    fig = outputs["plots"][0]
    if show_figures:
        fig.show()
    return


def test_scatter_plot_no_color_df(show_figures, wide_2d_df):
    outputs = scatter_plot(wide_2d_df)
    assert "plots" in outputs
    fig = outputs["plots"][0]
    if show_figures:
        fig.show()
    return


def test_scatter_plot_3d(show_figures, wide_3d_df, color_df):
    outputs = scatter_plot(wide_3d_df, color_df)
    assert "plots" in outputs
    fig = outputs["plots"][0]
    if show_figures:
        fig.show()
    return


def test_scatter_plot_4d_df(wide_4d_df, color_df):
    outputs = scatter_plot(wide_4d_df, color_df)

    assert "messages" in outputs
    assert "plots" not in outputs
    assert any(
        "Consider reducing the dimensionality" in message["msg"]
        for message in outputs["messages"]
    )


def test_scatter_plot_color_df_2d(show_figures, wide_2d_df):
    outputs = scatter_plot(wide_2d_df, wide_2d_df)
    assert "messages" in outputs
    assert "plots" not in outputs
    assert any(
        "The color dataframe should have 1 dimension only" in message["msg"]
        for message in outputs["messages"]
    )


def test_prot_quant_plot(show_figures, wide_4d_df):
    outputs = prot_quant_plot(wide_4d_df, "Protein1")
    assert "plots" in outputs
    fig = outputs["plots"][0]
    if show_figures:
        fig.show()
    return


def test_clustergram(show_figures, wide_4d_df, metadata_df):
    outputs = clustergram_plot(
        wide_4d_df, metadata_df, metadata_column="Group", flip_axes=False
    )
    assert "plots" in outputs
    fig = outputs["plots"][0]
    if show_figures:
        fig.show()
    return


def test_clustergram_no_metadata(show_figures, wide_4d_df):
    outputs = clustergram_plot(wide_4d_df, metadata_df=None, flip_axes=False)
    assert "plots" in outputs
    fig = outputs["plots"][0]
    if show_figures:
        fig.show()


def test_clustergram_nans_in_input(wide_4d_df):
    nan_df = wide_4d_df.copy()
    nan_df.iloc[0, 0] = np.nan

    outputs = clustergram_plot(nan_df, metadata_df=None, flip_axes=False)
    assert "messages" in outputs
    assert "plots" not in outputs
    assert any(
        "The selected input dataframe contains missing values." in message["msg"]
        for message in outputs["messages"]
    )


def test_clustergram_input_not_right_type(wide_4d_df):
    outputs1 = clustergram_plot([1, 2, 3, 4, 5], metadata_df=None, flip_axes=False)
    outputs2 = clustergram_plot(
        wide_4d_df, metadata_df=[1, 2, 3, 4, 5], flip_axes=False
    )
    assert "messages" in outputs1
    assert "plots" not in outputs1
    assert any(
        'The selected input for "input dataframe" is not a dataframe' in message["msg"]
        for message in outputs1["messages"]
    )

    assert "messages" in outputs2
    assert "plots" not in outputs2
    assert any(
        'The selected input for "metadata dataframe" is not a dataframe, '
        in message["msg"]
        for message in outputs2["messages"]
    )


def test_clustergram_dimension_mismatch(wide_4d_df):
    metadata_df_5_samples = pd.DataFrame(
        np.array(
            [
                ["Sample1", "Group1"],
                ["Sample2", "Group2"],
                ["Sample3", "Group1"],
                ["Sample4", "Group1"],
                ["Sample5", "Group3"],
            ]
        ),
        columns=["Sample", "Group"],
    )
    outputs = clustergram_plot(
        wide_4d_df, metadata_df_5_samples, metadata_column="Group", flip_axes=False
    )
    assert "plots" in outputs

    metadata_df_3_samples = pd.DataFrame(
        np.array(
            [
                ["Sample1", "Group1"],
                ["Sample2", "Group2"],
                ["Sample3", "Group1"],
            ]
        ),
        columns=["Sample", "Group"],
    )
    outputs = clustergram_plot(
        wide_4d_df, metadata_df_3_samples, metadata_column="Group", flip_axes=False
    )
    assert "messages" in outputs
    assert "plots" not in outputs
    assert any(
        "The input dataframe and the grouping contain different samples"
        in message["msg"]
        for message in outputs["messages"]
    )


def test_clustergram_different_samples(wide_4d_df):
    metadata_df_different_samples = pd.DataFrame(
        np.array(
            [
                ["Sample1", "Group1"],
                ["Sample2", "Group2"],
                ["Sample5", "Group1"],
                ["Sample4", "Group1"],
            ]
        ),
        columns=["Sample", "Group"],
    )
    outputs = clustergram_plot(
        wide_4d_df,
        metadata_df_different_samples,
        metadata_column="Group",
        flip_axes=False,
    )
    assert "messages" in outputs
    assert "plots" not in outputs
    assert any(
        "The input dataframe and the grouping contain different samples"
        in message["msg"]
        for message in outputs["messages"]
    )


def test_clustergram_no_matching_metadata_column(wide_4d_df, metadata_df):
    outputs = clustergram_plot(
        wide_4d_df,
        metadata_df,
        metadata_column="DefinitelyNotAValidColuuuuuuuuuuuuuuuuuuuumn",
        flip_axes=False,
    )
    assert "plots" not in outputs
    assert "messages" in outputs
    assert any(
        "The column selected for annotation is not present in the corresponding metadata dataframe"
        in message["msg"]
        for message in outputs["messages"]
    )


def test_clustergram_flip_axes(show_figures, wide_4d_df, metadata_df):
    outputs = clustergram_plot(
        wide_4d_df, metadata_df, metadata_column="Group", flip_axes=True
    )
    assert "plots" in outputs
    fig = outputs["plots"][0]
    if show_figures:
        fig.show()
    return


def test_create_histograms_one_bin_per_int_is_true():

    df_a = pd.DataFrame({"value": [1.2, 2.7, 3.5]})
    df_b = pd.DataFrame({"value": [2.1, 4.6, 5.9]})

    fig = create_histograms(
        dataframe_a=df_a,
        dataframe_b=df_b,
        relevant_column_a="value",
        relevant_column_b="value",
        name_a="A",
        name_b="B",
        one_bin_per_int=True,
    )

    trace_a = fig.data[0]
    trace_b = fig.data[1]

    # Check bin size is 1
    assert trace_a.xbins["size"] == 1
    assert trace_b.xbins["size"] == 1

    # Check min and max are rounded correctly
    # min_value should be floor(min(values_a.min(), values_b.min())) = floor(1.2) = 1
    # max_value should be ceil(max(values_a.max(), values_b.max())) = ceil(5.9) = 6
    assert trace_a.xbins["start"] == 1
    assert trace_a.xbins["end"] == 6
    assert trace_b.xbins["start"] == 1
    assert trace_b.xbins["end"] == 6


def test_create_histograms_with_empty_dataframe():
    df_empty = pd.DataFrame({"value": []})
    df_nonempty = pd.DataFrame({"value": [1, 2, 3]})

    fig = create_histograms(
        dataframe_a=df_empty,
        dataframe_b=df_nonempty,
        relevant_column_a="value",
        relevant_column_b="value",
        name_a="Empty",
        name_b="NonEmpty",
        one_bin_per_int=True,
    )

    trace_empty = fig.data[0]
    trace_nonempty = fig.data[1]

    # Ensure the function did not crash and returned a Figure
    assert isinstance(fig, Figure)

    # Even if dataframe_a is empty, trace_a should exist with default bin size 1
    assert trace_empty.xbins["size"] == 1

    # trace_b should have correct start/end bin values
    assert trace_nonempty.xbins["start"] == 1  # floor(min(values_b)) = 1
    assert trace_nonempty.xbins["end"] == 3  # ceil(max(values_b)) = 3
    assert trace_nonempty.xbins["size"] == 1


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
