from enum import Enum


class IntensityType(Enum):
    IBAQ = "iBAQ"
    INTENSITY = "Intensity"
    LFQ_INTENSITY = "LFQ intensity"
    RATIO_HL = "Ratio H/L"
    RATIO_LH = "Ratio L/H"
    RATIO_HL_NORMALIZED = "Ratio H/L normalized"
    RATIO_LH_NORMALIZED = "Ratio L/H normalized"
