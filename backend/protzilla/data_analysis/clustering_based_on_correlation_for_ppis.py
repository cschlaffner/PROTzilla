import logging

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import requests
from typing import Literal
from sklearn.metrics import silhouette_samples
import os
import hdbscan
from io import BytesIO
import zipfile

from backend.protzilla.utilities.utilities import (
    default_intensity_column,
    fig_to_base64,
)
from backend.protzilla.steps import OutputItem, OutputType
from protzilla.constants.paths import RUNS_PATH


def make_protein_ids_STRING_readable(protein_ids: list[str]) -> list[str]:
    """remove "-x" from protein names as STRING does not know them"""
    for i, protein_id in enumerate(protein_ids):
        if "-" in protein_id:
            protein_ids[i] = protein_ids[i][: protein_id.find("-")]
    return protein_ids


def get_STRING_information_for_cluster(
    proteins: list[str], image_type: Literal["svg", "highres_image"] = "highres_image"
):
    """to display the svgs: display(SVG(get_STRING_information_for_cluster(proteins))),
    there might be ids STRING does not know and will therefore ignore"""
    proteins = make_protein_ids_STRING_readable(proteins)
    request_url = f"https://version-12-0.string-db.org/api/{image_type}/network"

    params = {
        "identifiers": "\r".join(proteins),
        "species": 9606,  # Todo
        "network_flavor": "evidence",  # confidence vs. evidence
        "network_type": "physical",  # physical vs functional
        "required_score": 0,
        "show_query_node_labels": 1,
        "add_white_nodes": 0,  # if string only knows one of the ids, do not automatically add the top10 interactors of this protein
        "caller_identity": "Anna's bachelor thesis",
    }

    response = requests.post(request_url, data=params)
    return response.content


def show_heatmap_for_certain_cluster(proteins: list[str], axes, correlation_matrix):
    df = pd.DataFrame(
        np.zeros((len(proteins), len(proteins))), columns=proteins, index=proteins
    )
    for protein in proteins:
        for protein2 in proteins:
            df.loc[protein, protein2] = correlation_matrix.loc[protein, protein2]
    return sns.heatmap(
        df,
        xticklabels=df.columns.values,
        yticklabels=df.columns.values,
        cmap=sns.diverging_palette(220, 10, as_cmap=True),
        vmin=-1,
        vmax=1,
        ax=axes,
    )


def get_proteins_of_specific_cluster(
    cluster_label: int, all_labels, distance_matrix_used_for_clustering
) -> list[str]:
    proteins = []
    for i in range(0, len(all_labels)):
        if all_labels[i] == cluster_label:
            proteins.append(distance_matrix_used_for_clustering.columns[i])
    return proteins


def get_proteins_of_best_silhouette_cluster(
    clustering_labels, distance_matrix_used_for_clustering
):
    sil_scores = silhouette_samples(
        X=distance_matrix_used_for_clustering,
        labels=clustering_labels,
        metric="euclidean",
    )
    best_cluster = clustering_labels[np.argmax(sil_scores)]
    return get_proteins_of_specific_cluster(
        best_cluster, clustering_labels, distance_matrix_used_for_clustering
    )


def process_clustering(
    labels,
    clustering_algo,
    correlation_matrix,
    protein_id_to_number_of_residues,
    generate_STRING_networks: bool,
    cluster_labels_to_ignore=None,
):
    # run_directory = RUNS_PATH / disk_operator.run_dir

    clusters_too_big_for_alphafold = 0

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for cluster_id in set(labels):
            if cluster_labels_to_ignore and cluster_id in cluster_labels_to_ignore:
                continue
            fig, ax = plt.subplots(figsize=(10, 8))

            proteins = get_proteins_of_specific_cluster(
                cluster_id, labels, correlation_matrix
            )
            number_of_residues_in_cluster = (
                get_number_of_amino_acid_residues_in_cluster(
                    proteins, protein_id_to_number_of_residues
                )
            )
            alphafold_job_limit = 10000
            if number_of_residues_in_cluster > alphafold_job_limit:
                clusters_too_big_for_alphafold += 1

            show_heatmap_for_certain_cluster(proteins, ax, correlation_matrix)

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

                string_data = get_STRING_information_for_cluster(proteins)

                zipf.writestr(f"string_network/{string_filename}", string_data)

    zip_buffer.seek(0)
    return zip_buffer.getvalue(), clusters_too_big_for_alphafold
    # zip_buffer.getvalue() enthält zip als bytes

    for filename in os.listdir(f"plots/{clustering_algo}/heatmap/"):
        file_path = os.path.join(f"plots/{clustering_algo}/heatmap/", filename)
        os.remove(file_path)
    for filename in os.listdir(f"plots/{clustering_algo}/string_network/"):
        file_path = os.path.join(f"plots/{clustering_algo}/string_network/", filename)
        os.remove(file_path)

    for cluster_id in set(labels):
        if cluster_labels_to_ignore and cluster_id in cluster_labels_to_ignore:
            continue
        fig, ax = plt.subplots(figsize=(10, 8))

        proteins = get_proteins_of_specific_cluster(
            cluster_id, labels, correlation_matrix
        )
        number_of_residues_in_cluster = get_number_of_amino_acid_residues_in_cluster(
            proteins, protein_id_to_number_of_residues
        )

        show_heatmap_for_certain_cluster(proteins, ax, correlation_matrix)
        plt.savefig(
            f"plots/{clustering_algo}/heatmap/{clustering_algo}_heatmap_{cluster_id}__{number_of_residues_in_cluster}_residues.png",
            dpi=300,
        )
        plt.close(fig)

        with open(
            f"plots/{clustering_algo}/string_network/{clustering_algo}_cluster_{cluster_id}__{number_of_residues_in_cluster}_residues.png",
            "wb",
        ) as f:
            f.write(get_STRING_information_for_cluster(proteins))


def get_number_of_amino_acid_residues_in_cluster(
    uniprot_ids: list[str], protein_id_to_number_of_residues
) -> int:
    number_of_residues = 0
    for id in uniprot_ids:
        number_of_residues += protein_id_to_number_of_residues.get(
            id, 0
        )  # todo: wirklich 0?
    return number_of_residues


def get_protein_id_to_number_of_residues(protein_ids):
    protein_id_to_number_of_residues = {}
    for i in range(0, len(protein_ids), 1000):
        url = f"https://rest.uniprot.org/uniprotkb/accessions?accessions={','.join(protein_ids[i:min(i + 1000, len(protein_ids))])}&format=fasta"
        response = requests.get(url, timeout=20)  # todo: warnings wenn timeout/error
        response.raise_for_status()
        fasta = ""
        current_id = None
        for line in response.text.splitlines():
            if line.startswith(">"):
                if current_id is not None:
                    protein_id_to_number_of_residues[current_id] = len("".join(fasta))
                fasta = []
                current_id = line.split("|")[1]
            else:
                fasta.append(line.strip())
        if current_id is not None:
            protein_id_to_number_of_residues[current_id] = len("".join(fasta))
    return protein_id_to_number_of_residues


def get_correlation_mean_of_cluster(
    clustering_labels, cluster_of_interest, correlation_matrix
):
    proteins = get_proteins_of_specific_cluster(
        cluster_of_interest, clustering_labels, correlation_matrix
    )
    # print(proteins)

    # cluster_correlation_mean = 0
    # for protein in proteins:
    #     for protein2 in proteins:
    #         if protein == protein2:
    #             continue
    #         cluster_correlation_mean += correlation_matrix.loc[protein, protein2]
    if len(proteins) > 1:
        # return cluster_correlation_mean/(len(proteins)*len(proteins)-len(proteins))
        correlation = correlation_matrix.loc[proteins, proteins].to_numpy()
        # Remove diagonal (self-correlations)
        if (correlation.sum() - np.trace(correlation)) / (correlation.size - len(proteins)) > 1:
            tmp = 2
        return (correlation.sum() - np.trace(correlation)) / (
            correlation.size - len(proteins)
        )
    else:
        return 0  # wenn genau ein Protein im cluster todo


def get_correlation_matrix(protein_df: pd.DataFrame) -> dict:
    intensity_name = default_intensity_column(protein_df)
    protein_ids = [
        key for key, _ in protein_df.sort_values("Sample").groupby("Protein ID")
    ]

    # ToDo: Also remove NaNs

    protein_id_to_number_of_residues = get_protein_id_to_number_of_residues(protein_ids)
    ids_in_uniprot = set(protein_id_to_number_of_residues.keys())
    ids_not_in_uniprot = set(protein_ids) - ids_in_uniprot

    protein_to_intensities = {
        key: pd.Series(group[intensity_name].to_list())
        for key, group in protein_df.sort_values("Sample").groupby("Protein ID")
        if pd.Series(group[intensity_name].to_list()).nunique(dropna=True) > 1
        and key in ids_in_uniprot
    }
    correlation_matrix = pd.DataFrame(protein_to_intensities).corr()

    messages = []
    msg = f"{len(ids_not_in_uniprot)} protein ids were removed from the correlation matrix since the ids could not be found in uniprot."
    messages.append(dict(level=logging.WARNING, msg=msg))
    msg = f"{len(protein_ids) - len(correlation_matrix.columns) - len(ids_not_in_uniprot)} protein ids were removed from the correlation matrix since all the protein's intensity values are identical, which would lead to a standard deviation of 0 for this protein, which would result in undefined correlation values between this protein and all other proteins."
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
) -> dict:
    distance_matrix = correlation_matrix_df.to_numpy()
    distance_matrix = np.clip(
        distance_matrix, -0.999999, 0.999999
    )  # war notw. für den validity score von hdbscan ->wenn irgendwo eine 1 drin steht, wird das für die dist-matrix zu 0 und dann teilen wir im Algo durch 0
    distance_matrix = np.sqrt(2 * (1 - distance_matrix))
    np.fill_diagonal(distance_matrix, 0)
    test = distance_matrix_df = pd.DataFrame(
        distance_matrix,
        index=correlation_matrix_df.columns,
        columns=correlation_matrix_df.columns,
    )
    print("CREATED:", test.index[:5])
    return dict(
        distance_matrix_df=pd.DataFrame(
            distance_matrix,
            index=correlation_matrix_df.columns,
            columns=correlation_matrix_df.columns,
        ),
    )


def hdbscan_for_ppi(distance_matrix_df: pd.DataFrame, correlation_matrix_df) -> dict:
    print("RECEIVED:", distance_matrix_df.index[:5])
    distance_matrix = distance_matrix_df.to_numpy()
    clusterer = hdbscan.HDBSCAN(
        metric="precomputed", min_cluster_size=2, gen_min_span_tree=True
    )  # , cluster_selection_method="leaf") #eins kleiner
    clusterer.fit(distance_matrix)
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
    for label in set(clusterer.labels_):
        cluster_correlation_means.append(
            get_correlation_mean_of_cluster(
                clusterer.labels_, label, correlation_matrix_df
            )
        )

    fig_correlation_means, ax_correlation_means = plt.subplots()
    ax_correlation_means.hist(cluster_correlation_means, bins=40)
    ax_correlation_means.set_title("Histogram of Intra Cluster Correlation Means")
    ax_correlation_means.set_xlabel("Mean Correlation")
    ax_correlation_means.set_ylabel("Number of clusters with certain mean correlation")

    return dict(
        cluster_labels_df=OutputItem(
            output_type=OutputType.DATAFRAME,
            value=pd.DataFrame(clusterer.labels_, columns=["Label"]),
        ),
        dbcv_scores_df=OutputItem(
            output_type=OutputType.DATAFRAME,
            value=pd.DataFrame(score[1], columns=["DBCV"]),
        ),
        histogram_dbcv=OutputItem(OutputType.PNG_BASE64, fig_to_base64(fig_dbcv)),
        histogram_correlation_means=OutputItem(
            OutputType.PNG_BASE64, fig_to_base64(fig_correlation_means)
        ),
    )


def hdbscan_cluster_scores_histograms(
    output_dbcv_scores_df, output_cluster_labels_df, distance_matrix_df
) -> list[OutputItem]:
    fig_dbcv, ax_dbcv = plt.subplots()
    ax_dbcv.hist(output_dbcv_scores_df["DBCV"], bins=40)
    ax_dbcv.set_title("Histogram of DBCV Scores")
    ax_dbcv.set_xlabel("DBCV Score")
    ax_dbcv.set_ylabel("Number of clusters with certain DBCV Score")

    cluster_correlation_means = []
    for label in set(output_cluster_labels_df["Label"]):
        cluster_correlation_means.append(
            get_correlation_mean_of_cluster(
                output_cluster_labels_df["Label"], label, distance_matrix_df
            )
        )

    fig_correlation_means, ax_correlation_means = plt.subplots()
    ax_correlation_means.hist(cluster_correlation_means, bins=40)
    ax_correlation_means.set_title("Histogram of Intra Cluster Correlation Means")
    ax_correlation_means.set_xlabel("Mean Correlation")
    ax_correlation_means.set_ylabel("Number of clusters with certain mean correlation")
    return [fig_to_base64(fig_dbcv), fig_to_base64(fig_correlation_means)]


def get_clusters_based_on_correlation_mean(
    correlation_threshold: float,
    cluster_labels_df: pd.DataFrame,
    correlation_matrix_df: pd.DataFrame,
    output_name: str,
    generate_STRING_networks: bool,
) -> dict:
    cluster_labels_to_ignore = [-1]
    cluster_labels = cluster_labels_df["Label"].to_list()
    for label in set(cluster_labels):
        if (
            get_correlation_mean_of_cluster(
                cluster_labels, label, correlation_matrix_df
            )
            < correlation_threshold
        ):
            cluster_labels_to_ignore.append(label)
    # protein_id_to_number_of_residues = dict(zip(protein_id_to_number_of_residues_df["protein_id"], protein_id_to_number_of_residues_df["number_of_residues"]))
    protein_id_to_number_of_residues = get_protein_id_to_number_of_residues(
        list(correlation_matrix_df.columns)
    )
    zip_plot_in_bytes, clusters_too_big_for_alphafold = process_clustering(
        cluster_labels,
        output_name,
        correlation_matrix_df,
        protein_id_to_number_of_residues,
        generate_STRING_networks,
        cluster_labels_to_ignore,
    )

    messages = []
    if clusters_too_big_for_alphafold > 0:
        msg = f"{clusters_too_big_for_alphafold} clusters are too big for generating a AlphaFold Multimer query as AlphaFold only allows jobs of up to 10,000 residues as of June 2026."
        messages.append(dict(level=logging.WARNING, msg=msg))

    return dict(
        downloads=OutputItem(
            output_type=OutputType.DOWNLOAD,
            value={f"{output_name}.zip": zip_plot_in_bytes},
        ),
        messages=messages,
    )
