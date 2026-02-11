import shutil
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

import pytest

from protzilla import importing
from protzilla.importing.example_dataset_import import example_dataset_import
from tests.paths import (
    TEST_MSDATA_PATH,
    TEST_PEPTIDES_PATH,
    TEST_METADATA_PATH,
)


@pytest.fixture()
def tmp_example_data_dir(tmp_path_factory):
    test_tmp_data_dir = Path("example_data/")
    tmp_path = tmp_path_factory.mktemp(str(test_tmp_data_dir))
    return tmp_path


@pytest.fixture()
def example_data_paths(tmp_example_data_dir):
    tmp_protein_path = (
        tmp_example_data_dir.resolve() / "txt_REL_FREE-REPASE/proteinGroups.txt"
    )
    tmp_evidence_path = (
        tmp_example_data_dir.resolve() / "txt_REL_FREE-REPASE/evidence.txt"
    )
    tmp_meta_path = tmp_example_data_dir.resolve() / "meta.csv"
    return tmp_protein_path, tmp_evidence_path, tmp_meta_path


@contextmanager
def mock_example_data_download(
    monkeypatch,
    tmp_protein_path,
    tmp_evidence_path,
    tmp_meta_path,
    protein_file,
    evidence_file,
    meta_file,
):
    with (
        mock.patch.object(
            importing.example_dataset_import,
            "EXAMPLE_DATASET_PROTEIN_FILE",
            tmp_protein_path,
        ),
        mock.patch.object(
            importing.example_dataset_import,
            "EXAMPLE_DATASET_METADATA_FILE",
            tmp_meta_path,
        ),
        mock.patch.object(
            importing.example_dataset_import,
            "EXAMPLE_DATASET_EVIDENCE_FILE",
            tmp_evidence_path,
        ),
    ):

        def mock_download(
            import_peptide_data: bool,
            accession: str = "PXD014997",
            filename: str = "SEARCH-IDENTIFICATIONS_REL_FREE-RELAPSE.7z",
        ):
            tmp_protein_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(protein_file, tmp_protein_path)

            if import_peptide_data:
                tmp_evidence_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(evidence_file, tmp_evidence_path)

        monkeypatch.setattr(
            importing.example_dataset_import, "download_example_data", mock_download
        )

        shutil.copy(meta_file, tmp_meta_path)
        yield


@pytest.mark.parametrize(
    "import_peptide_data",
    [False, True],
)
def test_example_data_import(monkeypatch, example_data_paths, import_peptide_data):
    tmp_protein_path, tmp_evidence_path, tmp_meta_path = example_data_paths
    test_protein_file = TEST_MSDATA_PATH / "MaxQuant/small.tsv"
    test_evidence_file = TEST_PEPTIDES_PATH / "evidence_ratio_hl.txt"
    test_metadata_file = TEST_METADATA_PATH / "metadata_full.csv"

    with mock_example_data_download(
        monkeypatch,
        tmp_protein_path,
        tmp_evidence_path,
        tmp_meta_path,
        test_protein_file,
        test_evidence_file,
        test_metadata_file,
    ):
        import_results = example_dataset_import(
            import_peptide_data=import_peptide_data,
        )
        assert "protein_df" in import_results
        if import_peptide_data:
            assert "peptide_df" in import_results
        assert "metadata_df" in import_results
        assert len(import_results["messages"]) == 2
        sorted_messages = sorted(import_results["messages"], key=lambda x: x["msg"])
        assert sorted_messages[0]["msg"] == "Metadata file successfully imported."
        assert (
            sorted_messages[1]["msg"]
            == "Successfully imported 22 protein groups for 1 samples. 0 contaminant groups were dropped. 0 invalid "
            "proteins were filtered."
        )


@pytest.mark.parametrize(
    "protein_file,evidence_file,meta_file,message",
    [
        (
            "MaxQuant/proteinGroups_small_cut.txt",
            "evidence_ratio_hl.txt",
            "metadata_full.csv",
            "Ratio H/L was not found in the provided file",
        ),
        (
            "MaxQuant/small.tsv",
            "evidence_vsmall.txt",
            "metadata_full.csv",
            "Ratio H/L was not found in the provided file",
        ),
        (
            "MaxQuant/small.tsv",
            "evidence_ratio_hl.txt",
            "metadata_sample_column_missing.csv",
            "The metadata file must contain a column named 'Sample'",
        ),
    ],
)
def test_example_data_import_erroneous_data(
    monkeypatch, example_data_paths, protein_file, evidence_file, meta_file, message
):
    tmp_protein_path, tmp_evidence_path, tmp_meta_path = example_data_paths
    test_protein_file = TEST_MSDATA_PATH / protein_file
    test_evidence_file = TEST_PEPTIDES_PATH / evidence_file
    test_metadata_file = TEST_METADATA_PATH / meta_file

    with mock_example_data_download(
        monkeypatch,
        tmp_protein_path,
        tmp_evidence_path,
        tmp_meta_path,
        test_protein_file,
        test_evidence_file,
        test_metadata_file,
    ):
        import_results = example_dataset_import(import_peptide_data=True)
        assert "protein_df" not in import_results
        assert "peptide_df" not in import_results
        assert "metadata_df" not in import_results
        assert "messages" in import_results
        assert import_results["messages"][0]["msg"].startswith(message)
