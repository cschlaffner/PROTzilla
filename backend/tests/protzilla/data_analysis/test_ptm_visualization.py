import shutil
from pathlib import Path
from unittest import mock

import pandas as pd
import pytest

import main
from protzilla.constants.intensity_types import IntensityType
from protzilla.data_analysis.ptm_visualization import (
    create_overview_ptm_visualization,
    create_bar_ptm_visualization,
    create_details_ptm_visualization,
    ptm_vis_utils,
)
from protzilla.data_analysis.ptm_visualization.ptm_overview_plot import (
    get_detected_modifications,
)
from protzilla.importing import peptide_import
from protzilla.importing.metadata_import import metadata_import_method
from tests.paths import (
    TEST_PTM_VISUALIZATION_PATH,
    TEST_FASTA_PATH,
    TEST_PEPTIDES_PATH,
    TEST_METADATA_PATH,
)

GFAP_PATH = TEST_PTM_VISUALIZATION_PATH / "P14136"
GFAP_EVIDENCE_FILE_PATH = TEST_PEPTIDES_PATH / "evidence_P14136.txt"
GFAP_FASTA_FILE_PATH = TEST_FASTA_PATH / "uniprotkb_P14136.fasta"
GFAP_REGIONS_FILE_PATH = GFAP_PATH / "regions.csv"
GFAP_METADATA_FILE_PATH = GFAP_PATH / "metadata.csv"

TAU_PATH = TEST_PTM_VISUALIZATION_PATH / "P10636"
TAU_EVIDENCE_FILE_PATH = TEST_PEPTIDES_PATH / "evidence_P10636.txt"
TAU_FASTA_FILE_PATH = TEST_FASTA_PATH / "uniprotkb_P10636.fasta"
TAU_METADATA_FILE_PATH = TEST_METADATA_PATH / "metadata_full.csv"

Q_VALUE_THRESHOLD = 0.01


# TODO: test frontend again
@pytest.fixture()
def tmp_ptm_settings_dir(tmp_path_factory):
    test_tmp_data_dir = Path("ptm_settings/")
    tmp_path = tmp_path_factory.mktemp(str(test_tmp_data_dir))
    return tmp_path


def get_evidence_df(path: Path):
    outputs = peptide_import.evidence_import(
        file_path=path,
        intensity_name=IntensityType.INTENSITY.value,
        map_to_uniprot=False,
    )
    evidence_df = outputs["peptide_df"]
    return evidence_df


def get_metadata_df(path: Path):
    metadata_df = metadata_import_method(
        protein_df=None, file_path=path, feature_orientation="columns"
    )["metadata_df"]
    return metadata_df


def pytest_generate_tests(metafunc):
    # A generation function that makes sure that the matching test functions are run with all three plotting function
    # (overview, bar, details). Admittedly, it could look a bit prettier, but was currently not worth the effort
    if "plot_func" in metafunc.fixturenames:
        basic_kwargs = dict(
            evidence_df=get_evidence_df(GFAP_EVIDENCE_FILE_PATH),
            evidence_file_q_value_threshold=Q_VALUE_THRESHOLD,
            fasta_file_path=GFAP_FASTA_FILE_PATH,
            regions_file_path=GFAP_REGIONS_FILE_PATH,
        )
        kwargs_with_meta = dict(
            **basic_kwargs,
            metadata_df=get_metadata_df(GFAP_METADATA_FILE_PATH),
            metadata_column="Group",
        )
        plot_funcs_to_kwargs = [
            (create_bar_ptm_visualization, kwargs_with_meta),
            (create_details_ptm_visualization, kwargs_with_meta),
        ]

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
        return get_evidence_df(GFAP_EVIDENCE_FILE_PATH)

    @pytest.fixture
    def q_value_threshold(self):
        return Q_VALUE_THRESHOLD

    @pytest.fixture
    def fasta_file_path(self):
        return GFAP_FASTA_FILE_PATH

    @pytest.fixture
    def regions_file_path(self):
        return GFAP_REGIONS_FILE_PATH

    @pytest.fixture
    def expected_modifications_path(self):
        return GFAP_PATH / "expected_modifications.csv"

    @staticmethod
    def test_plotting_functions(plot_func, kwargs):
        result = plot_func(**kwargs)
        assert len(result["plots"]) == 1
        plot = result["plots"][0]

        all_layout_strings = {
            anno.text for anno in plot.layout.annotations if anno.text
        }
        all_data_strings = {
            subplot.text
            for subplot in plot.data
            if hasattr(subplot, "mode") and subplot.mode == "text"
        }
        all_plot_strings = all_layout_strings.union(all_data_strings)
        required_ptm_types = {
            "Phosphorylation",
            "Acetylation",
            "Citrullination",
            "Ubiquitination",
        }
        assert required_ptm_types.issubset(all_plot_strings)

        required_ptms = {"S8", "S13", "T35", "R152", "K154", "S409", "R413", "T411"}
        assert required_ptms.issubset(all_plot_strings)

        required_region_names = {
            "Blah-Term",
            "1A",
            "1B",
            "2A",
            "2B",
            "α",
            "ε",
        }
        assert required_region_names.issubset(all_plot_strings)

        if (
            plot_func == create_details_ptm_visualization
            or plot_func == create_bar_ptm_visualization
        ):
            required_groups = {"clean", "old", "exon"}
            assert required_groups.issubset(all_plot_strings)
            excluded_groups = {"AD", "CTR", "test", "fail"}
            assert all(g not in all_plot_strings for g in excluded_groups)

        if plot_func == create_details_ptm_visualization:
            required_cleavages = {"1", "7-9", "14", "35", "148", "156", "417"}
            assert required_cleavages.issubset(all_plot_strings)

    @staticmethod
    def test_fasta_non_matching_isoform_ids(plot_func, kwargs):
        kwargs["fasta_file_path"] = TEST_FASTA_PATH / "non_matching_P14136.fasta"
        with pytest.raises(
            ValueError,
            match=r"There seem to be isoforms of different proteins in the fasta file.*",
        ):
            plot_func(**kwargs)

    @staticmethod
    def test_fasta_proteins_not_in_evidence_df(plot_func, kwargs):
        kwargs["fasta_file_path"] = TEST_FASTA_PATH / "wrong_P14136.fasta"
        with pytest.raises(
            ValueError,
            match="No matching isoform IDs found between the uploaded evidence file and the "
            "fasta file.",
        ):
            plot_func(**kwargs)

    @staticmethod
    def test_malformed_fasta(plot_func, kwargs):
        kwargs["fasta_file_path"] = TEST_FASTA_PATH / "malformed.fasta"
        with pytest.raises(
            ValueError,
            match=r"Error parsing fasta file. Please check the format of the fasta file. "
            r"Uniprot style is recommended.",
        ):
            plot_func(**kwargs)

    @staticmethod
    def test_fasta_shortened_sequence(plot_func, kwargs):
        kwargs["fasta_file_path"] = TEST_FASTA_PATH / "short_P14136.fasta"
        with pytest.raises(
            ValueError,
            match=r"The longest original sequence has a length of [0-9]+, but the regions file only "
            r"contains regions up to position [0-9]+. Please adjust the regions in the "
            "corresponding CSV file to match the sequence length.",
        ):
            plot_func(**kwargs)

    @staticmethod
    def test_regions_not_matching_protein(plot_func, kwargs):
        kwargs["regions_file_path"] = GFAP_PATH / "regions_missing.csv"
        with pytest.raises(
            ValueError,
            match=r"Exon start .* does not match any region end, please check your supplied "
            r"region list - maybe it is missing some regions",
        ):
            plot_func(**kwargs)

        kwargs["regions_file_path"] = GFAP_PATH / "regions_shortened.csv"
        with pytest.raises(
            ValueError,
            match=r"The longest original sequence has a length of .*, but the regions file only "
            r"contains regions up to position .*. Please adjust the regions in the corresponding "
            r"CSV file to match the sequence length.",
        ):
            plot_func(**kwargs)

        kwargs["regions_file_path"] = GFAP_PATH / "regions_one_exon_missing.csv"
        with pytest.raises(
            ValueError,
            match=r"The longest original sequence has a length of .*, but the regions file only "
            r"contains regions up to position .*. Please adjust the regions in the corresponding "
            r"CSV file to match the sequence length.",
        ):
            plot_func(**kwargs)

    @staticmethod
    def test_malformed_regions_file(plot_func, kwargs):
        kwargs["regions_file_path"] = GFAP_PATH / "regions_missing_columns.csv"
        with pytest.raises(
            AssertionError,
            match=r"Regions file must contain at least the columns 'name', 'region_end', "
            r"'group' and 'short_name but got .*",
        ):
            plot_func(**kwargs)

        kwargs["regions_file_path"] = GFAP_PATH / "regions_renamed.csv"
        with pytest.raises(
            AssertionError,
            match=r"Regions file must contain at least the columns 'name', 'region_end', "
            r"'group' and 'short_name but got .*",
        ):
            plot_func(**kwargs)

    @staticmethod
    def test_regions_file_too_short_but_matching_region_end(plot_func, kwargs):
        new_kwargs = dict(
            evidence_df=get_evidence_df(TAU_EVIDENCE_FILE_PATH),
            evidence_file_q_value_threshold=Q_VALUE_THRESHOLD,
            fasta_file_path=TAU_FASTA_FILE_PATH,
            regions_file_path=TAU_PATH
            / "regions_too_short_but_matching_region_end.csv",
        )
        if "metadata_df" in kwargs:
            new_kwargs["metadata_df"] = get_metadata_df(TAU_METADATA_FILE_PATH)
            new_kwargs["metadata_column"] = "Group"

        with pytest.raises(
            ValueError,
            match=r"The longest original sequence has a length of .*, but the regions file only "
            r"contains regions up to position .*. Please adjust the regions in the corresponding "
            r"CSV file to match the sequence length.",
        ):
            plot_func(**new_kwargs)

    # TODO: remove all the old group files used for testing

    @staticmethod
    def test_metadata_file_names_differing(plot_func, bar_detail_kwargs):
        bar_detail_kwargs["metadata_df"]["Sample"] = bar_detail_kwargs["metadata_df"][
            "Sample"
        ].apply(lambda x: f"Different_{x}")
        with pytest.raises(
            ValueError, match=r"Group '.*' not found in provided groups file"
        ):
            plot_func(**bar_detail_kwargs)

    @staticmethod
    def test_no_groups_in_metadata(plot_func, bar_detail_kwargs):
        bar_detail_kwargs["metadata_df"] = pd.DataFrame(
            columns=bar_detail_kwargs["metadata_df"].columns
        )
        with pytest.raises(
            ValueError,
            match=r"No groups found in the provided groups file for (bar|details) plot visualization.",
        ):
            plot_func(**bar_detail_kwargs)

    @staticmethod
    def test_group_col_not_in_metadata_df(plot_func, bar_detail_kwargs):
        bar_detail_kwargs["metadata_column"] = "NonExistingColumn"
        with pytest.raises(
            AssertionError,
            match=r"Metadata column '.*' not found in metadata DataFrame columns: .*",
        ):
            plot_func(**bar_detail_kwargs)

    @staticmethod
    def test_different_metadata_column(
        evidence_df,
        q_value_threshold,
        fasta_file_path,
        regions_file_path,
    ):
        result = create_bar_ptm_visualization(
            evidence_df=evidence_df,
            evidence_file_q_value_threshold=q_value_threshold,
            fasta_file_path=fasta_file_path,
            regions_file_path=regions_file_path,
            metadata_df=get_metadata_df(GFAP_METADATA_FILE_PATH),
            metadata_column="Batch",
        )
        # TODO: talk to Chris if this is the desired output
        assert len(result["plots"]) == 1

    @staticmethod
    def test_detected_modifications(
        evidence_df,
        q_value_threshold,
        fasta_file_path,
        regions_file_path,
        expected_modifications_path,
        tmp_ptm_settings_dir,
    ):
        expected_modification_df = pd.read_csv(expected_modifications_path)
        result = get_detected_modifications(
            evidence_df,
            q_value_threshold,
            fasta_file_path,
            regions_file_path,
            metadata_df=get_metadata_df(GFAP_METADATA_FILE_PATH),
            metadata_column="Group",
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
        shutil.copytree(
            main.views_helper.SETTINGS_PATH, tmp_ptm_settings_dir, dirs_exist_ok=True
        )
        settings_reduced_ptms_file = Path(
            TEST_PTM_VISUALIZATION_PATH / f"ptm_settings_fewer_ptms.yaml"
        )
        shutil.copy(settings_reduced_ptms_file, tmp_ptm_settings_dir)
        with (
            mock.patch.object(
                main.views_helper,
                "SETTINGS_PATH",
                tmp_ptm_settings_dir.resolve(),
            ),
            mock.patch.object(
                ptm_vis_utils,
                "CUSTOM_PTM_SETTINGS_FILE_STEM",
                settings_reduced_ptms_file.stem,
            ),
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
                metadata_df=get_metadata_df(GFAP_METADATA_FILE_PATH),
                metadata_column="Group",
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
                metadata_df=get_metadata_df(GFAP_METADATA_FILE_PATH),
                metadata_column="Group",
            )
            assert (
                len(result["plots"]) == 1
                and len(result["messages"]) == 1
                and result["messages"][0]["level"] == 30
                and "More modifications were detected than are present in the settings"
                in result["messages"][0]["msg"]
            )


# TODO: do we need a test for figure orientation here? Somehow?
