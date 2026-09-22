import csv
import shutil
import tempfile
import types
from collections import OrderedDict
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, Iterator

import pandas as pd
from protein_sequencing.data_preprocessing.max_quant_preprocessor import (
    MaxQuantPreprocessor,
)

from backend.main.views_helper import load_settings_from_file
from backend.protzilla.constants.paths import (
    CUSTOM_PLOT_SETTINGS_FILE_STEM,
    CUSTOM_PTM_SETTINGS_FILE_STEM,
    DEFAULT_PLOT_SETTINGS_FILE_STEM,
    DEFAULT_PTM_SETTINGS_FILE_STEM,
    UPLOAD_PATH,
)


def load_regions_from_csv(regions_file_path: Path) -> list:
    regions = []
    with open(regions_file_path, "r") as f:
        csvreader = csv.DictReader(f, delimiter=",")
        assert set(csvreader.fieldnames) >= {
            "name",
            "region_end",
            "group",
            "short_name",
        }, (
            "Regions file must contain at least the columns 'name', 'region_end', 'group' and 'short_name but got "
            f"{csvreader.fieldnames}"
        )
        for row in csvreader:
            regions.append(
                (row["name"], int(row["region_end"]), row["group"], row["short_name"])
            )
    return regions


def convert_settings_mm_size_to_px(size):
    # Convert width/height in mm to px using 300 dpi
    return (size / 25.4) * 300


def get_modifications_dict(full_modifications_dict) -> dict:
    return {k: (v["name"], v["color"]) for k, v in full_modifications_dict.items()}


def get_included_modifications_dict(full_modifications_dict) -> dict:
    return {k: list(v["sites"]) for k, v in full_modifications_dict.items()}


def get_general_config_module(
    regions_file_path: Path, out_dir: Path
) -> types.ModuleType:
    regions = load_regions_from_csv(regions_file_path)

    protzilla_plot_settings = load_settings_from_file(
        file_stem=CUSTOM_PLOT_SETTINGS_FILE_STEM,
        default_file_stem=DEFAULT_PLOT_SETTINGS_FILE_STEM,
    )
    protzilla_ptm_settings = load_settings_from_file(
        file_stem=CUSTOM_PTM_SETTINGS_FILE_STEM,
        default_file_stem=DEFAULT_PTM_SETTINGS_FILE_STEM,
    )

    config_module = types.ModuleType("main_config")
    config_module.__dict__.update(
        {
            # Sequence Settings
            # First sequence is from (1, 44), second from (45, 73) and so on
            # Region Name, Region End, Group, Region Abbreviation
            "REGIONS": regions,
            # Modification Settings
            "MODIFICATION_LEGEND_TITLE": "PTMs",
            "MODIFICATIONS": get_modifications_dict(
                protzilla_ptm_settings["modifications"]
            ),
            "INCLUDED_MODIFICATIONS": get_included_modifications_dict(
                protzilla_ptm_settings["modifications"]
            ),
            # Input Output Settings
            "OUTPUT_FOLDER": out_dir,
            # Plot Settings
            # 0 for horizontal, 1 for vertical, note figure height and width are then automatically swapped
            "FIGURE_ORIENTATION": (
                1
                if protzilla_ptm_settings["other_settings"]["vertical_orientation"]
                else 0
            ),
            "PTMS_TO_HIGHLIGHT": [],  # Unused for now
            "PTM_HIGHLIGHT_LABEL_COLOR": "#cfcfcf",
            # just change width and height to change the size of the figure not the orientation
            "FIGURE_WIDTH": convert_settings_mm_size_to_px(
                protzilla_plot_settings["width"]
            ),
            "FIGURE_HEIGHT": convert_settings_mm_size_to_px(
                protzilla_plot_settings["height"]
            ),
            "FONT_SIZE": protzilla_plot_settings["text_size"],
            # Default Parameters
            "FONT": (
                protzilla_plot_settings["custom_font"]
                if protzilla_plot_settings["custom_font"]
                else protzilla_plot_settings["font"]
            ),
            # Sequence Plot
            "SEQUENCE_PLOT_FONT_SIZE": protzilla_plot_settings["text_size"],
            "SEQUENCE_PLOT_HEIGHT": 50,
            "EXONS_GAP": 10,
            "MIN_EXON_LENGTH": 5,
            "SEQUENCE_REGION_COLORS": protzilla_ptm_settings["color_settings"][
                "sequence_region_colors"
            ],
        }
    )
    return config_module


def get_preprocessor_config_module(
    fasta_file_path: Path,
    q_value_threshold: float,
    out_dir: Path,
) -> types.ModuleType:
    preprocessor_config_module = types.ModuleType("preprocessor_config")
    preprocessor_config_module.__dict__.update(
        {
            # General
            "FASTA_FILE": fasta_file_path,
            # this is the default path where the tool will save the alignment
            # just change if you want to supply your own alignment
            # CAUTION: the alignment must match with the fasta file
            "ALIGNED_FASTA_FILE": str(out_dir / "aligned.fasta"),
            # MaxQuant
            "THRESHOLD": q_value_threshold,
        }
    )
    return preprocessor_config_module


def get_group_dict_from_df(df: pd.DataFrame, group_col: str) -> dict:
    if group_col not in df.columns:
        raise ValueError(
            f"Groups DataFrame must contain the column {group_col} but got {set(df.columns)}"
        )

    # The ordered dict influences the way the groups are ordered in the details plot. This is the easiest way to enable
    # this customization without having to introduce an additional feature.
    groups = OrderedDict()
    # Seems weird. Is weird. But I wanted to keep it consistent with the original version
    for _, row in df.iterrows():
        groups[str(row[group_col])] = str(row[group_col])
    return groups


def get_modification_groups_from_settings(
    file_stem: str = CUSTOM_PTM_SETTINGS_FILE_STEM,
    default_file_stem: str = DEFAULT_PTM_SETTINGS_FILE_STEM,
) -> dict:
    modification_settings = load_settings_from_file(
        file_stem=file_stem,
        default_file_stem=default_file_stem,
    )["modifications"]

    return {k: v["above_below"] for k, v in modification_settings.items()}


def preprocess_files(
    psm_df: pd.DataFrame,
    evidence_file_q_value_threshold: float,
    fasta_file_path: Path,
    regions_file_path: Path,
    metadata_df: pd.DataFrame | None = None,
    metadata_column: str | None = None,
) -> tuple[types.ModuleType, Path]:
    out_dir = UPLOAD_PATH / "ptm_tmp"

    config_module = get_general_config_module(regions_file_path, out_dir)
    preprocessor_config_module = get_preprocessor_config_module(
        fasta_file_path=fasta_file_path,
        q_value_threshold=evidence_file_q_value_threshold,
        out_dir=out_dir,
    )

    MaxQuantPreprocessor(
        config_module,
        preprocessor_config_module,
        evidence_df=psm_df,
        metadata_df=metadata_df,
        metadata_column=metadata_column,
    )
    return config_module, out_dir


# The modification file written by protein_sequencing's preprocessor_helper.write_results starts
# with three metadata rows (modification type, label and isoform) before the per-sample rows.
MOD_FILE_HEADER_ROWS = 3
# Internal join key, holding the raw label of a modification site (e.g. "S199"). Dropped again
# before the table is handed to the front-end.
PTM_LABEL_COLUMN = "_ptm_label"
IN_PLOT_COLUMN = "In Plot"
MODIFICATION_TABLE_COLUMNS = ("Location", "Amino Acid", "Modification", "Isoform")
MODIFICATION_KEY_COLUMNS = ("Modification", PTM_LABEL_COLUMN, "Isoform")


def resolve_modification_type(modification_type: str, amino_acid: str) -> str:
    """
    Applies the same renaming that the plotters apply when they read the modification file (see
    OverviewPlotter.get_modifications_per_position). It is just a quirk that Deamidation and
    Citrullination are treated as the same modification type in some contexts. Without
    remapping, counts would not join onto the modification table for citrullinated sites.
    """
    if amino_acid == "R" and modification_type == "Deamidated":
        return "Citrullination"
    return modification_type


def read_modification_file(mod_file: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Splits the modification file into its metadata header rows and its per-sample rows."""
    df = pd.read_csv(mod_file, dtype={"ID": str, "Group": str})
    return df.iloc[:MOD_FILE_HEADER_ROWS], df.iloc[MOD_FILE_HEADER_ROWS:]


def group_count_column_name(group: str, group_size: int) -> str:
    # The group size is part of the name so that the fraction the plots actually draw
    # (count / group size) can be read off the table.
    return f"{group} (n={group_size})"


def get_ptm_counts_per_group(mod_file: Path, groups: Iterable[str]) -> pd.DataFrame:
    """
    Counts, per group, in how many samples each modification site was detected.

    The modification file holds one binary "was this PTM detected" flag per sample and site, so
    summing over a group yields the number of samples of that group in which the PTM was seen.

    :param mod_file: the modification file written by the preprocessor
    :param groups: the groups to create count columns for, in the order they should appear
    :return: a DataFrame with the columns "Modification", PTM_LABEL_COLUMN and "Isoform" plus one
        count column per group
    """
    header, samples = read_modification_file(mod_file)
    modification_columns = [
        column for column in header.columns if column not in ("ID", "Group")
    ]

    counts = pd.DataFrame(
        {
            "Modification": [
                resolve_modification_type(
                    header[column].iloc[0], header[column].iloc[1][0]
                )
                for column in modification_columns
            ],
            PTM_LABEL_COLUMN: [
                header[column].iloc[1] for column in modification_columns
            ],
            "Isoform": [header[column].iloc[2] for column in modification_columns],
        }
    )

    group_sizes = samples["Group"].value_counts()
    detected_per_group = (
        samples[modification_columns].astype(int).groupby(samples["Group"]).sum()
    )
    for group in groups:
        column_name = group_count_column_name(group, int(group_sizes.get(group, 0)))
        if group in detected_per_group.index:
            counts[column_name] = (
                detected_per_group.loc[group, modification_columns].astype(int).values
            )
        else:
            counts[column_name] = 0

    return counts


def add_group_counts_to_modifications(
    modification_df: pd.DataFrame,
    mod_file: Path,
    groups: Iterable[str],
    plotted_sites: set[tuple[str, str, str]],
) -> pd.DataFrame:
    """
    Adds an "In Plot" marker and one sample-count column per group to a modification table.

    The join runs on the modification label (e.g. "S8") instead of the reported location, because
    the location depends on the exon offsets of the plotter that produced the table, while the
    label is taken verbatim from the modification file.

    :param modification_df: a table as produced by get_modification_table(include_label=True)
    :param mod_file: the modification file written by the preprocessor
    :param groups: the groups the plot shows, in the order they should appear
    :param plotted_sites: the (modification, label, isoform) triples the plot actually draws
    :return: the table with the additional columns and without the internal label column
    """
    counts = get_ptm_counts_per_group(mod_file, groups)
    group_columns = [
        column for column in counts.columns if column not in MODIFICATION_KEY_COLUMNS
    ]
    counts[IN_PLOT_COLUMN] = [
        (modification, label, isoform) in plotted_sites
        for modification, label, isoform in zip(
            counts["Modification"], counts[PTM_LABEL_COLUMN], counts["Isoform"]
        )
    ]

    merged = modification_df.merge(
        counts, on=list(MODIFICATION_KEY_COLUMNS), how="left"
    )
    merged[IN_PLOT_COLUMN] = merged[IN_PLOT_COLUMN].fillna(False).astype(bool)
    merged[group_columns] = merged[group_columns].fillna(0).astype(int)

    displayed_columns = [
        column for column in modification_df.columns if column != PTM_LABEL_COLUMN
    ]
    return merged[[*displayed_columns, IN_PLOT_COLUMN, *group_columns]]


def get_plotted_sites_from_positions(
    modification_sites_by_position: dict,
) -> set[tuple[str, str, str]]:
    """Extracts the plotted (modification, label, isoform) triples from a BarPlotter filter result."""
    return {
        (resolve_modification_type(site[1], site[0][0]), site[0], site[3])
        for sites in modification_sites_by_position.values()
        for site in sites
    }


def get_plotted_sites_from_columns(
    filtered_df: pd.DataFrame,
) -> set[tuple[str, str, str]]:
    """Extracts the plotted (modification, label, isoform) triples from a DetailsPlotter filter result."""
    return {
        (
            resolve_modification_type(
                filtered_df[column].iloc[0], filtered_df[column].iloc[1][0]
            ),
            filtered_df[column].iloc[1],
            filtered_df[column].iloc[2],
        )
        for column in filtered_df.columns
        if column not in ("ID", "Group")
    }


@contextmanager
def preserve_modification_file(modification_file: Path) -> Iterator[Path]:
    """
    Yields a copy of the modification file that survives plotting.

    The plotters wipe their whole output directory once the figure is finished (see
    Plotter.finalize_plotting -> Plotter.clean_up), so the modification file is gone by the time
    the plot has been created. The copy lets the group counts be derived afterwards, which is
    required for the details plot because its position offsets only exist once it has been plotted.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        preserved_file = Path(tmp_dir) / Path(modification_file).name
        shutil.copyfile(modification_file, preserved_file)
        yield preserved_file
