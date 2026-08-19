import pandas as pd
import numpy as np
import pytest
from backend.protzilla.utilities.transform_dfs import long_to_wide
from backend.protzilla.constants.option_types import NumSVMethods
from backend.protzilla.data_preprocessing.batch_effect_correction import (
    long_to_pycombat_df,
    pycombat_df_to_long,
    get_covar_mod,
    turn_group_names_to_int,
    create_sv_dataframe,
    turn_covar_df_into_design_matrix,
    filter_samples_based_on_col,
    combat_correction,
    sva_correction,
    loess_correction,
)


@pytest.fixture
def long_protein_df() -> pd.DataFrame:
    wide_protein_df = pd.DataFrame(
        data=(
            ["Sample_01", "Gene_1", 0.0, 0.0, 0.0, 0.0],
            ["Sample_02", "Gene_2", 1.0, 2.0, 3.0, 4.0],
            ["Sample_03", "Gene_2", 1.0, 0.0, 1.0, 0.0],
            ["Sample_04", "Gene_2", 1.0, 2.0, 2.0, 2.0],
        ),
        columns=[
            "Sample",
            "Gene",
            "Protein_1",
            "Protein_2",
            "Protein_3",
            "Protein_4",
        ],
    )
    long_protein_df = pd.melt(
        wide_protein_df,
        id_vars=["Sample", "Gene"],
        var_name="Protein ID",
        value_name="Intensity",
    )
    long_protein_df = long_protein_df[["Sample", "Protein ID", "Gene", "Intensity"]]
    long_protein_df = long_protein_df.sort_values(
        by=["Sample", "Protein ID"], ignore_index=True
    )
    return long_protein_df


@pytest.fixture
def wide_protein_df() -> pd.DataFrame:
    wide_protein_df = pd.DataFrame(
        data=(
            ["Sample_01", "Gene_1", 0.0, 0.0, 0.0, 0.0],
            ["Sample_02", "Gene_2", 1.0, 2.0, 3.0, 4.0],
            ["Sample_03", "Gene_2", 1.0, 0.0, 1.0, 0.0],
            ["Sample_04", "Gene_2", 1.0, 2.0, 2.0, 2.0],
        ),
        columns=[
            "Sample",
            "Gene",
            "Protein_1",
            "Protein_2",
            "Protein_3",
            "Protein_4",
        ],
    )
    long_protein_df = pd.melt(
        wide_protein_df,
        id_vars=["Sample", "Gene"],
        var_name="Protein ID",
        value_name="Intensity",
    )
    long_protein_df = long_protein_df[["Sample", "Protein ID", "Gene", "Intensity"]]
    long_protein_df = long_protein_df.sort_values(
        by=["Sample", "Protein ID"], ignore_index=True
    )
    return long_to_wide(long_protein_df)


@pytest.fixture
def pycombat_protein_df() -> pd.DataFrame:
    pycombat_protein_df = pd.DataFrame(
        data=(
            ["Protein_1", 0.0, 1.0, 1.0, 1.0],
            ["Protein_2", 0.0, 2.0, 0.0, 2.0],
            ["Protein_3", 0.0, 3.0, 1.0, 2.0],
            ["Protein_4", 0.0, 4.0, 0.0, 2.0],
        ),
        columns=["Protein ID", "Sample_01", "Sample_02", "Sample_03", "Sample_04"],
    )
    pycombat_protein_df.columns.name = "Sample"
    pycombat_protein_df = pycombat_protein_df.set_index("Protein ID")
    return pycombat_protein_df


@pytest.fixture
def metadata_df() -> pd.DataFrame:
    metadata_df = pd.DataFrame(
        data=(
            ["Sample_01", "AD", "Female", "A", 1.0],
            ["Sample_02", "CTR", "Male", "A", 2.0],
            ["Sample_03", "AD", "Male", "B", 3.0],
            ["Sample_04", "CTR", "Female", "B", 4.0],
        ),
        columns=["Sample", "Group", "Sex", "Batch", "Run_order"],
    )
    return metadata_df


@pytest.fixture
def sv_df() -> pd.DataFrame:
    sv_df = pd.DataFrame(
        data=(
            ["Sample_01", 1.0, 5.0, 9.0],
            ["Sample_02", 2.0, 6.0, 10.0],
            ["Sample_03", 3.0, 7.0, 11.0],
            ["Sample_04", 4.0, 8.0, 12.0],
        ),
        columns=[
            "Sample",
            "SV1",
            "SV2",
            "SV3",
        ],
    )
    return sv_df


@pytest.fixture
def covar_df() -> pd.DataFrame:
    covar_df = pd.DataFrame(
        data=(
            ["Sample_01", "Female"],
            ["Sample_02", "Male"],
            ["Sample_03", "Male"],
            ["Sample_04", "Female"],
        ),
        columns=["Sample", "Sex"],
    )
    covar_df = covar_df.set_index("Sample")
    return covar_df


@pytest.fixture
def large_long_protein_df_loess() -> pd.DataFrame:
    wide_protein_df = pd.DataFrame(
        data=(
            ["Sample_01", "Gene_1", 0.0, 0.0, 0.0, 0.0],
            ["Sample_02", "Gene_2", 1.0, 2.0, 3.0, 4.0],
            ["Sample_03", "Gene_2", 1.0, 0.0, 1.0, 0.0],
            ["Sample_04", "Gene_2", 1.0, 2.0, 2.0, 2.0],
            ["Sample_05", "Gene_1", 0.0, 0.0, 0.0, 0.0],
            ["Sample_06", "Gene_2", 1.0, 2.0, 3.0, 4.0],
            ["Sample_07", "Gene_2", 1.0, 0.0, 1.0, 0.0],
            ["Sample_08", "Gene_2", 1.0, 2.0, 2.0, 2.0],
            ["Sample_09", "Gene_1", 0.0, 0.0, 0.0, 0.0],
            ["Sample_10", "Gene_2", 1.0, 2.0, 3.0, 4.0],
            ["Sample_11", "Gene_2", 1.0, 0.0, 1.0, 0.0],
            ["Sample_12", "Gene_2", 1.0, 2.0, 2.0, 2.0],
            ["Sample_13", "Gene_1", 0.0, 0.0, 0.0, 0.0],
            ["Sample_14", "Gene_2", 1.0, 2.0, 3.0, 4.0],
            ["Sample_15", "Gene_2", 1.0, 0.0, 1.0, 0.0],
            ["Sample_16", "Gene_2", 1.0, 2.0, 2.0, 2.0],
        ),
        columns=[
            "Sample",
            "Gene",
            "Protein_1",
            "Protein_2",
            "Protein_3",
            "Protein_4",
        ],
    )
    long_protein_df = pd.melt(
        wide_protein_df,
        id_vars=["Sample", "Gene"],
        var_name="Protein ID",
        value_name="Intensity",
    )
    long_protein_df = long_protein_df[["Sample", "Protein ID", "Gene", "Intensity"]]
    long_protein_df = long_protein_df.sort_values(
        by=["Sample", "Protein ID"], ignore_index=True
    )
    return long_protein_df


@pytest.fixture
def large_wide_protein_df() -> pd.DataFrame:
    wide_protein_df = pd.DataFrame(
        data=(
            ["Sample_01", "Gene_1", 0.0, 0.0, 0.0, 0.0],
            ["Sample_02", "Gene_2", 1.0, 2.0, 3.0, 4.0],
            ["Sample_03", "Gene_2", 1.0, 0.0, 1.0, 0.0],
            ["Sample_04", "Gene_2", 1.0, 2.0, 2.0, 2.0],
            ["Sample_05", "Gene_1", 0.0, 0.0, 0.0, 0.0],
            ["Sample_06", "Gene_2", 1.0, 2.0, 3.0, 4.0],
            ["Sample_07", "Gene_2", 1.0, 0.0, 1.0, 0.0],
            ["Sample_08", "Gene_2", 1.0, 2.0, 2.0, 2.0],
            ["Sample_09", "Gene_1", 0.0, 0.0, 0.0, 0.0],
            ["Sample_10", "Gene_2", 1.0, 2.0, 3.0, 4.0],
            ["Sample_11", "Gene_2", 1.0, 0.0, 1.0, 0.0],
            ["Sample_12", "Gene_2", 1.0, 2.0, 2.0, 2.0],
            ["Sample_13", "Gene_1", 0.0, 0.0, 0.0, 0.0],
            ["Sample_14", "Gene_2", 1.0, 2.0, 3.0, 4.0],
            ["Sample_15", "Gene_2", 1.0, 0.0, 1.0, 0.0],
            ["Sample_16", "Gene_2", 1.0, 2.0, 2.0, 2.0],
        ),
        columns=[
            "Sample",
            "Gene",
            "Protein_1",
            "Protein_2",
            "Protein_3",
            "Protein_4",
        ],
    )
    long_protein_df = pd.melt(
        wide_protein_df,
        id_vars=["Sample", "Gene"],
        var_name="Protein ID",
        value_name="Intensity",
    )
    long_protein_df = long_protein_df[["Sample", "Protein ID", "Gene", "Intensity"]]
    long_protein_df = long_protein_df.sort_values(
        by=["Sample", "Protein ID"], ignore_index=True
    )
    return long_to_wide(long_protein_df)


@pytest.fixture
def large_long_protein_df_sva() -> pd.DataFrame:
    np.random.seed(42)
    n_samples = 16
    n_proteins = 100

    sample_names = [f"Sample_{i:02d}" for i in range(1, n_samples + 1)]
    protein_names = [f"Protein_{i:02d}" for i in range(1, n_proteins + 1)]
    intensitiy_values = np.random.normal(
        loc=5.0, scale=2.0, size=(n_samples, n_proteins)
    )
    wide_protein_df = pd.DataFrame(
        intensitiy_values, index=sample_names, columns=protein_names
    )
    wide_protein_df.reset_index(names="Sample", inplace=True)
    wide_protein_df["Gene"] = "Gene_1"
    long_protein_df = pd.melt(
        wide_protein_df,
        id_vars=["Sample", "Gene"],
        var_name="Protein ID",
        value_name="Intensity",
    )
    long_protein_df = long_protein_df[["Sample", "Protein ID", "Gene", "Intensity"]]
    long_protein_df = long_protein_df.sort_values(
        by=["Sample", "Protein ID"], ignore_index=True
    )

    return long_protein_df


@pytest.fixture
def large_long_protein_df_combat() -> pd.DataFrame:
    wide_protein_df = pd.DataFrame(
        data=(
            ["Sample_01", "Gene_1", 0.9, 0.8, 0.6, 0.4],
            ["Sample_02", "Gene_2", 9.1, 2.0, 3.9, 4.0],
            ["Sample_03", "Gene_2", 1.0, 5.1, 1.0, 0.0],
            ["Sample_04", "Gene_2", 1.0, 2.0, 23.5, 2.0],
            ["Sample_05", "Gene_1", 0.1, 0.3, 0.4, 0.3],
            ["Sample_06", "Gene_2", 1.0, 2.0, 3.0, 4.0],
            ["Sample_07", "Gene_2", 1.7, 0.0, 1.0, 0.0],
            ["Sample_08", "Gene_2", 1.0, 3.2, 2.0, 2.0],
            ["Sample_09", "Gene_1", 0.0, 5.0, 0.8, 0.0],
            ["Sample_10", "Gene_2", 1.0, 2.0, 3.0, 4.0],
            ["Sample_11", "Gene_2", 1.0, 0.1, 6.0, 0.0],
            ["Sample_12", "Gene_2", 1.0, 6.0, 2.0, 2.0],
            ["Sample_13", "Gene_1", 0.45, 0.44, 3.0, 6.7],
            ["Sample_14", "Gene_2", 1.7, 2.2, 3.0, 4.0],
            ["Sample_15", "Gene_2", 1.7, 0.0, 5.1, 0.0],
            ["Sample_16", "Gene_2", 1.0, 2.8, 2.0, 2.0],
        ),
        columns=[
            "Sample",
            "Gene",
            "Protein_1",
            "Protein_2",
            "Protein_3",
            "Protein_4",
        ],
    )
    long_protein_df = pd.melt(
        wide_protein_df,
        id_vars=["Sample", "Gene"],
        var_name="Protein ID",
        value_name="Intensity",
    )
    long_protein_df = long_protein_df[["Sample", "Protein ID", "Gene", "Intensity"]]
    long_protein_df = long_protein_df.sort_values(
        by=["Sample", "Protein ID"], ignore_index=True
    )
    return long_protein_df


@pytest.fixture
def large_metadata_df() -> pd.DataFrame:
    metadata_df = pd.DataFrame(
        data=(
            ["Sample_01", "AD", "Female", "A", 1],
            ["Sample_02", "CTR", "Male", "A", 2],
            ["Sample_03", "AD", "Male", "B", 3],
            ["Sample_04", "CTR", "Female", "B", 4],
            ["Sample_05", "AD", "Female", "A", 5],
            ["Sample_06", "CTR", "Female", "A", 6],
            ["Sample_07", "AD", "Female", "B", 7],
            ["Sample_08", "CTR", "Male", "A", 8],
            ["Sample_09", "CTR", "Female", "B", 9],
            ["Sample_10", "AD", "Female", "B", 10],
            ["Sample_11", "AD", "Male", "B", 11],
            ["Sample_12", "CTR", "Female", "A", 12],
            ["Sample_13", "CTR", "Male", "B", 13],
            ["Sample_14", "CTR", "Male", "B", 14],
            ["Sample_15", "AD", "Female", "A", 15],
            ["Sample_16", "CTR", "Male", "A", 16],
        ),
        columns=["Sample", "Group", "Sex", "Batch", "Run_order"],
    )
    return metadata_df


@pytest.fixture
def large_long_protein_df_combat_corrected() -> pd.DataFrame:
    wide_protein_df = pd.DataFrame(
        data=(
            ["Sample_01", "Gene_1", 0.838383, 0.831484, 0.968833, 0.621030],
            ["Sample_02", "Gene_2", 7.906568, 1.956583, 5.869886, 4.623270],
            ["Sample_03", "Gene_2", 1.035978, 4.453557, 0.296224, 0.077550],
            ["Sample_04", "Gene_2", 1.137394, 2.036279, 19.616660, 2.002045],
            ["Sample_05", "Gene_1", 0.174952, 0.209892, 0.642766, 0.470750],
            ["Sample_06", "Gene_2", 0.963757, 1.895655, 2.630768, 4.931806],
            ["Sample_07", "Gene_2", 1.927078, 0.068544, 0.850719, -0.030888],
            ["Sample_08", "Gene_2", 1.189328, 3.448403, 2.772248, 1.617671],
            ["Sample_09", "Gene_1", 0.042854, 4.635392, 1.394590, 0.355475],
            ["Sample_10", "Gene_2", 1.160900, 1.801287, 2.456188, 3.262252],
            ["Sample_11", "Gene_2", 1.035978, 0.121701, 4.309895, 0.077550],
            ["Sample_12", "Gene_2", 0.963757, 6.868388, 1.000432, 1.926207],
            ["Sample_13", "Gene_1", 0.410475, 0.651260, 2.606110, 5.979923],
            ["Sample_14", "Gene_2", 1.778650, 2.176073, 2.606110, 3.757054],
            ["Sample_15", "Gene_2", 1.501814, -0.163063, 8.305344, 0.019910],
            ["Sample_16", "Gene_2", 1.189328, 2.951130, 2.772248, 1.617671],
        ),
        columns=[
            "Sample",
            "Gene",
            "Protein_1",
            "Protein_2",
            "Protein_3",
            "Protein_4",
        ],
    )
    long_protein_df = pd.melt(
        wide_protein_df,
        id_vars=["Sample", "Gene"],
        var_name="Protein ID",
        value_name="Intensity",
    )
    long_protein_df = long_protein_df[["Sample", "Protein ID", "Gene", "Intensity"]]
    long_protein_df = long_protein_df.sort_values(
        by=["Sample", "Protein ID"], ignore_index=True
    )
    return long_protein_df


@pytest.fixture
def large_long_protein_loess_corrected_df() -> pd.DataFrame:
    wide_protein_df = pd.DataFrame(
        data=(
            ["Sample_01", "Gene_1", 0.0, 0.0, -0.60, -1.2],
            ["Sample_02", "Gene_2", 1.0, 2.0, 2.40, 2.8],
            ["Sample_03", "Gene_2", 0.5, -1.0, 0.25, -0.5],
            ["Sample_04", "Gene_2", 0.5, 1.0, 1.25, 1.5],
            ["Sample_05", "Gene_1", 0.0, 0.0, -0.60, -1.2],
            ["Sample_06", "Gene_2", 1.0, 2.0, 2.40, 2.8],
            ["Sample_07", "Gene_2", 1.1, 0.2, 1.45, 0.7],
            ["Sample_08", "Gene_2", 1.0, 2.0, 2.40, 2.8],
            ["Sample_09", "Gene_1", 0.5, 1.0, 1.25, 1.5],
            ["Sample_10", "Gene_2", 1.5, 3.0, 4.25, 5.5],
            ["Sample_11", "Gene_2", 1.5, 1.0, 2.25, 1.5],
            ["Sample_12", "Gene_2", 1.0, 2.0, 2.40, 2.8],
            ["Sample_13", "Gene_1", 0.5, 1.0, 1.25, 1.5],
            ["Sample_14", "Gene_2", 0.5, 1.0, 1.25, 1.5],
            ["Sample_15", "Gene_2", 1.0, 0.0, 1.40, 0.8],
            ["Sample_16", "Gene_2", 1.0, 2.0, 2.40, 2.8],
        ),
        columns=[
            "Sample",
            "Gene",
            "Protein_1",
            "Protein_2",
            "Protein_3",
            "Protein_4",
        ],
    )
    long_protein_df = pd.melt(
        wide_protein_df,
        id_vars=["Sample", "Gene"],
        var_name="Protein ID",
        value_name="Intensity",
    )
    long_protein_df = long_protein_df[["Sample", "Protein ID", "Gene", "Intensity"]]
    long_protein_df = long_protein_df.sort_values(
        by=["Sample", "Protein ID"], ignore_index=True
    )
    return long_protein_df


@pytest.fixture
def long_sv_df() -> pd.DataFrame:
    long_sv_df = pd.DataFrame(
        data=(
            ["Sample_01", -0.719013],
            ["Sample_02", 0.313557],
            ["Sample_03", -0.145547],
            ["Sample_04", 0.024164],
            ["Sample_05", 0.270691],
            ["Sample_06", -0.027139],
            ["Sample_07", -0.035415],
            ["Sample_08", 0.157528],
            ["Sample_09", 0.061592],
            ["Sample_10", 0.139442],
            ["Sample_11", -0.069927],
            ["Sample_12", -0.118101],
            ["Sample_13", 0.039981],
            ["Sample_14", 0.125860],
            ["Sample_15", 0.309897],
            ["Sample_16", -0.327572],
        ),
        columns=[
            "Sample",
            "SV1",
        ],
    )
    return long_sv_df


def test_long_to_pycombat(long_protein_df: pd.DataFrame, pycombat_protein_df):
    df = long_to_pycombat_df(long_protein_df)
    pd.testing.assert_frame_equal(df, pycombat_protein_df)


def test_pycombat_to_long(
    pycombat_protein_df: pd.DataFrame, long_protein_df: pd.DataFrame
):
    df = pycombat_df_to_long(
        pycombat_df=pycombat_protein_df, original_protein_df=long_protein_df
    )
    pd.testing.assert_frame_equal(df, long_protein_df)


def test_get_covar_mod_none(metadata_df: pd.DataFrame):
    assert (
        get_covar_mod(
            samples=["Sample_01", "Sample_02", "Sample_03", "Sample_04"],
            metadata_df=metadata_df,
            covar_columns=[],
        )
        is None
    )


def test_get_covar_mod(metadata_df: pd.DataFrame, covar_df: pd.DataFrame):
    test_df = get_covar_mod(
        samples=["Sample_01", "Sample_02", "Sample_03", "Sample_04"],
        metadata_df=metadata_df,
        covar_columns=["Sex"],
    )
    pd.testing.assert_frame_equal(covar_df, test_df)


def test_turn_group_names_to_int():
    assert [0, 0, 1, 1, 0] == turn_group_names_to_int(
        groups=[
            "CTR",
            "CTR",
            "AD",
            "AD",
            "CTR",
        ]
    )


def test_create_sv_dataframe(sv_df: pd.DataFrame):
    samples = ["Sample_01", "Sample_02", "Sample_03", "Sample_04"]
    test_df = create_sv_dataframe(
        sv_columns=[
            [1.0, 2.0, 3.0, 4.0],
            [5.0, 6.0, 7.0, 8.0],
            [9.0, 10.0, 11.0, 12.0],
        ],
        samples_in_order=samples,
    )
    pd.testing.assert_frame_equal(sv_df, test_df)


def test_turn_covar_df_into_design_matrix(
    wide_protein_df: pd.DataFrame, covar_df: pd.DataFrame
):
    test_dm = turn_covar_df_into_design_matrix(wide_protein_df, covar_df)
    assert test_dm.shape[0] == 4
    assert test_dm.shape[1] == 2
    assert "Intercept" in test_dm.design_info.column_names


def test_turn_covar_df_into_design_matrix_no_covariates(
    wide_protein_df: pd.DataFrame,
):
    test_dm = turn_covar_df_into_design_matrix(wide_protein_df, None)
    assert test_dm.shape[0] == 4
    assert test_dm.shape[1] == 1
    assert "Intercept" in test_dm.design_info.column_names


def test_filter_samples_based_on_col(
    wide_protein_df: pd.DataFrame, metadata_df: pd.DataFrame
):
    test_df = filter_samples_based_on_col(
        wide_protein_df,
        metadata_df,
        column_name="Group",
        filter_names=["CTR"],
    )
    long_df = pd.DataFrame(
        data=(
            ["Sample_02", "Gene_2", 1.0, 2.0, 3.0, 4.0],
            ["Sample_04", "Gene_2", 1.0, 2.0, 2.0, 2.0],
        ),
        columns=[
            "Sample",
            "Gene",
            "Protein_1",
            "Protein_2",
            "Protein_3",
            "Protein_4",
        ],
    )
    long_df = pd.melt(
        long_df,
        id_vars=["Sample", "Gene"],
        var_name="Protein ID",
        value_name="Intensity",
    )
    long_df = long_df[["Protein ID", "Sample", "Gene", "Intensity"]]
    long_df = long_df.sort_values(by=["Sample", "Protein ID"], ignore_index=True)
    df = long_to_wide(long_df)
    pd.testing.assert_frame_equal(df, test_df)


def test_filter_samples_based_on_col_all_columns(
    wide_protein_df: pd.DataFrame, metadata_df: pd.DataFrame
):
    test_df = filter_samples_based_on_col(
        wide_protein_df,
        metadata_df,
        column_name="Group",
        filter_names=["AD", "CTR"],
    )

    pd.testing.assert_frame_equal(wide_protein_df, test_df)


def test_loess_correction_too_little_samples(
    long_protein_df: pd.DataFrame, metadata_df: pd.DataFrame
):
    loess_corrected = loess_correction(
        long_protein_df,
        metadata_df,
        group_column="Group",
        qc_group_names=["CTR"],
        batch_column="Batch",
        order_column="Run_order",
        frac=0.5,
    )

    pd.testing.assert_frame_equal(long_protein_df, loess_corrected["protein_df"])


def test_loess_correction(
    large_long_protein_df_loess: pd.DataFrame,
    large_metadata_df: pd.DataFrame,
    large_long_protein_loess_corrected_df: pd.DataFrame,
):
    loess_corrected = loess_correction(
        large_long_protein_df_loess,
        large_metadata_df,
        group_column="Group",
        qc_group_names=["CTR"],
        batch_column="Batch",
        order_column="Run_order",
        frac=0.5,
    )

    pd.testing.assert_frame_equal(
        large_long_protein_loess_corrected_df, loess_corrected["protein_df"]
    )


def test_sva_correction(
    large_long_protein_df_sva: pd.DataFrame,
    large_metadata_df: pd.DataFrame,
    large_long_protein_loess_corrected_df: pd.DataFrame,
    long_sv_df: pd.DataFrame,
):
    sva_corrected = sva_correction(
        protein_df=large_long_protein_df_sva,
        metadata_df=large_metadata_df,
        num_sv_method=NumSVMethods.be.value,
        group_column="Group",
        seed=42,
        covariates_columns=["Sex"],
    )

    test_protein_df = sva_corrected["protein_df"]
    test_sv_df = sva_corrected["surrogate_variable_df"]
    assert test_protein_df is not None
    assert {"Sample", "Protein ID", "Gene"}.issubset(test_protein_df.columns)

    pd.testing.assert_frame_equal(
        long_sv_df,
        test_sv_df,
        check_exact=False,
        atol=1e-6,
    )


def test_combat_correction(
    large_long_protein_df_combat: pd.DataFrame,
    large_metadata_df: pd.DataFrame,
    large_long_protein_df_combat_corrected: pd.DataFrame,
):
    combat_corrected = combat_correction(
        protein_df=large_long_protein_df_combat,
        metadata_df=large_metadata_df,
        par_prior=True,
        batch_column="Batch",
        covariates_columns=["Group", "Sex"],
    )

    pd.testing.assert_frame_equal(
        large_long_protein_df_combat_corrected,
        combat_corrected["protein_df"],
        check_exact=False,
        atol=1e-6,
    )
