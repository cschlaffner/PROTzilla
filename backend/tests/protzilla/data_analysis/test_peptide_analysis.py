
from backend.protzilla.constants.data_types import DataKey
from backend.protzilla.data_analysis.ptm_analysis import (
    ptms_per_sample,
    ptms_per_protein_and_sample,
)


def test_ptms_per_sample(psm_df):
    ptm_df = ptms_per_sample(psm_df)["ptm_df"]

    assert ptm_df.columns.tolist() == [
        "Sample",
        "Acetyl (Protein N-term)",
        "Oxidation (M)",
        "Unmodified",
        "Total Amount of Peptides",
    ]
    assert ptm_df["Sample"].tolist() == ["Sample1", "Sample2", "Sample3", "Sample4"]
    assert ptm_df["Unmodified"].tolist() == [8, 4, 5, 4]
    assert ptm_df["Acetyl (Protein N-term)"].tolist() == [2, 1, 0, 0]
    assert ptm_df["Oxidation (M)"].tolist() == [1, 0, 0, 0]
    assert ptm_df["Total Amount of Peptides"].tolist() == [10, 5, 5, 4]


def test_ptms_per_protein_and_sample(psm_df):
    ptm_df = ptms_per_protein_and_sample(psm_df)[DataKey.PTM_DF]

    assert ptm_df.columns.tolist() == [
        "Sample",
        "Protein1",
        "Protein2",
        "Protein3",
        "Protein4",
        "Protein5",
    ]
    assert ptm_df["Sample"].tolist() == ["Sample1", "Sample2", "Sample3", "Sample4"]
    assert ptm_df["Protein1"].tolist() == [
        "(1) Unmodified, ",
        "(1) Acetyl (Protein N-term), ",
        "(1) Unmodified, ",
        "(1) Unmodified, ",
    ]
    assert ptm_df["Protein2"].tolist() == [
        "(2) Acetyl (Protein N-term), (1) Oxidation (M), (1) Unmodified, ",
        "(1) Unmodified, ",
        "(1) Unmodified, ",
        "(1) Unmodified, ",
    ]
    assert ptm_df["Protein3"].tolist() == [
        "(4) Unmodified, ",
        "(1) Unmodified, ",
        "(1) Unmodified, ",
        "(1) Unmodified, ",
    ]
    assert ptm_df["Protein4"].tolist() == [
        "(1) Unmodified, ",
        "(1) Unmodified, ",
        "(1) Unmodified, ",
        "(1) Unmodified, ",
    ]
    assert ptm_df["Protein5"].tolist() == [
        "(1) Unmodified, ",
        "(1) Unmodified, ",
        "(1) Unmodified, ",
        "",
    ]
