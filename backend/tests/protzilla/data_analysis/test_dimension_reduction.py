import numpy as np
import pandas as pd
import pytest

from backend.protzilla.data_analysis.dimension_reduction import t_sne, umap
from protzilla.data_analysis.plots import scatter_plot
from protzilla.methods.data_analysis import DimensionReductionMetric, TSNEMethod
from tests.protzilla.data_analysis.test_scatter_plot import check_figure_output


@pytest.fixture
def dimension_reduction_df():
    dimension_reduction_list = (
        ["Sample1", "Protein1", "Gene1", 18],
        ["Sample1", "Protein2", "Gene1", 16],
        ["Sample1", "Protein3", "Gene1", 1],
        ["Sample2", "Protein1", "Gene1", 20],
        ["Sample2", "Protein2", "Gene1", 18],
        ["Sample2", "Protein3", "Gene1", 2],
        ["Sample3", "Protein1", "Gene1", 22],
        ["Sample3", "Protein2", "Gene1", 19],
        ["Sample3", "Protein3", "Gene1", 3],
        ["Sample4", "Protein1", "Gene1", 8],
        ["Sample4", "Protein2", "Gene1", 15],
        ["Sample4", "Protein3", "Gene1", 1],
        ["Sample5", "Protein1", "Gene1", 10],
        ["Sample5", "Protein2", "Gene1", 14],
        ["Sample5", "Protein3", "Gene1", 2],
        ["Sample6", "Protein1", "Gene1", 12],
        ["Sample6", "Protein2", "Gene1", 13],
        ["Sample6", "Protein3", "Gene1", 3],
        ["Sample7", "Protein1", "Gene1", 12],
        ["Sample7", "Protein2", "Gene1", 13],
        ["Sample7", "Protein3", "Gene1", 3],
    )

    dimension_reduction_df = pd.DataFrame(
        data=dimension_reduction_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    return dimension_reduction_df


@pytest.fixture
def dimension_reduction_four_proteins_df():
    dimension_reduction_list = (
        ["Sample1", "Protein1", "Gene1", 18],
        ["Sample1", "Protein2", "Gene1", 16],
        ["Sample1", "Protein3", "Gene1", 1],
        ["Sample1", "Protein4", "Gene1", 13],
        ["Sample1", "Protein5", "Gene1", 13],
        ["Sample2", "Protein1", "Gene1", 20],
        ["Sample2", "Protein2", "Gene1", 18],
        ["Sample2", "Protein3", "Gene1", 2],
        ["Sample2", "Protein4", "Gene1", 4],
        ["Sample2", "Protein5", "Gene1", 13],
        ["Sample3", "Protein1", "Gene1", 22],
        ["Sample3", "Protein2", "Gene1", 19],
        ["Sample3", "Protein3", "Gene1", 3],
        ["Sample3", "Protein4", "Gene1", 7],
        ["Sample3", "Protein5", "Gene1", 13],
        ["Sample4", "Protein1", "Gene1", 8],
        ["Sample4", "Protein2", "Gene1", 15],
        ["Sample4", "Protein3", "Gene1", 1],
        ["Sample4", "Protein4", "Gene1", 7],
        ["Sample4", "Protein5", "Gene1", 13],
        ["Sample5", "Protein1", "Gene1", 10],
        ["Sample5", "Protein2", "Gene1", 14],
        ["Sample5", "Protein3", "Gene1", 2],
        ["Sample5", "Protein4", "Gene1", 8],
        ["Sample5", "Protein5", "Gene1", 13],
        ["Sample6", "Protein1", "Gene1", 12],
        ["Sample6", "Protein2", "Gene1", 13],
        ["Sample6", "Protein3", "Gene1", 3],
        ["Sample6", "Protein4", "Gene1", 3],
        ["Sample6", "Protein5", "Gene1", 13],
        ["Sample7", "Protein1", "Gene1", 12],
        ["Sample7", "Protein2", "Gene1", 13],
        ["Sample7", "Protein3", "Gene1", 3],
        ["Sample7", "Protein4", "Gene1", 10],
        ["Sample7", "Protein5", "Gene1", 13],
    )

    dimension_reduction_df = pd.DataFrame(
        data=dimension_reduction_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    return dimension_reduction_df


@pytest.fixture
def metadata_df():
    return pd.DataFrame(
        np.array(
            [
                ["Sample1", "Group1", "Batch1"],
                ["Sample2", "Group2", "Batch2"],
                ["Sample3", "Group1", "Batch3"],
                ["Sample4", "Group1", "Batch10000230234456"],
                ["Sample5", "Group2", "Batch2"],
                ["Sample6", "Group1", "Batch2"],
                ["Sample7", "1puorG", "Batch3"],
            ]
        ),
        columns=["Sample", "Group", "Batch"],
    )


def check_dimensionality_reduction_output(
    out_df: pd.DataFrame, orig_df: pd.DataFrame, n_components: int
):
    assert (
        out_df.shape == (orig_df["Sample"].nunique(), n_components + 1)
        and out_df["Sample"].sort_values().tolist()
        == sorted(orig_df["Sample"].unique())
        and all(
            (
                pd.api.types.is_numeric_dtype(out_df[f"Component{i + 1}"])
                for i in range(n_components)
            )
        )
        and not out_df[[f"Component{i + 1}" for i in range(n_components)]]
        .isnull()
        .values.any()
    )


@pytest.mark.parametrize(
    "df_name,n_components,method",
    [
        ("dimension_reduction_df", 2, TSNEMethod.exact.value),
        ("dimension_reduction_four_proteins_df", 3, TSNEMethod.exact.value),
        ("dimension_reduction_df", 2, TSNEMethod.barnes_hut.value),
        ("dimension_reduction_four_proteins_df", 3, TSNEMethod.barnes_hut.value),
    ],
)
def test_tsne_metrics(df_name, n_components, method, request):
    for metric in DimensionReductionMetric:
        df = request.getfixturevalue(df_name)
        current_out = t_sne(
            df,
            method=method,
            n_components=n_components,
            perplexity=4,
            metric=metric.value,
            random_state=42,
        )
        check_dimensionality_reduction_output(
            current_out["embedded_data"], df, n_components
        )


def test_tsne_nan_handling(df_with_nan):
    with pytest.raises(
        ValueError,
        match="T-SNE does not accept missing values encoded as NaN. Consider preprocessing your data to remove NaN "
        "values.",
    ):
        _ = t_sne(
            df_with_nan,
            method=TSNEMethod.barnes_hut.value,
            n_components=2,
            perplexity=4,
        )


def test_tsne_perplexity(dimension_reduction_df):
    with pytest.raises(
        ValueError,
        match="Perplexity must be less than the number of samples. In the selected dataframe there "
        f"is {dimension_reduction_df['Sample'].nunique()} samples",
    ):
        _ = t_sne(
            dimension_reduction_df,
            method=TSNEMethod.barnes_hut.value,
            n_components=2,
            perplexity=30,
        )


def test_tsne_n_components(dimension_reduction_df):
    with pytest.raises(
        ValueError,
        match="The number of dimensions of the embedded space must be between 1 and "
        f"{min(dimension_reduction_df['Sample'].nunique(), dimension_reduction_df['Protein ID'].nunique())}",
    ):
        _ = t_sne(
            dimension_reduction_df,
            method="exact",
            n_components=8,
            perplexity=4,
            random_state=42,
        )


def test_tsne_n_components_barnes_hut(dimension_reduction_four_proteins_df):
    with pytest.raises(
        ValueError,
        match="The number of dimensions should be smaller than 4 because the underlying algorithm does not"
        " support a higher number of dimensions.",
    ):
        _ = t_sne(
            dimension_reduction_four_proteins_df,
            method=TSNEMethod.barnes_hut.value,
            n_components=4,
            perplexity=4,
            random_state=42,
        )


@pytest.mark.parametrize(
    "df_name,method,n_components,metadata_column",
    [
        ("dimension_reduction_df", TSNEMethod.exact.value, 2, "Group"),
        ("dimension_reduction_four_proteins_df", TSNEMethod.exact.value, 3, "Group"),
        ("dimension_reduction_df", TSNEMethod.exact.value, 2, "Batch"),
        ("dimension_reduction_four_proteins_df", TSNEMethod.exact.value, 3, "Batch"),
        ("dimension_reduction_df", TSNEMethod.barnes_hut.value, 2, "Group"),
        ("dimension_reduction_four_proteins_df", TSNEMethod.barnes_hut.value, 3, "Batch"),
    ],
)
def test_tsne_scatter_plot_integration(
    df_name, method, n_components, metadata_column, metadata_df, request
):
    df = request.getfixturevalue(df_name)
    tsne_out = t_sne(
        df,
        method=TSNEMethod.exact.value,
        n_components=n_components,
        perplexity=4,
        random_state=42,
    )
    outputs = scatter_plot(
        tsne_out["embedded_data"],
        metadata_df,
        metadata_column,
    )
    check_figure_output(
        outputs["plots"][0],
        expected_num_data_points=df["Sample"].nunique(),
        expected_dims=n_components,
        expected_nans_per_dim=tuple(0 for _ in range(n_components)),
    )


@pytest.mark.parametrize(
    "n_components",
    [2, 3],
)
def test_umap(dimension_reduction_df, n_components):
    # Unfortunately, UMAP results vary slightly between runs even with the same random seed, which makes exact
    # comparison impossible. Therefore, we only check the shape and types here.
    for metric in DimensionReductionMetric:
        current_out = umap(
            dimension_reduction_df,
            n_components=n_components,
            metric=metric.value,
            n_neighbors=3,
            random_state=42,
            transform_seed=42,
        )
        check_dimensionality_reduction_output(
            current_out["embedded_data"], dimension_reduction_df, n_components
        )


def test_umap_nan_handling(df_with_nan):
    with pytest.raises(
        ValueError,
        match="UMAP does not accept missing values encoded as NaN. Consider preprocessing your data to remove NaN "
        "values.",
    ):
        _ = umap(
            df_with_nan,
        )


@pytest.mark.parametrize(
    "df_name,n_components,metadata_column",
    [
        ("dimension_reduction_df", 2, "Batch"),
        ("dimension_reduction_four_proteins_df", 3, "Batch"),
        ("dimension_reduction_df", 2, "Group"),
        ("dimension_reduction_four_proteins_df", 3, "Group"),
    ],
)
def test_umap_scatter_plot_integration(
    df_name, n_components, metadata_column, metadata_df, request
):
    df = request.getfixturevalue(df_name)
    umap_out = umap(
        df,
        n_components=n_components,
        n_neighbors=3,
        random_state=42,
        transform_seed=42,
    )
    outputs = scatter_plot(
        umap_out["embedded_data"],
        metadata_df,
        metadata_column,
    )
    check_figure_output(
        outputs["plots"][0],
        expected_num_data_points=df["Sample"].nunique(),
        expected_dims=n_components,
        expected_nans_per_dim=tuple(0 for _ in range(n_components)),
    )
