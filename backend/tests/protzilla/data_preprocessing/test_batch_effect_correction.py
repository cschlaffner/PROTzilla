import pandas as pd
import pytest
from backend.protzilla.data_preprocessing.batch_effect_correction import (
    long_to_pycombat_df,
    pycombat_df_to_long,
    get_covar_mod,
    turn_group_names_to_int,
)


@pytest.fixture
def long_protein_df() -> pd.DataFrame:
    long_protein_df = pd.DataFrame(
        data=(
            ["Sample_1", "Gene_1", 0, 0, 0, 0],
            ["Sample_2", "Gene_2", 1, 2, 3, 4],
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
            ["Protein_1", 0, 1],
            ["Protein_2", 0, 2],
            ["Protein_3", 0, 3],
            ["Protein_4", 0, 4],
        ),
        columns=[
            "Protein ID",
            "Sample_1",
            "Sample_2",
        ],
    )
    pycombat_protein_df.columns.name = "Sample"
    pycombat_protein_df = pycombat_protein_df.set_index("Protein ID")
    return pycombat_protein_df


@pytest.fixture
def metadata_df() -> pd.DataFrame:
    metadata_df = pd.DataFrame(
        data=(
            ["Sample1", "AD", "Female", "A"],
            ["Sample2", "CTR", "Male", "A"],
            ["Sample3", "AD", "Male", "B"],
            ["Sample4", "CTR", "Female", "B"],
        ),
        columns=[
            "Sample",
            "Group",
            "Sex",
            "Batch",
        ],
    )
    return metadata_df


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
            samples=["Sample1", "Sample2", "Sample3", "Sample4"],
            metadata_df=metadata_df,
            covar_columns=[],
        )
        is None
    )


def test_get_covar_mod(metadata_df: pd.DataFrame):
    df = pd.DataFrame(
        data=(
            ["Sample1", "Female"],
            ["Sample2", "Male"],
            ["Sample3", "Male"],
            ["Sample4", "Female"],
        ),
        columns=["Sample", "Sex"],
    )
    df = df.set_index("Sample")
    test_df = get_covar_mod(
        samples=["Sample1", "Sample2", "Sample3", "Sample4"],
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
