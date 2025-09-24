# TODO: remove all files in this dir
# General Settings

# Sequence Settings
# First sequence is from (1, 44), second from (45, 73) and so on
# Region Name, Region End, Group, Region Abbreviation
REGIONS = [
    ("", 338, "A", ""),
    ("", 511, "B", ""),
    ("", 799, "A", ""),
    ("", 848, "B", ""),
    ("", 920, "A", ""),
]
# Modification Settings
MODIFICATION_LEGEND_TITLE = 'PTMs'
MODIFICATIONS = {
    'Phospho': ('Phosphorylation', '#000000'),
    'Acetyl': ('Acetylation', '#93478F'),
    'Methyl': ('Methylation', '#C35728'),
    'GG': ('Ubiquitination', '#548056'),
    'Citrullination': ('Citrullination', '#FF17E3'),
    'Deamidated': ('Deamidation', '#34AEEB'),
}

INCLUDED_MODIFICATIONS = {'Phospho': ['S', 'T', 'Y'],
                          'Acetyl': ['K'],
                          'Methyl': ['K', 'R'],
                          'GG': ['K'],
                          'Citrullination': ['R'],
                          'Deamidated': ['N', 'Q', 'R'],}

# Input Output Settings
OUTPUT_FOLDER = 'tests/output/'

# Plot Settings
FIGURE_ORIENTATION = 0  # 0 for horizontal, 1 for vertical, note figure height and width are then automatically swapped

# just change width and height to change the size of the figure not the orientation
FIGURE_WIDTH = 1200
FIGURE_HEIGHT = 1000

FONT_SIZE = 12

PTMS_TO_HIGHLIGHT = ['Phospho(S)@276', 'Phospho(S)@287']
PTM_HIGHLIGHT_LABEL_COLOR = '#cfcfcf'


# Default Parameters
FONT = 'Arial'

# Sequence Plot
SEQUENCE_PLOT_FONT_SIZE = FONT_SIZE
SEQUENCE_PLOT_HEIGHT = 50
# works best with an even number
EXONS_GAP = 10
MIN_EXON_LENGTH = 5

# Sequence Region Colors
SEQUENCE_REGION_COLORS = {
    'A': 'white',
    'B': 'lightgrey',
}
