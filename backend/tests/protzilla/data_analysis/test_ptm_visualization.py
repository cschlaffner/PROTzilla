from pathlib import Path

import pandas as pd
import pytest

from protzilla.data_analysis.ptm_visualization import create_overview_ptm_visualization, create_bar_ptm_visualization, \
    create_details_ptm_visualization
from protzilla.data_analysis.ptm_visualization.ptm_overview_plot import get_detected_modifications
from protzilla.importing import peptide_import
from tests.paths import TEST_PTM_VISUALIZATION_PATH


class TestPTMVisualization:
    @pytest.fixture
    def evidence_df(self):
        outputs = peptide_import.evidence_import(
            file_path=Path(f"{TEST_PTM_VISUALIZATION_PATH}/evidence_longer.txt"),
            map_to_uniprot=False,
        )

        return outputs['peptide_df']

    @pytest.fixture
    def q_value_threshold(self):
        return 0.01

    @pytest.fixture
    def fasta_file_path(self):
        return Path(f"{TEST_PTM_VISUALIZATION_PATH}/uniprotkb.fasta")

    @pytest.fixture
    def regions_file_path(self):
        return Path(f"{TEST_PTM_VISUALIZATION_PATH}/regions.csv")

    @pytest.fixture
    def group_file_path(self):
        return Path(f"{TEST_PTM_VISUALIZATION_PATH}/groups_max_quant.csv")

    @pytest.fixture
    def expected_modifications_path(self):
        return Path(f"{TEST_PTM_VISUALIZATION_PATH}/expected_modifications.csv")

    @staticmethod
    def test_overview_ptm_visualization(evidence_df, q_value_threshold, fasta_file_path, regions_file_path):
        result = create_overview_ptm_visualization(
            evidence_df=evidence_df,
            evidence_file_q_value_threshold=q_value_threshold,
            fasta_file_path=fasta_file_path,
            regions_file_path=regions_file_path,
        )
        assert len(result['plots']) == 1

    @staticmethod
    def test_bar_ptm_visualization(
            evidence_df,
            q_value_threshold,
            fasta_file_path,
            regions_file_path,
            group_file_path
    ):
        result = create_bar_ptm_visualization(
            evidence_df=evidence_df,
            evidence_file_q_value_threshold=q_value_threshold,
            fasta_file_path=fasta_file_path,
            regions_file_path=regions_file_path,
            groups_file_path=group_file_path
        )
        assert len(result['plots']) == 1

    @staticmethod
    def test_details_ptm_visualization(
            evidence_df,
            q_value_threshold,
            fasta_file_path,
            regions_file_path,
            group_file_path
    ):
        result = create_details_ptm_visualization(
            evidence_df=evidence_df,
            evidence_file_q_value_threshold=q_value_threshold,
            fasta_file_path=fasta_file_path,
            regions_file_path=regions_file_path,
            groups_file_path=group_file_path
        )
        assert len(result['plots']) == 1

    @staticmethod
    def test_fasta_non_matching_isoform_ids(evidence_df, q_value_threshold, regions_file_path, group_file_path):
        fasta_file_path = Path(f"{TEST_PTM_VISUALIZATION_PATH}/non_matching.fasta")
        with pytest.raises(ValueError, match=r"There seem to be isoforms of different proteins in the fasta file.*"):
            create_details_ptm_visualization(
                evidence_df,
                q_value_threshold,
                fasta_file_path,
                regions_file_path,
                group_file_path
            )

    @staticmethod
    def test_fasta_proteins_not_in_evidence_df(evidence_df, q_value_threshold, regions_file_path, group_file_path):
        fasta_file_path = Path(f"{TEST_PTM_VISUALIZATION_PATH}/wrong.fasta")
        with pytest.raises(ValueError, match="No matching isoform IDs found between the uploaded evidence file and the "
                                             "fasta file."):
            create_details_ptm_visualization(
                evidence_df,
                q_value_threshold,
                fasta_file_path,
                regions_file_path,
                group_file_path
            )

    @staticmethod
    def test_malformed_fasta(evidence_df, q_value_threshold, regions_file_path, group_file_path):
        fasta_file_path = Path(f"{TEST_PTM_VISUALIZATION_PATH}/malformed.fasta")
        with pytest.raises(ValueError, match=r"Error parsing fasta file. Please check the format of the fasta file. "
                                             r"Uniprot style is recommended."):
            create_details_ptm_visualization(
                evidence_df,
                q_value_threshold,
                fasta_file_path,
                regions_file_path,
                group_file_path
            )

    @staticmethod
    def test_fasta_shortened_sequence(evidence_df, q_value_threshold, regions_file_path, group_file_path):
        fasta_file_path = Path(f"{TEST_PTM_VISUALIZATION_PATH}/short.fasta")
        with pytest.raises(ValueError, match=r"Exon start .* does not match any region end, please check your supplied "
                                             r"region list - maybe it is missing some regions or it doesn't match the "
                                             r"provided fasta sequence."):
            create_details_ptm_visualization(
                evidence_df,
                q_value_threshold,
                fasta_file_path,
                regions_file_path,
                group_file_path
            )

    @staticmethod
    def test_regions_not_matching_protein(evidence_df, q_value_threshold, fasta_file_path, group_file_path):
        regions_file_path = Path(f"{TEST_PTM_VISUALIZATION_PATH}/regions_missing.csv")
        with pytest.raises(ValueError, match=r"Exon start .* does not match any region end, please check your supplied "
                                             r"region list - maybe it is missing some regions"):
            create_details_ptm_visualization(
                evidence_df,
                q_value_threshold,
                fasta_file_path,
                regions_file_path,
                group_file_path
            )

        regions_file_path = Path(f"{TEST_PTM_VISUALIZATION_PATH}/regions_shortened.csv")
        with pytest.raises(ValueError,
                           match=r"Exon start .* matches a region end for region .*, but there are not enough "
                                 r"regions after it, please check your supplied region list."):
            create_details_ptm_visualization(
                evidence_df,
                q_value_threshold,
                fasta_file_path,
                regions_file_path,
                group_file_path
            )

    @staticmethod
    def test_malformed_regions_file(evidence_df, q_value_threshold, fasta_file_path, group_file_path):
        regions_file_path = Path(f"{TEST_PTM_VISUALIZATION_PATH}/regions_missing_columns.csv")
        with pytest.raises(AssertionError,
                           match=r"Regions file must contain at least the columns 'name', 'region_end', "
                                 r"'group' and 'short_name but got .*"):
            create_details_ptm_visualization(
                evidence_df,
                q_value_threshold,
                fasta_file_path,
                regions_file_path,
                group_file_path
            )

        regions_file_path = Path(f"{TEST_PTM_VISUALIZATION_PATH}/regions_renamed.csv")
        with pytest.raises(AssertionError,
                           match=r"Regions file must contain at least the columns 'name', 'region_end', "
                                 r"'group' and 'short_name but got .*"):
            create_details_ptm_visualization(
                evidence_df,
                q_value_threshold,
                fasta_file_path,
                regions_file_path,
                group_file_path
            )

    @staticmethod
    def test_groups_differing(evidence_df, q_value_threshold, fasta_file_path, regions_file_path):
        group_file_path = Path(f"{TEST_PTM_VISUALIZATION_PATH}/groups_differing.csv")
        with pytest.raises(ValueError, match=r"Group .* not found in provided groups file"):
            create_details_ptm_visualization(
                evidence_df,
                q_value_threshold,
                fasta_file_path,
                regions_file_path,
                group_file_path
            )

    @staticmethod
    def test_groups_no_groups_provided(evidence_df, q_value_threshold, fasta_file_path, regions_file_path):
        group_file_path = Path(f"{TEST_PTM_VISUALIZATION_PATH}/groups_empty.csv")
        # Should still work
        create_overview_ptm_visualization(
            evidence_df,
            q_value_threshold,
            fasta_file_path,
            regions_file_path,
        )
        with pytest.raises(ValueError, match="No groups found in the provided groups file for bar plot visualization."):
            create_bar_ptm_visualization(
                evidence_df,
                q_value_threshold,
                fasta_file_path,
                regions_file_path,
                group_file_path
            )
        with pytest.raises(
                ValueError,
                match="No groups found in the provided groups file for details plot visualization."
        ):
            create_details_ptm_visualization(
                evidence_df,
                q_value_threshold,
                fasta_file_path,
                regions_file_path,
                group_file_path
            )

    @staticmethod
    def test_malformed_groups_file(evidence_df, q_value_threshold, fasta_file_path, regions_file_path):
        group_file_path = Path(f"{TEST_PTM_VISUALIZATION_PATH}/groups_renamed.csv")
        with pytest.raises(AssertionError, match=r"Groups file must contain the columns: :*"):
            create_bar_ptm_visualization(
                evidence_df,
                q_value_threshold,
                fasta_file_path,
                regions_file_path,
                group_file_path
            )

    @staticmethod
    def test_detected_modifications(
            evidence_df,
            q_value_threshold,
            fasta_file_path,
            regions_file_path,
            group_file_path,
            expected_modifications_path,
    ):
        expected_modification_df = pd.read_csv(expected_modifications_path)
        result = get_detected_modifications(
            evidence_df,
            q_value_threshold,
            fasta_file_path,
            regions_file_path,
        )
        modification_df = result['modification_df']

        pd.testing.assert_frame_equal(
            modification_df.sort_values(
                by=['Location', 'Amino Acid', 'Modification', 'Isoform']
            ).reset_index(drop=True),
            expected_modification_df.sort_values(
                by=['Location', 'Amino Acid', 'Modification', 'Isoform']
            ).reset_index(drop=True)
        )

        # TODO: Would have loved to test that the warning is thrown if more PTMs than specified in the settings are
        #  detected. However, I found no proper way of mocking the settings file and didn't want to change the actual
        #  settings file.
        # Check that warnings are thrown when more modifications are present in the evidence file than in the settings
        # result = create_overview_ptm_visualization(
        #     evidence_df=evidence_df,
        #     evidence_file_q_value_threshold=q_value_threshold,
        #     fasta_file_path=fasta_file_path,
        #     regions_file_path=regions_file_path,
        # )
        # assert (
        #         len(result['plots']) == 1
        #         and len(result['messages']) == 1
        #         and "More modifications were detected than are present in the settings" in result['messages'][0]
        # )
        # result = create_bar_ptm_visualization(
        #     evidence_df=evidence_df,
        #     evidence_file_q_value_threshold=q_value_threshold,
        #     fasta_file_path=fasta_file_path,
        #     regions_file_path=regions_file_path,
        #     groups_file_path=group_file_path
        # )
        # assert (
        #         len(result['plots']) == 1
        #         and len(result['messages']) == 1
        #         and "More modifications were detected than are present in the settings" in result['messages'][0]
        # )
        # result = create_details_ptm_visualization(
        #     evidence_df=evidence_df,
        #     evidence_file_q_value_threshold=q_value_threshold,
        #     fasta_file_path=fasta_file_path,
        #     regions_file_path=regions_file_path,
        #     groups_file_path=group_file_path
        # )
        # assert (
        #         len(result['plots']) == 1
        #         and len(result['messages']) == 1
        #         and "More modifications were detected than are present in the settings" in result['messages'][0]
        # )
