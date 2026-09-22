import re

import pandas as pd
import pytest
from tests.paths import TEST_FASTA_PATH, TEST_PEPTIDES_PATH, TEST_PTM_VISUALIZATION_PATH
from tests.protzilla.data_analysis.ptm_visualization.ptm_vis_test_utils import (
    get_evidence_df,
    get_metadata_df,
    mock_settings_file,
)

from backend.protzilla.data_analysis.ptm_visualization.ptm_bar_plot import (
    create_bar_ptm_visualization,
)
from backend.protzilla.data_analysis.ptm_visualization.ptm_details_plot import (
    create_details_ptm_visualization,
)
from backend.protzilla.data_analysis.ptm_visualization.ptm_overview_plot import (
    get_detected_modifications,
)

GFAP_PATH = TEST_PTM_VISUALIZATION_PATH / "P14136"
GFAP_EVIDENCE_FILE_PATH = TEST_PEPTIDES_PATH / "evidence_P14136.txt"
GFAP_FASTA_FILE_PATH = TEST_FASTA_PATH / "uniprotkb_P14136.fasta"
GFAP_REGIONS_FILE_PATH = GFAP_PATH / "regions.csv"
GFAP_METADATA_FILE_PATH = GFAP_PATH / "metadata.csv"
Q_VALUE_THRESHOLD = 0.01

from backend.protzilla.data_analysis.ptm_visualization.ptm_vis_utils import (
    IN_PLOT_COLUMN,
    PTM_LABEL_COLUMN,
    add_group_counts_to_modifications,
    get_ptm_counts_per_group,
)

# Mirrors the layout written by protein_sequencing's preprocessor_helper.write_results:
# a header row of modification ids, three metadata rows (type / label / isoform) and
# then one row per sample holding a binary "was this PTM detected" flag.
MOD_FILE_CONTENT = """ID,Group,Phospho(S)@8_general,Deamidated(R)@153_general,GG(K)@155_general
,,Phospho,Deamidated,GG
,,S8,R153,K155
,,general,general,general
ad1,AD,1,0,1
ad2,AD,1,1,0
ctr1,CTR,0,1,0
"""


@pytest.fixture
def mod_file(tmp_path):
    path = tmp_path / "result_max_quant_mods.csv"
    path.write_text(MOD_FILE_CONTENT)
    return path


class TestGetPTMCountsPerGroup:
    @staticmethod
    def test_counts_samples_in_which_ptm_was_detected(mod_file):
        counts = get_ptm_counts_per_group(mod_file, ["AD", "CTR"])

        phospho = counts[counts[PTM_LABEL_COLUMN] == "S8"].iloc[0]
        assert phospho["AD (n=2)"] == 2
        assert phospho["CTR (n=1)"] == 0

        gg = counts[counts[PTM_LABEL_COLUMN] == "K155"].iloc[0]
        assert gg["AD (n=2)"] == 1
        assert gg["CTR (n=1)"] == 0

    @staticmethod
    def test_column_name_carries_group_size_as_denominator(mod_file):
        counts = get_ptm_counts_per_group(mod_file, ["AD", "CTR"])

        assert "AD (n=2)" in counts.columns
        assert "CTR (n=1)" in counts.columns

    @staticmethod
    def test_deamidated_arginine_is_reported_as_citrullination(mod_file):
        # The plotters rename Deamidated on R to Citrullination, so the counts have to
        # use the same name or they will not join onto the modification table.
        counts = get_ptm_counts_per_group(mod_file, ["AD", "CTR"])

        citrullination = counts[counts[PTM_LABEL_COLUMN] == "R153"].iloc[0]
        assert citrullination["Modification"] == "Citrullination"
        assert citrullination["AD (n=2)"] == 1
        assert citrullination["CTR (n=1)"] == 1

    @staticmethod
    def test_only_requested_groups_get_a_column(mod_file):
        counts = get_ptm_counts_per_group(mod_file, ["AD"])

        assert "AD (n=2)" in counts.columns
        assert not any(column.startswith("CTR") for column in counts.columns)


class TestAddGroupCountsToModifications:
    @pytest.fixture
    def modification_df(self):
        # as produced by get_modification_table(..., include_label=True)
        return pd.DataFrame(
            [
                (8, "S", "Phospho", "general", "S8"),
                (153, "R", "Citrullination", "general", "R153"),
                (155, "K", "GG", "general", "K155"),
            ],
            columns=(
                "Location",
                "Amino Acid",
                "Modification",
                "Isoform",
                PTM_LABEL_COLUMN,
            ),
        )

    @staticmethod
    def test_counts_are_joined_onto_matching_modification_rows(
        modification_df, mod_file
    ):
        result = add_group_counts_to_modifications(
            modification_df, mod_file, groups=["AD", "CTR"], plotted_sites=set()
        )

        gg = result[result["Location"] == 155].iloc[0]
        assert gg["AD (n=2)"] == 1
        assert gg["CTR (n=1)"] == 0

    @staticmethod
    def test_join_uses_the_label_and_not_the_location(modification_df, mod_file):
        # The location of the phospho row is deliberately not the position of its label, to show
        # that the counts are joined via the label the modification file itself carries.
        modification_df.loc[0, "Location"] = 9

        result = add_group_counts_to_modifications(
            modification_df, mod_file, groups=["AD", "CTR"], plotted_sites=set()
        )

        phospho = result[result["Location"] == 9].iloc[0]
        assert phospho["AD (n=2)"] == 2
        assert phospho["CTR (n=1)"] == 0

    @staticmethod
    def test_in_plot_marks_only_the_sites_the_plot_draws(modification_df, mod_file):
        result = add_group_counts_to_modifications(
            modification_df,
            mod_file,
            groups=["AD", "CTR"],
            plotted_sites={
                ("Phospho", "S8", "general"),
                ("Citrullination", "R153", "general"),
            },
        )

        in_plot = dict(zip(result["Location"], result[IN_PLOT_COLUMN]))
        assert in_plot[8]
        assert in_plot[153]
        assert not in_plot[155]

    @staticmethod
    def test_label_join_key_is_not_exposed_in_the_result(modification_df, mod_file):
        result = add_group_counts_to_modifications(
            modification_df, mod_file, groups=["AD"], plotted_sites=set()
        )

        assert PTM_LABEL_COLUMN not in result.columns
        assert len(result) == len(modification_df)
        assert list(result.columns) == [
            "Location",
            "Amino Acid",
            "Modification",
            "Isoform",
            IN_PLOT_COLUMN,
            "AD (n=2)",
        ]


class TestGroupCountsInPlotOutput:
    """
    The group counts are added by the plot methods rather than the calculation method, because only
    the plotters know which sites and groups end up in the figure.
    """

    @staticmethod
    @pytest.fixture(scope="class")
    def base_modification_df():
        return get_detected_modifications(
            get_evidence_df(GFAP_EVIDENCE_FILE_PATH),
            Q_VALUE_THRESHOLD,
            GFAP_FASTA_FILE_PATH,
            GFAP_REGIONS_FILE_PATH,
        )["modification_df"]

    @staticmethod
    @pytest.fixture(scope="class")
    def plot_kwargs():
        return dict(
            psm_df=get_evidence_df(GFAP_EVIDENCE_FILE_PATH),
            evidence_file_q_value_threshold=Q_VALUE_THRESHOLD,
            fasta_file_path=GFAP_FASTA_FILE_PATH,
            regions_file_path=GFAP_REGIONS_FILE_PATH,
            metadata_df=get_metadata_df(GFAP_METADATA_FILE_PATH),
            metadata_column="Group",
        )

    @staticmethod
    @pytest.fixture(
        scope="class",
        params=[create_bar_ptm_visualization, create_details_ptm_visualization],
        ids=["bar", "details"],
    )
    def plot_output(request, plot_kwargs, base_modification_df):
        # the step hands the calculation output to the plot method as "output_<key>"
        return request.param(**plot_kwargs, output_modification_df=base_modification_df)

    @staticmethod
    def test_table_gains_a_count_column_per_plotted_group(plot_output):
        table = plot_output["modification_df"]

        group_names = {
            match.group(1)
            for match in (
                re.fullmatch(r"(.+) \(n=\d+\)", column) for column in table.columns
            )
            if match
        }
        # The groups the plots draw for this dataset. AD and CTR are in the metadata but none of
        # their samples contribute a modification, so they appear in neither plot nor table.
        assert group_names == {"clean", "exon", "old"}

    @staticmethod
    def test_every_detected_modification_is_still_listed(
        plot_output, base_modification_df
    ):
        table = plot_output["modification_df"]

        key_columns = ["Location", "Amino Acid", "Modification", "Isoform"]
        pd.testing.assert_frame_equal(
            table[key_columns].sort_values(by=key_columns).reset_index(drop=True),
            base_modification_df[key_columns]
            .sort_values(by=key_columns)
            .reset_index(drop=True),
        )

    @staticmethod
    def test_modifications_outside_the_plot_are_marked(plot_output):
        table = plot_output["modification_df"]

        assert IN_PLOT_COLUMN in table.columns
        assert table[IN_PLOT_COLUMN].any(), "no modification was marked as plotted"

    @staticmethod
    def test_plotted_modifications_were_detected_in_at_least_one_sample(plot_output):
        # Both plots drop sites that were not detected in any sample of the shown groups, so a
        # plotted site must have a non-zero count somewhere.
        table = plot_output["modification_df"]
        group_columns = [
            column for column in table.columns if re.fullmatch(r".+ \(n=\d+\)", column)
        ]

        plotted = table[table[IN_PLOT_COLUMN]]
        assert (plotted[group_columns].sum(axis=1) > 0).all()

    @staticmethod
    def test_counts_never_exceed_the_group_size(plot_output):
        table = plot_output["modification_df"]

        for column in table.columns:
            match = re.fullmatch(r".+ \(n=(\d+)\)", column)
            if match:
                assert table[column].max() <= int(match.group(1))


class TestModificationsMissingFromTheSettings:
    """
    The plots warn that modifications missing from the settings can be found in the tables section,
    so those modifications have to stay in the table and be marked as not plotted instead.
    """

    @staticmethod
    @pytest.fixture
    def tmp_ptm_settings_dir(tmp_path_factory):
        return tmp_path_factory.mktemp("ptm_settings")

    @staticmethod
    @pytest.mark.parametrize(
        "plot_func",
        [create_bar_ptm_visualization, create_details_ptm_visualization],
        ids=["bar", "details"],
    )
    def test_modifications_outside_the_settings_are_listed_but_not_marked_as_plotted(
        plot_func, tmp_ptm_settings_dir
    ):
        reduced_settings = TEST_PTM_VISUALIZATION_PATH / "ptm_settings_fewer_ptms.yaml"

        with mock_settings_file(reduced_settings, tmp_ptm_settings_dir):
            base_kwargs = dict(
                psm_df=get_evidence_df(GFAP_EVIDENCE_FILE_PATH),
                evidence_file_q_value_threshold=Q_VALUE_THRESHOLD,
                fasta_file_path=GFAP_FASTA_FILE_PATH,
                regions_file_path=GFAP_REGIONS_FILE_PATH,
            )
            table = plot_func(
                **base_kwargs,
                metadata_df=get_metadata_df(GFAP_METADATA_FILE_PATH),
                metadata_column="Group",
                output_modification_df=get_detected_modifications(**base_kwargs)[
                    "modification_df"
                ],
            )["modification_df"]

        # the reduced settings only contain Phospho
        plotted = set(table[table[IN_PLOT_COLUMN]]["Modification"])
        not_plotted = set(table[~table[IN_PLOT_COLUMN]]["Modification"])
        assert plotted == {"Phospho"}
        assert {"Citrullination", "Acetyl", "GG"}.issubset(not_plotted)


class TestPlottingWithoutTheCalculationOutput:
    @staticmethod
    @pytest.mark.parametrize(
        "plot_func",
        [create_bar_ptm_visualization, create_details_ptm_visualization],
        ids=["bar", "details"],
    )
    def test_plot_still_works_and_reports_no_table(plot_func):
        result = plot_func(
            psm_df=get_evidence_df(GFAP_EVIDENCE_FILE_PATH),
            evidence_file_q_value_threshold=Q_VALUE_THRESHOLD,
            fasta_file_path=GFAP_FASTA_FILE_PATH,
            regions_file_path=GFAP_REGIONS_FILE_PATH,
            metadata_df=get_metadata_df(GFAP_METADATA_FILE_PATH),
            metadata_column="Group",
        )

        assert len(result["plots"]) == 1
        assert "modification_df" not in result
