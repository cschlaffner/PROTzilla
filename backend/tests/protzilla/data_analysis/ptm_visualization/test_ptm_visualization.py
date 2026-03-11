from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import pytest

from protzilla.constants.paths import EXAMPLE_DATASET_METADATA_FILE
from protzilla.data_analysis.ptm_visualization import (
    create_overview_ptm_visualization,
    create_bar_ptm_visualization,
    create_details_ptm_visualization,
)
from protzilla.data_analysis.ptm_visualization.ptm_overview_plot import (
    get_detected_modifications,
)
from tests.paths import (
    TEST_PTM_VISUALIZATION_PATH,
    TEST_FASTA_PATH,
    TEST_PEPTIDES_PATH,
    TEST_METADATA_PATH,
)
from tests.protzilla.data_analysis.ptm_visualization.ptm_vis_test_utils import (
    get_evidence_df,
    get_metadata_df,
    mock_settings_file,
    run_plot_and_validate,
    alter_general_config,
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

SATB1_PATH = TEST_PTM_VISUALIZATION_PATH / "Q01826"
SATB1_EVIDENCE_FILE_PATH = TEST_PEPTIDES_PATH / "evidence_Q01826.txt"
SATB1_FASTA_FILE_PATH = TEST_FASTA_PATH / "Q01826_SATB1.fasta"
SATB1_REGIONS_FILE_PATH = SATB1_PATH / "Q01826_SATB1_regions.csv"

Q_VALUE_THRESHOLD = 0.01


@pytest.fixture()
def tmp_ptm_settings_dir(tmp_path_factory):
    test_tmp_data_dir = Path("ptm_settings/")
    tmp_path = tmp_path_factory.mktemp(str(test_tmp_data_dir))
    return tmp_path


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


@dataclass
class PlotValidationConfig:
    required_ptm_types: tuple[str, ...] = (
        "Phosphorylation",
        "Acetylation",
        "Citrullination",
        "Ubiquitination",
    )
    required_ptms: tuple[str, ...] = (
        "S8",
        "S13",
        "T35",
        "R152",
        "K154",
        "S409",
        "R413",
        "T411",
    )
    required_region_names: tuple[str, ...] = (
        "N-Term",
        "1Aaaa",
        "1Bbbb",
        "2Aaaa",
        "2Bbbb",
        "alpha",
        "epsilon",
    )
    required_region_short_names: tuple[str, ...] = (
        "N",
        "1B",
        "ε",
    )
    required_cleavages: tuple[str, ...] = (
        "1",
        "7-9",
        "14",
        "35",
        "148",
        "156",
        "417",
    )
    excluded_strings: tuple[str, ...] = ()


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

    @pytest.fixture
    def gfap_config(self):
        return PlotValidationConfig()

    @pytest.fixture
    def tau_cassette_exon_config(self):
        return PlotValidationConfig(
            required_ptm_types=("Phosphorylation", "Ubiquitination", "Acetylation"),
            required_ptms=(
                "S68",
                "T71",
                "T111",
                "S113",
                "T175",
                "T181",
                "S185",
                "S191",
                "S199",
                "S202",
                "T205",
                "S210",
                "T212",
                "S214",
                "T217",
                "T231",
                "S235",
                "S237",
                "S238",
                "K254",
                "K257",
                "S262",
                "K267",
                "K281",
                "S289",
                "K298",
                "S305",  # TODO: shouldn't the mod also be on K305?
                "K311",
                "K317",
                "K321",
                "K353",
                "T361",
                "K369",
                "Y394",
                "S396",
                "S400",
                "T403",
                "S404",
                "S412",
                "S416",
                "S422",
            ),
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
            required_region_short_names=(),
            required_cleavages=(),
        )

    @pytest.fixture
    def tau_substitution_config(self, tau_cassette_exon_config):
        required_ptms = list(tau_cassette_exon_config.required_ptms)
        required_ptms.pop(required_ptms.index("S68"))
        required_ptms.pop(required_ptms.index("S305"))
        required_ptms.append("K305")

        return PlotValidationConfig(
            required_ptm_types=tau_cassette_exon_config.required_ptm_types,
            required_ptms=tuple(required_ptms),
            required_region_names=tau_cassette_exon_config.required_region_names,
            required_region_short_names=(),
            required_cleavages=("103", "105", "306"),
        )

    @pytest.fixture
    def tau_5_config(self, tau_substitution_config):
        required_ptms = list(tau_substitution_config.required_ptms)
        last_ptm_index_before_cassette_exon = required_ptms.index("K267")
        required_ptms = required_ptms[: last_ptm_index_before_cassette_exon + 1] + [
            "K274",
            "K280",
            "K286",
            "K290",
            "K322",
            "K338",
            "S365",
            "S369",
            "S373",
            "S381",
            "S385",
            "S391",
            "T330",
            "T372",
            "Y363",
        ]

        region_names = list(tau_substitution_config.required_region_names)
        region_names.pop(region_names.index("R3"))

        return PlotValidationConfig(
            required_ptm_types=tau_substitution_config.required_ptm_types,
            required_ptms=tuple(required_ptms),
            required_region_names=tuple(region_names),
            required_region_short_names=(),
            required_cleavages=("103", "105"),
        )

    @pytest.fixture
    def tau_8_config(self, tau_cassette_exon_config):
        required_ptms = list(tau_cassette_exon_config.required_ptms)
        required_ptms.pop(required_ptms.index("S68"))

        return PlotValidationConfig(
            required_ptm_types=tau_cassette_exon_config.required_ptm_types,
            required_ptms=tuple(required_ptms),
            required_region_names=tau_cassette_exon_config.required_region_names,
            required_region_short_names=(),
            required_cleavages=("103", "105", "306"),
        )

    @pytest.fixture
    def satb1_config(self):
        return PlotValidationConfig(
            required_ptm_types=("Phosphorylation",),
            required_ptms=("S38", "S60", "S665", "S669"),
            required_region_names=("Pre-Exon", "Exon", "End"),
            required_region_short_names=("P", "E"),
            required_cleavages=("1",),
        )

    @staticmethod
    def test_plotting_functions(plot_func, kwargs, gfap_config):
        run_plot_and_validate(
            plot_func, kwargs, gfap_config, {"clean", "old", "exon"}
        )

    @staticmethod
    def test_plotting_functions_vertical_orientation(
        plot_func, kwargs, monkeypatch, gfap_config
    ):
        # Mocking the settings load function seemed easier than creating a whole new settings file just for this
        new_param_dict = {
            "FIGURE_ORIENTATION": 1,
        }
        alter_general_config(monkeypatch, new_param_dict)

        run_plot_and_validate(
            plot_func, kwargs, gfap_config, {"clean", "old", "exon"}
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

        # TODO: this file is basically the same as the shortened one
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
    def test_different_metadata_column(plot_func, bar_detail_kwargs, gfap_config):
        bar_detail_kwargs["metadata_column"] = "Batch"
        run_plot_and_validate(
            plot_func, bar_detail_kwargs, gfap_config, {"2", "3", "4"}
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

        settings_reduced_ptms_file = Path(
            TEST_PTM_VISUALIZATION_PATH / f"ptm_settings_fewer_ptms.yaml"
        )
        with mock_settings_file(settings_reduced_ptms_file, tmp_ptm_settings_dir):
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
    def test_cassette_exon(plot_func, kwargs, tau_cassette_exon_config):
        kwargs["evidence_df"] = get_evidence_df(TAU_EVIDENCE_FILE_PATH)
        if "metadata_df" in kwargs:
            kwargs["metadata_df"] = get_metadata_df(TAU_METADATA_FILE_PATH)
        kwargs["fasta_file_path"] = Path(TAU_PATH / "uniprotkb_P10636_7_8.fasta")
        kwargs["regions_file_path"] = TAU_REGIONS_FILE_PATH

        run_plot_and_validate(
            plot_func, kwargs, tau_cassette_exon_config, {"AD", "CTR"}
        )

    @staticmethod
    def test_modification_at_regions_starts_and_ends(
        plot_func, kwargs, tmp_ptm_settings_dir, gfap_config
    ):
        # TODO: bar plot orders ptms in alternative exon by number and doesn't take exon into account
        mock_start_peptide = kwargs["evidence_df"].iloc[97]
        mock_start_peptide["Modified sequence"] = (
            "_(Oxidation (Protein N-term))M(ci)ERRRIT_"
        )
        mock_start_peptide["Modifications"] = "Oxidation (Protein N-term); ci"
        kwargs["evidence_df"] = pd.concat(
            [kwargs["evidence_df"], pd.DataFrame([mock_start_peptide])],
            ignore_index=True,
        )

        # Beginning of exon 1
        mock_exon1_peptide = kwargs["evidence_df"].iloc[97]
        mock_exon1_peptide["Sequence"] = "ETSLDT"
        mock_exon1_peptide["Modified sequence"] = "_E(ci)TSLDT_"
        mock_exon1_peptide["Modifications"] = "ci"
        kwargs["evidence_df"] = pd.concat(
            [kwargs["evidence_df"], pd.DataFrame([mock_exon1_peptide])],
            ignore_index=True,
        )

        # End of exon 1
        mock_exon1_end_peptide = kwargs["evidence_df"].iloc[97]
        mock_exon1_end_peptide["Sequence"] = "KQEHKDVM"
        mock_exon1_end_peptide["Modified sequence"] = "_KQEHKDVM(ci)_"
        mock_exon1_end_peptide["Modifications"] = "ci"
        kwargs["evidence_df"] = pd.concat(
            [kwargs["evidence_df"], pd.DataFrame([mock_exon1_end_peptide])],
            ignore_index=True,
        )

        # Ensures that even though an aligned sequence has dashes in the alternative exon, the surrounding amino acids
        # are still plotted next to each other
        mock_peptide_exon_alignment_before_dash = kwargs["evidence_df"].iloc[97]
        mock_peptide_exon_alignment_before_dash["Sequence"] = "DTKSVSEG"
        mock_peptide_exon_alignment_before_dash["Modified sequence"] = "_DTKSVSEG(ci)_"
        mock_peptide_exon_alignment_before_dash["Modifications"] = "ci"
        kwargs["evidence_df"] = pd.concat(
            [
                kwargs["evidence_df"],
                pd.DataFrame([mock_peptide_exon_alignment_before_dash]),
            ],
            ignore_index=True,
        )
        mock_peptide_exon_alignment_after_dash = kwargs["evidence_df"].iloc[97]
        mock_peptide_exon_alignment_after_dash["Sequence"] = "HLKRNIVVK"
        mock_peptide_exon_alignment_after_dash["Modified sequence"] = "_H(ci)LKRNIVVK_"
        mock_peptide_exon_alignment_after_dash["Modifications"] = "ci"
        kwargs["evidence_df"] = pd.concat(
            [
                kwargs["evidence_df"],
                pd.DataFrame([mock_peptide_exon_alignment_after_dash]),
            ],
            ignore_index=True,
        )

        # First two peptides of Exon 2
        mock_exon2_peptide = kwargs["evidence_df"].iloc[97]
        mock_exon2_peptide["Protein ID"] = "P14136-3"
        mock_exon2_peptide["Sequence"] = "GGKST"
        mock_exon2_peptide["Modified sequence"] = "_G(ci)GKST_"
        mock_exon2_peptide["Modifications"] = "ci"
        kwargs["evidence_df"] = pd.concat(
            [kwargs["evidence_df"], pd.DataFrame([mock_exon2_peptide])],
            ignore_index=True,
        )
        mock_exon2_peptide = kwargs["evidence_df"].iloc[97]
        mock_exon2_peptide["Protein ID"] = "P14136-3"
        mock_exon2_peptide["Sequence"] = "GGKST"
        mock_exon2_peptide["Modified sequence"] = "_GG(ci)KST_"
        mock_exon2_peptide["Modifications"] = "ci"
        kwargs["evidence_df"] = pd.concat(
            [kwargs["evidence_df"], pd.DataFrame([mock_exon2_peptide])],
            ignore_index=True,
        )

        # Three peptides before alternative exon
        mock_pre_exon_peptide = kwargs["evidence_df"].iloc[97]
        mock_pre_exon_peptide["Sequence"] = "TFSNLQIR"
        mock_pre_exon_peptide["Modified sequence"] = "_TFSNLQIR(GG (R))_"
        mock_pre_exon_peptide["Modifications"] = "GG (R)"
        kwargs["evidence_df"] = pd.concat(
            [kwargs["evidence_df"], pd.DataFrame([mock_pre_exon_peptide])],
            ignore_index=True,
        )
        mock_pre_exon_peptide = kwargs["evidence_df"].iloc[97]
        mock_pre_exon_peptide["Sequence"] = "TFSNLQIR"
        mock_pre_exon_peptide["Modified sequence"] = "_TFSNLQI(GG (I))R_"
        mock_pre_exon_peptide["Modifications"] = "GG (I)"
        kwargs["evidence_df"] = pd.concat(
            [kwargs["evidence_df"], pd.DataFrame([mock_pre_exon_peptide])],
            ignore_index=True,
        )
        mock_pre_exon_peptide = kwargs["evidence_df"].iloc[97]
        mock_pre_exon_peptide["Sequence"] = "TFSNLQIR"
        mock_pre_exon_peptide["Modified sequence"] = "_TFSNLQ(GG (Q))IR_"
        mock_pre_exon_peptide["Modifications"] = "GG (Q)"
        kwargs["evidence_df"] = pd.concat(
            [kwargs["evidence_df"], pd.DataFrame([mock_pre_exon_peptide])],
            ignore_index=True,
        )

        # End of sequence/exon 2
        mock_sequence_end_peptide = kwargs["evidence_df"].iloc[97]
        mock_sequence_end_peptide["Protein ID"] = "P14136-3"
        mock_sequence_end_peptide["Sequence"] = "GTPPARG"
        mock_sequence_end_peptide["Modified sequence"] = "_GTPPARG(ci)_"
        mock_sequence_end_peptide["Modifications"] = "ci"
        kwargs["evidence_df"] = pd.concat(
            [kwargs["evidence_df"], pd.DataFrame([mock_sequence_end_peptide])],
            ignore_index=True,
        )

        additional_required_ptms = (
            "M1",
            "Q388",
            "I389",
            "R390",
            "E391",
            "G402",
            "H403",
            "M432",
            "G391",
            "G392",
            "G431",
        )
        additional_excluded_strings = ("M0",)
        gfap_config.required_ptms += additional_required_ptms
        gfap_config.excluded_strings += additional_excluded_strings
        gfap_config.required_region_short_names += ("α",)

        with mock_settings_file(
            TEST_PTM_VISUALIZATION_PATH / "ptm_settings_mods_at_first_location.yaml",
            tmp_ptm_settings_dir,
        ):
            run_plot_and_validate(
                plot_func, kwargs, gfap_config, {"clean", "old", "exon"}
            )

    @staticmethod
    def test_single_amino_acid_substitution_start_of_exon(
        plot_func, kwargs, satb1_config
    ):
        kwargs["evidence_df"] = get_evidence_df(SATB1_EVIDENCE_FILE_PATH)
        kwargs["fasta_file_path"] = SATB1_FASTA_FILE_PATH
        kwargs["regions_file_path"] = SATB1_REGIONS_FILE_PATH
        if "metadata_df" in kwargs:
            kwargs["metadata_df"] = get_metadata_df(EXAMPLE_DATASET_METADATA_FILE)

        run_plot_and_validate(
            plot_func, kwargs, satb1_config, {"REL-FREE", "RELAPSE"}
        )

    @staticmethod
    def test_single_amino_acid_substitution_end_of_exon(
        plot_func, kwargs, tau_substitution_config
    ):
        # TODO: region names and how they are separated are FUBAR
        kwargs["evidence_df"] = get_evidence_df(TAU_EVIDENCE_FILE_PATH)
        if "metadata_df" in kwargs:
            kwargs["metadata_df"] = get_metadata_df(TAU_METADATA_FILE_PATH)
        kwargs["fasta_file_path"] = TAU_PATH / "uniprotkb_P10636_5_8.fasta"
        kwargs["regions_file_path"] = TAU_REGIONS_FILE_PATH

        run_plot_and_validate(
            plot_func, kwargs, tau_substitution_config, {"AD", "CTR"}
        )

    @staticmethod
    def test_fasta_with_single_sequence(plot_func, kwargs, tau_8_config, tau_5_config):
        # Set up common test data
        kwargs["evidence_df"] = get_evidence_df(TAU_EVIDENCE_FILE_PATH)
        if "metadata_df" in kwargs:
            kwargs["metadata_df"] = get_metadata_df(TAU_METADATA_FILE_PATH)

        # Tau-8
        kwargs["fasta_file_path"] = TAU_PATH / "uniprotkb_P10636_8.fasta"
        kwargs["regions_file_path"] = TAU_REGIONS_FILE_PATH
        run_plot_and_validate(plot_func, kwargs, tau_8_config, {"AD", "CTR"})

        # Tau-5
        kwargs["fasta_file_path"] = TAU_PATH / "uniprotkb_P10636_5.fasta"
        kwargs["regions_file_path"] = TAU_PATH / "regions_P10636_5.csv"
        run_plot_and_validate(plot_func, kwargs, tau_5_config, {"AD", "CTR"})
