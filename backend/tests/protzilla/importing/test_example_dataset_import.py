import logging

from protzilla.importing.example_dataset_import import example_dataset_import


def test_example_dataset_import():
    outputs = example_dataset_import()

    # TODO[later]: could maybe compare lengths of final files to the dataframes
    assert "protein_df" in outputs
    assert "contaminants" in outputs
    assert "filtered_proteins" in outputs
    assert "metadata_df" in outputs
    assert "peptide_df" in outputs
    assert "messages" in outputs
    assert all(message["level"] == logging.INFO for message in outputs["messages"])
    assert all(
        "successfully" in message["msg"].lower() for message in outputs["messages"]
    )
