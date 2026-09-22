import types
from pathlib import Path

import pandas as pd
from protein_sequencing.overview_plot import OverviewPlotter

from backend.protzilla.data_analysis.ptm_visualization.ptm_vis_utils import (
    MODIFICATION_TABLE_COLUMNS,
    PTM_LABEL_COLUMN,
    get_modification_groups_from_settings,
    preprocess_files,
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


def get_modification_table(
    config_module: types.ModuleType,
    out_dir: Path,
    fasta_file_path: Path,
    mod_file: Path,
    include_label: bool = False,
) -> pd.DataFrame:
    """
    Builds the table of all modifications detected in the modification file.

    Although this function is used by different steps, it is tied to the OverviewPlot and thus is
    placed in this file. Everything else would require a bigger rework of the underlying code.

    :param include_label: whether to keep the internal label column (e.g. "S8"), which the group
        aware plots use to join their sample counts onto the table
    """
    plot_config_module = get_overview_plot_config_module(out_dir)
    overview_plotter = OverviewPlotter(
        config=config_module,
        plot_config=plot_config_module,
        input_file=str(fasta_file_path),
        output_path=str(out_dir),
    )

    modifications_by_position = overview_plotter.get_modifications_per_position(
        mod_file,
        filter_based_on_modifications_group=False,
    )
    modifications_list = [
        (location, mod[0][0], mod[1], mod[3], mod[0])
        for location, sublist in modifications_by_position.items()
        for mod in sublist
    ]
    modification_df = pd.DataFrame(
        modifications_list,
        columns=(*MODIFICATION_TABLE_COLUMNS, PTM_LABEL_COLUMN),
    )
    if include_label:
        return modification_df
    return modification_df.drop(columns=[PTM_LABEL_COLUMN])


def get_detected_modifications(
    psm_df: pd.DataFrame,
    evidence_file_q_value_threshold: float,
    fasta_file_path: Path,
    regions_file_path: Path,
) -> dict:
    config_module, out_dir = preprocess_files(
        psm_df=psm_df,
        evidence_file_q_value_threshold=evidence_file_q_value_threshold,
        fasta_file_path=fasta_file_path,
        regions_file_path=regions_file_path,
    )

    modification_df = get_modification_table(
        config_module=config_module,
        out_dir=out_dir,
        fasta_file_path=fasta_file_path,
        mod_file=out_dir / "result_max_quant_mods.csv",
    )
    return dict(modification_df=modification_df)


# --8<-- [start:create_overview_ptm_visualization]
def create_overview_ptm_visualization(
    psm_df: pd.DataFrame,
    evidence_file_q_value_threshold: float,
    fasta_file_path: Path,
    regions_file_path: Path,
) -> dict:
    config_module, out_dir = preprocess_files(
        psm_df=psm_df,
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


# --8<-- [end:create_overview_ptm_visualization]
