from pathlib import Path

import pandas as pd
import pytest

from protzilla.data_analysis.ptm_quantification.flexiquant import flexiquant_lf
from protzilla.importing.metadata_import import metadata_import_method
from protzilla.importing.peptide_import import peptide_import
from tests.paths import TEST_DATA_PATH


@pytest.fixture
def peptide_df():
    df = peptide_import(
        TEST_DATA_PATH / 'peptides/peptides_tau_small.txt',
        'Intensity',
        map_to_uniprot=False
    )['peptide_df']

    return df


@pytest.fixture
def metadata_df():
    dummy_protein_df = pd.DataFrame({'Sample': [
        'AD01_C1_INSOLUBLE_01',
        'AD01_C1_INSOLUBLE_02',
        'AD01_C1_INSOLUBLE_03',
    ]})  # Dummy DataFrame for metadata import
    df = metadata_import_method(
        dummy_protein_df,
        TEST_DATA_PATH / 'import_data/metadata/metadata_AD01.csv',
        feature_orientation='Columns'
    )['metadata_df']

    return df


def test_flexiquant_lf(peptide_df, metadata_df):
    reference_group = 'AD'
    protein_group = 'P10636'
    grouping_column = 'Group'
    num_samples = peptide_df['Sample'].nunique()

    mod_cutoff = 0.5
    result = flexiquant_lf(
        peptide_df,
        metadata_df,
        reference_group,
        protein_group,
        grouping_column,
        num_init=30,
        mod_cutoff=mod_cutoff
    )
    assert 'plots' in result and len(result['plots']) == num_samples
    removed_peptides = result['removed_peptides']
    assert set(removed_peptides).isdisjoint(set(result['diff_modified']))
    assert (
            len(result['messages']) == 1
            and result['messages'][0]['msg'] == f'All {num_samples} samples have been processed successfully. '
                                                f'{len(removed_peptides)} peptides have been removed.'
    )

# TODO: maybe also add CTR as group
# TODO: and or batch
