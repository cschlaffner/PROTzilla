from backend.protzilla.data_analysis.plots import *
from backend.tests.protzilla.data_analysis.test_clustering import *
from clusteredheatmap.algos.distance import DistanceError


@pytest.fixture
def wide_4d_df():
    df = pd.DataFrame(
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

    return df.melt(
        var_name="Protein ID", value_name="Intensity", ignore_index=False
    ).reset_index(names="Sample")


@pytest.fixture
def same_data_4d_df():
    df = pd.DataFrame(
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

    return df.melt(
        var_name="Protein ID", value_name="Intensity", ignore_index=False
    ).reset_index(names="Sample")


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


@pytest.fixture
def enrichment_df_string():
    return pd.DataFrame(
        np.array(
            [
                ["GO:0", "Protein1,Protein2", "cool protein"],
                ["GO:1", "Protein2,Protein3", "rock"],
            ]
        ),
        columns=["term", "inputGenes", "description"],
    )


def test_chm(show_figures, wide_4d_df, metadata_df):
    outputs = clusteredheatmap_plot(
        wide_4d_df,
        metadata_df,
        metadata_column_samplegroupings=["Group"],
        flip_axes=False,
    )
    assert "plots" in outputs
    fig = outputs["plots"][0]
    if show_figures:
        fig.show()
    return


def test_chm_no_metadata(show_figures, wide_4d_df):
    outputs = clusteredheatmap_plot(wide_4d_df, metadata_df=None, flip_axes=False)
    assert "plots" in outputs
    fig = outputs["plots"][0]
    if show_figures:
        fig.show()


def test_chm_nans_in_input(wide_4d_df):
    nan_df = wide_4d_df.copy()
    nan_df.iloc[0, 0] = np.nan

    with pytest.raises(ValueError) as e:
        outputs = clusteredheatmap_plot(nan_df, metadata_df=None, flip_axes=False)

    assert "Error in distance calculation" in str(e)


def test_chm_nans_in_input_cc(wide_4d_df, show_figures):
    nan_df = wide_4d_df.copy()
    nan_df.iloc[0, 2] = np.nan

    outputs = clusteredheatmap_plot(
        nan_df, use_completecase_analysis=True, metadata_df=None, flip_axes=False
    )
    assert "plots" in outputs
    fig = outputs["plots"][0]
    if show_figures:
        fig.show()


def test_chm_nans_in_input_cc_failurecriterion(wide_4d_df, show_figures):
    nan_df = wide_4d_df.copy()
    nan_df.iloc[0, 2] = np.nan
    nan_df.iloc[4, 2] = np.nan
    nan_df.iloc[9, 2] = np.nan
    nan_df.iloc[13, 2] = np.nan

    with pytest.raises(DistanceError) as e:
        outputs = clusteredheatmap_plot(
            nan_df, use_completecase_analysis=True, metadata_df=None, flip_axes=False
        )

    assert "cannot estimate distance" in str(e)


def test_chm_nans_in_input_good_method(wide_4d_df, show_figures):
    nan_df = wide_4d_df.copy()
    nan_df.iloc[0, 0] = np.nan

    outputs = clusteredheatmap_plot(
        nan_df, distance_method="nandist_euclidean", metadata_df=None, flip_axes=False
    )
    assert "plots" in outputs
    fig = outputs["plots"][0]
    if show_figures:
        fig.show()


def test_chm_invalid_color_scale(wide_4d_df):
    with pytest.raises(ValueError) as exc_info:
        clusteredheatmap_plot(
            wide_4d_df,
            metadata_df=None,
            flip_axes=False,
            heatmap_zmin=1.0,
            heatmap_zmax=1.0,
        )
    assert "must be in increasing order" in str(exc_info.value)


def test_chm_dimension_mismatch(wide_4d_df):
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
    outputs = clusteredheatmap_plot(
        wide_4d_df,
        metadata_df_5_samples,
        metadata_column_samplegroupings=["Group"],
        flip_axes=False,
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
    outputs = clusteredheatmap_plot(
        wide_4d_df,
        metadata_df_3_samples,
        metadata_column_samplegroupings=["Group"],
        flip_axes=False,
    )
    assert "plots" in outputs


def test_chm_different_samples(wide_4d_df):
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
    outputs = clusteredheatmap_plot(
        wide_4d_df,
        metadata_df_different_samples,
        metadata_column_samplegroupings=["Group"],
        flip_axes=False,
    )
    assert "plots" in outputs


def test_chm_flip_axes(show_figures, wide_4d_df, metadata_df):
    outputs = clusteredheatmap_plot(
        wide_4d_df,
        metadata_df,
        metadata_column_samplegroupings=["Group"],
        flip_axes=True,
    )
    assert "plots" in outputs
    fig = outputs["plots"][0]
    if show_figures:
        fig.show()
    return


def test_chm_enrichment(show_figures, wide_4d_df, enrichment_df_string):
    outputs = clusteredheatmap_plot(
        wide_4d_df,
        enrichment_df=enrichment_df_string,
    )
    assert "plots" in outputs
    fig = outputs["plots"][0]
    if show_figures:
        fig.show()
    return
