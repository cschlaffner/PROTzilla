from enum import Enum

class EmptyEnum(Enum):
    pass


class LogTransformationBaseType(Enum):
    LOG2 = "log2"
    LOG10 = "log10"


class SimpleImputerStrategyType(Enum):
    MEAN = "mean"
    MEDIAN = "median"
    MOST_FREQUENT = "most_frequent"


class ImputationByNormalDistributionSamplingStrategyType(Enum):
    PER_PROTEIN = "perProtein"
    PER_DATASET = "perDataset"


class BarAndPieChart(Enum):
    BAR_PLOT = "Bar chart"
    PIE_CHART = "Pie chart"


class BoxAndHistogramGraph(Enum):
    BOXPLOT = "Boxplot"
    HISTOGRAM = "Histogram"


class GroupBy(Enum):
    NO_GROUPING = "None"
    SAMPLE = "Sample"
    PROTEIN_ID = "Protein ID"


class VisualTransformations(Enum):
    LOG10 = "log10"
    LINEAR = "linear"