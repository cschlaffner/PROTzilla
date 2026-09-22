import types
from pathlib import Path

import pandas as pd
from protein_sequencing.bar_plot import BarPlotter

from backend.protzilla.data_analysis.ptm_visualization.ptm_overview_plot import (
    get_modification_table,
)
from backend.protzilla.data_analysis.ptm_visualization.ptm_vis_utils import (
    add_group_counts_to_modifications,
    get_group_dict_from_df,
    get_modification_groups_from_settings,
    get_plotted_sites_from_positions,
    preprocess_files,
    preserve_modification_file,
)


def get_bar_plot_config_module(
    metadata_df: pd.DataFrame, metadata_col: str, out_dir: Path
) -> types.ModuleType:
    modification_file = out_dir / "result_max_quant_mods.csv"
    bar_groups = get_group_dict_from_df(metadata_df, metadata_col)

    modifications_group = get_modification_groups_from_settings()

    if len(bar_groups) == 0:
        raise ValueError(
            "No groups found in the provided groups file for bar plot visualization."
        )
    plot_config_module = types.ModuleType("plot_config")
    plot_config_module.__dict__.update(
        {
            "MODIFICATIONS_GROUP": modifications_group,
            "BAR_GROUPS": bar_groups,
            "BAR_WIDTH": 0.8,
            "INVERT_AXIS_GROUP_B": True,
            "BAR_INPUT_FILE": modification_file,
            "SHOW_PLOT": False,
            "SAVE_PLOT": False,
        }
    )
    return plot_config_module


def _get_modification_table_with_group_counts(
    config_module: types.ModuleType,
    out_dir: Path,
    fasta_file_path: Path,
    modification_file: Path,
    bar_plotter: BarPlotter,
    plot_config_module: types.ModuleType,
) -> pd.DataFrame:
    # Re-running the filter is cheap (it only reads the modification file) and guarantees that the
    # table reports exactly the sites and groups the bar plot just drew.
    _, plotted_sites_by_position, filtered_df = (
        bar_plotter.filter_relevant_modification_sites(modification_file)
    )
    shown_groups = [
        group
        for group in plot_config_module.BAR_GROUPS
        if group in filtered_df["Group"].dropna().unique()
    ]

    modification_df = get_modification_table(
        config_module=config_module,
        out_dir=out_dir,
        fasta_file_path=fasta_file_path,
        mod_file=modification_file,
        include_label=True,
    )
    return add_group_counts_to_modifications(
        modification_df,
        modification_file,
        groups=shown_groups,
        plotted_sites=get_plotted_sites_from_positions(plotted_sites_by_position),
    )


# --8<-- [start:create_bar_ptm_visualization]
def create_bar_ptm_visualization(
    psm_df: pd.DataFrame,
    evidence_file_q_value_threshold: float,
    fasta_file_path: Path,
    regions_file_path: Path,
    metadata_df: pd.DataFrame,
    metadata_column: str,
    output_modification_df: pd.DataFrame | None = None,
) -> dict:
    config_module, out_dir = preprocess_files(
        psm_df=psm_df,
        evidence_file_q_value_threshold=evidence_file_q_value_threshold,
        fasta_file_path=fasta_file_path,
        regions_file_path=regions_file_path,
        metadata_df=metadata_df,
        metadata_column=metadata_column,
    )

    plot_config_module = get_bar_plot_config_module(
        metadata_df, metadata_column, out_dir
    )
    bar_plotter = BarPlotter(
        config=config_module,
        plot_config=plot_config_module,
        input_file=str(fasta_file_path),
        output_path=str(out_dir),
    )
    with preserve_modification_file(
        plot_config_module.BAR_INPUT_FILE
    ) as modification_file:
        fig, messages = bar_plotter.create_bar_plot()

        outputs = dict(plots=[fig], messages=messages)
        if output_modification_df is not None:
            outputs["modification_df"] = _get_modification_table_with_group_counts(
                config_module=config_module,
                out_dir=out_dir,
                fasta_file_path=fasta_file_path,
                modification_file=modification_file,
                bar_plotter=bar_plotter,
                plot_config_module=plot_config_module,
            )
    return outputs


# --8<-- [end:create_bar_ptm_visualization]
