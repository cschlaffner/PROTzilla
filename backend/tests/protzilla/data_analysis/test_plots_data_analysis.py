import numpy as np
import pytest

from backend.protzilla.data_analysis.plots import *
from backend.tests.protzilla.data_analysis.test_clustering import *


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
    # TODO: if scatterplot should be properly included, this fixture has to be adapted to mimic actual metadata, i.e. a
    #  df where samples are a column and not the index
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
    assert any("Consider reducing the dimensionality" in message["msg"] for message in outputs["messages"])


def test_scatter_plot_color_df_2d(show_figures, wide_2d_df):
    outputs = scatter_plot(wide_2d_df, wide_2d_df)
    assert "messages" in outputs
    assert "plots" not in outputs
    assert any("The color dataframe should have 1 dimension only" in message["msg"] for message in outputs["messages"])


def test_clustergram(show_figures, wide_4d_df, metadata_df):
    outputs = clustergram_plot(
        wide_4d_df,
        metadata_df,
        metadata_column='Group',
        flip_axes=False
    )
    assert "plots" in outputs
    fig = outputs["plots"][0]
    if show_figures:
        fig.show()
    return


def test_prot_quant_plot(show_figures, wide_4d_df):
    outputs = prot_quant_plot(wide_4d_df, "Protein1")
    assert "plots" in outputs
    fig = outputs["plots"][0]
    if show_figures:
        fig.show()
    return


def test_clustergram_no_metadata(show_figures, wide_4d_df):
    outputs = clustergram_plot(
        wide_4d_df,
        metadata_df=None,
        flip_axes=False
    )
    assert "plots" in outputs
    fig = outputs["plots"][0]
    if show_figures:
        fig.show()


def test_clustergram_input_not_right_type(wide_4d_df):
    outputs1 = clustergram_plot(
        [1, 2, 3, 4, 5],
        metadata_df=None,
        flip_axes=False
    )
    outputs2 = clustergram_plot(
        wide_4d_df,
        metadata_df=[1, 2, 3, 4, 5],
        flip_axes=False
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
        'The selected input for "grouping dataframe" is not a dataframe, ' in message["msg"]
        for message in outputs2["messages"])


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
        wide_4d_df,
        metadata_df_5_samples,
        metadata_column='Group',
        flip_axes=False
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
        wide_4d_df,
        metadata_df_3_samples,
        metadata_column='Group',
        flip_axes=False
    )
    assert "messages" in outputs
    assert "plots" not in outputs
    assert any(
        "The input dataframe and the grouping contain different samples" in message["msg"]
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
        metadata_column='Group',
        flip_axes=False
    )
    assert "messages" in outputs
    assert "plots" not in outputs
    assert any(
        "The input dataframe and the grouping contain different samples" in message["msg"]
        for message in outputs["messages"]
    )
