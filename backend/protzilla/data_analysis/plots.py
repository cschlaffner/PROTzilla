import logging

from backend.protzilla.constants.option_types import (
    PValueColumnName,
    SimpleImputerStrategyType,
)
from backend.protzilla.constants.data_types import ClassificationType
import dash_bio as dashbio
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
from sklearn.metrics import precision_recall_curve, auc, roc_curve
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances

from backend.protzilla.constants.colors import (
    PLOT_COLOR_SEQUENCE,
    PLOT_PRIMARY_COLOR,
    PLOT_SECONDARY_COLOR,
)
from backend.protzilla.utilities.clustergram import (
    Clustergram,
    AXIS_PROTEIN,
)
from backend.protzilla.utilities.transform_dfs import is_long_format, long_to_wide

colors = {
    "plot_bgcolor": "white",
    "gridcolor": "#F1F1F1",
    "linecolor": "#F1F1F1",
    "annotation_text_color": "#ffffff",
    "annotation_proteins_of_interest": "#4A536A",
}


def scatter_plot(
    input_df: pd.DataFrame,
    metadata_df: pd.DataFrame | None = None,
    metadata_column: str | None = None,
) -> dict:
    """
    Function to create a scatter plot from data.

    :param input_df: the dataframe that should be plotted. It should have either 2
        or 3 dimensions
    :param metadata_df: the Dataframe with one column according to which the marks should
        be colored. This is an optional parameter
    :param metadata_column: the name of the column in `metadata_df` that contains the
        group information for each sample. This parameter is required if `metadata_df`
        is provided.

    :return: returns a dictionary containing a list with a plotly figure and/or a list of messages
    """
    if isinstance(metadata_df, pd.DataFrame):
        if metadata_column not in metadata_df.columns:
            raise ValueError(
                "The column selected for annotation is not present in the corresponding metadata dataframe.",
            )

    intensity_df = input_df.copy()
    if isinstance(metadata_df, pd.DataFrame):
        intensity_df = pd.merge(
            intensity_df,
            metadata_df[["Sample", metadata_column]],
            on="Sample",
            how="left",
        )
    else:
        # Mock a metadata column here so that we can treat dfs with and without metadata the same way
        metadata_column = "mock_metadata_column"
        intensity_df[metadata_column] = None
    intensity_df = intensity_df.drop(columns="Sample")

    color_col = (
        metadata_column if intensity_df[metadata_column].notnull().any() else None
    )
    if intensity_df.shape[1] - 1 == 2:
        x_name, y_name = intensity_df.drop(columns=metadata_column).columns[:2]
        if not (
            pd.api.types.is_numeric_dtype(intensity_df[x_name])
            and pd.api.types.is_numeric_dtype(intensity_df[y_name])
        ):
            raise ValueError(
                "All columns used for the 2D scatter plot must be numeric."
            )
        fig = px.scatter(intensity_df, x=x_name, y=y_name, color=color_col)
    elif intensity_df.shape[1] - 1 == 3:
        x_name, y_name, z_name = intensity_df.drop(columns=metadata_column).columns[:3]
        if not (
            pd.api.types.is_numeric_dtype(intensity_df[x_name])
            and pd.api.types.is_numeric_dtype(intensity_df[y_name])
            and pd.api.types.is_numeric_dtype(intensity_df[z_name])
        ):
            raise ValueError(
                "All columns used for the 3D scatter plot must be numeric."
            )
        fig = px.scatter_3d(intensity_df, x=x_name, y=y_name, z=z_name, color=color_col)
    else:
        raise ValueError(
            f"The provided DataFrame has {intensity_df.shape[1] - 1} dimensions, but only 2D or 3D data can "
            "be plotted."
        )
    fig.update_layout(plot_bgcolor=colors["plot_bgcolor"])
    fig.update_xaxes(gridcolor=colors["gridcolor"], linecolor=colors["linecolor"])
    fig.update_yaxes(gridcolor=colors["gridcolor"], linecolor=colors["linecolor"])
    return dict(plots=[fig])


def create_volcano_plot(
    corrected_p_values_df: pd.DataFrame,
    log2_fold_change_df: pd.DataFrame,
    fc_threshold: float,
    alpha: float,
    group1: str,
    group2: str,
    item_type: PValueColumnName = PValueColumnName.protein_id,
    items_of_interest: list[str] | None = None,
) -> dict:
    """
    Function to create a volcano plot from p values and log2 fold change with the
    possibility to annotate proteins of interest.

    :param p_values:dataframe with p values
    :param log2_fc: dataframe with log2 fold change
    :param fc_threshold: the threshold for the fold change to show
    :param alpha: the alpha value for the significance line
    :param group1: the name of the first group
    :param group2: the name of the second group
    :param item_type: in ["Protein", "PTM"] the type of the items in the data
    :param items_of_interest: the items that should be annotated in the plot

    :return: returns a dictionary containing a list with a plotly figure and/or a list of messages
    """
    try:
        item_type = PValueColumnName(item_type)
    except ValueError:
        raise ValueError(
            f"Unknown column for p-values. Accepted types are {[item for item in PValueColumnName]}"
        )
    if item_type not in corrected_p_values_df.columns:
        raise KeyError(
            f"Column {item_type} not present in the data passed to this step. \
            Available columns are {[column for column in corrected_p_values_df.columns]}."
        )
    plot_df = corrected_p_values_df.join(
        log2_fold_change_df.set_index(item_type), on=item_type
    )
    fig = dashbio.VolcanoPlot(
        dataframe=plot_df,
        effect_size="log2_fold_change",
        p="corrected_p_value",
        snp=None,
        gene=None,
        genomewideline_value=-np.log10(alpha),
        effect_size_line=[-fc_threshold, fc_threshold],
        xlabel=f"log2(fc) ({group2} / {group1})",
        ylabel="-log10(p)",
        title="Volcano Plot",
        annotation=item_type,
        plot_bgcolor=colors["plot_bgcolor"],
        xaxis_gridcolor=colors["gridcolor"],
        yaxis_gridcolor=colors["gridcolor"],
    )
    if items_of_interest is None:
        items_of_interest = []

    # annotate the items of interest permanently in the plot
    for item in items_of_interest:
        fig.add_annotation(
            x=plot_df.loc[
                plot_df[item_type] == item,
                "log2_fold_change",
            ].values[0],
            y=-np.log10(
                plot_df.loc[
                    plot_df[item_type] == item,
                    "corrected_p_value",
                ].values[0]
            ),
            text=item,
            showarrow=True,
            arrowhead=1,
            font=dict(color=colors["annotation_text_color"]),
            align="center",
            arrowcolor=colors["annotation_proteins_of_interest"],
            bgcolor=colors["annotation_proteins_of_interest"],
            opacity=0.8,
            ax=0,
            ay=-20,
        )

    new_names = {
        "Point(s) of interest": f"Significant {item_type}s",
        "Dataset": f"Not Significant {item_type}s",
    }

    fig.for_each_trace(
        lambda t: t.update(
            name=new_names[t.name],
            legendgroup=new_names[t.name],
        )
    )
    fig.update_traces(
        marker=dict(color=PLOT_SECONDARY_COLOR),
        selector=dict(name=f"Significant {item_type}s"),
    )
    fig.update_traces(
        marker=dict(color=PLOT_PRIMARY_COLOR),
        selector=dict(name=f"Not Significant {item_type}s"),
    )

    return dict(
        plots=[fig],
        messages=[
            dict(
                level=logging.INFO,
                msg=f"Using possibly corrected alpha with value of {alpha}",
            )
        ],
    )

def clusteredheatmap_plot(
    protein_df: pd.DataFrame,
    metadata_df: pd.DataFrame | None,
    flip_axes: bool = False,
    metadata_column_samplegroupings: list[str] | None = None,
    # Algo params
    perform_row_clustering: bool = True,
    perform_column_clustering: bool = True,
    linkage_method: str = "single",
    distance_method: str = "euclidean",
    # Visu params
    heatmap_color_scale: str = "RdBu_r",
    heatmap_low_color_limit: float | None = None,
    heatmap_high_color_limit: float | None = None,
) -> dict:
    
    # c = ClusteredHeatMap()
    c = None

    fig = c.get_visualization_plotly()

    return dict(plots=[fig])

def clustergram_plot(
    protein_df: pd.DataFrame,
    metadata_df: pd.DataFrame | None,
    flip_axes: bool,
    metadata_column: str | None = None,
    heatmap_legend_title: str | None = None,
    dendrogram_line_width: int = 2,
    use_custom_color_scale: bool = False,
    heatmap_low_color_limit: float | None = None,
    heatmap_low_color: str | None = None,
    heatmap_high_color_limit: float | None = None,
    heatmap_high_color: str | None = None,
    imputation_strategy: SimpleImputerStrategyType = SimpleImputerStrategyType.MEAN.value,
) -> dict:
    """
    Creates a clustergram plot from a dataframe in protzilla wide format. The rows or
    columns of the clustergram are ordered according to the clustering resulting from
    the dendrogram. Optionally, a colorbar representing the different groups present
    in the data can be added and the axes of the heatmap can be inverted

    :param input_df: A dataframe in protzilla wide format, where each row
        represents a sample and each column represents a feature.
    :param metadata_df: A dataframe with a column that specifies the group of each
        sample in `input_df`. Each group will be assigned a color, which will be shown
        in the final plot as a colorbar next to the heatmap. This is an optional
        parameter
    :param flip_axes: If true, the rows and columns of the clustergram will be
        swapped. If false, the default orientation is used.
    :param metadata_column: The name of the column in `metadata_df` that contains the
        group information for each sample. This parameter is required if `metadata_df`
        is provided.
    :param heatmap_legend_title: The title to be displayed on top of the heatmap legend,
        e.g. "z-score" or "ratio h/l normalised"
    :param use_custom_color_scale: Whether or not to use custom value range limits
        and colors for the heatmap coloring
    :param heatmap_low_color_limit: (if use_custom_color_scale) the threshold for which
        all smaller values take heatmap_low_color
    :param heatmap_low_color: color used for the smallest mapped values
    :param heatmap_high_color_limit: (if use_custom_color_scale) the threshold for which
        all greater values take heatmap_high_color
    :param dendrogram_line_width: the width of the lines in the dendrogram
    :param heatmap_high_color: color used for the greatest mapped values

    return: returns a dictionary containing a list with a plotly figure and/or a list of messages
    """
    try:
        assert isinstance(protein_df, pd.DataFrame) and not protein_df.empty
        assert isinstance(metadata_df, pd.DataFrame) or not metadata_df

        input_df = protein_df

        messages = []
        input_df_wide = long_to_wide(input_df) if is_long_format(input_df) else input_df
        if input_df_wide.isna().any(axis=None):
            messages.append(
                dict(
                    level=logging.WARNING,
                    msg="The selected input dataframe contains missing values. The clustergram thus includes imputed values.",
                )
            )

        if isinstance(metadata_df, pd.DataFrame):
            assert metadata_column in metadata_df.columns
            # TODO: debatable if this filtering should be done here or in the filtering steps
            filtered_metadata_df = metadata_df[
                metadata_df["Sample"].isin(input_df_wide.index)
            ]

            assert len(input_df_wide) == len(filtered_metadata_df)
            # In the clustergram each row represents a sample that can pertain to a
            # group. In the following code the necessary data structures are created
            # to assign each group to a unique color.
            sample_group_dict = dict(
                zip(metadata_df["Sample"], metadata_df[metadata_column])
            )
            n_groups = len(set(sample_group_dict.values()))
            group_colors = px.colors.sample_colorscale(
                "Turbo",
                0.5 / n_groups + np.linspace(0, 1, n_groups, endpoint=False),
            )
            group_to_color_dict = dict(
                zip(
                    metadata_df[metadata_column].drop_duplicates(),
                    group_colors,
                )
            )
            # dictionary that maps each color to a group for the colorbar (legend)
            color_label_dict = {v: k for k, v in group_to_color_dict.items()}
            groups = [sample_group_dict[label] for label in input_df_wide.index]
            # maps each row (sample) to the corresponding color
            row_colors = [group_to_color_dict[g] for g in groups]
        else:
            row_colors = None
            color_label_dict = None

        if use_custom_color_scale:
            custom_color_scale = (
                (heatmap_low_color_limit, heatmap_low_color),
                (heatmap_high_color_limit, heatmap_high_color),
            )
        else:
            custom_color_scale = None

        imputer_parameters = dict(
            axis=AXIS_PROTEIN, missing_values="nan", strategy=imputation_strategy
        )

        clustergram = Clustergram(
            flip_axes=flip_axes,
            data=input_df_wide.values,
            row_labels=input_df_wide.index.values.tolist(),
            row_colors=row_colors,
            row_colors_to_label_dict=color_label_dict,
            column_labels=input_df_wide.columns.values.tolist(),
            line_width=dendrogram_line_width,
            color_map=px.colors.diverging.RdBu_r,
            hidden_labels=["row", "col"],
            custom_color_scale=custom_color_scale,
            heatmap_legend_title=heatmap_legend_title,
            imputer_parameters=imputer_parameters,
        )

        clustergram.update_layout(
            autosize=True,
        )
        return dict(plots=[clustergram], messages=messages)
    except AssertionError as e:
        if not isinstance(protein_df, pd.DataFrame):
            msg = 'The selected input for "input dataframe" is not a dataframe, dataframes have the suffix "df"'
        elif not isinstance(metadata_df, pd.DataFrame) and metadata_df is not None:
            msg = 'The selected input for "metadata dataframe" is not a dataframe, dataframes have the suffix "df"'
        elif (
            isinstance(metadata_df, pd.DataFrame)
            and metadata_column not in metadata_df.columns
        ):
            msg = "The column selected for annotation is not present in the corresponding metadata dataframe"
        elif isinstance(metadata_df, pd.DataFrame) and len(input_df_wide) != len(
            filtered_metadata_df
        ):
            msg = "The input dataframe and the grouping contain different samples"
        else:
            msg = f"An unknown error occurred: {e}"
        return dict(messages=[dict(level=logging.ERROR, msg=msg)])


def prot_quant_plot(
    protein_df: pd.DataFrame,
    protein_group: str,
    similarity: float = 1.0,
    similarity_measure: str = "euclidean distance",
) -> dict:
    """
    A function to create a graph visualising protein quantifications across all samples
    as a line diagram. It's possible to select one proteingroup that will be displayed in orange
    and choose a similarity measurement with a similarity score to get all proteingroups
    that are similar displayed in another color in this line diagram. All other proteingroups
    are displayed in the background as a grey polygon.

    :param input_df: A dataframe in protzilla wide format, where each row
        represents a sample and each column represents a feature.
    :param protein_group: Protein IDs as the columnheader of the dataframe
    :param similarity_measure: method to compare the chosen proteingroup with all others. The two
        methods are "cosine similarity" and "euclidean distance".
    :param similarity: similarity score of the chosen similarity measurement method.
    :return: returns a dictionary containing a list with a plotly figure
    """

    protein_wide_df = (
        long_to_wide(protein_df) if is_long_format(protein_df) else protein_df
    )

    if protein_group not in protein_wide_df.columns:
        raise ValueError("Please select a valid protein group.")
    elif similarity_measure == "euclidean distance" and similarity < 0:
        raise ValueError(
            "Similarity for euclidean distance should be greater than or equal to 0."
        )
    elif similarity_measure == "cosine similarity" and (
        similarity < -1 or similarity > 1
    ):
        raise ValueError("Similarity for cosine similarity should be between -1 and 1")

    fig = go.Figure()

    color_mapping = {
        "A": PLOT_PRIMARY_COLOR,
        "C": PLOT_COLOR_SEQUENCE[2],
    }

    lower_upper_x = []
    lower_upper_y = []

    lower_upper_x.append(protein_wide_df.index[0])
    lower_upper_y.append(protein_wide_df.iloc[0].min())

    for index, row in protein_wide_df.iterrows():
        lower_upper_x.append(index)
        lower_upper_y.append(row.max())

    for index, row in reversed(list(protein_wide_df.iterrows())):
        lower_upper_x.append(index)
        lower_upper_y.append(row.min())

    fig.add_trace(
        go.Scatter(
            x=lower_upper_x,
            y=lower_upper_y,
            fill="toself",
            name="Intensity Range",
            line=dict(color="silver"),
        )
    )

    similar_groups = []
    for group_to_compare in protein_wide_df.columns:
        if group_to_compare != protein_group:
            if similarity_measure == "euclidean distance":
                distance = euclidean_distances(
                    stats.zscore(protein_wide_df[protein_group]).reshape(1, -1),
                    stats.zscore(protein_wide_df[group_to_compare]).reshape(1, -1),
                )[0][0]
            else:
                distance = cosine_similarity(
                    stats.zscore(protein_wide_df[protein_group]).reshape(1, -1),
                    stats.zscore(protein_wide_df[group_to_compare]).reshape(1, -1),
                )[0][0]
            if similarity_measure == "euclidean distance":
                if distance <= similarity:
                    similar_groups.append(group_to_compare)
            else:
                if distance >= similarity:
                    similar_groups.append(group_to_compare)

    for group in similar_groups:
        fig.add_trace(
            go.Scatter(
                x=protein_wide_df.index,
                y=protein_wide_df[group],
                mode="lines",
                name=group[:15] + "..." if len(group) > 15 else group,
                line=dict(color=PLOT_COLOR_SEQUENCE[2]),
                showlegend=len(similar_groups) <= 7,
            )
        )

    if len(similar_groups) > 7:
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="lines",
                line=dict(color=PLOT_COLOR_SEQUENCE[2]),
                name="Similar Protein Groups",
            )
        )

    formatted_protein_name = (
        protein_group[:15] + "..." if len(protein_group) > 15 else protein_group
    )
    fig.add_trace(
        go.Scatter(
            x=protein_wide_df.index,
            y=protein_wide_df[protein_group],
            mode="lines",
            name=formatted_protein_name,
            line=dict(color=PLOT_SECONDARY_COLOR),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(color=color_mapping.get("A")),
            name="Experimental Group",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(color=color_mapping.get("C")),
            name="Control Group",
        )
    )

    fig.update_layout(
        title=f"Intensity of {formatted_protein_name} in all samples",
        plot_bgcolor=colors["plot_bgcolor"],
        xaxis_gridcolor=colors["gridcolor"],
        yaxis_gridcolor=colors["gridcolor"],
        xaxis_linecolor=colors["linecolor"],
        yaxis_linecolor=colors["linecolor"],
        xaxis_title="Sample",
        yaxis_title="Intensity",
        legend_title="Legend",
        xaxis=dict(
            tickmode="array",
            tickangle=0,
            tickvals=protein_wide_df.index,
            ticktext=[
                f"<span style='font-size: 10px; color:{color_mapping.get(label[0], 'black')}'><b>•</b></span>"
                for label in protein_wide_df.index
            ],
        ),
        autosize=True,
        margin=dict(l=100, r=300, t=100, b=100),
        legend=dict(
            x=1.05,
            y=1,
            bgcolor="rgba(255, 255, 255, 0.5)",
            orientation="v",
        ),
    )

    return dict(plots=[fig])


def precision_recall_plot(
    model: ClassificationType,
    X_test_df: pd.DataFrame,
    y_test_df: pd.DataFrame,
):
    y_score = model.predict_proba(X_test_df)[:, 1]
    precision, recall, _ = precision_recall_curve(y_test_df, y_score)
    auc_score = auc(recall, precision)
    fig = go.Figure()
    fig.add_shape(type="line", line=dict(dash="dash"), x0=0, x1=1, y0=1, y1=0)
    fig.add_trace(go.Scatter(x=recall, y=precision, mode="lines"))
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    fig.update_xaxes(constrain="domain")
    fig.update_layout(
        title=f"Precision-Recall Curve (AUC={auc_score:.4f})",
    )

    return dict(plots=[fig])


def roc_plot(
    model: ClassificationType,
    X_test_df: pd.DataFrame,
    y_test_df: pd.DataFrame,
):
    y_score = model.predict_proba(X_test_df)[:, 1]
    fpr, tpr, thresholds = roc_curve(y_test_df, y_score)
    auc_score = auc(fpr, tpr)
    fig = go.Figure()
    fig.add_shape(type="line", line=dict(dash="dash"), x0=0, x1=1, y0=0, y1=1)
    fig.add_trace(go.Scatter(x=fpr, y=tpr, mode="lines"))
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    fig.update_xaxes(constrain="domain")
    fig.update_layout(
        title=f"ROC Curve (AUC={auc_score:.4f})",
    )

    return dict(plots=[fig])
