import pytest
import pandas as pd

from backend.protzilla.constants.data_types import DataKey
from backend.protzilla.importing.fasta_import import fasta_generation, parse_fasta_id, fasta_import
from backend.tests.paths import TEST_FASTA_PATH


def test_parse_fasta_id():
    protein_id = "P14136-1"
    valid_fasta_id = (
        f">sp|{protein_id}|GFAP_HUMAN Isoform 1 of Glial fibrillary acidic protein OS=Homo sapiens "
        "OX=9606 GN=GFAP; "
    )
    metadata = parse_fasta_id(valid_fasta_id)
    assert metadata == protein_id

    invalid_fasta_id = ">sp"
    with pytest.raises(
        ValueError,
        match="Fasta file metadata is invalid. It has to include a protein id",
    ):
        parse_fasta_id(invalid_fasta_id)


@pytest.mark.parametrize(
    "fasta_file,protein_id",
    [
        (TEST_FASTA_PATH / "uniprotkb_P14136.fasta", ["P14136-1", "P14136-3"]),
        (
            TEST_FASTA_PATH / "uniprotkb_P10636.fasta",
            ["P10636-1", "P10636-6"],
        ),
        (TEST_FASTA_PATH / "malformed.fasta", ["P14136-1", "P14136-3"]),
    ],
)
def test_fasta_import(fasta_file, protein_id):
    output = fasta_import(fasta_file)
    assert DataKey.FASTA_DF in output
    assert set(output[DataKey.FASTA_DF]["Protein ID"]) == set(protein_id)


def test_import_of_malformed_fasta():
    malformed_fasta_file = TEST_FASTA_PATH / "even_more_malformed.fasta"
    with pytest.raises(
        ValueError,
        match="Fasta file metadata is invalid. It has to include a protein id",
    ):
        fasta_import(malformed_fasta_file)


def test_import_empty_fasta():
    empty_fasta_file = TEST_FASTA_PATH / "empty.fasta"
    with pytest.raises(ValueError, match="The provided fasta file is empty."):
        fasta_import(empty_fasta_file)


def test_import_fasta_with_no_sequences():
    no_sequences_fasta_file = TEST_FASTA_PATH / "no_sequences.fasta"
    with pytest.raises(
        ValueError,
        match="The provided fasta file does not contain protein sequences for all of the protein ids.",
    ):
        fasta_import(no_sequences_fasta_file)


def test_most_simple_fasta_generation():
    protein_df = pd.DataFrame({"Protein ID": ["P01308"]})
    output = fasta_generation(protein_df)
    generated_fasta_df: pd.DataFrame = output["fasta_df"]
    assert(len(generated_fasta_df) == 1)
    assert(list(generated_fasta_df.columns) == ["Protein ID", "Protein Sequence"])
    assert(generated_fasta_df["Protein ID"].iloc[0] == "P01308-1")
    assert(generated_fasta_df["Protein Sequence"].iloc[0] == "MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKTRREAEDLQVGQVELGGGPGAGSLQPLALEGSLQKRGIVEQCCTSICSLYQLENYCN")
