import shutil
from pathlib import Path
from unittest import mock

import pandas as pd
import pytest
from _pytest.monkeypatch import MonkeyPatch

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
from protzilla.data_analysis.ptm_visualization.ptm_vis_utils import (
    get_general_config_module,
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
TAU_REGIONS_FILE_PATH = TAU_PATH / "regions_P10636.csv"

Q_VALUE_THRESHOLD = 0.01


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


def alter_ptm_settings(monkeypatch: MonkeyPatch, new_param_dict: dict):
    def mock_figure_orientation(regions_file_path: Path, out_dir: Path):
        config_module = get_general_config_module(regions_file_path, out_dir)
        config_module.__dict__.update(new_param_dict)
        return config_module

    monkeypatch.setattr(
        ptm_vis_utils, "get_general_config_module", mock_figure_orientation
    )


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


def validate_plot_outputs(
    # TODO: this could probably be made prettier, especially not setting any default value
    plot,
    plot_func,
    all_groups: set,
    required_groups: set,
    required_ptm_types: tuple = (
        "Phosphorylation",
        "Acetylation",
        "Citrullination",
        "Ubiquitination",
    ),
    required_ptms: tuple = ("S8", "S13", "T35", "R152", "K154", "S409", "R413", "T411"),
    required_region_names: tuple = ("Blah-Term", "1A", "1B", "2A", "2B", "α", "ε"),
    required_cleavages: tuple = ("1", "7-9", "14", "35", "148", "156", "417"),
    additional_required_strings: tuple = (),
    additional_excluded_strings: tuple = (),
):
    all_layout_strings = {anno.text for anno in plot.layout.annotations if anno.text}
    all_data_strings = {
        subplot.text
        for subplot in plot.data
        if hasattr(subplot, "mode") and subplot.mode == "text"
    }
    all_plot_strings = all_layout_strings.union(all_data_strings)

    assert set(required_ptm_types).issubset(all_plot_strings)
    assert set(required_ptms).issubset(all_plot_strings)
    assert set(required_region_names).issubset(all_plot_strings)

    if plot_func in (create_details_ptm_visualization, create_bar_ptm_visualization):
        required_groups = set(required_groups)
        assert required_groups.issubset(all_plot_strings)
        excluded_groups = all_groups - required_groups
        assert all(g not in all_plot_strings for g in excluded_groups)

    if plot_func == create_details_ptm_visualization:
        assert set(required_cleavages).issubset(all_plot_strings)

    assert all(s in all_plot_strings for s in additional_required_strings)
    assert all(s not in all_plot_strings for s in additional_excluded_strings)


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

        validate_plot_outputs(
            plot,
            plot_func,
            all_groups=(
                set(kwargs["metadata_df"]["Group"].unique())
                if "metadata_df" in kwargs
                else set()
            ),
            required_groups={"clean", "old", "exon"},
        )

    @staticmethod
    def test_plotting_functions_vertical_orientation(plot_func, kwargs, monkeypatch):
        # Mocking the settings load function seemed easier than creating a whole new settings file just for this

        new_param_dict = {
            "FIGURE_ORIENTATION": 1,
        }
        alter_ptm_settings(monkeypatch, new_param_dict)

        result = plot_func(**kwargs)
        assert len(result["plots"]) == 1

        plot = result["plots"][0]
        validate_plot_outputs(
            plot,
            plot_func,
            all_groups=(
                set(kwargs["metadata_df"]["Group"].unique())
                if "metadata_df" in kwargs
                else set()
            ),
            required_groups={"clean", "old", "exon"},
        )

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

    @staticmethod
    def test_metadata_file_names_differing(plot_func, bar_detail_kwargs):
        bar_detail_kwargs["metadata_df"]["Sample"] = bar_detail_kwargs["metadata_df"][
            "Sample"
        ].apply(lambda x: f"Different_{x}")
        with pytest.raises(
            ValueError,
            match=r"The following samples from the evidence file are missing in the metadata file: .*",
        ):
            plot_func(**bar_detail_kwargs)

    @staticmethod
    def test_no_groups_in_metadata(plot_func, bar_detail_kwargs):
        bar_detail_kwargs["metadata_df"] = pd.DataFrame(
            columns=bar_detail_kwargs["metadata_df"].columns
        )
        with pytest.raises(
            ValueError,
            match=r"The following samples from the evidence file are missing in the metadata file: .*",
        ):
            plot_func(**bar_detail_kwargs)

    @staticmethod
    def test_group_col_not_in_metadata_df(plot_func, bar_detail_kwargs):
        bar_detail_kwargs["metadata_column"] = "NonExistingColumn"
        with pytest.raises(
            ValueError,
            match=r"Metadata column '.*' not found in metadata DataFrame columns: .*",
        ):
            plot_func(**bar_detail_kwargs)

    @staticmethod
    def test_evidence_samples_not_matching_metadata(plot_func, bar_detail_kwargs):
        new_evidence_df = bar_detail_kwargs["evidence_df"]
        new_evidence_df["Sample"] = new_evidence_df["Sample"].apply(
            lambda x: f"Different_{x}" if "AD" in x or "CTR" in x else x
        )
        bar_detail_kwargs["evidence_df"] = new_evidence_df

        with pytest.raises(
            ValueError,
            match=f"The following samples from the evidence file are missing in the metadata file: .*",
        ):
            plot_func(**bar_detail_kwargs)

    @staticmethod
    def test_different_metadata_column(
        plot_func,
        bar_detail_kwargs,
    ):
        metadata_df = bar_detail_kwargs["metadata_df"]
        bar_detail_kwargs["metadata_column"] = "Batch"
        result = plot_func(**bar_detail_kwargs)
        assert len(result["plots"]) == 1
        validate_plot_outputs(
            result["plots"][0],
            create_bar_ptm_visualization,
            all_groups=set(metadata_df[bar_detail_kwargs["metadata_column"]].unique()),
            required_groups={"2", "3", "4"},
        )

    @staticmethod
    def test_detected_modifications(
        evidence_df,
        q_value_threshold,
        fasta_file_path,
        regions_file_path,
        expected_modifications_path,
        tmp_ptm_settings_dir,
    ):
        # Check that warnings are thrown when more modifications are present in the evidence file than in the settings
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

    @staticmethod
    def test_cassette_exon(plot_func, kwargs):
        kwargs["evidence_df"] = get_evidence_df(TAU_EVIDENCE_FILE_PATH)
        if "metadata_df" in kwargs:
            kwargs["metadata_df"] = get_metadata_df(TAU_METADATA_FILE_PATH)
        kwargs["fasta_file_path"] = Path(TAU_PATH / "uniprotkb_P10636_7_8.fasta")
        kwargs["regions_file_path"] = Path(TAU_PATH / "regions_P10636_7_8.csv")

        result = plot_func(**kwargs)
        assert len(result["plots"]) == 1
        plot = result["plots"][0]

        all_groups = (
            set(kwargs["metadata_df"]["Group"].unique())
            if "metadata_df" in kwargs
            else set()
        )
        validate_plot_outputs(
            plot,
            plot_func,
            all_groups=all_groups,
            required_groups={"AD"},
            required_ptm_types=("Phosphorylation",),
            required_ptms=("S68", "T71", "S113"),
            required_region_names=(
                "N-term",
                "N1",
                "N2",
                "Mid",
                "PRR",
                "R1",
                "R2",
                "R3",
                "R4",
                "C-term",
            ),
            required_cleavages=(),
        )

    @staticmethod
    def test_modification_at_first_location(plot_func, kwargs):
        # TODO: maybe also test with the other functions later
        if plot_func != create_overview_ptm_visualization:
            return

        ##### Overlapping Exons
        # Tau
        # kwargs["evidence_df"] = get_evidence_df(TAU_EVIDENCE_FILE_PATH)
        # if "metadata_df" in kwargs:
        #     kwargs["metadata_df"] = get_metadata_df(TAU_METADATA_FILE_PATH)
        # # TODO: migrate to repo if test stays
        # # TODO: might be the better file for test above
        # kwargs["fasta_file_path"] = Path("/home/hendraet/stud_sync/Studium/phd/proteomics/data/ptm_vis_data/uniprotkb_P10636_5_8.fasta")
        # kwargs["regions_file_path"] = Path(TAU_PATH / "regions_P10636_7_8.csv")

        # GFAP
        # mock_start_peptide = kwargs["evidence_df"].iloc[97]
        # mock_start_peptide["Modified sequence"] = "_(Oxidation (Protein N-term))M(ci)ERRRIT_"
        # mock_start_peptide["Modifications"] = "Oxidation (Protein N-term); ci"
        # kwargs["evidence_df"] = pd.concat(
        #     [kwargs["evidence_df"], pd.DataFrame([mock_start_peptide])], ignore_index=True
        # )
        #
        # mock_exon1_peptide = kwargs["evidence_df"].iloc[97]
        # mock_exon1_peptide["Sequence"] = "GGKST"
        # mock_exon1_peptide["Modified sequence"] = "_G(ci)GKST_"
        # mock_exon1_peptide["Modifications"] = "ci"
        # kwargs["evidence_df"] = pd.concat(
        #     [kwargs["evidence_df"], pd.DataFrame([mock_exon1_peptide])], ignore_index=True
        # )
        #
        # # TODO: drawing is fucked and does not point to the exon - talk to Chris
        # mock_exon2_peptide = kwargs["evidence_df"].iloc[97]
        # mock_exon2_peptide["Sequence"] = "ETSLDT"
        # mock_exon2_peptide["Modified sequence"] = "_E(ci)TSLDT_"
        # mock_exon2_peptide["Modifications"] = "ci"
        # kwargs["evidence_df"] = pd.concat(
        #     [kwargs["evidence_df"], pd.DataFrame([mock_exon2_peptide])], ignore_index=True
        # )

        result = create_overview_ptm_visualization(**kwargs)
        assert len(result["plots"]) == 1
        plot = result["plots"][0]
        # TODO: remove
        plot.show()
        ######### TODO: double check that these are all the modifications that we could have found

        # TODO: this check is for the mocked GFAP
        validate_plot_outputs(
            plot,
            plot_func,
            all_groups=(
                set(kwargs["metadata_df"]["Group"].unique())
                if "metadata_df" in kwargs
                else set()
            ),
            required_groups={"clean", "old", "exon"},
            additional_required_strings=("M1", "G391", "E391"),
            additional_excluded_strings=("M0",),
        )

    @staticmethod
    def test_single_amino_acid_substitution_start_of_exon(plot_func, kwargs):
        # TODO: maybe also test with the other functions later
        if plot_func != create_overview_ptm_visualization:
            return

        # AML
        # TODO: doesn't work because we don't have a clean exon, but a single amino acid with two possibilites
        kwargs["evidence_df"] = get_evidence_df(
            Path(
                "/home/hendraet/stud_sync/Studium/phd/proteomics/data/PXD014997_AML_phosphoproteome/txt/evidence_Q01826.txt"
            )
        )
        kwargs["fasta_file_path"] = Path(
            "/home/hendraet/stud_sync/Studium/phd/proteomics/data/PXD014997_AML_phosphoproteome/ptm/Q01826_SATB1.fasta"
        )
        kwargs["regions_file_path"] = Path(
            "/home/hendraet/stud_sync/Studium/phd/proteomics/data/PXD014997_AML_phosphoproteome/ptm/Q01826_SATB1_regions.csv"
        )

        result = create_overview_ptm_visualization(**kwargs)
        assert len(result["plots"]) == 1
        plot = result["plots"][0]
        # TODO: remove
        plot.show()

        # TODO: adapt
        validate_plot_outputs(
            plot,
            plot_func,
            all_groups=(
                set(kwargs["metadata_df"]["Group"].unique())
                if "metadata_df" in kwargs
                else set()
            ),
            required_groups={"clean", "old", "exon"},
            additional_required_strings=("M1", "G391", "E391"),
            additional_excluded_strings=("M0",),
        )

    # TODO: fix
    @staticmethod
    def test_single_amino_acid_substitution_end_of_exon(plot_func, kwargs):
        # TODO: maybe also test with the other functions later
        if plot_func != create_overview_ptm_visualization:
            return

        ##### Overlapping Exons
        # Tau
        kwargs["evidence_df"] = get_evidence_df(TAU_EVIDENCE_FILE_PATH)
        if "metadata_df" in kwargs:
            kwargs["metadata_df"] = get_metadata_df(TAU_METADATA_FILE_PATH)
        # TODO: migrate to repo if test stays
        # TODO: might be the better file for test above
        kwargs["fasta_file_path"] = Path("/home/hendraet/stud_sync/Studium/phd/proteomics/data/ptm_vis_data/uniprotkb_P10636_5_8.fasta")
        kwargs["regions_file_path"] = Path(TAU_PATH / "regions_P10636_7_8.csv")

        result = create_overview_ptm_visualization(**kwargs)
        assert len(result["plots"]) == 1
        plot = result["plots"][0]
        # TODO: remove
        plot.show()

        validate_plot_outputs(
            plot,
            plot_func,
            all_groups=(
                set(kwargs["metadata_df"]["Group"].unique())
                if "metadata_df" in kwargs
                else set()
            ),
            required_groups={"clean", "old", "exon"},
            additional_required_strings=("M1", "G391", "E391"),
            additional_excluded_strings=("M0",),
        )
