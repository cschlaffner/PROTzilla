import logging
from collections import Counter
from math import sqrt, ceil

import pandas as pd
import plotly.graph_objects as go
from numpy import arange, array, flip, nan, ones
from plotly import colors
from plotly.figure_factory import create_dendrogram
from plotly.subplots import make_subplots
from pydeseq2.preprocessing import deseq2_norm
from scipy import stats
from scipy.cluster.hierarchy import linkage
from scipy.spatial.distance import cdist

from protzilla.data_analysis.ptm_quantification.flexiquant import flexiquant_lf


# TODO: also needs form
# TODO: tests?
def multiflex_lf(
        peptide_df: pd.DataFrame,
        metadata_df: pd.DataFrame,
        reference_group: str,
        grouping_column: str,
        num_init: int = 30,
        mod_cutoff: float = 0.5,
        # TODO: check what these params change and try to test them (in a small grid_search way?)
        imputation_cosine_similarity: float = 0.98,
        deseq2_normalization: bool = True,
        colormap: int = 1,
) -> dict:
    """
    Quantifies the extent of protein modifications in proteomics data by using robust linear regression to compare modified and unmodified peptide precursors
    and facilitates the analysis of modification dynamics and coregulated modifications across large datasets without the need for preselecting specific proteins.

    Parts of the implementation have been adapted from https://gitlab.com/SteenOmicsLab/multiflex-lf.
    Args:
        peptide_df (pd.DataFrame): DataFrame containing peptide-level quantification data with columns for
            'Protein ID', 'Sequence', 'Sample', and 'Intensity'.
        metadata_df (pd.DataFrame): DataFrame containing sample metadata with columns for 'Sample' and 'Group'.
        reference_group (str): The reference group used for comparison in the analysis.
        grouping_column (str): The column in metadata_df that contains group information.
        num_init (int, optional): Number of initializations for the robust linear regression. Default is 30.
        mod_cutoff (float, optional): Modification cutoff value for RM score calculation. Default is 0.5.
        imputation_cosine_similarity (float, optional): Cosine similarity threshold for missing value imputation.
            Default is 0.98.
        deseq2_normalization (bool, optional): Whether to apply DESeq2 normalization to RM scores before clustering.
            Default is True.
        colormap (int, optional): Colormap index for heatmap visualization. Default is 1 (RdBu). Other options:
            2: PiYG, 3: PRGn, 4: PuOr, 5: RdGy, 6: RdYlGn, 7: RdYlBu.
    Returns:
        dict: A dictionary containing the following keys:
            - 'RM_scores_clustered' (pd.DataFrame): DataFrame of clustered RM scores
            - 'diff_modified' (pd.DataFrame): DataFrame of modified peptide differences
            - 'raw_scores' (pd.DataFrame): DataFrame of raw peptide scores
            - 'removed_peptides' (pd.DataFrame): DataFrame of removed peptides during analysis
            - 'RM_scores' (pd.DataFrame): DataFrame of RM scores for all peptides
            - 'plots' (list): List of Plotly figures including RM score distribution plots,
                peptide clustering heatmap, and protein-wise heatmaps
            - 'messages' (list): List of log messages generated during the analysis
    """

    # create dataframe input for multiflex-lf
    df_intens_matrix_all_proteins = pd.DataFrame(
        {
            "ProteinID": peptide_df["Protein ID"],
            "PeptideID": peptide_df["Sequence"],
            "Sample": peptide_df["Sample"],
            "Intensity": peptide_df["Intensity"],
        }
    )
    if grouping_column not in metadata_df.columns:
        return dict(
            messages=[
                dict(
                    level=logging.ERROR,
                    msg=f"Grouping column {grouping_column} not found in metadata.",
                )
            ],
        )

    # add Group column to input
    df_intens_matrix_all_proteins = pd.merge(
        df_intens_matrix_all_proteins, metadata_df[["Sample", grouping_column]], on="Sample"
    )

    # check if reference identifier exists in Group column
    # TODO: test
    if str(reference_group) not in set(df_intens_matrix_all_proteins["Group"].astype(str)):
        return dict(
            messages=[
                dict(
                    level=logging.ERROR,
                    msg=f"Reference group {reference_group} not found in metadata.",
                )
            ],
        )
    if df_intens_matrix_all_proteins[grouping_column].nunique() < 2:
        return dict(
            messages=[
                dict(
                    level=logging.ERROR,
                    msg="At least two groups are required for multiFLEX-LF analysis.",
                )
            ],
        )

    df_intens_matrix_all_proteins = (
        df_intens_matrix_all_proteins.dropna(subset=["Intensity"])
        .groupby(["ProteinID", "PeptideID", "Group", "Sample"])["Intensity"]
        .apply(max)
        .unstack(level=["Group", "Sample"])
        .T
    )
    df_intens_matrix_all_proteins = df_intens_matrix_all_proteins.set_index(
        [
            df_intens_matrix_all_proteins.index.get_level_values("Group"),
            df_intens_matrix_all_proteins.index.get_level_values("Sample"),
        ]
    )
    df_intens_matrix_all_proteins = df_intens_matrix_all_proteins.sort_index(axis=0).sort_index(axis=1)

    # create a list of all proteins in the dataset
    list_proteins = (
        df_intens_matrix_all_proteins.columns.get_level_values("ProteinID")
        .unique()
        .sort_values()
    )

    df_diff_modified = pd.DataFrame()
    df_raw_scores = pd.DataFrame()
    df_removed_peptides = pd.DataFrame()
    RM_scores_df = pd.DataFrame()

    skipped_proteins = []

    flexi_error_messages = set()
    for protein in list_proteins:
        flexi_result = flexiquant_lf(
            peptide_df=peptide_df,
            metadata_df=metadata_df,
            reference_group=reference_group,
            protein_group=protein,
            grouping_column=grouping_column,
            num_init=num_init,
            mod_cutoff=mod_cutoff,
        )

        # TODO: test
        error_messages = [
            message
            for message in flexi_result["messages"]
            if message["level"] == logging.ERROR
        ]
        if any(error_messages):
            skipped_proteins.append(protein)
            flexi_error_messages.update(msg['msg'] for msg in error_messages)
            continue

        protein_raw_scores = flexi_result["raw_scores"]
        protein_raw_scores = protein_raw_scores.T
        protein_raw_scores.columns = protein_raw_scores.loc["Sample"]
        protein_raw_scores["ProteinID"] = protein
        protein_raw_scores.drop(
            index=[
                "Sample",
                "Slope",
                "R2 model",
                "R2 data",
                "Reproducibility factor",
                "Group",
            ],
            inplace=True,
        )
        protein_raw_scores = (
            protein_raw_scores.reset_index()
            .rename(columns={"index": "PeptideID"})
            .set_index(["ProteinID", "PeptideID"])
        )
        df_raw_scores = pd.concat([df_raw_scores, protein_raw_scores])

        protein_diff_modified = flexi_result["diff_modified"]
        protein_diff_modified.drop(columns=["Group"], inplace=True)
        protein_diff_modified = protein_diff_modified.T
        protein_diff_modified.columns = protein_diff_modified.loc["Sample"]
        protein_diff_modified["ProteinID"] = protein
        protein_diff_modified.drop(index="Sample", inplace=True)
        protein_diff_modified = (
            protein_diff_modified.reset_index()
            .rename(columns={"index": "PeptideID"})
            .set_index(["ProteinID", "PeptideID"])
        )
        df_diff_modified = pd.concat([df_diff_modified, protein_diff_modified])

        protein_removed_peptides = flexi_result["removed_peptides"]
        protein_removed_peptides_df = pd.DataFrame(
            {"ProteinID": protein, "PeptideID": protein_removed_peptides}
        )
        df_removed_peptides = pd.concat(
            [df_removed_peptides, protein_removed_peptides_df]
        )

        protein_RM_scores = flexi_result["RM_scores"]
        protein_RM_scores = protein_RM_scores.T
        protein_RM_scores.columns = pd.MultiIndex.from_arrays(
            [protein_RM_scores.loc["Group"], protein_RM_scores.loc["Sample"]],
            names=["Group", "Sample"],
        )
        protein_RM_scores["ProteinID"] = protein
        protein_RM_scores.drop(
            index=[
                "Sample",
                "Slope",
                "R2 model",
                "R2 data",
                "Reproducibility factor",
                "Group",
            ],
            inplace=True,
        )
        protein_RM_scores = (
            protein_RM_scores.reset_index()
            .rename(columns={"index": "PeptideID"})
            .set_index(["ProteinID", "PeptideID"])
        )
        RM_scores_df = pd.concat([RM_scores_df, protein_RM_scores])

    if RM_scores_df.empty:
        if len(flexi_error_messages) > 0:
            message = ("RM scores were not computed because the FlexiQuant-LF analysis failed for all proteins!\n"
                       "Errors:\n- ") + "\n- ".join(flexi_error_messages)
        else:
            message = "RM scores were not computed! Intensities of at least 5 peptides per protein have to be given!"
        return dict(
            messages=[
                dict(
                    level=logging.ERROR,
                    msg=message,
                )
            ],
        )

    # define the colormap for the heatmap as specified by the user
    _cmaps = {
        1: "RdBu",
        2: "PiYG",
        3: "PRGn",  # preserves original first colormap==3 branch
        4: "PuOr",
        5: "RdGy",
        6: "RdYlGn",
        7: "RdYlBu",
    }
    if colormap in _cmaps:
        color_map = _cmaps[colormap]
    else:
        color_map = _cmaps[0]

    # sort the proteins descending by number of peptides and samples with a RM scores below the modification cutoff
    sorted_proteins = list(
        RM_scores_df[RM_scores_df < mod_cutoff]
        .count(axis=1)
        .groupby("ProteinID")
        .sum()
        .sort_values(ascending=False)
        .index
    )

    heatmap_plots = []
    # go through all protein in the sorted order
    for protein_id in sorted_proteins:
        # dataframe of the RM scores of the current protein
        df_RM_scores_protein = RM_scores_df.loc[protein_id]

        # skip the protein, if dataframe empty
        if df_RM_scores_protein.empty:
            continue

        # create heatmap of the current protein
        heatmap_plots.append(
            create_heatmap(df_RM_scores_protein, protein_id, color_map, mod_cutoff)
        )

    # keep only peptides that have RM scores in at least two groups
    to_remove = RM_scores_df.loc[
        RM_scores_df.T.groupby("Group").count().replace(0, nan).count() < 2
    ].index
    df_RM_scores_all_proteins_reduced = RM_scores_df.drop(to_remove, axis=0)
    removed_peptides = pd.DataFrame(list(to_remove))

    if df_RM_scores_all_proteins_reduced.empty:
        # TODO: would be nice to test in case where enough groups are present
        if len(removed_peptides) > 0:
            removed_peptides.columns = ["ProteinID", "PeptideID"]
            removed_peptides = removed_peptides.set_index(["ProteinID"])
        return dict(
            messages=[
                dict(
                    level=logging.ERROR,
                    msg="No peptides with RM scores in at least two groups available for clustering!",
                )
            ],
            removed_peptides=removed_peptides,
        )

    # impute missing values for clustering
    (
        df_RM_scores_all_proteins_reduced,
        df_RM_scores_all_proteins_imputed,
        removed,
    ) = missing_value_imputation(df_RM_scores_all_proteins_reduced, round(1 - imputation_cosine_similarity, 3))
    removed_peptides = pd.concat([removed_peptides, removed])

    # check if RM scores dataframe is empty, if true return error and finish analysis
    # TODO: test
    if df_RM_scores_all_proteins_imputed.empty:
        # add removed peptides to csv file
        if len(removed_peptides) > 0:
            removed_peptides.columns = ["ProteinID", "PeptideID"]
            removed_peptides = removed_peptides.set_index(["ProteinID"])

        return dict(
            messages=[
                dict(
                    level=logging.ERROR,
                    msg="Imputation of RM scores for clustering was unsuccessful! Too many missing values in the data!",
                )
            ],
            removed_peptides=removed_peptides,
        )

    # list of all groups for creation the distribution plots and protein-wise heatmaps
    list_groups = list(set(RM_scores_df.columns.get_level_values("Group")))
    list_groups.sort()

    # TODO: test this whole path
    if deseq2_normalization:
        groups = pd.DataFrame(list(RM_scores_df.columns))
        groups.columns = ["Group", "Sample"]
        df_normalization = df_RM_scores_all_proteins_imputed.copy()

        # one column per peptide, one row per sample
        df_normalization = df_normalization.T
        df_normalization = df_normalization.astype(float)

        # apply normalization
        df_normalization = deseq2_norm(df_normalization)[0]

        # transpose back
        df_normalization = df_normalization.T

        # keep only normalized RM scores which were not missing before the previous imputation
        # then reimpute the missing values
        df_RM_scores_all_proteins_reduced = df_normalization[~df_RM_scores_all_proteins_reduced.isna()]
        df_RM_scores_all_proteins_reduced = round(df_RM_scores_all_proteins_reduced, 5)

        # impute missing values again
        (
            df_RM_scores_all_proteins_reduced,
            df_RM_scores_all_proteins_imputed,
            removed,
        ) = missing_value_imputation(
            df_RM_scores_all_proteins_reduced,
            round(1 - imputation_cosine_similarity, 5),
        )
        # dataframe of peptides that were removed during imputation
        if len(removed) > 0:
            removed_peptides = pd.concat((removed_peptides, removed))

        rm_score_dist_plots = create_RM_score_distribution_plots(df_RM_scores_all_proteins_reduced, list_groups)
    else:
        rm_score_dist_plots = create_RM_score_distribution_plots(RM_scores_df, list_groups)

    if len(removed_peptides) > 0:
        removed_peptides.columns = ["ProteinID", "PeptideID"]
        removed_peptides = removed_peptides.set_index(["ProteinID"])

    linkage_matrix = linkage(
        df_RM_scores_all_proteins_imputed,
        metric=lambda u, v: RM_score_distance(u, v, mod_cutoff),
        method="average",
    )

    # create plotly figure
    (
        peptide_clustering_fig,
        array_RM_scores_all_proteins_reduced,
        ordered_peptides,
    ) = peptide_clustering(
        df_RM_scores=df_RM_scores_all_proteins_reduced,
        linkage_matrix=linkage_matrix,
        mod_cutoff=mod_cutoff,
        cmap=color_map,
        colors=["black"] * 8,
        clust_threshold=None,
        clust_ids=[],
    )

    # create output of the RM scores in same order as in the heatmap
    output_df = pd.DataFrame(flip(array_RM_scores_all_proteins_reduced, axis=0))
    output_df.columns = df_RM_scores_all_proteins_reduced.columns.get_level_values(
        "Sample"
    )
    # add the ID column
    output_df.index = pd.MultiIndex.from_tuples(
        flip(array(df_RM_scores_all_proteins_reduced.index)[ordered_peptides]),
        names=("ProteinID", "PeptideID"),
    )
    output_df = output_df.reset_index()
    output_df.index.names = ["ID"]

    return dict(
        RM_scores_clustered=output_df,
        diff_modified=df_diff_modified,
        raw_scores=df_raw_scores,
        removed_peptides=removed_peptides,
        RM_scores=RM_scores_df,
        plots=[rm_score_dist_plots, peptide_clustering_fig] + heatmap_plots,
        messages=[],
    )


def create_RM_score_distribution_plots(
        RM_scores_df: pd.DataFrame,
        list_groups: list[str],
        nbins: int = 30
) -> go.Figure:
    """
    Constructs a figure of distribution plots of the RM scores. For every group a separate plot is created
    with the different samples in different colors.
    """

    num_groups = len(list_groups)
    num_cols = ceil(sqrt(num_groups))

    fig = make_subplots(
        cols=num_cols,
        rows=num_groups // num_cols + (num_groups % num_cols > 0),
        subplot_titles=["Group: " + group for group in list_groups],
        horizontal_spacing=0.05,
        vertical_spacing=0.05,
    )

    # list of colors for the color coding of the different samples in one group
    n_most_common_group = Counter(RM_scores_df.columns.get_level_values("Group")).most_common(1)[0][1]
    colors_list = colors.sample_colorscale('Phase', [i / n_most_common_group for i in range(n_most_common_group)])

    data_min = RM_scores_df.min(axis=None)
    data_max = RM_scores_df.max(axis=None)
    bin_size = (data_max - data_min) / nbins

    for group_idx, group in enumerate(list_groups):
        df_group = RM_scores_df[group]
        row = group_idx // num_cols + 1
        col = group_idx % num_cols + 1

        for sample_idx, sample in enumerate(df_group):
            sample_data = df_group[sample].dropna()
            fig.add_trace(
                go.Histogram(
                    x=sample_data,
                    xbins_size=bin_size,
                    name=sample,
                    marker_color=colors_list[sample_idx],
                    opacity=0.5,
                    showlegend=df_group.shape[1] <= 10,
                    legendgroup=sample,
                ),
                row=row,
                col=col,
            )

            kernel = stats.gaussian_kde(sample_data.tolist())
            x_eval = arange(data_min, data_max + bin_size, bin_size / 10)
            pdf = kernel.pdf(x_eval)
            fig.add_trace(
                go.Scatter(
                    x=x_eval,
                    y=pdf,
                    mode='lines',
                    marker_color=colors_list[sample_idx],
                    showlegend=False,
                    yaxis='y',
                    legendgroup=sample
                ),
                row=row,
                col=col,
            )

    fig.update_xaxes(
        title_text="RM score",
        range=[0, data_max + bin_size],
    )
    fig.update_yaxes(
        title_text="Count",
    )
    fig.update_layout(
        title_text="Distribution of RM scores of multiFLEX-LF",
        barmode='overlay',
    )

    return fig


def create_heatmap(
        df_RM_scores: pd.DataFrame,
        protein_id: str,
        color_scale: str,
        mod_cutoff: float
) -> go.Figure:
    """
    Constructs a heatmap of the RM scores for a protein
    """

    # Create Plotly subplots figure
    fig = make_subplots(
        rows=1,
        cols=1,  # +1 for colorbar
        shared_yaxes=True,
        horizontal_spacing=0.01,
    )

    df_RM_scores = df_RM_scores.astype(float)
    fig.add_trace(
        go.Heatmap(
            z=df_RM_scores.values,
            x=df_RM_scores.columns.get_level_values("Sample"),
            y=df_RM_scores.index.get_level_values("PeptideID"),
            zmin=0,
            zmax=mod_cutoff * 2,
            hovertemplate="Sample: %{x}<br />Peptide: %{y}<br />RM score: %{z}",
            colorscale=color_scale,
            showscale=True,
            colorbar=dict(
                title="RM score",
                title_side="top",
                tickmode="array",
                thicknessmode="pixels",
                thickness=25,
                len=1,
                x=1.05,
                ticks="outside",
                dtick=5,
            ),
        ),
    )

    # Update layout
    fig.update_layout(
        title_text=f"Protein: {protein_id}",
        title_x=0.5,
        height=20 * df_RM_scores.shape[0] + 200,  # Adjust height to fit
        autosize=True,
        xaxis_title="",
        yaxis_title="Peptides",
        yaxis_nticks=df_RM_scores.shape[0],  # Adjust number of ticks
    )

    return fig


def missing_value_imputation(df_RM_scores: pd.DataFrame, max_cos_dist: float):
    """
    Impute missing values by calculating the median of the RM scores of all peptides
    with a cosine distance (i.e. 1 - cosine similarity) of at most max_cos_dist from
    the current peptide. If not all missing values of a peptide were imputed, it is
    removed from further analysis.
    """

    # copy df
    df_RM_scores_imputed = df_RM_scores.copy()

    for peptide in df_RM_scores.index:
        # get RM scores of the current peptide
        df_RM_scores_pep = df_RM_scores.loc[peptide]

        # skip if no missing value for peptide
        if not df_RM_scores_pep.isna().any():
            continue

        # remove NaN values
        df_RM_scores_pep = pd.DataFrame(df_RM_scores_pep.dropna())

        # get all other peptides and keep only samples that have a RM scores for the current peptides
        df_RM_scores_other_peps = df_RM_scores[df_RM_scores_pep.index].drop(
            peptide, axis=0
        )

        # calculate all pairwise cosine distances between the current peptide and all other
        cos_dist_other_peps = cdist(
            df_RM_scores_pep.T, df_RM_scores_other_peps, "cosine"
        )[0]

        # get the index of the closest peptides
        index_impute = df_RM_scores_other_peps[
            cos_dist_other_peps <= max_cos_dist
            ].index

        # skip peptide if less than 2 close peptides were found
        if len(index_impute) < 2:
            continue

        # calculate the median RM scores of the closest peptides
        df_imputation_values = (
            df_RM_scores.loc[index_impute].median().drop(df_RM_scores_pep.index)
        )

        # replace the missing values with the calculated values
        df_RM_scores_imputed.loc[
            peptide, df_imputation_values.index
        ] = df_imputation_values

    # remove all peptides that still have missing values
    remove_nans = df_RM_scores_imputed[df_RM_scores_imputed.isna().any(axis=1)].index
    df_RM_scores_imputed = df_RM_scores_imputed.drop(remove_nans, axis=0)
    df_RM_scores = df_RM_scores.drop(remove_nans, axis=0)

    return df_RM_scores, df_RM_scores_imputed, pd.DataFrame(list(remove_nans))


def RM_score_distance(u: float, v: float, mod_cutoff: float):
    """
    Calculation of the customized Manhattan distance between the arrays of RM scores u and v
    """
    # initialize distance vector
    if len(u) == len(v):
        dist = ones(len(u))
    else:
        return

    # calculate absolute differences between the elements of u and v
    for i in range(len(dist)):
        x = u[i]
        y = v[i]

        # penalize jumps from below to above the modification cutoff
        if (x < mod_cutoff and y >= mod_cutoff) or (x >= mod_cutoff and y < mod_cutoff):
            dist[i] = abs(x - y) + 1
        else:
            dist[i] = abs(x - y)

    # return sum of the penalized absolute differences
    return dist.sum()


def peptide_clustering(
        df_RM_scores: pd.DataFrame,
        linkage_matrix: pd.DataFrame,
        mod_cutoff: float,
        cmap: str,
        colors: list[str],
        clust_threshold: float | None,
        clust_ids: list,
):
    """
    Clustering results are saved as interactive HTML file with the dendrogram and the heatmap.
    """
    # initialize plotly figure and create the dendrogram based on the linkage matrix
    plotly_figure = create_dendrogram(
        df_RM_scores.astype(float),
        orientation="right",
        linkagefun=lambda x: linkage_matrix,
        colorscale=colors,
        color_threshold=clust_threshold,
    )

    # set x-axis of the dendrogram to x2 (axis nr. 2)
    for i in range(len(plotly_figure["data"])):
        plotly_figure["data"][i]["xaxis"] = "x2"

    # get order of the peptides in the dendrogram
    clust_leaves = plotly_figure["layout"]["yaxis"]["ticktext"]
    clust_leaves = list(map(int, clust_leaves))

    # create numpy array from the RM scores dataframe
    # and sort the peptides by the order in the dendrogram
    heat_data = df_RM_scores.to_numpy()
    heat_data = heat_data[clust_leaves, :]

    # define row and column labels for the heatmap
    row_names = [str(i[0]) + "<br />Peptide: " + str(i[1]) for i in df_RM_scores.index]
    row_names = list(array(row_names)[clust_leaves])
    col_names = list(df_RM_scores.columns.get_level_values(1))

    if len(clust_ids) == 0:
        # define the row IDs shown upon hovering over the cells of the heatmap
        clust_id = array(
            [[i] * df_RM_scores.shape[1] for i in range(len(clust_leaves) - 1, -1, -1)]
        )
    else:
        ## if cluster ids given add the cluster id to the hover information
        clust_id = array(
            [
                [str(i) + "<br />Cluster: " + str(clust_ids[i])] * df_RM_scores.shape[1]
                for i in range(len(clust_leaves) - 1, -1, -1)
            ]
        )

    # create heatmap
    heatmap = go.Heatmap(
        z=heat_data,
        colorscale=cmap,
        zmin=0,
        zmax=mod_cutoff * 2,
        customdata=clust_id,
        hovertemplate="Sample: %{x}<br />Protein: %{y}<br />RM score: %{z}<br />ID: %{customdata}",
        colorbar=dict(
            title="RM score",
            title_side="top",
            tickmode="array",
            thicknessmode="pixels",
            thickness=25,
            lenmode="pixels",
            len=250,
            yanchor="top",
            y=1,
            x=1.05,
            ticks="outside",
            dtick=5,
        ),
    )

    # align y-axis of heatmap to dendrogram
    heatmap["y"] = plotly_figure["layout"]["yaxis"]["tickvals"]

    # add the heatmap to plotly figure plotly_figure
    plotly_figure.add_trace(heatmap)

    # edit layout of plotly_figure
    figure_width = min(max(df_RM_scores.shape[1] * 50 + 100, 500), 1500)
    plotly_figure.update_layout(autosize=True, height=900, font={"size": 11})

    # amount of the figure size used for the dendrogram
    dendrogram_width = 100 / figure_width

    # update x-axis of the heatmap
    plotly_figure.update_layout(
        xaxis={
            "domain": [dendrogram_width, 1],
            "mirror": False,
            "showgrid": False,
            "showline": False,
            "zeroline": False,
            "showticklabels": True,
            "ticks": "outside",
            "ticktext": col_names,  # list of sample names
            "tickvals": arange(0, len(col_names)),
        }
    )

    # update x-axis (xaxis2) of the dendrogram
    plotly_figure.update_layout(
        xaxis2={
            "domain": [0, dendrogram_width],
            "mirror": False,
            "showgrid": False,
            "showline": False,
            "zeroline": False,
            "showticklabels": True,
            "ticks": "",
        }
    )

    # update y-axis of the heatmap
    plotly_figure.update_layout(
        yaxis={
            "domain": [0, 1],
            "mirror": False,
            "showgrid": False,
            "showline": False,
            "zeroline": False,
            "showticklabels": False,
            "ticks": "",
            "side": "right",
            "ticktext": row_names,  # list of the peptides
        }
    )

    # set plot title and axes lables
    plotly_figure.update_layout(
        title="Clustered Heatmap of RM scores",
        xaxis_title="Sample",
        yaxis_title="Peptides",
        xaxis2_title="",
        template="plotly_white",
    )

    # return the figure, the matrix of the RM scores in clustering order and the clustering order of the peptides
    return plotly_figure, heat_data, clust_leaves
