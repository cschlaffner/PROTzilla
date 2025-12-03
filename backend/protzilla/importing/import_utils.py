from enum import Enum


class IntensityNameType(Enum):
    INTENSITY = "Intensity"
    MAXLFQ_TOTAL_INTENSITY = "MaxLFQ Total Intensity"
    MAXLFQ_INTENSITY = "MaxLFQ Intensity"
    TOTAL_INTENSITY = "Total Intensity"
    MAXLFQ_UNIQUE_INTENSITY = "MaxLFQ Unique Intensity"
    UNIQUE_SPECTRAL_COUNT = "Unique Spectral Count"
    UNIQUE_INTENSITY = "Unique Intensity"
    SPECTRAL_COUNT = "Spectral Count"
    TOTAL_SPECTRAL_COUNT = "Total Spectral Count"


class FeatureOrientationType(Enum):
    COLUMNS = "Columns (samples in rows, features in columns)"
    ROWS = "Rows (features in rows, samples in columns)"


class EmptyEnum(Enum):
    pass


class AggregationMethods(Enum):
    sum = "Sum"
    median = "Median"
    mean = "Mean"
