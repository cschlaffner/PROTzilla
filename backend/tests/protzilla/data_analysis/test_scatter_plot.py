import itertools

from backend.protzilla.data_analysis.plots import *
from backend.tests.protzilla.data_analysis.test_clustering import *


@pytest.fixture
def wide_2d_df():
    return pd.DataFrame(
        {
            "Sample": ["Sample1", "Sample2", "Sample3", "Sample4"],
            "Protein1": [4, 8, 2, 13],
            "Protein2": [10, 2, 7, 5],
        }
    )


@pytest.fixture
def wide_3d_df():
    return pd.DataFrame(
        {
            "Sample": ["Sample1", "Sample2", "Sample3", "Sample4"],
            "Protein1": [4, 8, 2, 13],
            "Protein2": [10, 2, 7, 5],
            "Protein3": [3, 4, 1, 7],
        }
    )


@pytest.fixture
def wide_4d_df():
    return pd.DataFrame(
        {
            "Sample": ["Sample1", "Sample2", "Sample3", "Sample4"],
            "Protein1": [4, 8, 2, 13],
            "Protein2": [10, 2, 7, 5],
            "Protein3": [3, 4, 1, 7],
            "Protein4": [2, 7, 4, 1],
        }
    )


@pytest.fixture
def metadata_df():
    return pd.DataFrame(
        np.array(
            [
                ["Sample1", "Group1", "Batch1"],
                ["Sample2", "Group2", "Batch2"],
                ["Sample3", "Group1", "Batch3"],
                ["Sample4", "Group1", "Batch10000230234456"],
            ]
        ),
        columns=["Sample", "Group", "Batch"],
    )


def check_figure_output(
    fig, expected_dims: int, expected_num_data_points: int, expected_nans_per_dim: tuple
):
    combined_x = list(itertools.chain.from_iterable([data.x for data in fig.data]))
    combined_y = list(itertools.chain.from_iterable([data.y for data in fig.data]))
    if expected_dims == 3:
        combined_z = list(itertools.chain.from_iterable([data.z for data in fig.data]))
    else:
        combined_z = []
    assert (
        len(combined_x) == expected_num_data_points
        and len(combined_y) == expected_num_data_points
        and (len(combined_z) == expected_num_data_points or expected_dims == 2)
    )
    assert (
        sum(pd.isna(x) for x in combined_x) == expected_nans_per_dim[0]
        and sum(pd.isna(y) for y in combined_y) == expected_nans_per_dim[1]
        and (
            expected_dims == 2
            or sum(pd.isna(z) for z in combined_z) == expected_nans_per_dim[2]
        )
    )


@pytest.mark.parametrize(
    "df_name,metadata_df_name,metadata_col",
    [
        ("wide_2d_df", None, None),
        ("wide_2d_df", "metadata_df", "Group"),
        ("wide_2d_df", "metadata_df", "Batch"),
        ("wide_3d_df", None, None),
        ("wide_3d_df", "metadata_df", "Group"),
        ("wide_3d_df", "metadata_df", "Batch"),
    ],
)
def test_scatter_plot(df_name, metadata_df_name, metadata_col, request):
    df = request.getfixturevalue(df_name)
    metadata_df = (
        request.getfixturevalue(metadata_df_name)
        if metadata_df_name is not None
        else None
    )
    outputs = scatter_plot(df, metadata_df, metadata_col)
    assert "plots" in outputs and len(outputs["plots"]) == 1
    fig = outputs["plots"][0]
    check_figure_output(
        fig,
        expected_num_data_points=df.shape[0],
        expected_dims=df.shape[1] - 1,
        expected_nans_per_dim=tuple(0 for _ in range(df.shape[1] - 1)),
    )


def test_scatter_plot_1d_df(wide_2d_df, metadata_df):
    metadata_column = metadata_df.columns[1]
    df = wide_2d_df.drop(columns=["Protein2"])
    with pytest.raises(
        ValueError,
        match=f"The provided DataFrame has 1 dimensions, but only 2D or 3D data can be plotted.",
    ):
        _ = scatter_plot(df, metadata_df, metadata_column)


def test_scatter_plot_4d_df(wide_4d_df, metadata_df):
    metadata_column = metadata_df.columns[1]
    with pytest.raises(
        ValueError,
        match=f"The provided DataFrame has 4 dimensions, but only 2D or 3D data can be plotted.",
    ):
        _ = scatter_plot(wide_4d_df, metadata_df, metadata_column)


def test_scatter_plot_metadata_column_not_found(wide_2d_df, metadata_df):
    metadata_column = "NonExistingColumn"
    with pytest.raises(
        ValueError,
        match="The column selected for annotation is not present in the corresponding metadata dataframe.",
    ):
        _ = scatter_plot(wide_2d_df, metadata_df, metadata_column)


def test_scatter_plot_missing_values_2d(wide_2d_df, metadata_df):
    metadata_column = metadata_df.columns[1]
    df_with_nan = wide_2d_df.copy()
    df_with_nan.loc[0, "Protein1"] = np.nan
    df_with_nan.loc[2, "Protein2"] = np.nan

    outputs = scatter_plot(df_with_nan, metadata_df, metadata_column)
    assert "plots" in outputs and len(outputs["plots"]) == 1
    fig = outputs["plots"][0]
    check_figure_output(
        fig,
        expected_num_data_points=df_with_nan.shape[0],
        expected_dims=2,
        expected_nans_per_dim=(1, 1),
    )


def test_scatter_plot_missing_values_3d(wide_3d_df, metadata_df):
    metadata_column = metadata_df.columns[1]
    df_with_nan = wide_3d_df.copy()
    df_with_nan.loc[1, "Protein1"] = np.nan
    df_with_nan.loc[3, "Protein3"] = np.nan

    outputs = scatter_plot(df_with_nan, metadata_df, metadata_column)
    assert "plots" in outputs and len(outputs["plots"]) == 1
    fig = outputs["plots"][0]
    check_figure_output(
        fig,
        expected_num_data_points=df_with_nan.shape[0],
        expected_dims=3,
        expected_nans_per_dim=(1, 0, 1),
    )


def test_scatter_plot_non_numeric_data_2d(wide_2d_df, metadata_df):
    metadata_column = metadata_df.columns[1]
    df_non_numeric = wide_2d_df.copy()
    df_non_numeric["Protein1"] = ["A", "B", "C", "D"]

    with pytest.raises(
        ValueError,
        match="All columns used for the 2D scatter plot must be numeric.",
    ):
        _ = scatter_plot(df_non_numeric, metadata_df, metadata_column)


def test_scatter_plot_non_numeric_data_3d(wide_3d_df, metadata_df):
    metadata_column = metadata_df.columns[1]
    df_non_numeric = wide_3d_df.copy()
    df_non_numeric["Protein1"] = ["A", "B", "C", "D"]

    with pytest.raises(
        ValueError,
        match="All columns used for the 3D scatter plot must be numeric.",
    ):
        _ = scatter_plot(df_non_numeric, metadata_df, metadata_column)
