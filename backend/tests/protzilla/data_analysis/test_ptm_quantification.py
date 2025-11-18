import pandas as pd
import pytest

from protzilla.data_analysis.ptm_quantification.flexiquant import flexiquant_lf
from protzilla.importing.metadata_import import metadata_import_method
from protzilla.importing.peptide_import import peptide_import
from tests.paths import TEST_DATA_PATH


def get_peptide_df() -> pd.DataFrame:
    df = peptide_import(
        TEST_DATA_PATH / 'peptides/peptides_tau_small.txt',
        'Intensity',
        map_to_uniprot=False
    )['peptide_df']
    return df


@pytest.fixture
def peptide_df():
    return get_peptide_df()


@pytest.fixture
def peptide_df_few_peptides():
    peptide_df = get_peptide_df()
    all_peptides = peptide_df['Sequence'].unique()
    selected_peptides = all_peptides[:8]
    peptide_df_shortened = peptide_df[peptide_df['Sequence'].isin(selected_peptides)]
    return peptide_df_shortened


@pytest.fixture
def peptide_df_one_sample_with_few_peptides():
    peptide_df = get_peptide_df()
    first_sample = peptide_df['Sample'].iloc[0]
    first_sample_peptides = peptide_df[peptide_df['Sample'] == first_sample]['Sequence'].unique()
    selected_peptides = first_sample_peptides[:3]
    peptide_df_shortened = peptide_df[
        ~(
                (peptide_df['Sample'] == first_sample)
                & ~(peptide_df['Sequence'].isin(selected_peptides))
        )
    ]
    return peptide_df_shortened


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


def test_grouping_column_not_in_df(peptide_df, metadata_df):
    reference_group = 'AD'
    protein_group = 'P10636'
    grouping_column = 'NonExistentGroup'

    result = flexiquant_lf(
        peptide_df,
        metadata_df,
        reference_group,
        protein_group,
        grouping_column,
        num_init=30,
        mod_cutoff=0.5
    )
    assert 'messages' in result
    assert result['messages'][0]['msg'] == f"No {grouping_column} column found in provided dataframe."


def test_reference_cond_not_in_group(peptide_df, metadata_df):
    reference_group = 'AAAAAAD'
    protein_group = 'P10636'
    grouping_column = 'Group'

    result = flexiquant_lf(
        peptide_df,
        metadata_df,
        reference_group,
        protein_group,
        grouping_column,
        num_init=30,
        mod_cutoff=0.5
    )
    assert 'messages' in result
    assert result['messages'][0]['msg'] == f"Reference sample '{reference_group}' not found in provided data."


def test_not_enough_valid_peptides(peptide_df_few_peptides, metadata_df):
    reference_group = 'AD'
    protein_group = 'P10636'
    grouping_column = 'Group'

    result = flexiquant_lf(
        peptide_df_few_peptides,
        metadata_df,
        reference_group,
        protein_group,
        grouping_column,
        num_init=30,
        mod_cutoff=0.5
    )
    assert 'plots' in result and len(result['plots']) == 0
    assert 'messages' in result
    assert result['messages'][0]['msg'] == ("No samples were processed. This is probably due to the fact that there "
                                            "are not enough valid peptides in the samples.")


def test_one_sample_with_not_enough_valid_peptides(peptide_df_one_sample_with_few_peptides, metadata_df):
    reference_group = 'AD'
    protein_group = 'P10636'
    grouping_column = 'Group'
    num_samples = peptide_df_one_sample_with_few_peptides['Sample'].nunique()
    num_proper_samples = num_samples - 1

    result = flexiquant_lf(
        peptide_df_one_sample_with_few_peptides,
        metadata_df,
        reference_group,
        protein_group,
        grouping_column,
        num_init=30,
        mod_cutoff=0.5
    )
    assert 'plots' in result and len(result['plots']) == num_proper_samples
    assert 'messages' in result
    removed_peptides = result['removed_peptides']
    assert result['messages'][0]['msg'] == (f"{num_proper_samples}/{num_samples} samples have been processed "
                                            f"successfully. The remaining samples have been skipped due to "
                                            f"insufficient valid peptides. {len(removed_peptides)} peptides have been "
                                            f"removed.")
