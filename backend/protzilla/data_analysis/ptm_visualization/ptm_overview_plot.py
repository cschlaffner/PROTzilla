import types
from pathlib import Path

import pandas as pd

from protein_sequencing.overview_plot import OverviewPlotter
from backend.protzilla.data_analysis.ptm_visualization.ptm_vis_utils import (
    preprocess_files,
    get_modification_groups_from_settings,
)


def get_overview_plot_config_module(out_dir: Path) -> types.ModuleType:
    modification_file = out_dir / "result_max_quant_mods.csv"
    modifications_group = get_modification_groups_from_settings()

    plot_config_module = types.ModuleType("plot_config")
    plot_config_module.__dict__.update(
        {
            "MODIFICATIONS_GROUP": modifications_group,
            "INPUT_FILE": modification_file,
            "SEQUENCE_MIN_LINE_LENGTH": 20,
            "SHOW_PLOT": False,
            "SAVE_PLOT": False,
        }
    )
    return plot_config_module


def get_detected_modifications(
    evidence_df: pd.DataFrame,
    evidence_file_q_value_threshold: float,
    fasta_file_path: Path,
    regions_file_path: Path,
) -> dict:
    # Although this function is used by different steps, it is tied to the OverviewPlot and thus is placed in this file
    # Everything else would require a bigger rework of the underlying code.
    config_module, out_dir = preprocess_files(
        evidence_df=evidence_df,
        evidence_file_q_value_threshold=evidence_file_q_value_threshold,
        fasta_file_path=fasta_file_path,
        regions_file_path=regions_file_path,
    )

    plot_config_module = get_overview_plot_config_module(out_dir)
    overview_plotter = OverviewPlotter(
        config=config_module,
        plot_config=plot_config_module,
        input_file=str(fasta_file_path),
        output_path=str(out_dir),
    )

    modifications_by_position = overview_plotter.get_modifications_per_position(
        overview_plotter.plot_config.INPUT_FILE,
        filter_based_on_modifications_group=False,
    )
    modifications_list = [
        (location, mod[0][0], mod[1], mod[3])
        for location, sublist in modifications_by_position.items()
        for mod in sublist
    ]
    modification_df = pd.DataFrame(
        modifications_list,
        columns=("Location", "Amino Acid", "Modification", "Isoform"),
    )
    return dict(modification_df=modification_df)


def create_overview_ptm_visualization(
    evidence_df: pd.DataFrame,
    evidence_file_q_value_threshold: float,
    fasta_file_path: Path,
    regions_file_path: Path,
) -> dict:
    config_module, out_dir = preprocess_files(
        evidence_df=evidence_df,
        evidence_file_q_value_threshold=evidence_file_q_value_threshold,
        fasta_file_path=fasta_file_path,
        regions_file_path=regions_file_path,
    )

    plot_config_module = get_overview_plot_config_module(out_dir)
    overview_plotter = OverviewPlotter(
        config=config_module,
        plot_config=plot_config_module,
        input_file=str(fasta_file_path),
        output_path=str(out_dir),
    )
    fig, messages = overview_plotter.create_overview_plot()

    return dict(plots=[fig], messages=messages)
