import pandas as pd
from backend.protzilla.data_preprocessing.peptide_filter import by_existing_proteins


def test_by_existing_proteins_filters_correctly():
    peptide_df = pd.DataFrame(
        {
            "Protein ID": ["P1", "P1", "P2", "P3"],
            "Sequence": ["AAA", "BBB", "CCC", "DDD"],
        }
    )

    protein_df = pd.DataFrame({"Protein ID": ["P1", "P3"]})

    filtered_peptides_df = by_existing_proteins(peptide_df, protein_df)["peptide_df"]

    expected_df = pd.DataFrame(
        {"Protein ID": ["P1", "P1", "P3"], "Sequence": ["AAA", "BBB", "DDD"]}
    )

    pd.testing.assert_frame_equal(
        filtered_peptides_df.reset_index(drop=True), expected_df.reset_index(drop=True)
    )
