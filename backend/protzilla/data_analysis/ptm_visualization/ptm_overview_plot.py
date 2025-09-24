import types
from pathlib import Path

from protein_sequencing.data_preprocessing.max_quant_preprocessor import MaxQuantPreprocessor
from protein_sequencing.overview_plot import OverviewPlotter
from protzilla.data_analysis.ptm_visualization.ptm_vis_utils import get_general_config_module, \
    get_preprocessor_config_module


def get_overview_plot_config_module(out_dir: Path) -> types.ModuleType:
    modification_file = out_dir / 'result_max_quant_mods.csv'
    plot_config_module = types.ModuleType('plot_config')
    plot_config_module.__dict__.update({
        # TODO: probably needs to be more dynamic (which PTMs are here)
        #    - get from the settings-PTM list
        'MODIFICATIONS_GROUP': {
            'Phospho': 'B',
            'Acetyl': 'B',
            'GG': 'B',
            'Citrullination': 'B',
            'Methyl': 'B',
            'Deamidated': 'B',
        },
        'INPUT_FILE': modification_file,
        'SEQUENCE_MIN_LINE_LENGTH': 20,
        'SHOW_PLOT': False,
        'SAVE_PLOT': False,
    })
    return plot_config_module


def create_overview_ptm_visualization(
        evidence_file_path: Path,
        evidence_file_q_value_threshold: float,
        fasta_file_path: Path,
        regions_file_path: Path,
) -> dict:
    # TODO: install as package and not clone from github directly
    # TODO: unify plot functions into a single one?
    # TODO[Chris]: would be good to have a second set of fasta files/regions/PTMs to test this properly
    # TODO: test all of this
    # TODO: clean the ptm_visualization directory

    out_dir = Path(__file__).parent / 'tmp'

    config_module = get_general_config_module(regions_file_path, out_dir)
    preprocessor_config_module = get_preprocessor_config_module(
        evidence_file_path=evidence_file_path,
        fasta_file_path=fasta_file_path,
        groups_file_path=None,
        q_value_threshold=evidence_file_q_value_threshold,
        out_dir=out_dir
    )
    MaxQuantPreprocessor(config_module, preprocessor_config_module)

    plot_config_module = get_overview_plot_config_module(out_dir)
    overview_plotter = OverviewPlotter(
        config=config_module,
        plot_config=plot_config_module,
        input_file=str(fasta_file_path),
        output_path=str(out_dir)
    )
    # TODO[Chris]: PROTzilla colors? - yes - bzw wäre cool, wenn das irgendwie customizable
    fig = overview_plotter.create_overview_plot()

    return dict(plots=[fig])
