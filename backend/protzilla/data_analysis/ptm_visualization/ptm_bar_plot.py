import types
from pathlib import Path

import pandas as pd

from protein_sequencing.bar_plot import BarPlotter
from protzilla.data_analysis.ptm_visualization.ptm_vis_utils import get_group_dict_from_csv, preprocess_files


def get_bar_plot_config_module(groups_file_path: Path, out_dir: Path) -> types.ModuleType:
    modification_file = out_dir / 'result_max_quant_mods.csv'
    bar_groups = get_group_dict_from_csv(groups_file_path)
    if len(bar_groups) == 0:
        raise ValueError("No groups found in the provided groups file for bar plot visualization.")
    plot_config_module = types.ModuleType('plot_config')
    plot_config_module.__dict__.update({
        # TODO: probably needs to be more dynamic (which PTMs are here)
        'MODIFICATIONS_GROUP': {
            'Phospho': 'A',
            'Acetyl': 'B',
            'GG': 'B',
            'Citrullination': 'B',
            'Methyl': 'A',
            'Deamidated': 'A',
        },
        'BAR_GROUPS': bar_groups,
        'BAR_WIDTH': 0.8,
        'INVERT_AXIS_GROUP_B': True,
        'BAR_INPUT_FILE': modification_file,
        'SHOW_PLOT': False,
        'SAVE_PLOT': False,
    })
    return plot_config_module


def create_bar_ptm_visualization(
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
        groups_file_path=groups_file_path
    )

    plot_config_module = get_bar_plot_config_module(groups_file_path, out_dir)
    bar_plotter = BarPlotter(
        config=config_module,
        plot_config=plot_config_module,
        input_file=str(fasta_file_path),
        output_path=str(out_dir)
    )
    fig, messages = bar_plotter.create_bar_plot()

    return dict(plots=[fig], messages=messages)
