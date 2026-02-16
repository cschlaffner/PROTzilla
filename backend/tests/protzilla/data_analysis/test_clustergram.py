from backend.protzilla.data_analysis.plots import *
from backend.tests.protzilla.data_analysis.test_clustering import *


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
def same_data_4d_df():
    return pd.DataFrame(
        np.array(
            [
                [5, 5, 5, 5],
                [5, 5, 5, 5],
                [5, 5, 5, 5],
                [5, 5, 5, 5],
            ]
        ),
        columns=["Protein1", "Protein2", "Protein3", "Protein4"],
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


def test_clustergram_identical_data(same_data_4d_df):
    with pytest.raises(ValueError) as exc_info:
        clustergram_plot(
            same_data_4d_df,
            metadata_df=None,
            flip_axes=False,
            heatmap_low_color_limit=0.0,
            heatmap_high_color_limit=7.0,
        )
    assert (
        str(exc_info.value) == "Data consists only of identical values. Not plotting."
    )


def test_clustergram_invalid_color_scale(wide_4d_df):
    with pytest.raises(ValueError) as exc_info:
        clustergram_plot(
            wide_4d_df,
            metadata_df=None,
            flip_axes=False,
            use_custom_color_scale=True,
            heatmap_low_color_limit=1.0,
            heatmap_high_color_limit=1.0,
        )
    assert (
        str(exc_info.value)
        == "Lower colour limit must be less than higher colour limit."
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
