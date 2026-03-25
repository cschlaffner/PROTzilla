import pytest
import pandas as pd

from backend.protzilla.data_preprocessing.simplification import (
    group_replicates,
    metadata_filter_by_samples,
)


@pytest.fixture
def metadata_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Sample": ["MS01", "MS02", "MS03", "MS04"],
            "Sample ID": ["A", "A", "B", "B"],
            "Repliacte no": ["1", "2", "1", "2"],
        }
    )


@pytest.fixture
def protein_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Sample": ["MS01", "MS02", "MS03", "MS04"],
            "Protein ID": ["SDK1"] * 4,
            "Intensity": [5, 15, 1, 2],
        }
    )


@pytest.fixture
def metadata_df_with_spills() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Sample": ["MS01", "MS02", "MS03", "MS04", "MS05"],
            "Sample ID": ["A", "A", "B", "B", "C"],
            "Repliacte no": ["1", "2", "1", "2", "1"],
        }
    )


def test_group_replicates(metadata_df: pd.DataFrame, protein_df: pd.DataFrame):
    result: pd.DataFrame = group_replicates(
        metadata_df, protein_df, "Sample ID", "mean"
    )["protein_df"]

    assert set(result.columns) == {"Sample", "Protein ID", "Intensity"}
    assert set(result["Sample"].unique()) == {"A", "B"}
    entry_a = result[(result["Sample"] == "A") & (result["Protein ID"] == "SDK1")]
    entry_b = result[(result["Sample"] == "B") & (result["Protein ID"] == "SDK1")]
    assert len(entry_a) == len(entry_b) == 1
    assert entry_a["Intensity"].eq(10).all()
    assert entry_b["Intensity"].eq(1.5).all()


def test_filter_metadata(
    metadata_df: pd.DataFrame,
    metadata_df_with_spills: pd.DataFrame,
    protein_df: pd.DataFrame,
):

    result: pd.DataFrame = metadata_filter_by_samples(
        metadata_df_with_spills, protein_df, "Sample"
    )["metadata_df"]

    assert result.equals(metadata_df)
