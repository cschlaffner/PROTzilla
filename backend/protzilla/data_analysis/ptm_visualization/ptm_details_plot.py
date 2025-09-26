import itertools
import types
from pathlib import Path

import pandas as pd

from protein_sequencing.data_preprocessing.max_quant_preprocessor import MaxQuantPreprocessor
from protein_sequencing.details_plot import DetailsPlotter
from protzilla.constants.colors import PLOT_COLOR_SEQUENCE
from protzilla.data_analysis.ptm_visualization.ptm_vis_utils import get_general_config_module, \
    get_preprocessor_config_module, get_group_dict_from_csv


def get_details_plot_config_module(groups_file_path: Path, out_dir: Path) -> types.ModuleType:
    modification_file = out_dir / 'result_max_quant_mods.csv'
    cleavage_file = out_dir / 'result_max_quant_cleavages.csv'

    groups = get_group_dict_from_csv(groups_file_path)
    # TODO[Chris]: hacky way to map groups to some colors - do we care? Need more colors?
    details_groups = {k: ([v], color) for (k, v), color in zip(groups.items(), itertools.cycle(PLOT_COLOR_SEQUENCE))}

    plot_config_module = types.ModuleType('plot_config')
    plot_config_module.__dict__.update({
        # Details plot settings
        'MODIFICATION_THRESHOLD': 1,

        'INPUT_FILES': {
            'B': ('Cleavage', cleavage_file),
            'A': ('PTM', modification_file),
        },

        'CLEAVAGES_TO_HIGHLIGHT': [],
        'CLEAVAGE_HIGHLIGHT_COLOR': '#ff0000',

        # TODO: settings
        'CLEAVAGE_LABEL_COLOR': '#333333',
        'CLEAVAGE_SCALE_COLOR_LOW': '#B35806',
        'CLEAVAGE_SCALE_COLOR_MID': '#F7F7F7',
        'CLEAVAGE_SCALE_COLOR_HIGH': '#542788',
        'CLEAVAGE_LEGEND_TITLE': 'Proteolytic<br>Cleavage<br>Patient<br>Frequency',

        'PTM_SCALE_COLOR_LOW': '#B35806',
        'PTM_SCALE_COLOR_MID': '#F5F5F5',
        'PTM_SCALE_COLOR_HIGH': '#01665E',
        'PTM_LEGEND_TITLE': 'PTM Patient <br>Frequency',
        'GROUPS': details_groups,
        'PTM_RECT_LENGTH': 25,
        # TODO: customizable
        'REGION_LABEL_ANGLE_GROUPS': 0,
        'SHOW_PLOT': False,
        'SAVE_PLOT': False,
    })
    return plot_config_module


def create_details_ptm_visualization(
        evidence_df: pd.DataFrame,
        evidence_file_q_value_threshold: float,
        fasta_file_path: Path,
        regions_file_path: Path,
        groups_file_path: Path,
) -> dict:
    # TODO: figure out how to do region labels
    out_dir = Path(__file__).parent / 'tmp'

    config_module = get_general_config_module(regions_file_path, out_dir)
    preprocessor_config_module = get_preprocessor_config_module(
        fasta_file_path=fasta_file_path,
        groups_file_path=groups_file_path,
        q_value_threshold=evidence_file_q_value_threshold,
        out_dir=out_dir
    )
    MaxQuantPreprocessor(config_module, preprocessor_config_module, evidence_df=evidence_df)

    plot_config_module = get_details_plot_config_module(groups_file_path, out_dir)
    plotter = DetailsPlotter(
        config=config_module,
        plot_config=plot_config_module,
        input_file=str(fasta_file_path),
        output_path=str(out_dir)
    )
    fig = plotter.create_details_plot()

    return dict(plots=[fig])
