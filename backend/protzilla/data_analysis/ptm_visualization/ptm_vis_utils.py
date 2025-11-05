import csv
import types
from pathlib import Path

import pandas as pd

from main.views_helper import load_settings_from_file
from protein_sequencing.data_preprocessing.max_quant_preprocessor import (
    MaxQuantPreprocessor,
)
from protzilla.constants.paths import (
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
            "FIGURE_ORIENTATION": 1
            if protzilla_ptm_settings["other_settings"]["vertical_orientation"]
            else 0,
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
            "FONT": protzilla_plot_settings["custom_font"]
            if protzilla_plot_settings["custom_font"]
            else protzilla_plot_settings["font"],
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
    groups_file_path: Path | None,
    q_value_threshold: float,
    out_dir: Path,
) -> types.ModuleType:
    preprocessor_config_module = types.ModuleType("preprocessor_config")
    preprocessor_config_module.__dict__.update(
        {
            # General
            "FASTA_FILE": fasta_file_path,
            "GROUPS_CSV": groups_file_path,
            # this is the default path where the tool will save the alignment
            # just change if you want to supply your own alignment
            # CAUTION: the alignment must match with the fasta file
            "ALIGNED_FASTA_FILE": str(out_dir / "aligned.fasta"),
            # MaxQuant
            "THRESHOLD": q_value_threshold,
        }
    )
    return preprocessor_config_module


def get_group_dict_from_csv(groups_file_path: Path) -> dict:
    groups = {}
    with open(groups_file_path, "r") as f:
        csvreader = csv.DictReader(f, delimiter=",")
        assert set(csvreader.fieldnames) >= {"file_name", "group_name", "replicate"}, (
            "Groups file must contain at least the columns 'file_name', 'group_name' and 'replicate' but got "
            f"{csvreader.fieldnames}"
        )
        for row in csvreader:
            # Seems weird. Is weird. But I didn't want to touch the underlying code
            groups[row["group_name"]] = row["group_name"]
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
    evidence_df: pd.DataFrame,
    evidence_file_q_value_threshold: float,
    fasta_file_path: Path,
    regions_file_path: Path,
    groups_file_path: Path | None = None,
) -> tuple[types.ModuleType, Path]:
    out_dir = UPLOAD_PATH / "ptm_tmp"

    config_module = get_general_config_module(regions_file_path, out_dir)
    preprocessor_config_module = get_preprocessor_config_module(
        fasta_file_path=fasta_file_path,
        groups_file_path=groups_file_path,
        q_value_threshold=evidence_file_q_value_threshold,
        out_dir=out_dir,
    )

    MaxQuantPreprocessor(
        config_module, preprocessor_config_module, evidence_df=evidence_df
    )
    return config_module, out_dir
