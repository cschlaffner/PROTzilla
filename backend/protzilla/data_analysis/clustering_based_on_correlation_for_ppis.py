from collections import Counter
import json
import logging
import math
from joblib import Parallel, delayed
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from typing import Literal
from sklearn.metrics import silhouette_samples, silhouette_score
from backend.protzilla.constants.data_types import DataKey
from backend.protzilla.constants.option_types import (
    ClusteringLinkagePPI,
    CorrelationMethod,
    DistanceFromCorrelation,
    StopCriterionKmedoids,
    StringDbNetworkType,
)
import hdbscan
import kmedoids
from io import BytesIO
import zipfile
from scipy.spatial.distance import squareform
from dynamicTreeCut import cutreeHybrid  # does not work with numpy >= 2.4
from scipy.cluster.hierarchy import cophenet, linkage


from backend.protzilla.utilities.utilities import (
    default_intensity_column,
    fig_to_base64,
)
from backend.protzilla.steps import OutputItem, OutputType
from protzilla.constants.paths import RUNS_PATH


def make_protein_ids_STRING_readable(protein_ids: list[str]) -> list[str]:
    """remove "-x" from protein names as STRING does not know them"""
    return [protein_id.split("-")[0] for protein_id in protein_ids]


def _get_number_of_protein_ids_not_known_by_STRING(
    protein_ids: list[str], taxonomic_identifier: int
) -> int:
    request_url = "https://version-12-0.string-db.org/api/tsv-no-header/get_string_ids"
    params = {
        "identifiers": "\r".join(protein_ids),
        "species": taxonomic_identifier,
        "caller_identity": "PROTzilla",
    }
    results = requests.post(request_url, data=params)
    return len(protein_ids) - len(results.text.strip().split("\n"))


def get_STRING_information_for_cluster(
    proteins: list[str],
    taxonomic_identifier: int,
    network_flavor: StringDbNetworkType,
    min_required_string_score: int,
) -> tuple[bytes, int]:
    """Fetches a PNG image of all known physical interactions between the proteins from the STRING API.
    Attention: There is no warning if STRING does not know one or more of the proteins.
    Therefore, we also determine and return the number of unknown protein ids in the query.
    """
    proteins = make_protein_ids_STRING_readable(proteins)

    request_url = f"https://version-12-0.string-db.org/api/highres_image/network"

    params = {
        "identifiers": "\r".join(proteins),
        "species": taxonomic_identifier,
        "network_flavor": network_flavor,
        "network_type": "physical",
        "required_score": min_required_string_score,
        "show_query_node_labels": 1,
        "add_white_nodes": 0,  # if string only knows one of the ids, do not automatically add the top10 interactors of this protein
        "caller_identity": "PROTzilla",
    }

    response = requests.post(request_url, data=params)
    unknown_ids = _get_number_of_protein_ids_not_known_by_STRING(
        proteins, taxonomic_identifier
    )
    return response.content, unknown_ids


def get_heatmap_for_certain_cluster(
    proteins: list[str], axes: Axes, correlation_matrix: pd.DataFrame
) -> Axes:
    correlation_matrix_of_cluster = correlation_matrix.loc[proteins, proteins]
    return sns.heatmap(
        correlation_matrix_of_cluster,
        xticklabels=correlation_matrix_of_cluster.columns.values,
        yticklabels=correlation_matrix_of_cluster.columns.values,
        cmap=sns.diverging_palette(220, 10, as_cmap=True),
        vmin=-1,
        vmax=1,
        ax=axes,
    )


def get_proteins_of_specific_cluster(
    cluster_label: int, all_labels: pd.Series
) -> list[str]:
    """returns ids of all proteins with cluster_label"""
    return all_labels[cluster_label == all_labels].index.tolist()


def get_alphafold_query_file_for_specific_cluster(
    name: str, model_seed: int, fasta_df: pd.DataFrame, proteins: list[str]
) -> str:
    """This function creates a json that can be uploaded to AlphaFold Server for a multimer prediction of the proteins."""
    query = {
        "name": name,
        "modelSeeds": [],
        "sequences": [],
        "dialect": "alphafoldserver",
        "version": 1,
    }

    if model_seed != -1:
        query["modelSeeds"] = [model_seed]

    for protein_id in proteins:
        query["sequences"].append(
            {
                "proteinChain": {
                    "sequence": fasta_df.loc[
                        fasta_df["Protein ID"] == protein_id, "Protein Sequence"
                    ].iloc[0],
                    "count": 1,
                }
            }
        )
    return json.dumps([query], indent=4)


def get_number_of_amino_acid_residues_in_cluster(
    uniprot_ids: list[str], protein_id_to_number_of_residues: dict[str, int]
) -> int:
    number_of_residues = 0
    for id in uniprot_ids:
        number_of_residues += protein_id_to_number_of_residues.get(id, 0)
    return number_of_residues


def get_protein_id_to_number_of_residues(fasta_df: pd.DataFrame) -> dict[str, int]:
    protein_id_to_number_of_residues = {}
    for protein_id, protein_sequence in fasta_df[
        ["Protein ID", "Protein Sequence"]
    ].itertuples(index=False):
        protein_id_to_number_of_residues[protein_id] = len(protein_sequence)
    return protein_id_to_number_of_residues


def get_correlation_mean_of_cluster(
    clustering_labels: pd.Series,
    cluster_of_interest: int,
    correlation_matrix: pd.DataFrame,
) -> float:
    """Get the mean of the correlation values of the cluster.
    The values on the diagonal of the cluster (self-correlations) are ignored, so that smaller clusters are not favored.
    Clusters containing exactly one protein are perfectly correlated."""
    proteins = get_proteins_of_specific_cluster(cluster_of_interest, clustering_labels)
    assert (
        len(proteins) > 1
    ), "Tried to determine correlation mean for cluster of size 1. This means that clusters of size 1 are not properly ignored."
    # temporary fix as long as we drop the index every time we write to disk
    if isinstance(correlation_matrix.index, pd.RangeIndex):
        correlation_matrix.index = correlation_matrix.columns
    cluster_correlation_values = correlation_matrix.loc[proteins, proteins].to_numpy()
    return (cluster_correlation_values.sum() - np.trace(cluster_correlation_values)) / (
        cluster_correlation_values.size - len(proteins)
    )


def get_correlation_matrix(
    protein_df: pd.DataFrame, fasta_df: pd.DataFrame, method: CorrelationMethod
) -> dict:
    """
    Determines a correlation matrix for a protein dataframe.
    Proteins that are not in the fasta are removed from the matrix, as well as proteins, that have the same
    intensity value across all samples. If the user properly imputed the data there should not be any NaN values
    in the correlation matrix. If there are any, the belonging proteins are removed, too.
    :param protein_df: DataFrame containing Protein Ids, intensities and samples.
    :param fasta_df: DataFrame containing the amino acid sequences of proteins.
    :param method: Correlation method. Pearson or Spearman.
    :return: A dict containing the correlation matrix, the removed protein ids and messages.
    """
    intensity_name = default_intensity_column(protein_df)
    protein_df["Protein ID"] = protein_df["Protein ID"].apply(
        lambda id: id if "-" in id else f"{id}-1"
    )

    protein_ids_in_protein_df = set(protein_df["Protein ID"])
    number_of_protein_ids_in_input = protein_df["Protein ID"].nunique()
    protein_id_to_number_of_residues = get_protein_id_to_number_of_residues(fasta_df)
    ids_in_provided_fasta = set(
        protein_id_to_number_of_residues.keys()
    )  # might also contain ids that were removed during imputation
    number_of_ids_not_in_provided_fasta = len(
        protein_ids_in_protein_df - ids_in_provided_fasta
    )

    protein_to_intensities = {
        id: pd.Series(group[intensity_name].to_list())
        for id, group in protein_df.sort_values("Sample").groupby("Protein ID")
        if pd.Series(group[intensity_name].to_list()).nunique(dropna=True)
        > 1  # std of a protein must be != 0, otherwise it results in a correlation of NaN
        and id in ids_in_provided_fasta
    }
    correlation_matrix = pd.DataFrame(protein_to_intensities).corr(method)

    messages = []

    # remove NaN values
    number_of_removals_caused_by_nans = 0
    if np.isnan(correlation_matrix).any().any():
        not_nan_mask = ~correlation_matrix.isna().any(axis=1)
        correlation_matrix = correlation_matrix.loc[not_nan_mask, not_nan_mask]
        number_of_removals_caused_by_nans = (~not_nan_mask).sum()
        msg = f"{number_of_removals_caused_by_nans} proteins had a correlation of NaN with at least one other protein. \
        Therefore, these proteins were removed. This should not occur if data was imputed properly."
        messages.append(dict(level=logging.ERROR, msg=msg))

    if number_of_ids_not_in_provided_fasta > 0:
        msg = f"{number_of_ids_not_in_provided_fasta} protein ids were removed from the correlation matrix since the ids were not found in the provided fasta."
        messages.append(dict(level=logging.WARNING, msg=msg))

    number_of_ids_removed_due_to_std_of_zero = (
        number_of_protein_ids_in_input
        - len(correlation_matrix.columns)
        - number_of_ids_not_in_provided_fasta
        - number_of_removals_caused_by_nans
    )
    if number_of_ids_removed_due_to_std_of_zero > 0:
        msg = f"{number_of_ids_removed_due_to_std_of_zero} \
        protein ids were removed from the correlation matrix since all the protein's intensity values were identical, \
        which would have lead to a standard deviation of 0 for this protein, \
        which would have resulted in undefined correlation values between this protein and all other proteins."
        messages.append(dict(level=logging.WARNING, msg=msg))

    return dict(
        correlation_matrix_df=correlation_matrix,
        removed_protein_ids_df=pd.DataFrame(
            {
                "Protein ID": sorted(
                    protein_ids_in_protein_df - set(correlation_matrix.columns)
                )
            }
        ),
        messages=messages,
    )


def get_distance_matrix_from_correlation_matrix_df(
    correlation_matrix_df: pd.DataFrame,
    distance_method: DistanceFromCorrelation,
    hdbscan_suitable: bool,
) -> dict:
    """Determines a distance matrix based on the correlation matrix (high correlation = low distance, low correlation = high distance).
    Whether no correlation and anti-correleation are regarded the same or not is determined by the user input.
    :param correlation_matrix_df: DataFrame containing the correlation matrix.
    :param distance_method: Determines which method is used to derive the distance from the correlation.
    :param hdbscan_suitable: The HDBSCAN validity index cannot deal with perfect correlations. Therefore, the user has the option to clipp the distance matrix between -0.999999 and 0.999999.
    :return: Returns a DataFrame containing the distance matrix.
    """
    distance_matrix = correlation_matrix_df.to_numpy()
    if hdbscan_suitable:
        # without this clipping, the final distance matrix could contain values of exactly 0 that are not on the diagonal
        # hdbscan.validity.validity_index cannot deal with these zeros
        distance_matrix = np.clip(distance_matrix, -0.999999, 0.999999)
    else:
        # without clipping distance_matrix could contain values >1 due to rounding inaccuracies
        # this would lead to a negative distance or taking the root of something negative, which would result in NaNs
        distance_matrix = np.clip(distance_matrix, -1, 1)
    if distance_method == DistanceFromCorrelation.weight_in_negative_correlations:
        distance_matrix = np.sqrt(2 * (1 - distance_matrix))
    else:
        distance_matrix = 1 - np.maximum(0, distance_matrix)
    np.fill_diagonal(distance_matrix, 0)
    return dict(
        distance_matrix_df=pd.DataFrame(
            distance_matrix,
            index=correlation_matrix_df.columns,
            columns=correlation_matrix_df.columns,
        ),
    )


def get_cluster_sizes_histogram(labels: pd.Series) -> Figure:
    fig_cluster_sizes, ax_cluster_sizes = plt.subplots()
    ax_cluster_sizes.hist(list(Counter(labels).values()), bins=40)
    ax_cluster_sizes.set_title("Histogram of Cluster Sizes")
    ax_cluster_sizes.set_xlabel("Cluster Size")
    ax_cluster_sizes.set_ylabel("Number of clusters with certain cluster size")
    plt.close(fig_cluster_sizes)
    return fig_cluster_sizes


def get_cluster_correlation_means_histogram(
    cluster_correlation_means: list[float], clusters_of_size_one_omitted: bool = False
) -> Figure:
    fig_correlation_means, ax_correlation_means = plt.subplots()
    ax_correlation_means.hist(cluster_correlation_means, bins=40)
    if clusters_of_size_one_omitted:
        ax_correlation_means.set_title(
            "Histogram of Intra Cluster Correlation Means (clusters with exactly one protein are omitted)"
        )
    else:
        ax_correlation_means.set_title("Histogram of Intra Cluster Correlation Means")
    ax_correlation_means.set_xlabel("Mean Correlation")
    ax_correlation_means.set_ylabel("Number of clusters with certain mean correlation")
    plt.close(fig_correlation_means)
    return fig_correlation_means


def get_cluster_silhouette_histogram(
    distance_matrix: np.ndarray,
    labels: pd.Series,
) -> tuple[Figure, pd.Series]:
    silhouette_per_cluster = pd.Series(dtype=float)
    if labels.nunique() == 1 and labels.iloc[0] == -1:
        raise ValueError(
            "None of the proteins were assigned to a cluster. Try clustering again with different parameters."
        )
    if labels.nunique() < 2:
        raise ValueError(
            "All proteins were clustered in one big cluster. Try clustering again with different parameters."
        )
    silhouette_scores_per_sample = silhouette_samples(
        distance_matrix, labels, metric="precomputed"
    )
    for label in labels.unique():
        if label == -1:
            continue
        mask = labels == label
        silhouette_per_cluster.loc[label] = silhouette_scores_per_sample[mask].mean()
    fig_silhouette, ax_silhouette = plt.subplots()
    ax_silhouette.hist(silhouette_per_cluster, bins=40)
    ax_silhouette.set_title(
        "Histogram of Silhouette Scores (clusters with exactly one protein are omitted)"
    )
    ax_silhouette.set_xlabel("Silhouette Score")
    ax_silhouette.set_ylabel("Number of clusters with certain Silhouette Score")
    plt.close(fig_silhouette)
    return fig_silhouette, silhouette_per_cluster


def hdbscan_for_ppi(
    distance_matrix_df: pd.DataFrame,
    correlation_matrix_df: pd.DataFrame,
    protein_df: pd.DataFrame,
    min_cluster_size: int,
) -> dict:
    """Runs the HDBSCAN algorithm (from the hdbscan library) for clustering the proteins that are likely to interact into groups.
    :param distance_matrix_df: Dataframe containing the distance matrix.
    :param correlation_matrix_df: Dataframe containing the original correlation matrix.
    :param protein_df: Dataframe used for the correlation matrix. Used to determine the original number of features.
    :param min_cluster_size: HDBSCAN won't determine clusters with less than min_cluster_size proteins.
    :return: Returns a dict with a dataframe containing the assigned labels, a dataframe with a dbcv score for each cluster and
    histograms of the dbcv scores, correlation means and cluster sizes."""
    distance_matrix = distance_matrix_df.to_numpy()
    clusterer = hdbscan.HDBSCAN(
        metric="precomputed",
        min_cluster_size=min_cluster_size,
    )
    clusterer.fit(distance_matrix)
    labels = pd.Series(clusterer.labels_, index=distance_matrix_df.index, name="Label")
    dbcv, dbcv_per_cluster = hdbscan.validity.validity_index(
        distance_matrix,
        clusterer.labels_,
        metric="precomputed",
        d=protein_df["Sample"].nunique(),
        per_cluster_scores=True,
    )

    fig_dbcv, ax_dbcv = plt.subplots()
    ax_dbcv.hist(dbcv_per_cluster, bins=40)
    ax_dbcv.set_title("Histogram of DBCV Scores")
    ax_dbcv.set_xlabel("DBCV Score")
    ax_dbcv.set_ylabel("Number of clusters with certain DBCV Score")

    cluster_correlation_means = []
    for label in sorted(labels.unique()):
        if label == -1:
            continue
        cluster_correlation_means.append(
            get_correlation_mean_of_cluster(labels, label, correlation_matrix_df)
        )

    return dict(
        cluster_labels_df=OutputItem(
            output_type=OutputType.DATAFRAME,
            value=pd.DataFrame(
                {"Protein Id": correlation_matrix_df.columns, "Label": labels}
            ),
        ),
        dbcv_scores_df=OutputItem(
            output_type=OutputType.DATAFRAME,
            value=pd.DataFrame(
                {
                    "Cluster Id": range(0, len(dbcv_per_cluster)),
                    "DBCV": dbcv_per_cluster,
                }
            ),
        ),
        cluster_correlation_means_df=OutputItem(
            output_type=OutputType.DATAFRAME,
            value=pd.DataFrame(
                {
                    "Cluster Id": range(0, len(cluster_correlation_means)),
                    "Correlation Mean": cluster_correlation_means,
                }
            ),
        ),
        histogram_dbcv=OutputItem(OutputType.PNG_BASE64, fig_to_base64(fig_dbcv)),
        histogram_correlation_means=OutputItem(
            OutputType.PNG_BASE64,
            fig_to_base64(
                get_cluster_correlation_means_histogram(cluster_correlation_means)
            ),
        ),
        histogram_cluster_sizes=OutputItem(
            OutputType.PNG_BASE64,
            fig_to_base64(
                get_cluster_sizes_histogram(
                    pd.Series([label for label in labels if label > -1])
                )
            ),
        ),
    )


def save_heatmap(
    zip: zipfile.ZipFile,
    proteins: list[str],
    correlation_matrix_df: pd.DataFrame,
    output_name: str,
    cluster_id: int,
    number_of_residues_in_cluster: int,
) -> None:
    fig, ax = plt.subplots(figsize=(10, 8))

    get_heatmap_for_certain_cluster(proteins, ax, correlation_matrix_df)

    heatmap_filename = (
        f"{output_name}_heatmap_{cluster_id}"
        f"__{number_of_residues_in_cluster}_residues.png"
    )
    heatmap_buffer = BytesIO()
    plt.savefig(heatmap_buffer, format="png", dpi=300)
    plt.close(fig)

    heatmap_buffer.seek(0)

    zip.writestr(f"heatmap/{heatmap_filename}", heatmap_buffer.getvalue())


def save_STRING_network(
    zip: zipfile.ZipFile,
    proteins: list[str],
    taxonomic_id: int,
    network_flavor: StringDbNetworkType,
    output_name: str,
    cluster_id: int,
    number_of_residues_in_cluster: int,
    min_required_string_score: int,
) -> None:
    string_data, number_of_ids_not_known_by_STRING = get_STRING_information_for_cluster(
        proteins, taxonomic_id, network_flavor, min_required_string_score
    )

    string_filename = (
        f"{output_name}_cluster_{cluster_id}"
        f"__{number_of_residues_in_cluster}_residues_{number_of_ids_not_known_by_STRING}_unknown_ids.png"
    )

    zip.writestr(
        f"string_network/{string_filename}",
        string_data,
    )


def create_filtered_clusters_output(
    cluster_labels_df: pd.DataFrame,
    output_name: str,
    correlation_matrix_df: pd.DataFrame,
    generate_STRING_networks: bool,
    cluster_labels_to_ignore: list[int],
    only_include_alphafold_compatible_clusters: bool,
    fasta_df: pd.DataFrame,
    generate_alphafold_queries: bool,
    model_seed: int,
    taxonomic_identifier: str,
    network_flavor: StringDbNetworkType,
    min_required_string_score: int,
) -> dict:
    """Create a zip file containing the user requested data (heatmaps, STRING networks, AlphaFold query files)
    for all clusters that are not in cluster_labels_to_ignore."""

    protein_id_to_number_of_residues = get_protein_id_to_number_of_residues(fasta_df)
    labels = cluster_labels_df["Label"]
    ALPHAFOLD_JOB_LIMIT = 5000

    clusters_too_big_for_alphafold = 0
    at_least_one_failed_string_request = False

    selected_clusters = []

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip:
        for cluster_id in labels.unique():
            if cluster_id in cluster_labels_to_ignore:
                continue

            proteins = get_proteins_of_specific_cluster(cluster_id, labels)
            number_of_residues_in_cluster = (
                get_number_of_amino_acid_residues_in_cluster(
                    proteins, protein_id_to_number_of_residues
                )
            )

            if number_of_residues_in_cluster > ALPHAFOLD_JOB_LIMIT:
                clusters_too_big_for_alphafold += 1
                if only_include_alphafold_compatible_clusters:
                    continue

            selected_clusters.append(cluster_id)

            save_heatmap(
                zip,
                proteins,
                correlation_matrix_df,
                output_name,
                cluster_id,
                number_of_residues_in_cluster,
            )

            if generate_STRING_networks:
                # transformation necessary due to the dropdown format containing id and organism name
                taxonomic_id = int(taxonomic_identifier.split()[0])
                try:
                    save_STRING_network(
                        zip,
                        proteins,
                        taxonomic_id,
                        network_flavor,
                        output_name,
                        cluster_id,
                        number_of_residues_in_cluster,
                        min_required_string_score,
                    )
                except Exception:
                    at_least_one_failed_string_request = True

            if generate_alphafold_queries:
                query_filename = (
                    f"{output_name}_alphafold_query_{cluster_id}"
                    f"__{number_of_residues_in_cluster}_residues.json"
                )
                zip.writestr(
                    f"alphafold_prediction_queries/{query_filename}",
                    get_alphafold_query_file_for_specific_cluster(
                        f"cluster{cluster_id}", model_seed, fasta_df, proteins
                    ),
                )

    zip_buffer.seek(0)
    zip_plot_in_bytes = zip_buffer.getvalue()

    messages = []
    if clusters_too_big_for_alphafold > 0:
        msg = f"{clusters_too_big_for_alphafold} clusters are too big for generating a AlphaFold Multimer query as AlphaFold only allows jobs of up to 5,000 residues as of June 2026."
        messages.append(dict(level=logging.WARNING, msg=msg))

    if at_least_one_failed_string_request:
        msg = f"At least one request for a STRING network failed."
        messages.append(dict(level=logging.WARNING, msg=msg))

    return dict(
        downloads=OutputItem(
            output_type=OutputType.DOWNLOAD,
            value={f"{output_name}.zip": zip_plot_in_bytes},
        ),
        selected_clusters_df=OutputItem(
            output_type=OutputType.DATAFRAME,
            value=pd.DataFrame(sorted(selected_clusters), columns=["Cluster Id"]),
        ),
        messages=messages,
    )


def get_clusters_based_on_correlation_mean(
    threshold: float,
    cluster_correlation_means_df: pd.DataFrame,
    cluster_labels_df: pd.DataFrame,
    correlation_matrix_df: pd.DataFrame,
    output_name: str,
    generate_STRING_networks: bool,
    only_include_alphafold_compatible_clusters: bool,
    fasta_df: pd.DataFrame,
    generate_alphafold_queries: bool,
    model_seed: int,
    taxonomic_identifier: str,
    network_flavor: StringDbNetworkType,
    min_required_string_score: int,
) -> dict:
    """Selects all clusters with a mean correlation above a certain threshold and
    creates the requested output zip (heatmaps, STRING networks, AlphaFold json queries) for them.
    :param threshold: The minimum corrrelation mean for a cluster to be included.
    :param cluster_correlation_means_df: DataFrame that contains the mean correlation for each cluster (ignoring correlation values on the diagonal)
    :param cluster_labels_df: DataFrame that contains the labels of the clustering.
    :param correlation_matrix_df: DataFrame that contains the correlation matrix that was clustered.
    :param output_name: Name of the output zip
    :param generate_STRING_networks: Bool that determines whether STRING networks are added to the zip.
    :param only_include_alphafold_compatible_clusters: Bool that determines whether clusters that are too big for AlphaFold are removed from the output zip.
    :param fasta_df: DataFrame that contains the amino acid sequences of all the proteins in the correlation matrix.
    :param generate_alphafold_queries: Bool that determines whether json queries for AlphaFold are added for each cluster to the output zip.
    :param model_seed: Seed that will be used in the generated queries for AlphaFold.
    :param taxonomic_identifier: If STRING networks are generated, the user needs to select to which species the proteins belong.
    :param network_flavor: If STRING networks are generated, the user can select whether one wants to see which specific
    sources support a protein interaction or whether just a generall confidence score should be included.
    :return: A dict that contains a zip that contains heatmaps for the selected clusters
    and that might also contain STRING network images and AlphaFold server json queries.
    """
    cluster_labels_to_ignore = [
        -1
    ]  # proteins that are assigned no cluster are labeled with -1
    for label in cluster_labels_df["Label"].unique():
        if label == -1:
            continue
        if cluster_correlation_means_df.loc[label, "Correlation Mean"] < threshold:
            cluster_labels_to_ignore.append(label)

    return create_filtered_clusters_output(
        cluster_labels_df,
        output_name,
        correlation_matrix_df,
        generate_STRING_networks,
        cluster_labels_to_ignore,
        only_include_alphafold_compatible_clusters,
        fasta_df,
        generate_alphafold_queries,
        model_seed,
        taxonomic_identifier,
        network_flavor,
        min_required_string_score,
    )


def get_clusters_based_on_dbcv(
    threshold: float,
    cluster_labels_df: pd.DataFrame,
    correlation_matrix_df: pd.DataFrame,
    dbcv_scores_df: pd.DataFrame,
    output_name: str,
    generate_STRING_networks: bool,
    only_include_alphafold_compatible_clusters: bool,
    fasta_df: pd.DataFrame,
    generate_alphafold_queries: bool,
    model_seed: int,
    taxonomic_identifier: str,
    network_flavor: StringDbNetworkType,
    min_required_string_score: int,
) -> dict:
    """Selects all clusters with a dbcv score above a certain threshold and
    creates the requested output zip (heatmaps, STRING networks, AlphaFold json queries) for them.
    :param threshold: The minimum dbcv score for a cluster to be included.
    :param cluster_labels_df: DataFrame that contains the labels of the clustering.
    :param correlation_matrix_df: DataFrame that contains the correlation matrix that was clustered.
    :param output_name: Name of the output zip
    :param generate_STRING_networks: Bool that determines whether STRING networks are added to the zip.
    :param only_include_alphafold_compatible_clusters: Bool that determines whether clusters that are too big for AlphaFold are removed from the output zip.
    :param fasta_df: DataFrame that contains the amino acid sequences of all the proteins in the correlation matrix.
    :param generate_alphafold_queries: Bool that determines whether json queries for AlphaFold are added for each cluster to the output zip.
    :param model_seed: Seed that will be used in the generated queries for AlphaFold.
    :param taxonomic_identifier: If STRING networks are generated, the user needs to select to which species the proteins belong.
    :param network_flavor: If STRING networks are generated, the user can select whether one wants to see which specific
    sources support a protein interaction or whether just a generall confidence score should be included.
    :return: A dict that contains a zip that contains heatmaps for the selected clusters
    and that might also contain STRING network images and AlphaFold server json queries.
    """
    cluster_labels_to_ignore = [-1]
    for label in cluster_labels_df["Label"].unique():
        if label == -1:
            continue
        if dbcv_scores_df.loc[label, "DBCV"] < threshold:
            cluster_labels_to_ignore.append(label)

    return create_filtered_clusters_output(
        cluster_labels_df,
        output_name,
        correlation_matrix_df,
        generate_STRING_networks,
        cluster_labels_to_ignore,
        only_include_alphafold_compatible_clusters,
        fasta_df,
        generate_alphafold_queries,
        model_seed,
        taxonomic_identifier,
        network_flavor,
        min_required_string_score,
    )


def hierarchical_clustering_for_ppi(
    distance_matrix_df: pd.DataFrame,
    correlation_matrix_df: pd.DataFrame,
    linkage_method: ClusteringLinkagePPI,
    deep_split: float,
    min_cluster_size: int,
) -> dict:
    """Runs hierarchical clustering using scipy's linkage method in order to cluster proteins that are likely to interact.
    :param distance_matrix_df: Dataframe containing the distance matrix.
    :param correlation_matrix_df: Dataframe containing the original correlation matrix.
    :param linkage_method: Determines whether single or average linkage is used for the hierarchical clustering.
    :param deep_split: Integer between 0 and 4 which influences cluster size. The parameter is used by the dynamicTreeCut library, which we use to determine
    where to cut the dendrogram. 0 bigger clusters, 4 means smaller clusters.
    :param min_cluster_size: All clusters will have at least min_cluster_size many proteins.
    :return: Returns a dict with a dataframe containing the assigned labels, a dataframe with a silhouette score for each cluster and
    histograms of the silhouette scores, correlation means and cluster sizes."""

    distance_matrix = distance_matrix_df.to_numpy()
    Z = linkage(squareform(distance_matrix), linkage_method)
    labels = pd.Series(
        cutreeHybrid(
            Z, distance_matrix, minClusterSize=min_cluster_size, deepSplit=deep_split
        )["labels"],
        index=distance_matrix_df.index,
    )
    labels = labels - 1

    cluster_correlation_means = []
    for label in sorted(labels.unique()):
        if label == -1:
            continue
        cluster_correlation_means.append(
            get_correlation_mean_of_cluster(labels, label, correlation_matrix_df)
        )

    silhouette_scores_histogram, silhouette_scores_per_cluster = (
        get_cluster_silhouette_histogram(distance_matrix, labels)
    )
    msg = f"Clustering has Cophenetic Correlation score of {cophenet(Z, squareform(distance_matrix))[0]}."
    return dict(
        cluster_labels_df=OutputItem(
            output_type=OutputType.DATAFRAME,
            value=pd.DataFrame(
                {"Protein Id": correlation_matrix_df.columns, "Label": labels}
            ),
        ),
        silhouette_scores_df=OutputItem(
            output_type=OutputType.DATAFRAME,
            value=pd.DataFrame(
                {
                    "Cluster Id": range(0, len(silhouette_scores_per_cluster)),
                    "Silhouette": silhouette_scores_per_cluster,
                }
            ),
        ),
        cluster_correlation_means_df=OutputItem(
            output_type=OutputType.DATAFRAME,
            value=pd.DataFrame(
                {
                    "Cluster Id": range(0, len(cluster_correlation_means)),
                    "Correlation Mean": cluster_correlation_means,
                }
            ),
        ),
        histogram_silhouette=OutputItem(
            OutputType.PNG_BASE64, fig_to_base64(silhouette_scores_histogram)
        ),
        histogram_correlation_means=OutputItem(
            OutputType.PNG_BASE64,
            fig_to_base64(
                get_cluster_correlation_means_histogram(cluster_correlation_means)
            ),
        ),
        histogram_cluster_sizes=OutputItem(
            OutputType.PNG_BASE64,
            fig_to_base64(
                get_cluster_sizes_histogram(
                    pd.Series([label for label in labels if label != -1])
                )
            ),
        ),
        messages=[dict(level=logging.INFO, msg=msg)],
    )


def get_clusters_based_on_silhouette(
    threshold: float,
    cluster_labels_df: pd.DataFrame,
    correlation_matrix_df: pd.DataFrame,
    silhouette_scores_df: pd.DataFrame,
    output_name: str,
    generate_STRING_networks: bool,
    only_include_alphafold_compatible_clusters: bool,
    fasta_df: pd.DataFrame,
    generate_alphafold_queries: bool,
    model_seed: int,
    taxonomic_identifier: str,
    network_flavor: StringDbNetworkType,
    min_required_string_score: int,
) -> dict:
    """Selects all clusters with a Silhouette score above a certain threshold and
    creates the requested output zip (heatmaps, STRING networks, AlphaFold json queries) for them.
    :param threshold: The minimum Silhouette score for a cluster to be included.
    :param cluster_labels_df: DataFrame that contains the labels of the clustering.
    :param correlation_matrix_df: DataFrame that contains the correlation matrix that was clustered.
    :param output_name: Name of the output zip
    :param generate_STRING_networks: Bool that determines whether STRING networks are added to the zip.
    :param only_include_alphafold_compatible_clusters: Bool that determines whether clusters that are too big for AlphaFold are removed from the output zip.
    :param fasta_df: DataFrame that contains the amino acid sequences of all the proteins in the correlation matrix.
    :param generate_alphafold_queries: Bool that determines whether json queries for AlphaFold are added for each cluster to the output zip.
    :param model_seed: Seed that will be used in the generated queries for AlphaFold.
    :param taxonomic_identifier: If STRING networks are generated, the user needs to select to which species the proteins belong.
    :param network_flavor: If STRING networks are generated, the user can select whether one wants to see which specific
    sources support a protein interaction or whether just a generall confidence score should be included.
    :return: A dict that contains a zip that contains heatmaps for the selected clusters
    and that might also contain STRING network images and AlphaFold server json queries.
    """
    cluster_labels_to_ignore = [-1]
    for label in cluster_labels_df["Label"].unique():
        if label == -1:
            continue
        if silhouette_scores_df.loc[label, "Silhouette"] < threshold:
            cluster_labels_to_ignore.append(label)
    return create_filtered_clusters_output(
        cluster_labels_df,
        output_name,
        correlation_matrix_df,
        generate_STRING_networks,
        cluster_labels_to_ignore,
        only_include_alphafold_compatible_clusters,
        fasta_df,
        generate_alphafold_queries,
        model_seed,
        taxonomic_identifier,
        network_flavor,
        min_required_string_score,
    )


def _is_stopping_criterion_fullfilled(
    stop_criterion: StopCriterionKmedoids,
    labels: np.ndarray,
    label: int,
    correlation_matrix_df: pd.DataFrame,
    min_correlation_mean: float,
    max_cluster_size: int,
) -> bool:
    return (
        (
            stop_criterion == StopCriterionKmedoids.correlation_mean
            and get_correlation_mean_of_cluster(
                pd.Series(labels, index=correlation_matrix_df.columns),
                label,
                correlation_matrix_df,
            )
            >= min_correlation_mean
        )
        or (
            stop_criterion == StopCriterionKmedoids.max_cluster_size
            and (labels == label).sum() <= max_cluster_size
        )
        or (
            stop_criterion
            == StopCriterionKmedoids.correlation_mean_and_max_cluster_size
            and get_correlation_mean_of_cluster(
                pd.Series(labels, index=correlation_matrix_df.columns),
                label,
                correlation_matrix_df,
            )
            >= min_correlation_mean
            and (labels == label).sum() <= max_cluster_size
        )
    )


def _get_upper_bound_on_cluster_numbers_to_inspect(
    number_of_proteins_in_cluster: int,
    min_cluster_size: int,
    average_expected_cluster_size: int,
    min_number_of_silhouette_scores_to_inspect: int,
) -> int:
    return (
        math.ceil(number_of_proteins_in_cluster / min_cluster_size)
        if math.ceil(number_of_proteins_in_cluster / average_expected_cluster_size) - 1
        < min_number_of_silhouette_scores_to_inspect
        else math.ceil(number_of_proteins_in_cluster / average_expected_cluster_size)
    )


def _evaluate_number_of_clusters(number_of_clusters, distance_matrix, random_seed):
    labels = kmedoids.fasterpam(
        distance_matrix, number_of_clusters, random_state=random_seed
    ).labels
    score = silhouette_score(X=distance_matrix, labels=labels, metric="precomputed")
    return score


def kmedoids_with_subsampling(
    distance_matrix: np.ndarray,
    correlation_matrix: pd.DataFrame,
    random_seed: int,
    average_expected_cluster_size: int,
    continue_subsampling_as_long_as_silhouette_improves: bool,
    stop_criterion: StopCriterionKmedoids,
    min_correlation_mean: float,
    max_cluster_size: int,
    min_cluster_size: int,
    min_number_of_silhouette_scores_to_inspect: int,
    labels_parent: pd.Series | None = None,
    distance_matrix_parent: np.ndarray | None = None,
) -> list[list[str]]:
    """
    Runs kmedoids clustering with the FasterPAM algorithm using kmedoid's fasterPAM algorithm (https://doi.org/10.1016/j.is.2021.101804)
    in order to cluster proteins that are likely to interact. Determine the best number of clusters using the silhouette score.
    Split clusters that do not meet the stopping criterion and repeat the process.
    :param distance_matrix: Numpy array containing the distance matrix.
    :param correlation_matrix_df: Dataframe containing the original correlation matrix.
    :param random_seed: Random seed used for the fasterPAM executions.
    :param continue_subsampling_as_long_as_silhouette_improves: Determines whether clusters which already meet the stopping criterion
    will still be split if the silhouette score of the clustered version of the cluster is better than the silhouette score of the current clustering.
    :param min_correlation_mean: Float that determines the minimum cluster correlation mean of a cluster to stop it from being split any further.
    :param average_expected_cluster_size: Used to determine an upper bound on the number of clusters that should be considered.
    :param max_cluster_size: If one selects a stopping criterion that includes a maximum cluster size, one also needs to provide the maximum cluster size.
    :param min_cluster_size: The minimum number of proteins in each cluster in the output.
    :param min_number_of_silhouette_scores_to_inspect: If (number of proteins in cluster / average_expected_cluster_size) < min_number_of_silhouette_scores_to_inspect
    min_cluster_size will be used to determine the different numbers of clusters for which the silhouette score will be determined.
    :param labels_parent: Set to the labels determined in the previous kmedoids_with_subsampling call.
    Only set if the previous clustering met the stopping criterion and continue_subsampling_as_long_as_silhouette_improves is True.
    :param distance_matrix_parent: Set to the distance matrix used in the previous kmedoids_with_subsampling call.
    Only set if the previous clustering met the stopping criterion and continue_subsampling_as_long_as_silhouette_improves is True.
    :return: Returns a list of lists. Each of the lists contains all protein-ids of one cluster.
    """
    clusters = []
    number_of_proteins_in_cluster = len(correlation_matrix.columns)
    upper_bound_on_cluster_numbers_to_inspect = (
        _get_upper_bound_on_cluster_numbers_to_inspect(
            number_of_proteins_in_cluster,
            min_cluster_size,
            average_expected_cluster_size,
            min_number_of_silhouette_scores_to_inspect,
        )
    )
    silhouette_scores = Parallel(n_jobs=-1)(
        delayed(_evaluate_number_of_clusters)(i, distance_matrix, random_seed)
        for i in range(2, upper_bound_on_cluster_numbers_to_inspect + 1)
    )
    best_number_of_clusters = 2 + silhouette_scores.index(max(silhouette_scores))
    labels = kmedoids.fasterpam(
        distance_matrix, best_number_of_clusters, random_state=random_seed
    ).labels
    if labels_parent is not None:
        s_score_parent = silhouette_score(
            X=distance_matrix_parent, labels=labels_parent.values, metric="precomputed"
        )
        labels_with_parent_label_compatible_ids = labels + labels_parent.max() + 1
        labels_parent.loc[correlation_matrix.columns] = (
            labels_with_parent_label_compatible_ids
        )
        s_score_parent_with_subclustering = silhouette_score(
            X=distance_matrix_parent, labels=labels_parent.values, metric="precomputed"
        )
        if s_score_parent_with_subclustering < s_score_parent:
            return [list(correlation_matrix.columns)]
    for label in np.unique(labels):
        cluster_indices = np.where(labels == label)[0]
        proteins = list(correlation_matrix.columns[cluster_indices])

        is_stopping_criterion_fullfilled = False
        if len(proteins) > min_cluster_size:
            is_stopping_criterion_fullfilled = _is_stopping_criterion_fullfilled(
                stop_criterion,
                labels,
                label,
                correlation_matrix,
                min_correlation_mean,
                max_cluster_size,
            )
        if len(proteins) < min_cluster_size:
            continue
        elif len(proteins) == min_cluster_size or (
            is_stopping_criterion_fullfilled
            and not continue_subsampling_as_long_as_silhouette_improves
        ):
            clusters.append(proteins)
        else:
            correlation_matrix_new = correlation_matrix.iloc[
                cluster_indices, cluster_indices
            ]
            distance_matrix_new = distance_matrix[
                np.ix_(cluster_indices, cluster_indices)
            ]
            if is_stopping_criterion_fullfilled:
                additional_params = {
                    "labels_parent": pd.Series(
                        labels, index=correlation_matrix.columns
                    ),
                    "distance_matrix_parent": distance_matrix,
                }
            else:
                additional_params = dict()
            clusters = clusters + kmedoids_with_subsampling(
                distance_matrix_new,
                correlation_matrix_new,
                random_seed,
                average_expected_cluster_size,
                continue_subsampling_as_long_as_silhouette_improves,
                stop_criterion,
                min_correlation_mean,
                max_cluster_size,
                min_cluster_size,
                min_number_of_silhouette_scores_to_inspect,
                **additional_params,
            )
    return clusters


def k_medoids_for_ppi(
    distance_matrix_df: pd.DataFrame,
    correlation_matrix_df: pd.DataFrame,
    random_seed: int,
    continue_subsampling_as_long_as_silhouette_improves: bool,
    stop_criterion: StopCriterionKmedoids,
    min_correlation_mean: float,
    average_expected_cluster_size: int,
    max_cluster_size: int,
    min_cluster_size: int,
    min_number_of_silhouette_scores_to_inspect: int,
) -> dict:
    """Runs kmedoids clustering with the FasterPAM algorithm using kmedoid's fasterPAM algorithm (https://doi.org/10.1016/j.is.2021.101804)
    in order to cluster proteins that are likely to interact. Determine the best number of clusters using the silhouette score.
    Split clusters that do not meet the stopping criterion and repeat the process.
    :param distance_matrix_df: Dataframe containing the distance matrix.
    :param correlation_matrix_df: Dataframe containing the original correlation matrix.
    :param random_seed: Random seed used for the fasterPAM executions.
    :param continue_subsampling_as_long_as_silhouette_improves: Determines whether clusters which already meet the stopping criterion
    will still be split if the silhouette score of the clustered version of the cluster is better than the silhouette score of the current clustering.
    :param min_correlation_mean: Float that determines the minimum cluster correlation mean of a cluster to stop it from being split any further.
    :param average_expected_cluster_size: Used to determine an upper bound on the number of clusters that should be considered.
    :param max_cluster_size: If one selects a stopping criterion that includes a maximum cluster size, one also needs to provide the maximum cluster size.
    :param min_cluster_size: The minimum number of proteins in each cluster in the output.
    :param min_number_of_silhouette_scores_to_inspect: If (number of proteins in cluster / average_expected_cluster_size) < min_number_of_silhouette_scores_to_inspect
    min_cluster_size will be used to determine the different numbers of clusters for which the silhouette score will be determined.
    :return: Returns a dict with a dataframe containing the assigned labels, a dataframe with the silhouette score for each cluster and
    histograms of the silhouette scores, correlation means and cluster sizes."""

    if (
        _get_upper_bound_on_cluster_numbers_to_inspect(
            len(correlation_matrix_df.columns),
            min_cluster_size,
            average_expected_cluster_size,
            min_number_of_silhouette_scores_to_inspect,
        )
        < 2
    ):
        raise ValueError(
            "Please change min_cluster_size/average_expected_cluster_size/min_number_of_silhouette_scores_to_inspect. The current combination allows less than 2 clusters for the input."
        )

    if average_expected_cluster_size < min_cluster_size:
        raise ValueError(
            "Min cluster size cannot be smaller than average expected cluster size."
        )

    distance_matrix = distance_matrix_df.to_numpy()
    clusters = kmedoids_with_subsampling(
        distance_matrix,
        correlation_matrix_df,
        random_seed,
        average_expected_cluster_size,
        continue_subsampling_as_long_as_silhouette_improves,
        stop_criterion,
        min_correlation_mean,
        max_cluster_size,
        min_cluster_size,
        min_number_of_silhouette_scores_to_inspect,
    )

    if len(clusters) == 0:
        msg = "No cluster was found."
        return dict(
            messages=[dict(level=logging.ERROR, msg=msg)],
        )

    cluster_map: dict[str, int] = {
        protein: cluster_id
        for cluster_id, cluster in enumerate(clusters)
        for protein in cluster
    }

    labels = pd.Series(
        [cluster_map.get(protein, -1) for protein in correlation_matrix_df.columns],
        index=correlation_matrix_df.columns,
    )

    silhouette_scores_histogram, silhouette_scores_per_cluster = (
        get_cluster_silhouette_histogram(distance_matrix, labels)
    )

    cluster_correlation_means = []
    for label in sorted(labels.unique()):
        if label == -1:
            continue
        cluster_correlation_means.append(
            get_correlation_mean_of_cluster(labels, label, correlation_matrix_df)
        )

    return dict(
        cluster_labels_df=OutputItem(
            output_type=OutputType.DATAFRAME,
            value=pd.DataFrame(
                {"Protein Id": correlation_matrix_df.columns, "Label": labels}
            ),
        ),
        silhouette_scores_df=OutputItem(
            output_type=OutputType.DATAFRAME,
            value=pd.DataFrame(
                {
                    "Cluster Id": range(0, len(silhouette_scores_per_cluster)),
                    "Silhouette": silhouette_scores_per_cluster,
                }
            ),
        ),
        cluster_correlation_means_df=OutputItem(
            output_type=OutputType.DATAFRAME,
            value=pd.DataFrame(
                {
                    "Cluster Id": range(0, len(cluster_correlation_means)),
                    "Correlation Mean": cluster_correlation_means,
                }
            ),
        ),
        histogram_silhouette=OutputItem(
            OutputType.PNG_BASE64, fig_to_base64(silhouette_scores_histogram)
        ),
        histogram_correlation_means=OutputItem(
            OutputType.PNG_BASE64,
            fig_to_base64(
                get_cluster_correlation_means_histogram(
                    cluster_correlation_means, clusters_of_size_one_omitted=True
                )
            ),
        ),
        histogram_cluster_sizes=OutputItem(
            OutputType.PNG_BASE64,
            fig_to_base64(
                get_cluster_sizes_histogram(
                    pd.Series([label for label in labels if label != -1])
                )
            ),
        ),
    )
