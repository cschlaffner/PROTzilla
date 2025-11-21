import pandas as pd
import pytest
from gseapy import heatmap

from protzilla.data_analysis.plots import clustergram_plot
from protzilla.data_analysis.ptm_quantification.flexiquant import flexiquant_lf
from protzilla.data_analysis.ptm_quantification.multiflex import multiflex_lf
from protzilla.importing.metadata_import import metadata_import_method
from protzilla.importing.peptide_import import peptide_import
from tests.paths import TEST_DATA_PATH


def get_peptide_df_AD_only() -> pd.DataFrame:
    df = peptide_import(
        TEST_DATA_PATH / 'peptides/peptides_tau_AD01.txt',
        'Intensity',
        map_to_uniprot=False
    )['peptide_df']
    return df


@pytest.fixture
def peptide_df_single_group():
    return get_peptide_df_AD_only()


@pytest.fixture
def peptide_df_one_sample_with_few_peptides():
    peptide_df = get_peptide_df_AD_only()
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


def get_peptide_df_AD_CTR() -> pd.DataFrame:
    df = peptide_import(
        TEST_DATA_PATH / 'peptides/peptides_tau_AD01_CTR01.txt',
        'Intensity',
        map_to_uniprot=False
    )['peptide_df']
    return df


@pytest.fixture
def peptide_df():
    peptide_df = get_peptide_df_AD_CTR()
    peptide_df = peptide_df[peptide_df['Protein ID'] == 'P10636']
    return peptide_df


@pytest.fixture
def peptide_df_not_all_proteins_present_in_both_conditions():
    return get_peptide_df_AD_CTR()


@pytest.fixture
def peptide_df_few_peptides():
    peptide_df = get_peptide_df_AD_CTR()
    all_peptides = peptide_df['Sequence'].unique()
    selected_peptides = all_peptides[:8]
    peptide_df_shortened = peptide_df[peptide_df['Sequence'].isin(selected_peptides)]
    return peptide_df_shortened


@pytest.fixture
def metadata_df():
    dummy_protein_df = pd.DataFrame({'Sample': [
        'AD01_C1_INSOLUBLE_01',
        'AD01_C1_INSOLUBLE_02',
        'AD01_C1_INSOLUBLE_03',
        'CTR01_C1_INSOLUBLE_01',
    ]})  # Dummy DataFrame for metadata import
    df = metadata_import_method(
        dummy_protein_df,
        TEST_DATA_PATH / 'import_data/metadata/metadata_AD01_CTR01.csv',
        feature_orientation='Columns'
    )['metadata_df']

    return df


@pytest.mark.parametrize(
    "reference_group,grouping_column",
    [
        ('AD', 'Group'),
        ('CTR', 'Group'),
        ('C1', 'Batch'),
        ('C2', 'Batch'),
    ],
)
def test_flexiquant(peptide_df, metadata_df, reference_group, grouping_column):
    protein_group = 'P10636'
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


def test_flexiquant_grouping_column_not_in_df(peptide_df, metadata_df):
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


def test_flexiquant_reference_group_not_in_group(peptide_df, metadata_df):
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


def test_flexiquant_not_enough_valid_peptides(peptide_df_few_peptides, metadata_df):
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


def test_flexiquant_one_sample_with_not_enough_valid_peptides(peptide_df_one_sample_with_few_peptides, metadata_df):
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


def check_multiflex_plots_valid(result: dict, n_samples):
    assert 'plots' in result and len(result['plots']) == 3
    plots = result['plots']
    rm_score_hist_data = plots[0].data

    # one hist and one scatter for each sample
    assert len(rm_score_hist_data) == 2 * n_samples
    rm_score_plot_types = set(trace.type for trace in rm_score_hist_data)
    assert 'histogram' in rm_score_plot_types and 'scatter' in rm_score_plot_types

    clustergram_data = plots[1].data
    assert 'heatmap' in set(trace.type for trace in clustergram_data)

    heatmap_data = plots[2].data
    assert len(heatmap_data) == 1 and 'heatmap' in set(trace.type for trace in heatmap_data)


@pytest.mark.parametrize(
    "deseq2_normalization,reference_group,grouping_column,colormap",
    [
        (True, 'AD', 'Group', 0),
        (False, 'AD', 'Group', 1),
        (True, 'CTR', 'Group', 2),
        (False, 'CTR', 'Group', 3),
        (True, 'C1', 'Batch', 4),
        (False, 'C1', 'Batch', 5),
        (False, 'AD', 'Group', 6),
        (False, 'AD', 'Group', 7),
        (False, 'AD', 'Group', 8),
    ],
)
def test_multiflex(peptide_df, metadata_df, deseq2_normalization, reference_group, grouping_column, colormap):
    n_samples = metadata_df['Sample'].nunique()

    result = multiflex_lf(
        peptide_df=peptide_df,
        metadata_df=metadata_df,
        reference_group=reference_group,
        grouping_column=grouping_column,
        # TODO: test any of these args?
        num_init=30,
        mod_cutoff=0.5,
        imputation_cosine_similarity=0.98,
        deseq2_normalization=deseq2_normalization,
        colormap=colormap,
    )
    assert (
            'messages' in result
            and 'skipped_proteins' in result
            and len(result['messages']) == 0
            and len(result['skipped_proteins']) == 0
    )
    check_multiflex_plots_valid(result, n_samples)


def test_multiflex_grouping_column_not_in_df(peptide_df, metadata_df):
    reference_group = 'AD'
    grouping_column = 'NonExistentGroup'

    result = multiflex_lf(
        peptide_df=peptide_df,
        metadata_df=metadata_df,
        reference_group=reference_group,
        grouping_column=grouping_column,
        num_init=30,
        mod_cutoff=0.5,
        imputation_cosine_similarity=0.98,
        deseq2_normalization=True,
        colormap=1,
    )
    assert 'messages' in result
    assert result['messages'][0]['msg'] == f"Grouping column {grouping_column} not found in metadata."


def test_multiflex_reference_group_not_in_df(peptide_df, metadata_df):
    reference_group = 'AAAAADDDDDD'
    grouping_column = 'Group'

    result = multiflex_lf(
        peptide_df=peptide_df,
        metadata_df=metadata_df,
        reference_group=reference_group,
        grouping_column=grouping_column,
        num_init=30,
        mod_cutoff=0.5,
        imputation_cosine_similarity=0.98,
        deseq2_normalization=True,
        colormap=1,
    )
    assert 'messages' in result and len(result['messages']) == 1
    assert result['messages'][0]['msg'] == f"Reference group {reference_group} not found in metadata."


def test_multiflex_not_enough_valid_peptides(peptide_df_few_peptides, metadata_df):
    # TODO: migrate peptide_df_few_peptides so that it has two groups
    reference_group = 'AD'
    grouping_column = 'Group'

    result = multiflex_lf(
        peptide_df=peptide_df_few_peptides,
        metadata_df=metadata_df,
        reference_group=reference_group,
        grouping_column=grouping_column,
        num_init=30,
        mod_cutoff=0.5,
        imputation_cosine_similarity=0.98,
        deseq2_normalization=True,
        colormap=1,
    )
    assert 'messages' in result and len(result['messages']) == 1
    assert result['messages'][0]['msg'] == ('RM scores were not computed! Intensities of at least 5 peptides per '
                                            'protein have to be given!')


def test_multiflex_only_one_group(peptide_df_single_group, metadata_df):
    reference_group = 'AD'
    grouping_column = 'Group'

    result = multiflex_lf(
        peptide_df=peptide_df_single_group,
        metadata_df=metadata_df,
        reference_group=reference_group,
        grouping_column=grouping_column,
        num_init=30,
        mod_cutoff=0.5,
        imputation_cosine_similarity=0.98,
        deseq2_normalization=True,
        colormap=1,
    )

    assert 'messages' in result
    assert result['messages'][0]['msg'] == "At least two groups are required for multiFLEX-LF analysis."


def test_multiflex_no_peptides_in_two_conditions(peptide_df, metadata_df):
    reference_group = 'AD'
    grouping_column = 'Group'

    # Remove peptides in a way that half of the peptides are only in AD samples and the other half only in CTR samples
    all_peptides = peptide_df['Sequence'].unique()
    ad_peptides = all_peptides[ : len(all_peptides) // 2]
    peptide_df_modified = peptide_df[
        (peptide_df['Sample'].str.contains('AD') & peptide_df['Sequence'].isin(ad_peptides)) |
        (~peptide_df['Sample'].str.contains('AD') & ~peptide_df['Sequence'].isin(ad_peptides))
    ]

    result = multiflex_lf(
        peptide_df=peptide_df_modified,
        metadata_df=metadata_df,
        reference_group=reference_group,
        grouping_column=grouping_column,
        num_init=30,
        mod_cutoff=0.5,
        imputation_cosine_similarity=0.98,
        deseq2_normalization=True,
        colormap=1,
    )
    assert 'messages' in result and 'plots' not in result
    assert result['messages'][0]['msg'] == ("No peptides with RM scores in at least two groups available for "
                                            "clustering!")


def test_multiflex_flexiquant_errors(peptide_df_not_all_proteins_present_in_both_conditions, metadata_df):
    n_samples = metadata_df['Sample'].nunique()
    reference_group = 'CTR'
    grouping_column = 'Group'
    # get all proteins that are always nan in the CTR group
    proteins_not_in_control = (
        peptide_df_not_all_proteins_present_in_both_conditions[
            peptide_df_not_all_proteins_present_in_both_conditions['Sample'].str.contains('CTR')
        ]
        .groupby('Protein ID')
        .filter(lambda x: x['Intensity'].isna().all())['Protein ID']
        .unique()
    )
    n_proteins_not_in_control = len(proteins_not_in_control)

    result = multiflex_lf(
        peptide_df=peptide_df_not_all_proteins_present_in_both_conditions,
        metadata_df=metadata_df,
        reference_group=reference_group,
        grouping_column=grouping_column,
        num_init=30,
        mod_cutoff=0.5,
        imputation_cosine_similarity=0.98,
        deseq2_normalization=False,
        colormap=1,
    )
    assert (
            'messages' in result
            and len(result['messages']) == n_proteins_not_in_control
            and all([p[i] in result['messages'][i] for i, p in enumerate(proteins_not_in_control)])
    )
    assert (
            'skipped_proteins' in result
            and len(result['messages']) == n_proteins_not_in_control
            and set(result['skipped_proteins']) == set(proteins_not_in_control)
    )
    check_multiflex_plots_valid(result, n_samples)
