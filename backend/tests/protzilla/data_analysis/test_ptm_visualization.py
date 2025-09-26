from pathlib import Path

import pytest

from protzilla.data_analysis.ptm_visualization import create_overview_ptm_visualization, create_bar_ptm_visualization, \
    create_details_ptm_visualization
from protzilla.importing import peptide_import
from tests.paths import TEST_PTM_VISUALIZATION_PATH


# TODO:
#  - Add one path for MaxQuant Preprocessor
#  - Happy paths for: (using the uniprotkb file, the regions file and evidence_longer file)
#    - [X] Overview plot
#    - [X] Bar plot
#    - [X] Details plot
#  - Non-happy stuff:
#    - Fasta
#      - Fasta with non-matching iso-form ids (non_matching.fasta)
#      - Proteins from fasta not in evidence_df (wrong.fasta)
#      - Malformed fasta (non-uniprot style) - maybe like Tariks old file (malformed.fasta)
#      - Not full sequence covered (short.fasta)
#    - Regions
#      - regions not matching the protein
#      - malformed regions file, e.g. differently named columns or columns missing
#      - Missing regions in between
#      - Missing regions at the end
#    - Groups
#      - Differing groups
#      - No groups
#      - Not all groups present in evidence_df

@pytest.fixture
def evidence_df():
    outputs = peptide_import.evidence_import(
        file_path=Path(f"{TEST_PTM_VISUALIZATION_PATH}/evidence_longer.txt"),
        map_to_uniprot=False,
    )

    return outputs['peptide_df']


@pytest.fixture
def q_value_threshold():
    return 0.01


@pytest.fixture
def fasta_file_path():
    return Path(f"{TEST_PTM_VISUALIZATION_PATH}/uniprotkb.fasta")


@pytest.fixture
def regions_file_path():
    return Path(f"{TEST_PTM_VISUALIZATION_PATH}/regions.csv")


@pytest.fixture
def group_file_path():
    return Path(f"{TEST_PTM_VISUALIZATION_PATH}/groups_max_quant.csv")


def test_overview_ptm_visualization(evidence_df, q_value_threshold, fasta_file_path, regions_file_path):
    result = create_overview_ptm_visualization(
            evidence_df,
            q_value_threshold,
            fasta_file_path,
            regions_file_path,
    )
    assert len(result['plots']) == 1


def test_bar_ptm_visualization(evidence_df, q_value_threshold, fasta_file_path, regions_file_path, group_file_path):
    result = create_bar_ptm_visualization(
        evidence_df=evidence_df,
        evidence_file_q_value_threshold=q_value_threshold,
        fasta_file_path=fasta_file_path,
        regions_file_path=regions_file_path,
        groups_file_path=group_file_path
    )
    assert len(result['plots']) == 1


def test_details_ptm_visualization(evidence_df, q_value_threshold, fasta_file_path, regions_file_path, group_file_path):
    result = create_details_ptm_visualization(
        evidence_df=evidence_df,
        evidence_file_q_value_threshold=q_value_threshold,
        fasta_file_path=fasta_file_path,
        regions_file_path=regions_file_path,
        groups_file_path=group_file_path
    )
    assert len(result['plots']) == 1
