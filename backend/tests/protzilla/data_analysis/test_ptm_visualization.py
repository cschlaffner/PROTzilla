import shutil
from pathlib import Path
from unittest import mock

import pandas as pd
import pytest

import main
from protzilla.data_analysis.ptm_visualization import (
    create_overview_ptm_visualization,
    create_bar_ptm_visualization,
    create_details_ptm_visualization,
)
from protzilla.data_analysis.ptm_visualization.ptm_overview_plot import (
    get_detected_modifications,
)
from protzilla.importing import peptide_import
from tests.paths import TEST_PTM_VISUALIZATION_PATH

FASTA_FILE_PATH = TEST_PTM_VISUALIZATION_PATH / "uniprotkb.fasta"
REGIONS_FILE_PATH = TEST_PTM_VISUALIZATION_PATH / "regions.csv"
GROUP_FILE_PATH = TEST_PTM_VISUALIZATION_PATH / "groups_max_quant.csv"
Q_VALUE_THRESHOLD = 0.01

TAU_PATH = TEST_PTM_VISUALIZATION_PATH / "P10636"
TAU_FASTA_FILE_PATH = TAU_PATH / "uniprotkb_P10636_short.fasta"
TAU_REGIONS_FILE_PATH = TAU_PATH / "regions_P10636.csv"
TAU_GROUP_FILE_PATH = TAU_PATH / "groups_max_quant_AD.csv"


@pytest.fixture()
def tmp_ptm_settings_dir(tmp_path_factory):
    test_tmp_data_dir = Path("ptm_settings/")
    tmp_path = tmp_path_factory.mktemp(str(test_tmp_data_dir))
    return tmp_path


def get_evidence_df(path: Path):
    outputs = peptide_import.evidence_import(file_path=path, map_to_uniprot=False)
    evidence_df = outputs["peptide_df"]
    return evidence_df


def pytest_generate_tests(metafunc):
    # A generation function that makes sure that the matching test functions are run with all three plotting function
    # (overview, bar, details). Admittedly, it could look a bit prettier, but was currently not wort the effort
    if "plot_func" in metafunc.fixturenames:
        basic_kwargs = dict(
            evidence_df=get_evidence_df(TEST_PTM_VISUALIZATION_PATH / "evidence.txt"),
            evidence_file_q_value_threshold=Q_VALUE_THRESHOLD,
            fasta_file_path=FASTA_FILE_PATH,
            regions_file_path=REGIONS_FILE_PATH,
        )
        kwargs_with_groups = dict(**basic_kwargs, groups_file_path=GROUP_FILE_PATH)
        plot_funcs_to_kwargs = [
            (create_bar_ptm_visualization, kwargs_with_groups),
            (create_details_ptm_visualization, kwargs_with_groups),
        ]

        if metafunc.definition.name == "test_plotting_functions":
            # Additional files, but for the happy path only
            tau_kwargs = dict(
                evidence_df=get_evidence_df(TAU_PATH / "evidence.txt"),
                evidence_file_q_value_threshold=Q_VALUE_THRESHOLD,
                fasta_file_path=TAU_FASTA_FILE_PATH,
                regions_file_path=TAU_REGIONS_FILE_PATH,
            )
            tau_kwargs_with_groups = dict(
                **tau_kwargs, groups_file_path=TAU_GROUP_FILE_PATH
            )
            plot_funcs_to_kwargs.extend(
                [
                    (create_overview_ptm_visualization, tau_kwargs),
                    (create_bar_ptm_visualization, tau_kwargs_with_groups),
                    (create_details_ptm_visualization, tau_kwargs_with_groups),
                ]
            )

        if "bar_detail_kwargs" in metafunc.fixturenames:
            metafunc.parametrize("plot_func,bar_detail_kwargs", plot_funcs_to_kwargs)

        if "kwargs" in metafunc.fixturenames:
            plot_funcs_to_kwargs.append(
                (create_overview_ptm_visualization, basic_kwargs)
            )
            metafunc.parametrize("plot_func,kwargs", plot_funcs_to_kwargs)


class TestPTMVisualization:
    @pytest.fixture
    def evidence_df(self):
        return get_evidence_df(TEST_PTM_VISUALIZATION_PATH / "evidence.txt")

    @pytest.fixture
    def q_value_threshold(self):
        return Q_VALUE_THRESHOLD

    @pytest.fixture
    def fasta_file_path(self):
        return FASTA_FILE_PATH

    @pytest.fixture
    def regions_file_path(self):
        return REGIONS_FILE_PATH

    @pytest.fixture
    def group_file_path(self):
        return GROUP_FILE_PATH

    @pytest.fixture
    def expected_modifications_path(self):
        return TEST_PTM_VISUALIZATION_PATH / "expected_modifications.csv"

    @staticmethod
    def test_plotting_functions(plot_func, kwargs):
        result = plot_func(**kwargs)
        assert len(result["plots"]) == 1

    @staticmethod
    def test_fasta_non_matching_isoform_ids(plot_func, kwargs):
        kwargs["fasta_file_path"] = Path(
            f"{TEST_PTM_VISUALIZATION_PATH}/non_matching.fasta"
        )
        with pytest.raises(
            ValueError,
            match=r"There seem to be isoforms of different proteins in the fasta file.*",
        ):
            plot_func(**kwargs)

    @staticmethod
    def test_fasta_proteins_not_in_evidence_df(plot_func, kwargs):
        kwargs["fasta_file_path"] = Path(f"{TEST_PTM_VISUALIZATION_PATH}/wrong.fasta")
        with pytest.raises(
            ValueError,
            match="No matching isoform IDs found between the uploaded evidence file and the "
            "fasta file.",
        ):
            plot_func(**kwargs)

    @staticmethod
    def test_malformed_fasta(plot_func, kwargs):
        kwargs["fasta_file_path"] = Path(
            f"{TEST_PTM_VISUALIZATION_PATH}/malformed.fasta"
        )
        with pytest.raises(
            ValueError,
            match=r"Error parsing fasta file. Please check the format of the fasta file. "
            r"Uniprot style is recommended.",
        ):
            plot_func(**kwargs)

    @staticmethod
    def test_fasta_shortened_sequence(plot_func, kwargs):
        kwargs["fasta_file_path"] = Path(f"{TEST_PTM_VISUALIZATION_PATH}/short.fasta")
        with pytest.raises(
            ValueError,
            match=r"The longest original sequence has a length of [0-9]+, but the regions file only "
            r"contains regions up to position [0-9]+. Please adjust the regions in the "
            "corresponding CSV file to match the sequence length.",
        ):
            plot_func(**kwargs)

    @staticmethod
    def test_regions_not_matching_protein(plot_func, kwargs):
        kwargs["regions_file_path"] = Path(
            f"{TEST_PTM_VISUALIZATION_PATH}/regions_missing.csv"
        )
        with pytest.raises(
            ValueError,
            match=r"Exon start .* does not match any region end, please check your supplied "
            r"region list - maybe it is missing some regions",
        ):
            plot_func(**kwargs)

        kwargs["regions_file_path"] = Path(
            f"{TEST_PTM_VISUALIZATION_PATH}/regions_shortened.csv"
        )
        with pytest.raises(
            ValueError,
            match=r"The longest original sequence has a length of .*, but the regions file only "
            r"contains regions up to position .*. Please adjust the regions in the corresponding "
            r"CSV file to match the sequence length.",
        ):
            plot_func(**kwargs)

        kwargs["regions_file_path"] = Path(
            f"{TEST_PTM_VISUALIZATION_PATH}/regions_one_exon_missing.csv"
        )
        with pytest.raises(
            ValueError,
            match=r"The longest original sequence has a length of .*, but the regions file only "
            r"contains regions up to position .*. Please adjust the regions in the corresponding "
            r"CSV file to match the sequence length.",
        ):
            plot_func(**kwargs)

    @staticmethod
    def test_malformed_regions_file(plot_func, kwargs):
        kwargs["regions_file_path"] = Path(
            f"{TEST_PTM_VISUALIZATION_PATH}/regions_missing_columns.csv"
        )
        with pytest.raises(
            AssertionError,
            match=r"Regions file must contain at least the columns 'name', 'region_end', "
            r"'group' and 'short_name but got .*",
        ):
            plot_func(**kwargs)

        kwargs["regions_file_path"] = Path(
            f"{TEST_PTM_VISUALIZATION_PATH}/regions_renamed.csv"
        )
        with pytest.raises(
            AssertionError,
            match=r"Regions file must contain at least the columns 'name', 'region_end', "
            r"'group' and 'short_name but got .*",
        ):
            plot_func(**kwargs)

    @staticmethod
    def test_regions_file_too_short_but_matching_region_end(plot_func, kwargs):
        new_kwargs = dict(
            evidence_df=get_evidence_df(TAU_PATH / "evidence.txt"),
            evidence_file_q_value_threshold=Q_VALUE_THRESHOLD,
            fasta_file_path=TAU_FASTA_FILE_PATH,
            regions_file_path=TAU_PATH
            / "regions_too_short_but_matching_region_end.csv",
        )
        if "groups_file_path" in kwargs:
            new_kwargs["groups_file_path"] = TAU_GROUP_FILE_PATH

        with pytest.raises(
            ValueError,
            match=r"The longest original sequence has a length of .*, but the regions file only "
            r"contains regions up to position .*. Please adjust the regions in the corresponding "
            r"CSV file to match the sequence length.",
        ):
            plot_func(**new_kwargs)

    @staticmethod
    def test_groups_differing(plot_func, bar_detail_kwargs):
        bar_detail_kwargs["groups_file_path"] = Path(
            f"{TEST_PTM_VISUALIZATION_PATH}/groups_differing.csv"
        )
        with pytest.raises(
            ValueError, match=r"Group .* not found in provided groups file"
        ):
            plot_func(**bar_detail_kwargs)

    @staticmethod
    def test_groups_no_groups_provided(plot_func, bar_detail_kwargs):
        bar_detail_kwargs["groups_file_path"] = Path(
            f"{TEST_PTM_VISUALIZATION_PATH}/groups_empty.csv"
        )
        with pytest.raises(
            ValueError,
            match=r"No groups found in the provided groups file for (bar|details) plot visualization.",
        ):
            plot_func(**bar_detail_kwargs)

    @staticmethod
    def test_malformed_groups_file(plot_func, bar_detail_kwargs):
        bar_detail_kwargs["groups_file_path"] = Path(
            f"{TEST_PTM_VISUALIZATION_PATH}/groups_renamed.csv"
        )
        with pytest.raises(
            AssertionError, match=r"Groups file must contain the columns: :*"
        ):
            plot_func(**bar_detail_kwargs)

    @staticmethod
    def test_detected_modifications(
        evidence_df,
        q_value_threshold,
        fasta_file_path,
        regions_file_path,
        group_file_path,
        expected_modifications_path,
        tmp_ptm_settings_dir,
    ):
        expected_modification_df = pd.read_csv(expected_modifications_path)
        result = get_detected_modifications(
            evidence_df,
            q_value_threshold,
            fasta_file_path,
            regions_file_path,
        )
        modification_df = result["modification_df"]

        pd.testing.assert_frame_equal(
            modification_df.sort_values(
                by=["Location", "Amino Acid", "Modification", "Isoform"]
            ).reset_index(drop=True),
            expected_modification_df.sort_values(
                by=["Location", "Amino Acid", "Modification", "Isoform"]
            ).reset_index(drop=True),
        )

        # Check that warnings are thrown when more modifications are present in the evidence file than in the settings
        settings_reduced_ptms_file = Path(
            TEST_PTM_VISUALIZATION_PATH / "ptm_settings_fewer_ptms.yaml"
        )
        shutil.copy(settings_reduced_ptms_file, tmp_ptm_settings_dir)
        with mock.patch.object(
            main.views_helper, "SETTINGS_PATH", tmp_ptm_settings_dir.resolve()
        ):
            result = create_overview_ptm_visualization(
                evidence_df=evidence_df,
                evidence_file_q_value_threshold=q_value_threshold,
                fasta_file_path=fasta_file_path,
                regions_file_path=regions_file_path,
            )
            assert (
                len(result["plots"]) == 1
                and len(result["messages"]) == 1
                and result["messages"][0]["level"] == 30
                and "More modifications were detected than are present in the settings"
                in result["messages"][0]["msg"]
            )
            result = create_bar_ptm_visualization(
                evidence_df=evidence_df,
                evidence_file_q_value_threshold=q_value_threshold,
                fasta_file_path=fasta_file_path,
                regions_file_path=regions_file_path,
                groups_file_path=group_file_path,
            )
            assert (
                len(result["plots"]) == 1
                and len(result["messages"]) == 1
                and result["messages"][0]["level"] == 30
                and "More modifications were detected than are present in the settings"
                in result["messages"][0]["msg"]
            )
            result = create_details_ptm_visualization(
                evidence_df=evidence_df,
                evidence_file_q_value_threshold=q_value_threshold,
                fasta_file_path=fasta_file_path,
                regions_file_path=regions_file_path,
                groups_file_path=group_file_path,
            )
            assert (
                len(result["plots"]) == 1
                and len(result["messages"]) == 1
                and result["messages"][0]["level"] == 30
                and "More modifications were detected than are present in the settings"
                in result["messages"][0]["msg"]
            )
