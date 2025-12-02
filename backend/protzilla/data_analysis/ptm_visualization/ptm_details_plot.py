import itertools
import types
from pathlib import Path

import pandas as pd

from main.views_helper import load_settings_from_file
from protein_sequencing.details_plot import DetailsPlotter
from protzilla.constants.colors import PLOT_COLOR_SEQUENCE
from protzilla.constants.paths import (
    CUSTOM_PTM_SETTINGS_FILE_STEM,
    DEFAULT_PTM_SETTINGS_FILE_STEM,
)
from protzilla.data_analysis.ptm_visualization.ptm_vis_utils import (
    get_group_dict_from_csv,
    preprocess_files,
)


def get_details_plot_config_module(
    groups_file_path: Path, out_dir: Path
) -> types.ModuleType:
    modification_file = out_dir / "result_max_quant_mods.csv"
    cleavage_file = out_dir / "result_max_quant_cleavages.csv"

    settings = load_settings_from_file(
        file_stem=CUSTOM_PTM_SETTINGS_FILE_STEM,
        default_file_stem=DEFAULT_PTM_SETTINGS_FILE_STEM,
    )
    color_settings = settings["color_settings"]

    groups = get_group_dict_from_csv(groups_file_path)
    try:
        missing_groups = set(groups.keys()) - set(
            color_settings["group_label_colors"].keys()
        )
        given_color_dict = {
            k: ([v], color_settings["group_label_colors"][k])
            for k, v in groups.items()
            if k not in missing_groups
        }
        fallback_dict = {k: v for k, v in groups.items() if k in missing_groups}
        fallback_color_dict = {
            k: ([v], color)
            for (k, v), color in zip(
                fallback_dict.items(), itertools.cycle(PLOT_COLOR_SEQUENCE)
            )
        }
        details_groups = {**given_color_dict, **fallback_color_dict}
    except:
        raise ValueError(
            "Not all groups in the provided groups file have a corresponding label colour defined in the settings. "
            "Couldn't use default colour cycle as fallback. Please provide colors for all group labels in the "
            "'PTM Visualization' settings.."
        )

    if len(details_groups) == 0:
        raise ValueError(
            "No groups found in the provided groups file for details plot visualization."
        )

    plot_config_module = types.ModuleType("plot_config")
    plot_config_module.__dict__.update(
        {
            # Details plot settings
            "MODIFICATION_THRESHOLD": 1,
            "INPUT_FILES": {
                "B": ("Cleavage", cleavage_file),
                "A": ("PTM", modification_file),
            },
            "CLEAVAGES_TO_HIGHLIGHT": [],
            "CLEAVAGE_HIGHLIGHT_COLOR": "#ff0000",
            "CLEAVAGE_LABEL_COLOR": color_settings["cleavage_label_color"],
            "CLEAVAGE_SCALE_COLOR_LOW": color_settings["cleavage_scale_color_low"],
            "CLEAVAGE_SCALE_COLOR_MID": color_settings["cleavage_scale_color_mid"],
            "CLEAVAGE_SCALE_COLOR_HIGH": color_settings["cleavage_scale_color_high"],
            "CLEAVAGE_LEGEND_TITLE": "Proteolytic<br>Cleavage<br>Frequency",
            "PTM_SCALE_COLOR_LOW": color_settings["ptm_scale_color_low"],
            "PTM_SCALE_COLOR_MID": color_settings["ptm_scale_color_mid"],
            "PTM_SCALE_COLOR_HIGH": color_settings["ptm_scale_color_high"],
            "PTM_LEGEND_TITLE": "PTM <br>Frequency",
            "GROUPS": details_groups,
            "PTM_RECT_LENGTH": 25,
            "REGION_LABEL_ANGLE_GROUPS": settings["other_settings"]["label_angle"],
            "SHOW_PLOT": False,
            "SAVE_PLOT": False,
        }
    )
    return plot_config_module


def create_details_ptm_visualization(
    evidence_df: pd.DataFrame,
    evidence_file_q_value_threshold: float,
    fasta_file_path: Path,
    regions_file_path: Path,
    groups_file_path: Path,
) -> dict:
    config_module, out_dir = preprocess_files(
        evidence_df=evidence_df,
        evidence_file_q_value_threshold=evidence_file_q_value_threshold,
        fasta_file_path=fasta_file_path,
        regions_file_path=regions_file_path,
        groups_file_path=groups_file_path,
    )

    plot_config_module = get_details_plot_config_module(groups_file_path, out_dir)
    plotter = DetailsPlotter(
        config=config_module,
        plot_config=plot_config_module,
        input_file=str(fasta_file_path),
        output_path=str(out_dir),
    )
    fig, messages = plotter.create_details_plot()

    return dict(plots=[fig], messages=messages)
