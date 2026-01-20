import pandas as pd
import pytest

from backend.protzilla.data_analysis.dimension_reduction import t_sne, umap


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
def tsne_assertion_df_2d():
    assertion_tsne_list = (
        ["Sample1", -664.979919, 230.476990],
        ["Sample2", -331.823853, 792.581787],
        ["Sample3", -945.627319, 948.698303],
        ["Sample4", 1057.182739, -454.083984],
        ["Sample5", 506.428101, -61.508503],
        ["Sample6", 201.733047, -738.819336],
        ["Sample7", 201.733047, -738.819336],
    )
    tsne_assertion_df = pd.DataFrame(
        data=assertion_tsne_list,
        columns=["Sample", "Component1", "Component2"],
    )

    return tsne_assertion_df


@pytest.fixture
def tsne_assertion_df_3d():
    assertion_tsne_list = (
        ["Sample1", -185.471146, 40.492714, 61.039135],
        ["Sample2", -109.450661, -86.972496, -115.099686],
        ["Sample3", 129.066925, 148.503708, 58.841263],
        ["Sample4", 111.788994, -110.931160, -13.378016],
        ["Sample5", -1.360091, -72.723167, 67.371521],
        ["Sample6", 49.287201, 15.484677, -90.011147],
        ["Sample7", -32.561390, 66.274124, 57.044739],
    )
    tsne_assertion_df = pd.DataFrame(
        data=assertion_tsne_list,
        columns=["Sample", "Component1", "Component2", "Component3"],
    )

    return tsne_assertion_df


@pytest.mark.parametrize(
    "df,n_components,assertion_df",
    [
        ("dimension_reduction_df", 2, "tsne_assertion_df_2d"),
        ("dimension_reduction_four_proteins_df", 3, "tsne_assertion_df_3d"),
    ],
)
def test_tsne_reproducibility(df, n_components, assertion_df, request):
    current_out = t_sne(
        request.getfixturevalue(df),
        n_components=n_components,
        perplexity=4,
        random_state=42,
    )

    pd.testing.assert_frame_equal(
        current_out["embedded_data"],
        request.getfixturevalue(assertion_df),
        check_dtype=False,
    )


def test_tsne_nan_handling(df_with_nan):
    with pytest.raises(
        ValueError,
        match="T-SNE does not accept missing values encoded as NaN. Consider preprocessing your data to remove NaN "
        "values.",
    ):
        _ = t_sne(
            df_with_nan,
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
            n_components=8,
            perplexity=4,
            random_state=42,
            method="exact",
        )


def test_tsne_n_components_barnes_hut(dimension_reduction_four_proteins_df):
    with pytest.raises(
        ValueError,
        match="The number of dimensions should be smaller than 4 because the underlying algorithm does not"
        " support a higher number of dimensions.",
    ):
        _ = t_sne(
            dimension_reduction_four_proteins_df,
            n_components=4,
            perplexity=4,
            random_state=42,
        )


@pytest.mark.parametrize(
    "n_components",
    [2, 3],
)
def test_umap_reproducibility(dimension_reduction_df, n_components):
    current_out = umap(
        dimension_reduction_df,
        n_components=n_components,
        n_neighbors=3,
        random_state=42,
        transform_seed=42,
    )
    # Unfortunately, UMAP results vary slightly between runs even with the same random seed, which makes exact
    # comparison impossible. Therefore, we only check the shape and types here.
    assert (
        current_out["embedded_data"].shape
        == (dimension_reduction_df["Sample"].nunique(), n_components + 1)
        and current_out["embedded_data"]["Sample"].sort_values().tolist()
        == sorted(dimension_reduction_df["Sample"].unique())
        and pd.api.types.is_numeric_dtype(current_out["embedded_data"]["Component1"])
        and pd.api.types.is_numeric_dtype(current_out["embedded_data"]["Component2"])
        and not current_out["embedded_data"][["Component1", "Component2"]]
        .isnull()
        .values.any()
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
