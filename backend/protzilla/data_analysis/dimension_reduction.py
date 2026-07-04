from enum import Enum

import pandas as pd
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import plotly.express as px
import logging

from backend.protzilla.utilities.transform_dfs import is_long_format, long_to_wide
from backend.protzilla.utilities.utilities import collect_col_for_sample_in_order


class TSNEMethod(Enum):
    barnes_hut = "Barnes-Hut approximation"
    exact = "exact"


def t_sne(
    protein_df: pd.DataFrame,
    method: str,
    n_components: int = 2,
    perplexity: float = 30.0,
    metric: str = "euclidean",
    random_state: int = 42,
    max_iter: int = 1000,
    n_iter_without_progress: int = 300,
):
    """
    A function that uses t-SNE to reduce the dimension of a dataframe and returns a
    dataframe in wide format with the entered number of components.
    Please note that this function is a simplified version of t-SNE, and it only
    enables you to adjust the most significant parameters that affect the output.
    You can find the default values for the non-adjustable parameters here:
    https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html

    :param protein_df: the dataframe, whose dimensions should be reduced.
    :type protein_df: pd.DataFrame
    :param n_components: The dimension of the space to embed into.
    :type n_components: int
    :param perplexity: the perplexity is related to the number of nearest neighbors
    :type perplexity: float
    :param metric: The metric to use when calculating distance between instances in a
        feature array. Possible metrics are: euclidean, manhattan, cosine and haversine
    :type metric: str
    :param random_state: determines the random number generator.
    :type random_state: int
    :param max_iter: maximum number of iterations for the optimization
    :type max_iter: int
    :param n_iter_without_progress: Maximum number of iterations without progress
        before we abort the optimization, used after 250 initial iterations with early
        exaggeration. Note that progress is only checked every 50 iterations so this
        value is rounded to the next multiple of 50.
    :type n_iter_without_progress: int
    :param method: the method 'exact' will run on the slower, but exact, algorithm in
        O(N^2) time. However, the 'exact' method cannot scale to millions of examples.
        Barnes-Hut approximation will run faster, but not exact, in O(NlogN) time.
    :type method: str
    :return: a dictionary with a single key, "embedded_data", which contains a new
        DataFrame in wide format. This DataFrame consists of the t-SNE embedded data
        with two columns, "Component1" and "Component2" and assigns these to the
        corresponding Sample.
    :rtype: dict
    """

    input_df = protein_df

    intensity_df_wide = (
        long_to_wide(input_df) if is_long_format(input_df) else input_df.copy()
    )
    if intensity_df_wide.isnull().sum().any():
        raise ValueError(
            "T-SNE does not accept missing values encoded as NaN. Consider preprocessing your data to remove NaN "
            "values."
        )
    if perplexity >= intensity_df_wide.shape[0]:
        raise ValueError(
            "Perplexity must be less than the number of samples. In the selected dataframe there "
            f"is {intensity_df_wide.shape[0]} samples"
        )
    if (
        min(intensity_df_wide.shape[0], intensity_df_wide.shape[1]) <= n_components
        or n_components <= 1
    ):
        raise ValueError(
            "The number of dimensions of the embedded space must be between 1 and "
            f"{min(intensity_df_wide.shape[0], intensity_df_wide.shape[1])} (the smaller one of number of "
            "samples/features). "
        )
    if n_components > 3 and method == TSNEMethod.barnes_hut.value:
        raise ValueError(
            "The number of dimensions should be smaller than 4 because the underlying algorithm does not"
            " support a higher number of dimensions."
        )

    embedded_data_model = TSNE(
        n_components=n_components,
        perplexity=perplexity,
        random_state=random_state,
        max_iter=max_iter,
        n_iter_without_progress=n_iter_without_progress,
        method=TSNEMethod(method).name,
        metric=metric,
    ).fit_transform(intensity_df_wide)

    embedded_data = pd.DataFrame(
        embedded_data_model,
        index=intensity_df_wide.index,
        columns=[f"Component{i+1}" for i in range(n_components)],
    ).reset_index()
    return dict(embedded_data=embedded_data)


def umap(
    protein_df: pd.DataFrame,
    n_neighbors: float = 15,
    n_components: int = 2,
    min_dist: float = 0.1,
    metric: str = "euclidean",
    random_state: int = 42,
    transform_seed: int = 42,
):
    """
    A function that uses UMAP to reduce the dimension of a dataframe and returns a
    dataframe in wide format with the entered number of components.
    Please note that this function is a simplified version of UMAP, and it only
    enables you to adjust the most significant parameters that affect the output.
    You can find the default values for the non-adjustable parameters here:
    https://umap-learn.readthedocs.io/en/latest/api.html

    :param protein_df: the dataframe, whose dimensions should be reduced.
    :type protein_df: pd.DataFrame
    :param n_components: The dimension of the space to embed into.
    :type n_components: int
    :param n_neighbors: The size of local neighborhood in terms of number of
        neighboring sample points
    :type n_neighbors: float
    :param min_dist: the effective minimum distance between embedded points. Smaller
        values will result in a more clustered/clumped embedding where nearby points on
        the manifold are drawn closer together, while larger values will result on a more
        even dispersal of points.
    :type min_dist: float
    :param metric: The metric to use when calculating distance between instances in a
        feature array.
    :type metric: str
    :param random_state: determines the random number generator.
    :type random_state: int
    :param transform_seed: Random seed used for the stochastic aspects of the transform
        operation.
    :type transform_seed: int
    :return: a dictionary with a single key, "embedded_data", which contains a new
        DataFrame in wide format. This DataFrame consists of the UMAP embedded data
        with two columns, "Component1" and "Component2", and assigns these to the
        corresponding Sample.
    :rtype: dict
    """

    # umap import is slow, so it should only get imported when needed
    from umap import UMAP

    input_df = protein_df

    intensity_df_wide = long_to_wide(input_df) if is_long_format(input_df) else input_df
    if intensity_df_wide.isnull().sum().any():
        raise ValueError(
            "UMAP does not accept missing values encoded as NaN. Consider preprocessing your data to remove NaN "
            "values."
        )
    embedded_data_model = UMAP(
        n_neighbors=n_neighbors,
        n_components=n_components,
        min_dist=min_dist,
        metric=metric,
        random_state=random_state,
        transform_seed=transform_seed,
    ).fit_transform(intensity_df_wide)

    embedded_data = pd.DataFrame(
        embedded_data_model,
        index=intensity_df_wide.index,
        columns=[f"Component{i+1}" for i in range(n_components)],
    ).reset_index()

    return dict(embedded_data=embedded_data)


colors = {
    "plot_bgcolor": "white",
    "gridcolor": "#F1F1F1",
    "linecolor": "#F1F1F1",
    "annotation_text_color": "#ffffff",
    "annotation_proteins_of_interest": "#4A536A",
}


def dimension_reduction_pca(
    protein_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    pca_threshold: float,
    color_col: str,
):
    """
    A function that performs Principle Components Analysis (PCA) on the protein data. It calculates all enough
    principle components to account for pca_threshold percent of the variance.

    :param protein_df: the dataframe, from which the principle components should be induced.
    :param metadata_df: the dataframe containing the metadata for the protein df.
    :param pca_threshold: The percentage of variance that should be explained by the principle components.
    :param color_col: the name of the column in metadata that should be colored in the scatter plot (e.g. Group, Batch, ...)

    :return: a dictionary with the dataframe which contains the principle components
    """
    wide_protein_df = long_to_wide(protein_df)

    pca = PCA(n_components=pca_threshold, svd_solver="full")
    pca_array = pca.fit_transform(wide_protein_df)

    pca_df = pd.DataFrame(
        {f"PC{i+1}": pca_array[:, i] for i in range(pca_array.shape[1])}
    )

    return {"pca_df": pca_df}


def pca_scatter_plot(
    protein_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    pca_threshold: float,
    color_col: str,
):
    """
    Creates the scatterplot for the principle components analysis. The PCA scatter plot only visualizes
    the first two principle components and colors the samples according to the column provided with color_col.

    :param protein_df: the dataframe, from which the principle components should be induced.
    :param metadata_df: the dataframe containing the metadata for the protein df.
    :param pca_threshold: The percentage of variance that should be explained by the principle components.
    :param color_col: the name of the column in metadata that should be colored in the scatter plot (e.g. Group, Batch, ...)

    :return: a dictionary with the dataframe which contains the principle components and the 2D scatter plot with the first
        two principle components
    """

    pca_df = dimension_reduction_pca(protein_df, metadata_df, pca_threshold, color_col)[
        "pca_df"
    ]

    wide_protein_df = long_to_wide(protein_df)
    samples = wide_protein_df.index
    color_column_list = collect_col_for_sample_in_order(
        samples=samples, metadata_df=metadata_df, col_name=color_col
    )

    if len(pca_df.columns) < 2:
        return {
            "pca_df": pca_df,
            "plots": [px.scatter()],
            "messages": [
                {
                    "level": logging.WARNING,
                    "msg": "Cannot display the scatterplot: There are less than two principle components.",
                }
            ],
        }

    plot_df = pd.DataFrame(
        {"PC1": pca_df["PC1"], "PC2": pca_df["PC2"], color_col: color_column_list}
    )

    fig = px.scatter(plot_df, x="PC1", y="PC2", color=color_col)

    fig.update_layout(title="PCA Scatterplot", plot_bgcolor=colors["plot_bgcolor"])
    fig.update_xaxes(gridcolor=colors["gridcolor"], linecolor=colors["linecolor"])
    fig.update_yaxes(gridcolor=colors["gridcolor"], linecolor=colors["linecolor"])

    return {"pca_df": pca_df, "plots": [fig]}
