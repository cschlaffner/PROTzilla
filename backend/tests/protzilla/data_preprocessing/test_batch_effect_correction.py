import pandas as pd
from patsy import DesignMatrix, dmatrix
import pytest
from backend.protzilla.data_preprocessing.batch_effect_correction import (
    long_to_pycombat_df,
    pycombat_df_to_long,
    get_covar_mod,
    turn_group_names_to_int,
    create_sv_dataframe,
    turn_covar_df_into_design_matrix,
)


@pytest.fixture
def long_protein_df() -> pd.DataFrame:
    long_protein_df = pd.DataFrame(
        data=(
            ["Sample_1", "Gene_1", 0, 0, 0, 0],
            ["Sample_2", "Gene_2", 1, 2, 3, 4],
            ["Sample_3", "Gene_2", 1, 0, 1, 0],
            ["Sample_4", "Gene_2", 1, 2, 2, 2],
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
        long_protein_df,
        id_vars=["Sample", "Gene"],
        var_name="Protein ID",
        value_name="Intensity",
    )
    long_protein_df = long_protein_df[["Protein ID", "Sample", "Gene", "Intensity"]]
    long_protein_df = long_protein_df.sort_values(
        by=["Sample", "Protein ID"], ignore_index=True
    )
    return long_protein_df


@pytest.fixture
def pycombat_protein_df() -> pd.DataFrame:
    pycombat_protein_df = pd.DataFrame(
        data=(
            ["Protein_1", 0, 1, 1, 1],
            ["Protein_2", 0, 2, 0, 2],
            ["Protein_3", 0, 3, 1, 2],
            ["Protein_4", 0, 4, 0, 2],
        ),
        columns=["Protein ID", "Sample_1", "Sample_2", "Sample_3", "Sample_4"],
    )
    pycombat_protein_df.columns.name = "Sample"
    pycombat_protein_df = pycombat_protein_df.set_index("Protein ID")
    return pycombat_protein_df


@pytest.fixture
def metadata_df() -> pd.DataFrame:
    metadata_df = pd.DataFrame(
        data=(
            ["Sample_1", "AD", "Female", "A"],
            ["Sample_2", "CTR", "Male", "A"],
            ["Sample_3", "AD", "Male", "B"],
            ["Sample_4", "CTR", "Female", "B"],
        ),
        columns=[
            "Sample",
            "Group",
            "Sex",
            "Batch",
        ],
    )
    return metadata_df


@pytest.fixture
def sv_df() -> pd.DataFrame:
    sv_df = pd.DataFrame(
        data=(
            ["Sample_1", 1, 5, 9],
            ["Sample_2", 2, 6, 10],
            ["Sample_3", 3, 7, 11],
            ["Sample_4", 4, 8, 12],
        ),
        columns=[
            "Sample",
            "SV1",
            "SV2",
            "SV3",
        ],
    )
    return sv_df


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
            samples=["Sample_1", "Sample_2", "Sample_3", "Sample_4"],
            metadata_df=metadata_df,
            covar_columns=[],
        )
        is None
    )


def test_get_covar_mod(metadata_df: pd.DataFrame):
    df = pd.DataFrame(
        data=(
            ["Sample_1", "Female"],
            ["Sample_2", "Male"],
            ["Sample_3", "Male"],
            ["Sample_4", "Female"],
        ),
        columns=["Sample", "Sex"],
    )
    df = df.set_index("Sample")
    test_df = get_covar_mod(
        samples=["Sample_1", "Sample_2", "Sample_3", "Sample_4"],
        metadata_df=metadata_df,
        covar_columns=["Sex"],
    )
    pd.testing.assert_frame_equal(df, test_df)


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
    samples = ["Sample_1", "Sample_2", "Sample_3", "Sample_4"]
    test_df = create_sv_dataframe(
        sv_columns=[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]],
        samples_in_order=samples,
    )
    pd.testing.assert_frame_equal(sv_df, test_df)
