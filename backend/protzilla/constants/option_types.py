from enum import Enum, StrEnum


class EmptyEnum(Enum):
    pass


class LogTransformationBaseType(StrEnum):
    LOG2 = "log2"
    LOG10 = "log10"

class LogBaseWithNoneType(StrEnum):
    LOG2 = "log2"
    LOG10 = "log10"
    # i hate this ~T
    NONE = "None"


class SimpleImputerStrategyType(StrEnum):
    MEAN = "mean"
    MEDIAN = "median"
    MOST_FREQUENT = "most_frequent"


class ImputationByNormalDistributionSamplingStrategyType(StrEnum):
    PER_PROTEIN = "perProtein"
    PER_DATASET = "perDataset"


class BarAndPieChart(StrEnum):
    BAR_PLOT = "Bar chart"
    PIE_CHART = "Pie chart"


class BoxAndHistogramGraph(StrEnum):
    BOXPLOT = "Boxplot"
    HISTOGRAM = "Histogram"


class GroupBy(StrEnum):
    NO_GROUPING = "None"
    SAMPLE = "Sample"
    PROTEIN_ID = "Protein ID"


class MultipleTestingCorrectionMethod(StrEnum):
    benjamini_hochberg = "Benjamini-Hochberg"
    bonferroni = "Bonferroni"
    none = "None"


class VisualTransformations(StrEnum):
    LOG10 = "log10"
    LINEAR = "linear"


class PValueColumnName(StrEnum):
    protein_id = "Protein ID"
    ptm = "PTM"


FC_SIGNIFICANCE_COLUMNS = ["Protein ID", "fc_z_score", "fc_significance"]
CORRECTED_P_VALUES_COLUMNS = [
    "Protein ID",
    "corrected_p_value",
]  # not true for PTM data
LOG2_FOLD_CHANGE_COLUMNS = ["Protein ID", "log2_fold_change"]  # not true for PTM data
T_STATISTIC_COLUMNS = ["Protein ID", "t_statistic"]
