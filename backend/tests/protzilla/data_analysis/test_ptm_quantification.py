import pandas as pd
import plotly.graph_objs
import pytest
from statsmodels.compat.pandas import assert_frame_equal

from backend.protzilla.constants.data_types import DataKey
from backend.protzilla.data_analysis.ptm_quantification.flexiquant import (
    flexiquant_lf,
    calc_raw_scores,
    postprocess_raw_scores,
    normalize_t3median,
)
from backend.protzilla.data_analysis.ptm_quantification.multiflex import multiflex_lf
from backend.protzilla.importing.metadata_import import metadata_import_method
from backend.protzilla.importing.peptide_import import peptide_import
from backend.tests.paths import TEST_DATA_PATH, TEST_PEPTIDES_PATH
from backend.protzilla.constants.intensity_types import IntensityType


@pytest.fixture(scope="module")
def peptide_df_AD_only() -> pd.DataFrame:
    df = peptide_import(
        file_path=TEST_PEPTIDES_PATH / "peptides_P10636_AD01.txt",
        intensity_name=IntensityType.INTENSITY.value,
        map_to_uniprot=False,
    )[DataKey.PEPTIDE_DF]
    return df


@pytest.fixture
def peptide_df_one_sample_with_few_peptides(peptide_df_AD_only):
    first_sample = peptide_df_AD_only["Sample"].iloc[0]
    first_sample_peptides = peptide_df_AD_only[
        peptide_df_AD_only["Sample"] == first_sample
    ]["Sequence"].unique()
    selected_peptides = first_sample_peptides[:3]
    peptide_df_shortened = peptide_df_AD_only[
        ~(
            (peptide_df_AD_only["Sample"] == first_sample)
            & ~(peptide_df_AD_only["Sequence"].isin(selected_peptides))
        )
    ]
    return peptide_df_shortened


@pytest.fixture(scope="module")
def peptide_df_AD_CTR() -> pd.DataFrame:
    df = peptide_import(
        file_path=TEST_PEPTIDES_PATH / "peptides_P10636_AD01_CTR01.txt",
        intensity_name=IntensityType.INTENSITY.value,
        map_to_uniprot=False,
    )[DataKey.PEPTIDE_DF]
    return df


@pytest.fixture(scope="module")
def peptide_df(peptide_df_AD_CTR):
    peptide_df = peptide_df_AD_CTR[peptide_df_AD_CTR["Protein ID"] == "P10636"]
    return peptide_df


@pytest.fixture(scope="module")
def peptide_df_few_peptides(peptide_df_AD_CTR):
    all_peptides = peptide_df_AD_CTR["Sequence"].unique()
    selected_peptides = all_peptides[:8]
    peptide_df_shortened = peptide_df_AD_CTR[
        peptide_df_AD_CTR["Sequence"].isin(selected_peptides)
    ]
    return peptide_df_shortened


@pytest.fixture(scope="module")
def metadata_df():
    dummy_protein_df = pd.DataFrame(
        {
            "Sample": [
                "AD01_C1_INSOLUBLE_01",
                "AD01_C1_INSOLUBLE_02",
                "AD01_C1_INSOLUBLE_03",
                "CTR01_C1_INSOLUBLE_01",
            ]
        }
    )  # Dummy DataFrame for metadata import
    df = metadata_import_method(
        dummy_protein_df,
        TEST_DATA_PATH / "import_data/metadata/metadata_AD01_CTR01.csv",
        feature_orientation="Columns",
    )[DataKey.METADATA_DF]

    return df


def test_flexiquant_calculation():
    distance_df = pd.read_csv(TEST_DATA_PATH / "ptm_quantification_data/distances.csv")
    median_intensities = pd.read_csv(
        TEST_DATA_PATH / "ptm_quantification_data/median_intensities.csv", header=None
    ).set_index(0)[1]
    rm_scores_df = pd.read_csv(TEST_DATA_PATH / "ptm_quantification_data/rm_scores.csv")
    rm_scores_raw_df = pd.read_csv(
        TEST_DATA_PATH / "ptm_quantification_data/rm_scores_raw.csv"
    )

    rm_scores_raw_calc_df = calc_raw_scores(distance_df, median_intensities)
    assert_frame_equal(
        rm_scores_raw_calc_df.sort_index(axis=1), rm_scores_raw_df.sort_index(axis=1)
    )

    rm_scores_postprocessed_df, _ = postprocess_raw_scores(rm_scores_raw_calc_df)
    rm_scores_calc_df = normalize_t3median(rm_scores_postprocessed_df)
    assert_frame_equal(
        rm_scores_calc_df.sort_index(axis=1), rm_scores_df.sort_index(axis=1)
    )


@pytest.mark.parametrize(
    "reference_group,grouping_column,mod_cutoff",
    [
        ("AD", "Group", 0.5),
        ("CTR", "Group", 0.5),
        ("C1", "Batch", 0.5),
        ("C2", "Batch", 0.5),
        ("AD", "Group", 0.0),
        ("AD", "Group", 0.05),
        ("AD", "Group", 0.95),
        ("AD", "Group", 1.0),
    ],
)
def test_flexiquant(
    peptide_df, metadata_df, reference_group, grouping_column, mod_cutoff
):
    protein_group = "P10636"
    num_samples = peptide_df["Sample"].nunique()

    result = flexiquant_lf(
        peptide_df,
        metadata_df,
        reference_group,
        protein_group,
        grouping_column,
        num_init=30,
        mod_cutoff=mod_cutoff,
    )
    # Check calculations
    meta_columns = [
        "Sample",
        grouping_column,
        "Reproducibility factor",
        "R2 data",
        "R2 model",
        "Slope",
    ]
    rm_scores = result["RM_scores"].drop(meta_columns, axis=1)
    diff_mod_mask = result["diff_modified"].drop(["Sample", grouping_column], axis=1)
    diff_mod_scores = rm_scores[diff_mod_mask].where(diff_mod_mask, other=-1)
    assert diff_mod_scores.lt(mod_cutoff).all().all()

    non_diff_mod_scores = rm_scores[~diff_mod_mask].fillna(mod_cutoff + 1)
    assert non_diff_mod_scores.ge(mod_cutoff).all().all()

    # Check plots
    assert "plots" in result and len(result["plots"]) == num_samples
    removed_peptides = result["removed_peptides"]
    assert set(removed_peptides).isdisjoint(set(result["diff_modified"]))
    assert (
        len(result["messages"]) == 1
        and result["messages"][0]["msg"]
        == f"All {num_samples} samples have been processed successfully. "
        f"{len(removed_peptides)} peptides have been removed."
    )

    x_max_expected = (
        peptide_df[peptide_df["Sample"].str.contains(reference_group)]
        .groupby("Sequence")
        .median(numeric_only=True)["Intensity"]
        .max()
    )
    y_axes_maxes = peptide_df.groupby("Sample")["Intensity"].max()

    # Sanity checking that plot is not completely malformed
    for i, plot in enumerate(result["plots"]):
        full_fig = plot.full_figure_for_development()
        x_max_plot = full_fig.layout.xaxis.range[1]
        y_max_plot = full_fig.layout.yaxis2.range[1]

        sample = [
            idx for idx in y_axes_maxes.index if idx in full_fig.layout.title.text
        ]
        y_max_expected = y_axes_maxes[sample[0]]

        # These magic numbers are just a heuristic and especially the y-values are also dependent on the calculated
        # slope and confidence bands. Reimplementing the slope and confidence band calculation would be overkill, so I
        # left this, but these heuristic should at least catch any major mishaps in the regression and subsequent
        # plotting.
        assert x_max_expected <= x_max_plot < 1.1 * x_max_expected
        assert y_max_expected <= y_max_plot < 1.5 * y_max_expected


def test_flexiquant_grouping_column_not_in_df(peptide_df, metadata_df):
    reference_group = "AD"
    protein_group = "P10636"
    grouping_column = "NonExistentGroup"

    result = flexiquant_lf(
        peptide_df,
        metadata_df,
        reference_group,
        protein_group,
        grouping_column,
        num_init=30,
        mod_cutoff=0.5,
    )
    assert "messages" in result
    assert (
        result["messages"][0]["msg"]
        == f"No {grouping_column} column found in provided dataframe."
    )


def test_flexiquant_reference_group_not_in_group(peptide_df, metadata_df):
    reference_group = "AAAAAAD"
    protein_group = "P10636"
    grouping_column = "Group"

    result = flexiquant_lf(
        peptide_df,
        metadata_df,
        reference_group,
        protein_group,
        grouping_column,
        num_init=30,
        mod_cutoff=0.5,
    )
    assert "messages" in result
    assert (
        result["messages"][0]["msg"]
        == f"Reference sample '{reference_group}' not found in provided data."
    )


def test_flexiquant_not_enough_valid_peptides(peptide_df_few_peptides, metadata_df):
    reference_group = "AD"
    protein_group = "P10636"
    grouping_column = "Group"

    result = flexiquant_lf(
        peptide_df_few_peptides,
        metadata_df,
        reference_group,
        protein_group,
        grouping_column,
        num_init=30,
        mod_cutoff=0.5,
    )
    assert "plots" in result and len(result["plots"]) == 0
    assert "messages" in result
    assert result["messages"][0]["msg"] == (
        "No samples were processed. This is probably due to the fact that there "
        "are not enough valid peptides in the samples."
    )


def test_flexiquant_one_sample_with_not_enough_valid_peptides(
    peptide_df_one_sample_with_few_peptides, metadata_df
):
    reference_group = "AD"
    protein_group = "P10636"
    grouping_column = "Group"
    num_samples = peptide_df_one_sample_with_few_peptides["Sample"].nunique()
    num_proper_samples = num_samples - 1

    result = flexiquant_lf(
        peptide_df_one_sample_with_few_peptides,
        metadata_df,
        reference_group,
        protein_group,
        grouping_column,
        num_init=30,
        mod_cutoff=0.5,
    )
    assert "plots" in result and len(result["plots"]) == num_proper_samples
    assert "messages" in result
    removed_peptides = result["removed_peptides"]
    assert result["messages"][0]["msg"] == (
        f"{num_proper_samples}/{num_samples} samples have been processed "
        f"successfully. The remaining samples have been skipped due to "
        f"insufficient valid peptides. {len(removed_peptides)} peptides have been "
        f"removed."
    )


def check_multiflex_plots_valid(result: dict, n_samples):
    assert "plots" in result and len(result["plots"]) == 3
    plots = result["plots"]
    rm_score_hist_data = plots[0].data

    # one hist and one scatter for each sample
    assert len(rm_score_hist_data) == 2 * n_samples
    rm_score_plot_types = set(trace.type for trace in rm_score_hist_data)
    assert "histogram" in rm_score_plot_types and "scatter" in rm_score_plot_types

    clustergram_data = plots[1].data
    assert "heatmap" in set(trace.type for trace in clustergram_data)

    heatmap_data = plots[2].data
    assert len(heatmap_data) == 1 and "heatmap" in set(
        trace.type for trace in heatmap_data
    )


@pytest.mark.parametrize(
    "deseq2_normalization,reference_group,grouping_column,colormap,imputation_cosine_similarity",
    [
        (True, "AD", "Group", "Red-Blue", 0.0),
        (False, "AD", "Group", "Pink-Green", 1.0),
        (True, "CTR", "Group", "Purple-Green", 0.98),
        (False, "CTR", "Group", "Orange-Purple", 0.5),
        (True, "C1", "Batch", "Red-Grey", 0.5),
        (False, "C1", "Batch", "Red-Yellow-Green", 0.5),
        (False, "AD", "Group", "Red-Yellow-Blue", 0.5),
        (False, "AD", "Group", "Coloooooooooooor", 0.5),
    ],
)
def test_multiflex(
    peptide_df,
    metadata_df,
    deseq2_normalization,
    reference_group,
    grouping_column,
    colormap,
    imputation_cosine_similarity,
):
    n_samples = metadata_df["Sample"].nunique()

    result = multiflex_lf(
        peptide_df=peptide_df,
        metadata_df=metadata_df,
        reference_group=reference_group,
        grouping_column=grouping_column,
        num_init=30,
        mod_cutoff=0.5,
        imputation_cosine_similarity=imputation_cosine_similarity,
        deseq2_normalization=deseq2_normalization,
        colormap=colormap,
    )
    assert (
        "messages" in result
        and "skipped_proteins" in result
        and len(result["messages"]) == 0
        and len(result["skipped_proteins"]) == 0
    )
    check_multiflex_plots_valid(result, n_samples)


def test_multiflex_grouping_column_not_in_df(peptide_df, metadata_df):
    reference_group = "AD"
    grouping_column = "NonExistentGroup"

    result = multiflex_lf(
        peptide_df=peptide_df,
        metadata_df=metadata_df,
        reference_group=reference_group,
        grouping_column=grouping_column,
        num_init=30,
        mod_cutoff=0.5,
        imputation_cosine_similarity=0.98,
        deseq2_normalization=True,
        colormap="Red-Blue",
    )
    assert "messages" in result
    assert (
        result["messages"][0]["msg"]
        == f"Grouping column {grouping_column} not found in metadata."
    )


def test_multiflex_reference_group_not_in_df(peptide_df, metadata_df):
    reference_group = "AAAAADDDDDD"
    grouping_column = "Group"

    result = multiflex_lf(
        peptide_df=peptide_df,
        metadata_df=metadata_df,
        reference_group=reference_group,
        grouping_column=grouping_column,
        num_init=30,
        mod_cutoff=0.5,
        imputation_cosine_similarity=0.98,
        deseq2_normalization=True,
        colormap="Red-Blue",
    )
    assert "messages" in result and len(result["messages"]) == 1
    assert (
        result["messages"][0]["msg"]
        == f"Reference group {reference_group} not found in metadata."
    )


def test_multiflex_not_enough_valid_peptides(peptide_df_few_peptides, metadata_df):
    reference_group = "AD"
    grouping_column = "Group"

    result = multiflex_lf(
        peptide_df=peptide_df_few_peptides,
        metadata_df=metadata_df,
        reference_group=reference_group,
        grouping_column=grouping_column,
        num_init=30,
        mod_cutoff=0.5,
        imputation_cosine_similarity=0.98,
        deseq2_normalization=True,
        colormap="Red-Blue",
    )
    assert "messages" in result and len(result["messages"]) == 1
    assert result["messages"][0]["msg"] == (
        "RM scores were not computed! Intensities of at least 5 peptides per "
        "protein have to be given!"
    )


def test_multiflex_only_one_group(peptide_df_AD_only, metadata_df):
    reference_group = "AD"
    grouping_column = "Group"

    result = multiflex_lf(
        peptide_df=peptide_df_AD_only,
        metadata_df=metadata_df,
        reference_group=reference_group,
        grouping_column=grouping_column,
        num_init=30,
        mod_cutoff=0.5,
        imputation_cosine_similarity=0.98,
        deseq2_normalization=True,
        colormap="Red-Blue",
    )

    assert "messages" in result
    assert (
        result["messages"][0]["msg"]
        == "At least two groups are required for multiFLEX-LF analysis."
    )


def test_multiflex_no_peptides_in_two_conditions(peptide_df, metadata_df):
    reference_group = "AD"
    grouping_column = "Group"

    # Remove peptides in a way that half of the peptides are only in AD samples and the other half only in CTR samples
    all_peptides = peptide_df["Sequence"].unique()
    ad_peptides = all_peptides[: len(all_peptides) // 2]
    peptide_df_modified = peptide_df[
        (
            peptide_df["Sample"].str.contains("AD")
            & peptide_df["Sequence"].isin(ad_peptides)
        )
        | (
            ~peptide_df["Sample"].str.contains("AD")
            & ~peptide_df["Sequence"].isin(ad_peptides)
        )
    ]

    result = multiflex_lf(
        peptide_df=peptide_df_modified,
        metadata_df=metadata_df,
        reference_group=reference_group,
        grouping_column=grouping_column,
        num_init=30,
        mod_cutoff=0.5,
        imputation_cosine_similarity=0.98,
        deseq2_normalization=True,
        colormap="Red-Blue",
    )
    assert "messages" in result and "plots" not in result
    assert result["messages"][0]["msg"] == (
        "No peptides with RM scores in at least two groups available for " "clustering!"
    )


def test_multiflex_flexiquant_errors(peptide_df_AD_CTR, metadata_df):
    n_samples = metadata_df["Sample"].nunique()
    reference_group = "CTR"
    grouping_column = "Group"
    # get all proteins that are always nan in the CTR group
    proteins_not_in_control = (
        peptide_df_AD_CTR[peptide_df_AD_CTR["Sample"].str.contains("CTR")]
        .groupby("Protein ID")
        .filter(lambda x: x["Intensity"].isna().all())["Protein ID"]
        .unique()
    )
    n_proteins_not_in_control = len(proteins_not_in_control)

    result = multiflex_lf(
        peptide_df=peptide_df_AD_CTR,
        metadata_df=metadata_df,
        reference_group=reference_group,
        grouping_column=grouping_column,
        num_init=30,
        mod_cutoff=0.5,
        imputation_cosine_similarity=0.98,
        deseq2_normalization=False,
        colormap="Red-Blue",
    )
    assert (
        "messages" in result
        and len(result["messages"]) == n_proteins_not_in_control
        and all(
            [
                p[i] in result["messages"][i]
                for i, p in enumerate(proteins_not_in_control)
            ]
        )
    )
    assert (
        "skipped_proteins" in result
        and len(result["messages"]) == n_proteins_not_in_control
        and set(result["skipped_proteins"]) == set(proteins_not_in_control)
    )
    check_multiflex_plots_valid(result, n_samples)
