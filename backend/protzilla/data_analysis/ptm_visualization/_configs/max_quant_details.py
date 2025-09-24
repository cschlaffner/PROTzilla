# Details plot settings
MODIFICATION_THRESHOLD = 1

INPUT_FILES = {
    'B': ('Cleavage', 'tests/output/result_max_quant_cleavages.csv'),
    'A': ('PTM', 'tests/output/result_max_quant_mods.csv'),
}

CLEAVAGES_TO_HIGHLIGHT = ['2-4', '15']
CLEAVAGE_HIGHLIGHT_COLOR = '#ff0000'

CLEAVAGE_LABEL_COLOR = '#333333'
CLEAVAGE_SCALE_COLOR_LOW = '#B35806'
CLEAVAGE_SCALE_COLOR_MID = '#F7F7F7'
CLEAVAGE_SCALE_COLOR_HIGH = '#542788'
CLEAVAGE_LEGEND_TITLE = 'Proteolytic<br>Cleavage<br>Patient<br>Frequency'
#CLEAVAGE_LEGEND_TITLE = 'Proteolytic Cleavage Patient Frequency'

PTM_SCALE_COLOR_LOW = '#B35806'
PTM_SCALE_COLOR_MID = '#F5F5F5'
PTM_SCALE_COLOR_HIGH = '#01665E'
PTM_LEGEND_TITLE = 'PTM Patient <br>Frequency'

# GROUPS = {"CTR": (["CTR"], '#4DAF4A'),
#                     "DLB": (["DLB"], '#8DD3C7'),
#                     "PSP": (["PSP"], '#FF7F00'),
#                     "PiD": (["PiD"], '#984EA3'),
#                     "FTLD": (["FTLDTau"], '#17DFFF'),
#                     "CBD": (["CBD"], '#FFD92F'),
#                     "CTE": (["CTE"], '#1740B6'),
#                     "AD": (["AD", "NPCAD"], '#E41A1C'),
#                     "fAD": (["fAD"], '#9C0B0C'),}

# GROUPS = {"CTRL": (["CTRL"], '#4DAF4A'),
#                     "AD": (["AD", "NPCAD"], '#E41A1C'),}

# GROUPS = {
#     "CTRL": (["CTRL", "CTR", "Control"], '#4DAF4A'),
#     "FTLD-Tau": (["FTLD-Tau"], '#17DFFF'),
#     "FTLD-PiD": (["FTLD-PiD"], '#984EA3'),
# }
GROUPS = {
    'Clean': (['Clean'], '#4DAF4A'),
    'Old': (['Old'], '#17DFFF'),
    'Exon': (['Exon'], '#984EA3'),
}
PTM_RECT_LENGTH = 25
REGION_LABEL_ANGLE_GROUPS = 0
