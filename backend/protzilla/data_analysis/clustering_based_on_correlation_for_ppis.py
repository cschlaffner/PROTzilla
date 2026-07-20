from collections import Counter
import json
import logging
from matplotlib.axes import Axes
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from typing import Literal
from sklearn.metrics import silhouette_samples
from backend.protzilla.constants.option_types import (
    ClusteringLinkagePPI,
    CorrelationMethod,
    DistanceFromCorrelation,
    StringDbNetworkType,
)
import hdbscan
from io import BytesIO
import zipfile
from scipy.spatial.distance import squareform
from dynamicTreeCut import cutreeHybrid  # does not work with numpy >= 2.4
from scipy.cluster.hierarchy import linkage


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
    network_flavor: StringDbNetworkType.values,
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
        "required_score": 0,
        "show_query_node_labels": 1,
        "add_white_nodes": 0,  # if string only knows one of the ids, do not automatically add the top10 interactors of this protein
        "caller_identity": "PROTzilla",
    }

    response = requests.post(request_url, data=params)
    return response.content, _get_number_of_protein_ids_not_known_by_STRING(
        proteins, taxonomic_identifier
    )


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


def get_output_zip_for_clustering(
    labels: pd.Series,
    clustering_algo: str,
    correlation_matrix: pd.DataFrame,
    protein_id_to_number_of_residues: dict[str, int],
    generate_STRING_networks: bool,
    only_include_alphafold_compatible_clusters: bool,
    fasta_df: pd.DataFrame,
    cluster_labels_to_ignore: list[str],
    generate_alphafold_queries: bool,
    model_seed: int,
    taxonomic_identifier: int,
    network_flavor: StringDbNetworkType.values,
) -> tuple[bytes, int]:
    """Create a zip file containing the user requested data (heatmaps, STRING networks, AlphaFold query files)
    for all clusters that are not in cluster_labels_to_ignore."""

    clusters_too_big_for_alphafold = 0

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for cluster_id in labels.unique():
            if cluster_id in cluster_labels_to_ignore:
                continue
            fig, ax = plt.subplots(figsize=(10, 8))

            proteins = get_proteins_of_specific_cluster(cluster_id, labels)
            number_of_residues_in_cluster = (
                get_number_of_amino_acid_residues_in_cluster(
                    proteins, protein_id_to_number_of_residues
                )
            )
            alphafold_job_limit = 5000
            if number_of_residues_in_cluster > alphafold_job_limit:
                clusters_too_big_for_alphafold += 1
                if only_include_alphafold_compatible_clusters:
                    continue

            get_heatmap_for_certain_cluster(proteins, ax, correlation_matrix)

            heatmap_filename = (
                f"{clustering_algo}_heatmap_{cluster_id}"
                f"__{number_of_residues_in_cluster}_residues.png"
            )
            heatmap_buffer = BytesIO()
            plt.savefig(heatmap_buffer, format="png", dpi=300)
            plt.close(fig)

            heatmap_buffer.seek(0)

            zipf.writestr(f"heatmap/{heatmap_filename}", heatmap_buffer.getvalue())

            if generate_STRING_networks:
                string_filename = (
                    f"{clustering_algo}_cluster_{cluster_id}"
                    f"__{number_of_residues_in_cluster}_residues.png"
                )

                string_data, number_of_ids_not_known_by_STRING = (
                    get_STRING_information_for_cluster(
                        taxonomic_identifier, proteins, network_flavor
                    )
                )

                zipf.writestr(
                    f"string_network/{string_filename}_{number_of_ids_not_known_by_STRING}_unknown_ids",
                    string_data,
                )

            if generate_alphafold_queries:
                query_filename = (
                    f"{clustering_algo}_alphafold_query_{cluster_id}"
                    f"__{number_of_residues_in_cluster}_residues.json"
                )
                zipf.writestr(
                    f"alphafold_prediction_queries/{query_filename}",
                    get_alphafold_query_file_for_specific_cluster(
                        f"cluster{cluster_id}", model_seed, fasta_df, proteins
                    ),
                )

    zip_buffer.seek(0)
    return zip_buffer.getvalue(), clusters_too_big_for_alphafold


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
    if len(proteins) > 1:
        cluster_correlation_values = correlation_matrix.loc[
            proteins, proteins
        ].to_numpy()
        return (
            cluster_correlation_values.sum() - np.trace(cluster_correlation_values)
        ) / (cluster_correlation_values.size - len(proteins))
    else:
        return 1


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
    protein_ids = [
        id if "-" in id else f"{id}-1"
        for id, _ in protein_df.sort_values("Sample").groupby("Protein ID")
    ]
    protein_id_to_number_of_residues = get_protein_id_to_number_of_residues(fasta_df)
    ids_in_uniprot = set(protein_id_to_number_of_residues.keys())
    ids_not_in_uniprot = set(protein_ids) - ids_in_uniprot

    protein_to_intensities = {
        key: pd.Series(group[intensity_name].to_list())
        for key, group in protein_df.sort_values("Sample").groupby("Protein ID")
        if pd.Series(group[intensity_name].to_list()).nunique(dropna=True)
        > 1  # std of a protein must be != 0, otherwise it results in a correlation of NaN
        and key in ids_in_uniprot
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

    if len(ids_not_in_uniprot) > 0:
        msg = f"{len(ids_not_in_uniprot)} protein ids were removed from the correlation matrix since the ids were not found in the provided fasta."
        messages.append(dict(level=logging.WARNING, msg=msg))

    if (
        len(protein_ids)
        - len(correlation_matrix.columns)
        - len(ids_not_in_uniprot)
        - number_of_removals_caused_by_nans
    ):
        msg = f"{len(protein_ids) - len(correlation_matrix.columns) - len(ids_not_in_uniprot) - number_of_removals_caused_by_nans} \
        protein ids were removed from the correlation matrix since all the protein's intensity values were identical, \
        which would have lead to a standard deviation of 0 for this protein, \
        which would have resulted in undefined correlation values between this protein and all other proteins."
        messages.append(dict(level=logging.WARNING, msg=msg))

    return dict(
        correlation_matrix_df=correlation_matrix,
        removed_protein_ids_df=pd.DataFrame(
            {"Protein Id": list(set(protein_ids) - set(correlation_matrix.columns))}
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


def get_cluster_sizes_histogram(labels: pd.Series) -> Axes:
    fig_cluster_sizes, ax_cluster_sizes = plt.subplots()
    ax_cluster_sizes.hist(Counter(labels).values(), bins=40)
    ax_cluster_sizes.set_title("Histogram of Cluster Sizes")
    ax_cluster_sizes.set_xlabel("Cluster Size")
    ax_cluster_sizes.set_ylabel("Number of clusters with certain cluster size")
    return fig_cluster_sizes


def get_cluster_correlation_means_histogram(
    cluster_correlation_means: list[float],
) -> Axes:
    fig_correlation_means, ax_correlation_means = plt.subplots()
    ax_correlation_means.hist(cluster_correlation_means, bins=40)
    ax_correlation_means.set_title("Histogram of Intra Cluster Correlation Means")
    ax_correlation_means.set_xlabel("Mean Correlation")
    ax_correlation_means.set_ylabel("Number of clusters with certain mean correlation")
    return fig_correlation_means


def hdbscan_for_ppi(
    distance_matrix_df: pd.DataFrame,
    correlation_matrix_df: pd.DataFrame,
    min_cluster_size: int,
) -> dict:
    """Runs the HDBSCAN algorithm (from the hdbscan library) for clustering the proteins that are likely to interact into groups.
    :param distance_matrix_df: Dataframe containing the distance matrix.
    :param correlation_matrix_df: Dataframe containing the original correlation matrix.
    :param min_cluster_size: HDBSCAN won't determine clusters with less than min_cluster_size proteins.
    :return: Returns a dict with a dataframe containing the assigned labels, a dataframe with a dbcv score for each cluster and
    histograms of the dbcv scores, correlation means and cluster sizes."""
    distance_matrix = distance_matrix_df.to_numpy()
    clusterer = hdbscan.HDBSCAN(
        metric="precomputed", min_cluster_size=min_cluster_size, gen_min_span_tree=True
    )
    clusterer.fit(distance_matrix)
    labels = pd.Series(clusterer.labels_, index=distance_matrix_df.index, name="Label")
    score = hdbscan.validity.validity_index(
        distance_matrix,
        clusterer.labels_,
        metric="precomputed",
        d=distance_matrix.shape[0],
        per_cluster_scores=True,
    )

    fig_dbcv, ax_dbcv = plt.subplots()
    ax_dbcv.hist(score[1], bins=40)
    ax_dbcv.set_title("Histogram of DBCV Scores")
    ax_dbcv.set_xlabel("DBCV Score")
    ax_dbcv.set_ylabel("Number of clusters with certain DBCV Score")

    cluster_correlation_means = []
    for label in labels.unique():
        if label == -1:
            continue
        cluster_correlation_means.append(
            get_correlation_mean_of_cluster(labels, label, correlation_matrix_df)
        )

    return dict(
        cluster_labels_df=OutputItem(
            output_type=OutputType.DATAFRAME,
            value=labels.to_frame(),
        ),
        dbcv_scores_df=OutputItem(
            output_type=OutputType.DATAFRAME,
            value=pd.DataFrame(score[1], columns=["DBCV"]),
        ),
        histogram_dbcv=OutputItem(OutputType.PNG_BASE64, fig_to_base64(fig_dbcv)),
        histogram_correlation_means=OutputItem(
            OutputType.PNG_BASE64,
            fig_to_base64(
                get_cluster_correlation_means_histogram(cluster_correlation_means)
            ),
        ),
        histogram_cluster_sizes=OutputItem(
            OutputType.PNG_BASE64, fig_to_base64(get_cluster_sizes_histogram(labels))
        ),
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
    taxonomic_identifier: int,
    network_flavor: StringDbNetworkType.values,
) -> dict:
    protein_id_to_number_of_residues = get_protein_id_to_number_of_residues(fasta_df)
    zip_plot_in_bytes, clusters_too_big_for_alphafold = get_output_zip_for_clustering(
        cluster_labels_df["Label"],
        output_name,
        correlation_matrix_df,
        protein_id_to_number_of_residues,
        generate_STRING_networks,
        only_include_alphafold_compatible_clusters,
        fasta_df,
        cluster_labels_to_ignore,
        generate_alphafold_queries,
        model_seed,
        taxonomic_identifier,
        network_flavor,
    )

    messages = []
    if clusters_too_big_for_alphafold > 0:
        msg = f"{clusters_too_big_for_alphafold} clusters are too big for generating a AlphaFold Multimer query as AlphaFold only allows jobs of up to 5,000 residues as of June 2026."
        messages.append(dict(level=logging.WARNING, msg=msg))

    return dict(
        downloads=OutputItem(
            output_type=OutputType.DOWNLOAD,
            value={f"{output_name}.zip": zip_plot_in_bytes},
        ),
        messages=messages,
    )


def get_clusters_based_on_correlation_mean(
    threshold: float,
    cluster_labels_df: pd.DataFrame,
    correlation_matrix_df: pd.DataFrame,
    output_name: str,
    generate_STRING_networks: bool,
    only_include_alphafold_compatible_clusters: bool,
    fasta_df: pd.DataFrame,
    generate_alphafold_queries: bool,
    model_seed: int,
    taxonomic_identifier: int,
    network_flavor: StringDbNetworkType.values,
) -> dict:
    """Selects all clusters with a mean correlation above a certain threshold and
    creates the requested output zip (heatmaps, STRING networks, AlphaFold json queries) for them.
    :param threshold: The minimum corrrelation mean for a cluster to be included.
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
    ]  # HDBSCAN labels proteins that are assigned to no cluster with -1
    for label in cluster_labels_df["Label"].unique():
        if label == -1:
            continue
        if (
            get_correlation_mean_of_cluster(
                cluster_labels_df["Label"], label, correlation_matrix_df
            )
            < threshold
        ):
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
    taxonomic_identifier: int,
    network_flavor: StringDbNetworkType.values,
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

    silhouette_per_cluster = pd.Series(dtype=float)
    silhouette_scores_per_sample = silhouette_samples(
        distance_matrix, labels, metric="precomputed"
    )
    for label in labels.unique():
        mask = labels == label
        silhouette_per_cluster.loc[label] = silhouette_scores_per_sample[mask].mean()
    fig_silhouette, ax_silhouette = plt.subplots()
    ax_silhouette.hist(silhouette_per_cluster, bins=40)
    ax_silhouette.set_title("Histogram of Silhouette Scores")
    ax_silhouette.set_xlabel("Silhouette Score")
    ax_silhouette.set_ylabel("Number of clusters with certain Silhouette Score")

    cluster_correlation_means = []
    for label in labels.unique():
        cluster_correlation_means.append(
            get_correlation_mean_of_cluster(labels, label, correlation_matrix_df)
        )

    return dict(
        cluster_labels_df=OutputItem(
            output_type=OutputType.DATAFRAME,
            value=pd.DataFrame(labels, columns=["Label"]),
        ),
        silhouette_scores_df=OutputItem(
            output_type=OutputType.DATAFRAME,
            value=pd.DataFrame(silhouette_per_cluster, columns=["Silhouette"]),
        ),
        histogram_silhouette=OutputItem(
            OutputType.PNG_BASE64, fig_to_base64(fig_silhouette)
        ),
        histogram_correlation_means=OutputItem(
            OutputType.PNG_BASE64,
            fig_to_base64(
                get_cluster_correlation_means_histogram(cluster_correlation_means)
            ),
        ),
        histogram_cluster_sizes=OutputItem(
            OutputType.PNG_BASE64, fig_to_base64(get_cluster_sizes_histogram(labels))
        ),
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
    taxonomic_identifier: int,
    network_flavor: StringDbNetworkType.values,
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
    cluster_labels_to_ignore = []
    for label in cluster_labels_df["Label"].unique():
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
    )
