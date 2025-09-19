import csv
import itertools
import types
from pathlib import Path

from protein_sequencing.bar_plot import BarPlotter
from protein_sequencing.data_preprocessing.max_quant_preprocessor import MaxQuantPreprocessor
from protein_sequencing.details_plot import DetailsPlotter
from protein_sequencing.overview_plot import OverviewPlotter
from protzilla.constants.colors import PLOT_COLOR_SEQUENCE


def load_regions_from_csv(regions_file_path: Path) -> list:
    # TODO: figure out how the other default_config is loaded in code
    regions = []
    with open(regions_file_path, 'r') as f:
        csvreader = csv.DictReader(f, delimiter=',')
        for row in csvreader:
            regions.append((row['name'], int(row['region_end']), row['group'], ''))
    return regions


def get_general_config_module(
        regions_file_path: Path,
        out_dir: Path,
        font_size: int = 12
) -> types.ModuleType:
    # TODO: would need some kind of annotation/hint how the regions file should look like
    regions = load_regions_from_csv(regions_file_path)

    # TODO[Chris]: in general, go through configs and figure out what should be user-controlled
    config_module = types.ModuleType('main_config')
    config_module.__dict__.update({
        # Sequence Settings
        # First sequence is from (1, 44), second from (45, 73) and so on
        # Region Name, Region End, Group, Region Abbreviation
        'REGIONS': regions,
        # Modification Settings
        'MODIFICATION_LEGEND_TITLE': 'PTMs',
        # TODO[Chris]: should this be customizable? - yes csv would be ok
        #   - Kürzel in Pep. Seq., Display Name, Farbe und dann darunter sind die Sites
        #   - könnte man in settings speichern (dann aber auch ordentlich abfangen, wenn user welche will, die nicht
        #     drin sind) und dann auch PTMs dort auslesen und man kann es aus nem dropdown auswählen
        'MODIFICATIONS': {
            'Phospho': ('Phosphorylation', '#000000'),
            'Acetyl': ('Acetylation', '#93478F'),
            'Methyl': ('Methylation', '#C35728'),
            'GG': ('Ubiquitination', '#548056'),
            'Citrullination': ('Citrullination', '#FF17E3'),
            'Deamidated': ('Deamidation', '#34AEEB'),
        },
        'INCLUDED_MODIFICATIONS': {
            'Phospho': ['S', 'T', 'Y'],
            'Acetyl': ['K'],
            'Methyl': ['K', 'R'],
            'GG': ['K'],
            'Citrullination': ['R'],
            'Deamidated': ['N', 'Q', 'R'],
        },

        # Input Output Settings
        'OUTPUT_FOLDER': out_dir,

        # Plot Settings
        # 0 for horizontal, 1 for vertical, note figure height and width are then automatically swapped
        # TODO: customize
        'FIGURE_ORIENTATION': 0,

        # just change width and height to change the size of the figure not the orientation
        # TODO: customize
        'FIGURE_WIDTH': 1200,
        # TODO: customize
        'FIGURE_HEIGHT': 1000,
        # TODO: customize - load from settings
        'FONT_SIZE': font_size,
        # TODO: remove
        'PTMS_TO_HIGHLIGHT': ['Phospho(S)@276', 'Phospho(S)@287'],
        # TODO: remove
        'PTM_HIGHLIGHT_LABEL_COLOR': '#cfcfcf',

        # Default Parameters
        # TODO: customize - load from settings
        'FONT': 'Arial',

        # Sequence Plot
        # TODO: customize - load from settings
        'SEQUENCE_PLOT_FONT_SIZE': font_size,
        'SEQUENCE_PLOT_HEIGHT': 50,
        'EXONS_GAP': 10,
        'MIN_EXON_LENGTH': 5,

        # TODO: customize in den allgemeinen settings
        'SEQUENCE_REGION_COLORS': {
            'A': 'white',
            'B': 'lightgrey',
        },
    })
    return config_module


def get_preprocessor_config_module(
        evidence_file_path: Path,
        fasta_file_path: Path,
        groups_file_path: Path,
        out_dir: Path
) -> types.ModuleType:
    preprocessor_config_module = types.ModuleType('preprocessor_config')
    preprocessor_config_module.__dict__.update({
        # General
        'FASTA_FILE': fasta_file_path,
        'ISOFORM_HELPER_DICT': {},  # TODO: ?
        'GROUPS_CSV': groups_file_path,

        # this is the default path where the tool will save the alignment
        # just change if you want to supply your own alignment
        # CAUTION: the alignment must match with the fasta file
        'ALIGNED_FASTA_FILE': str(out_dir / "aligned.fasta"),

        # MaxQuant
        'MAX_QUANT_FILE': evidence_file_path,
        # TODO: q-value sollte nen Form field sein
        'THRESHOLD': 0.01,
    })
    return preprocessor_config_module


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
        fasta_file_path: Path,
        groups_file_path: Path,
        regions_file_path: Path,
) -> dict:
    # TODO: install as package and not clone from github directly
    # TODO[Chris]: would be good to have a second set of fasta files/regions/PTMs to test this properly
    # TODO: test all of this
    # TODO: clean the ptm_visualization directory
    # TODO: fix the calling of the clustal script

    out_dir = Path(__file__).parent / 'tmp'

    config_module = get_general_config_module(regions_file_path, out_dir)
    preprocessor_config_module = get_preprocessor_config_module(
        evidence_file_path,
        fasta_file_path,
        groups_file_path,
        out_dir
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
    # TODO[Chris]: crop plot? Currently quite large/oversized
    fig = overview_plotter.create_overview_plot()

    return dict(plots=[fig])


def get_group_dict_from_csv(groups_file_path: Path) -> dict:
    groups = {}
    with open(groups_file_path, 'r') as f:
        csvreader = csv.DictReader(f, delimiter=',')
        for row in csvreader:
            # Seems weird. Is weird. But I didn't want to touch the underlying code
            groups[row['group_name']] = row['group_name']
    return groups


def get_bar_plot_config_module(groups_file_path: Path, out_dir: Path) -> types.ModuleType:
    modification_file = out_dir / 'result_max_quant_mods.csv'
    bar_groups = get_group_dict_from_csv(groups_file_path)
    plot_config_module = types.ModuleType('plot_config')
    plot_config_module.__dict__.update({
        # TODO: probably needs to be more dynamic (which PTMs are here)
        'MODIFICATIONS_GROUP': {
            'Phospho': 'A',
            'Acetyl': 'A',
            'GG': 'A',
            'Citrullination': 'A',
            'Methyl': 'A',
            'Deamidated': 'A',
        },
        'BAR_GROUPS': bar_groups,
        'BAR_WIDTH': 0.8,
        # TODO: settings
        'INVERT_AXIS_GROUP_B': True,
        'BAR_INPUT_FILE': modification_file,
        'SHOW_PLOT': False,
        'SAVE_PLOT': False,
    })
    return plot_config_module


def create_bar_ptm_visualization(
        evidence_file_path: Path,
        fasta_file_path: Path,
        groups_file_path: Path,
        regions_file_path: Path,
) -> dict:
    out_dir = Path(__file__).parent / 'tmp'

    config_module = get_general_config_module(regions_file_path, out_dir)
    preprocessor_config_module = get_preprocessor_config_module(
        evidence_file_path,
        fasta_file_path,
        groups_file_path,
        out_dir
    )
    MaxQuantPreprocessor(config_module, preprocessor_config_module)

    plot_config_module = get_bar_plot_config_module(groups_file_path, out_dir)
    bar_plotter = BarPlotter(
            config=config_module,
            plot_config=plot_config_module,
            input_file=str(fasta_file_path),
            output_path=str(out_dir)
    )
    fig = bar_plotter.create_bar_plot()

    return dict(plots=[fig])


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

        # TODO erstmal weglassen
        'CLEAVAGES_TO_HIGHLIGHT': ['2-4', '15'],  # TODO[Chris]: make customizable - but what does it translate to?
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
        # TODO[Chris]: what is this even for? - why is it mapped to list
        'GROUPS': details_groups,
        'PTM_RECT_LENGTH': 25,
        # TODO: customizable
        'REGION_LABEL_ANGLE_GROUPS': 0,
        'SHOW_PLOT': False,
        'SAVE_PLOT': False,
    })
    return plot_config_module


def create_details_ptm_visualization(
        evidence_file_path: Path,
        fasta_file_path: Path,
        groups_file_path: Path,
        regions_file_path: Path,
) -> dict:
    # TODO: figure out how to do region labels
    out_dir = Path(__file__).parent / 'tmp'

    config_module = get_general_config_module(regions_file_path, out_dir)
    preprocessor_config_module = get_preprocessor_config_module(
        evidence_file_path,
        fasta_file_path,
        groups_file_path,
        out_dir
    )
    MaxQuantPreprocessor(config_module, preprocessor_config_module)

    plot_config_module = get_details_plot_config_module(groups_file_path, out_dir)
    plotter = DetailsPlotter(
        config=config_module,
        plot_config=plot_config_module,
        input_file=str(fasta_file_path),
        output_path=str(out_dir)
    )
    fig = plotter.create_details_plot()

    return dict(plots=[fig])
