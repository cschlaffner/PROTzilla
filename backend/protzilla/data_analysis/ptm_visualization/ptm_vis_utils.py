import csv
import types
from pathlib import Path

from main.views_helper import load_plot_settings_from_file
from protzilla.constants.paths import CUSTOM_PLOT_SETTINGS_FILE_STEM


def load_regions_from_csv(regions_file_path: Path) -> list:
    # TODO: figure out how the other default_config is loaded in code because apparently our csv is not used for actual
    #  regions
    regions = []
    with open(regions_file_path, 'r') as f:
        csvreader = csv.DictReader(f, delimiter=',')
        for row in csvreader:
            regions.append((row['name'], int(row['region_end']), row['group'], ''))
    return regions


def convert_settings_mm_size_to_px(size):
    # Convert width/height in mm to px using 300 dpi
    return (size / 25.4) * 300


def get_modifications_dict(full_modifications_dict) -> dict:
    return {k: (v['name'], v['color']) for k, v in full_modifications_dict.items()}


def get_included_modifications_dict(full_modifications_dict) -> dict:
    return {k: v['sites'] for k, v in full_modifications_dict.items()}


def get_general_config_module(
        regions_file_path: Path,
        out_dir: Path
) -> types.ModuleType:
    # TODO: would need some kind of annotation/hint (displayed to the user) how the regions file should look like
    regions = load_regions_from_csv(regions_file_path)

    # TODO: save this dict at the proper location and load from there
    #   - könnte man in settings speichern (dann aber auch ordentlich abfangen, wenn user welche will, die nicht
    #     drin sind) und dann auch PTMs dort auslesen und man kann es aus nem dropdown auswählen
    blah_modifications = {
        'Phospho': {
            'name': 'Phosphorylation',
            'color': '#000000',
            'sites': ['S', 'T', 'Y'],
        },
        'Acetyl': {
            'name': 'Acetylation',
            'color': '#93478F',
            'sites': ['K'],
        },
        'Methyl': {
            'name': 'Methylation',
            'color': '#C35728',
            'sites': ['K', 'R'],
        },
        'GG': {
            'name': 'Ubiquitination',
            'color': '#548056',
            'sites': ['K'],
        },
        'Citrullination': {
            'name': 'Citrullination',
            'color': '#FF17E3',
            'sites': ['R'],
    },
        'Deamidated': {
            'name': 'Deamidation',
            'color': '#34AEEB',
            'sites': ['N', 'Q', 'R'],
        },
    }

    protzilla_settings = load_plot_settings_from_file(file_stem=CUSTOM_PLOT_SETTINGS_FILE_STEM)

    config_module = types.ModuleType('main_config')
    config_module.__dict__.update({
        # Sequence Settings
        # First sequence is from (1, 44), second from (45, 73) and so on
        # Region Name, Region End, Group, Region Abbreviation
        'REGIONS': regions,
        # Modification Settings
        'MODIFICATION_LEGEND_TITLE': 'PTMs',
        'MODIFICATIONS': get_modifications_dict(blah_modifications),
        'INCLUDED_MODIFICATIONS': get_included_modifications_dict(blah_modifications),

        # Input Output Settings
        'OUTPUT_FOLDER': out_dir,

        # Plot Settings
        # 0 for horizontal, 1 for vertical, note figure height and width are then automatically swapped
        # TODO: customize (settings?)
        'FIGURE_ORIENTATION': 0,

        'PTMS_TO_HIGHLIGHT': [],  # Unused for now
        'PTM_HIGHLIGHT_LABEL_COLOR': '#cfcfcf',

        # just change width and height to change the size of the figure not the orientation
        'FIGURE_WIDTH': convert_settings_mm_size_to_px(protzilla_settings['width']),
        'FIGURE_HEIGHT': convert_settings_mm_size_to_px(protzilla_settings['height']),
        'FONT_SIZE': protzilla_settings['text_size'],

        # Default Parameters
        'FONT': protzilla_settings['custom_font'] if protzilla_settings['custom_font'] else protzilla_settings['font'],

        # Sequence Plot
        'SEQUENCE_PLOT_FONT_SIZE': protzilla_settings['text_size'],
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
        fasta_file_path: Path,
        groups_file_path: Path | None,
        q_value_threshold: float,
        out_dir: Path
) -> types.ModuleType:
    preprocessor_config_module = types.ModuleType('preprocessor_config')
    preprocessor_config_module.__dict__.update({
        # General
        'FASTA_FILE': fasta_file_path,
        'GROUPS_CSV': groups_file_path,

        # this is the default path where the tool will save the alignment
        # just change if you want to supply your own alignment
        # CAUTION: the alignment must match with the fasta file
        'ALIGNED_FASTA_FILE': str(out_dir / "aligned.fasta"),

        # MaxQuant
        'THRESHOLD': q_value_threshold
    })
    return preprocessor_config_module


def get_group_dict_from_csv(groups_file_path: Path) -> dict:
    groups = {}
    with open(groups_file_path, 'r') as f:
        csvreader = csv.DictReader(f, delimiter=',')
        for row in csvreader:
            # Seems weird. Is weird. But I didn't want to touch the underlying code
            groups[row['group_name']] = row['group_name']
    return groups
