import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def input_imputation_df():
    test_intensity_list = (
        ["Sample1", "Protein1", "Gene1", np.nan],
        ["Sample1", "Protein2", "Gene2", 20],
        ["Sample1", "Protein3", "Gene3", 10],
        ["Sample2", "Protein1", "Gene1", 1],
        ["Sample2", "Protein2", "Gene2", np.nan],
        ["Sample2", "Protein3", "Gene3", 2],
        ["Sample3", "Protein1", "Gene1", 100],
        ["Sample3", "Protein2", "Gene2", np.nan],
        ["Sample3", "Protein3", "Gene3", 80],
    )

    input_imputation_df = pd.DataFrame(
        data=test_intensity_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )

    return input_imputation_df

@pytest.fixture
def assertion_df_knn():
    assertion_list = (
        ["Sample1", "Protein1", "Gene1", 50.5],
        ["Sample1", "Protein2", "Gene2", 20],
        ["Sample1", "Protein3", "Gene3", 10],
        ["Sample2", "Protein1", "Gene1", 1.0],
        ["Sample2", "Protein2", "Gene2", 20],
        ["Sample2", "Protein3", "Gene3", 2],
        ["Sample3", "Protein1", "Gene1", 100],
        ["Sample3", "Protein2", "Gene2", 20],
        ["Sample3", "Protein3", "Gene3", 80],
    )
    assertion_df = pd.DataFrame(
        data=assertion_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )
    return assertion_df

@pytest.fixture
def assertion_df_min_value_per_df():
    assertion_list = (
        ["Sample1", "Protein1", "Gene1", 0.1],
        ["Sample1", "Protein2", "Gene2", 20],
        ["Sample1", "Protein3", "Gene3", 10],
        ["Sample2", "Protein1", "Gene1", 1],
        ["Sample2", "Protein2", "Gene2", 0.1],
        ["Sample2", "Protein3", "Gene3", 2],
        ["Sample3", "Protein1", "Gene1", 100],
        ["Sample3", "Protein2", "Gene2", 0.1],
        ["Sample3", "Protein3", "Gene3", 80],
    )
    assertion_df = pd.DataFrame(
        data=assertion_list,
        columns=["Sample", "Protein ID", "Gene", "Intensity"],
    )
    return assertion_df