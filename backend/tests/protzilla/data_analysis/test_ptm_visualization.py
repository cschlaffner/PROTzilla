import shutil
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Any
from unittest import mock

import pandas as pd
import pytest
from _pytest.monkeypatch import MonkeyPatch

import main
from protzilla.constants.intensity_types import IntensityType
from protzilla.constants.paths import EXAMPLE_DATASET_METADATA_FILE
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
            # TODO
            # regions_file_path=GFAP_REGIONS_FILE_PATH,
            regions_file_path=Path(
                "/home/hendraet/stud_sync/Studium/phd/proteomics/PROTzilla/backend/tests/test_data/ptm_visualization_data/P14136/regions_new.csv"
            ),
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


def validate_plot_outputs(
    plot,
    plot_func,
    all_groups: set,
    required_groups: set,
    validation_config: Optional[PlotValidationConfig],
):
    # TODO: maybe we have to soften the set-constraint and check that soem strings only appear once
    all_layout_strings = {anno.text for anno in plot.layout.annotations if anno.text}
    all_data_strings = {
        subplot.text
        for subplot in plot.data
        if hasattr(subplot, "mode") and subplot.mode == "text"
    }
    all_plot_strings = all_layout_strings.union(all_data_strings)

    assert set(validation_config.required_ptm_types).issubset(all_plot_strings)
    assert set(validation_config.required_ptms).issubset(all_plot_strings)
    assert set(validation_config.required_region_names).issubset(all_plot_strings)

    if plot_func in (create_details_ptm_visualization, create_bar_ptm_visualization):
        required_groups = set(required_groups)
        assert required_groups.issubset(all_plot_strings)
        excluded_groups = all_groups - required_groups
        assert all(g not in all_plot_strings for g in excluded_groups)

    if plot_func == create_details_ptm_visualization:
        assert set(validation_config.required_cleavages).issubset(all_plot_strings)
        assert set(validation_config.required_region_short_names).issubset(
            all_plot_strings
        )

    assert all(s not in all_plot_strings for s in validation_config.excluded_strings)


@contextmanager
def mock_settings_file(new_settings_file_path: Path, tmp_dir: Path):
    shutil.copytree(main.views_helper.SETTINGS_PATH, tmp_dir, dirs_exist_ok=True)
    shutil.copy(new_settings_file_path, tmp_dir)
    with (
        # Mocking is a bit more difficult because the values of default arguments are not overwritten once a function
        # is imported, so it would not be enough just to overwrite SETTINGS_PATH
        mock.patch.object(
            main.views_helper.load_settings_from_file,
            "__defaults__",
            (
                main.views_helper.load_settings_from_file.__defaults__[0],
                tmp_dir.resolve(),
            ),
        ),
        mock.patch.object(
            ptm_vis_utils,
            "CUSTOM_PTM_SETTINGS_FILE_STEM",
            new_settings_file_path.stem,
        ),
    ):
        yield


def mock_ptms_at_all_positions(
    peptide_blueprint: pd.Series,
    sequence: str,
    exon: str | None = None,
    peptide_length: int = 7,
    protein_id: str | None = None,
) -> list[Any]:
    peptides = []
    for i in range(0, len(sequence), peptide_length):
        peptide = sequence[i : i + peptide_length]
        peptides.append(peptide)
    if exon is not None:
        for i in range(0, len(exon), peptide_length):
            peptide = exon[i : i + peptide_length]
            peptides.append(peptide)

    mock_peptides = []
    for peptide in peptides:
        mod_seq = f"_{peptide}_"
        for i in range(1, len(mod_seq) - 1):
            mock_peptide = peptide_blueprint.copy()
            mock_peptide["Sequence"] = peptide
            mod_seq_start = mod_seq[: i + 1]
            mod_seq_end = mod_seq[i + 1 :]
            new_mod_seq = f"{mod_seq_start}(ci){mod_seq_end}"
            mock_peptide["Modified sequence"] = new_mod_seq
            mock_peptide["Modifications"] = "ci"
            if protein_id is not None:
                mock_peptide["Protein ID"] = protein_id
            mock_peptides.append(mock_peptide)
    return mock_peptides


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
    def tau_casette_exon_config(self):
        return PlotValidationConfig(
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
            required_region_short_names=(),
            required_cleavages=(),
        )

    @pytest.fixture
    def tau_substitution_config(self, tau_casette_exon_config):
        return PlotValidationConfig(
            required_ptm_types=("Phosphorylation", "Ubiquitination", "Acetylation"),
            required_ptms=("S113", "K305", "K311", "K317", "K321"),
            required_region_names=tau_casette_exon_config.required_region_names,
            required_region_short_names=(),
            required_cleavages=("306",),
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

    # TODO: would our way of region files even work if alternative exons have the exact same length?
    @staticmethod
    def test_plotting_functions(plot_func, kwargs, gfap_config):
        #######################################
        # TODO: continue fixing the migration of the regions file. Currently, sth is broken
        result = plot_func(**kwargs)
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
            validation_config=gfap_config,
        )

    @staticmethod
    def test_plotting_functions_vertical_orientation(
        plot_func, kwargs, monkeypatch, gfap_config
    ):
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
            validation_config=gfap_config,
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
    def test_different_metadata_column(plot_func, bar_detail_kwargs, gfap_config):
        metadata_df = bar_detail_kwargs["metadata_df"]
        bar_detail_kwargs["metadata_column"] = "Batch"
        result = plot_func(**bar_detail_kwargs)
        assert len(result["plots"]) == 1
        validate_plot_outputs(
            result["plots"][0],
            create_bar_ptm_visualization,
            all_groups=set(metadata_df[bar_detail_kwargs["metadata_column"]].unique()),
            required_groups={"2", "3", "4"},
            validation_config=gfap_config,
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
    def test_cassette_exon(plot_func, kwargs, tau_casette_exon_config):
        kwargs["evidence_df"] = get_evidence_df(TAU_EVIDENCE_FILE_PATH)
        if "metadata_df" in kwargs:
            kwargs["metadata_df"] = get_metadata_df(TAU_METADATA_FILE_PATH)
        kwargs["fasta_file_path"] = Path(TAU_PATH / "uniprotkb_P10636_7_8.fasta")
        kwargs["regions_file_path"] = TAU_REGIONS_FILE_PATH

        sequence = "MAEPRQEFEVMEDHAGTYGLGDRKDQGGYTMHQDQEGDTDAGLKESPLQTPTEDGSEEPGSETSDAKSTPTAEAEEAGIGDTPSLEDEAAGHVTQARMVSKSKDGTGSDDKKAKGADGKTKIATPRGAAPPGQKGQANATRIPAKTPPAPKTPPSSGEPPKSGDRSGYSSPGSPGTPGSRSRTPSLPTPPTREPKKVAVVRTPPKSPSSAKSRLQTAPVPMPDLKNVKSKIGSTENLKHQPGGGKVQIINKKLDLSNVQSKCGSKDNIKHVPGGGSVQIVYKPVDLSKVTSKCGSLGNIHHKPGGGQVEVKSEKLDFKDRVQSKIGSLDNITHVPGGGNKKIETHKLTFRENAKAKTDHGAEIVYKSPVVSGDTSPRHLSNVSSTGSIDMVDSPQLATLADEVSASLAKQGL"
        peptide_blueprint = kwargs["evidence_df"].iloc[93]
        mock_peptides = mock_ptms_at_all_positions(
            peptide_blueprint, sequence, protein_id="P10636-7"
        )

        kwargs["evidence_df"] = pd.concat(
            [kwargs["evidence_df"], pd.DataFrame(mock_peptides)],
            ignore_index=True,
        )

        result = plot_func(**kwargs)
        assert len(result["plots"]) == 1
        plot = result["plots"][0]
        # TODO: remove
        plot.show()

        # TODO: we need more checks that we don't plot more regions than actually present
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
            validation_config=tau_casette_exon_config,
        )

    @staticmethod
    def test_modification_at_first_location(
        plot_func, kwargs, tmp_ptm_settings_dir, gfap_config
    ):
        # TODO: reformat a bit.
        sequence = "MERRRITSAARRSYVSSGEMMVGGLAPGRRLGPGTRLSLARMPPPLPTRVDFSLAGALNAGFKETRASERAEMMELNDRFASYIEKVRFLEQQNKALAAELNQLRAKEPTKLADVYQAELRELRLRLDQLTANSARLEVERDNLAQDLATVRQKLQDETNLRLEAENNLAAYRQEADEATLARLDLERKIESLEEEIRFLRKIHEEEVRELQEQLARQQVHVELDVAKPDLTAALKEIRTQYEAMASSNMHEAEEWYRSKFADLTDAAARNAELLRQAKHEANDYRRQLQSLTCDLESLRGTNESLERQMREQEERHVREAASYQEALARLEEEGQSLKDEMARHLQEYQDLLNVKLALDIEIATYRKLLEGEENRITIPVQTFSNLQIRETSLDTKSVSEGHLKRNIVVKTVEMRDGEVIKESKQEHKDVM"
        exon = "GGKSTKDGENHKVTRYLKSLTIRVIPIQAHQIVNGTPPARG"
        peptide_blueprint = kwargs["evidence_df"].iloc[97]

        mock_peptides = mock_ptms_at_all_positions(peptide_blueprint, sequence, exon)

        kwargs["evidence_df"] = pd.concat(
            [kwargs["evidence_df"], pd.DataFrame(mock_peptides)],
            ignore_index=True,
        )

        # TODO: maybe go completely overboard and see what happens if we have modifications on all locations
        # mock_start_peptide = kwargs["evidence_df"].iloc[97]
        # mock_start_peptide["Modified sequence"] = (
        #     "_(Oxidation (Protein N-term))M(ci)ERRRIT_"
        # )
        # mock_start_peptide["Modifications"] = "Oxidation (Protein N-term); ci"
        # kwargs["evidence_df"] = pd.concat(
        #     [kwargs["evidence_df"], pd.DataFrame([mock_start_peptide])],
        #     ignore_index=True,
        # )
        #
        # mock_exon1_peptide = kwargs["evidence_df"].iloc[97]
        # mock_exon1_peptide["Sequence"] = "ETSLDT"
        # mock_exon1_peptide["Modified sequence"] = "_E(ci)TSLDT_"
        # mock_exon1_peptide["Modifications"] = "ci"
        # kwargs["evidence_df"] = pd.concat(
        #     [kwargs["evidence_df"], pd.DataFrame([mock_exon1_peptide])],
        #     ignore_index=True,
        # )
        # # TODO: Maybe just export the final df instead of all this mocking
        # mock_exon1_end_peptide = kwargs["evidence_df"].iloc[97]
        # mock_exon1_end_peptide["Sequence"] = "KQEHKDVM"
        # mock_exon1_end_peptide["Modified sequence"] = "_KQEHKDVM(ci)_"
        # mock_exon1_end_peptide["Modifications"] = "ci"
        # kwargs["evidence_df"] = pd.concat(
        #     [kwargs["evidence_df"], pd.DataFrame([mock_exon1_end_peptide])],
        #     ignore_index=True,
        # )
        #
        # mock_exon2_peptide = kwargs["evidence_df"].iloc[97]
        # mock_exon2_peptide["Sequence"] = "GGKST"
        # mock_exon2_peptide["Modified sequence"] = "_G(ci)GKST_"
        # mock_exon2_peptide["Modifications"] = "ci"
        # kwargs["evidence_df"] = pd.concat(
        #     [kwargs["evidence_df"], pd.DataFrame([mock_exon2_peptide])],
        #     ignore_index=True,
        # )
        # mock_exon2_peptide = kwargs["evidence_df"].iloc[97]
        # mock_exon2_peptide["Sequence"] = "GGKST"
        # mock_exon2_peptide["Modified sequence"] = "_GG(ci)KST_"
        # mock_exon2_peptide["Modifications"] = "ci"
        # kwargs["evidence_df"] = pd.concat(
        #     [kwargs["evidence_df"], pd.DataFrame([mock_exon2_peptide])],
        #     ignore_index=True,
        # )
        #
        # # TODO: can we somehow test the locations or the visual soundness?
        # mock_pre_exon_peptide = kwargs["evidence_df"].iloc[97]
        # mock_pre_exon_peptide["Sequence"] = "TFSNLQIR"
        # mock_pre_exon_peptide["Modified sequence"] = "_TFSNLQIR(GG (R))_"
        # mock_pre_exon_peptide["Modifications"] = "GG (R)"
        # kwargs["evidence_df"] = pd.concat(
        #     [kwargs["evidence_df"], pd.DataFrame([mock_pre_exon_peptide])],
        #     ignore_index=True,
        # )
        # mock_pre_exon_peptide = kwargs["evidence_df"].iloc[97]
        # mock_pre_exon_peptide["Sequence"] = "TFSNLQIR"
        # mock_pre_exon_peptide["Modified sequence"] = "_TFSNLQI(GG (I))R_"
        # mock_pre_exon_peptide["Modifications"] = "GG (I)"
        # kwargs["evidence_df"] = pd.concat(
        #     [kwargs["evidence_df"], pd.DataFrame([mock_pre_exon_peptide])],
        #     ignore_index=True,
        # )
        # mock_pre_exon_peptide = kwargs["evidence_df"].iloc[97]
        # mock_pre_exon_peptide["Sequence"] = "TFSNLQIR"
        # mock_pre_exon_peptide["Modified sequence"] = "_TFSNLQ(GG (Q))IR_"
        # mock_pre_exon_peptide["Modifications"] = "GG (Q)"
        # kwargs["evidence_df"] = pd.concat(
        #     [kwargs["evidence_df"], pd.DataFrame([mock_pre_exon_peptide])],
        #     ignore_index=True,
        # )
        #
        # mock_sequence_end_peptide = kwargs["evidence_df"].iloc[97]
        # mock_sequence_end_peptide["Sequence"] = "GTPPARG"
        # mock_sequence_end_peptide["Modified sequence"] = "_GTPPARG(ci)_"
        # mock_sequence_end_peptide["Modifications"] = "ci"
        # kwargs["evidence_df"] = pd.concat(
        #     [kwargs["evidence_df"], pd.DataFrame([mock_sequence_end_peptide])],
        #     ignore_index=True,
        # )

        # TODO: why do we have a split in Pre-Exon region?
        with mock_settings_file(
            TEST_PTM_VISUALIZATION_PATH / "ptm_settings_mods_at_first_location.yaml",
            tmp_ptm_settings_dir,
        ):
            result = plot_func(**kwargs)
            assert len(result["plots"]) == 1
            plot = result["plots"][0]
            # TODO: remove
            plot.show()

            additional_required_ptms = ("M1", "G391", "E391")
            additional_excluded_strings = ("M0",)
            gfap_config.required_ptms += additional_required_ptms
            gfap_config.excluded_strings += additional_excluded_strings
            gfap_config.required_region_short_names += ("α",)

            # TODO: reuse
            # validate_plot_outputs(
            #     plot,
            #     plot_func,
            #     all_groups=(
            #         set(kwargs["metadata_df"]["Group"].unique())
            #         if "metadata_df" in kwargs
            #         else set()
            #     ),
            #     required_groups={"clean", "old", "exon"},
            #     validation_config=gfap_config,
            # )

    @staticmethod
    def test_single_amino_acid_substitution_start_of_exon(
        plot_func, kwargs, satb1_config
    ):
        kwargs["evidence_df"] = get_evidence_df(SATB1_EVIDENCE_FILE_PATH)
        kwargs["fasta_file_path"] = SATB1_FASTA_FILE_PATH
        kwargs["regions_file_path"] = SATB1_REGIONS_FILE_PATH
        if "metadata_df" in kwargs:
            kwargs["metadata_df"] = get_metadata_df(EXAMPLE_DATASET_METADATA_FILE)

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
            required_groups={"REL-FREE", "RELAPSE"},
            validation_config=satb1_config,
        )

    @staticmethod
    def test_single_amino_acid_substitution_end_of_exon(
        plot_func, kwargs, tau_substitution_config
    ):
        kwargs["evidence_df"] = get_evidence_df(TAU_EVIDENCE_FILE_PATH)
        if "metadata_df" in kwargs:
            kwargs["metadata_df"] = get_metadata_df(TAU_METADATA_FILE_PATH)
        kwargs["fasta_file_path"] = TAU_PATH / "uniprotkb_P10636_5_8.fasta"
        kwargs["regions_file_path"] = TAU_REGIONS_FILE_PATH

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
            required_groups=(
                {"AD", "CTR"}
                if plot_func == create_details_ptm_visualization
                else {"AD"}
            ),
            validation_config=tau_substitution_config,
        )
