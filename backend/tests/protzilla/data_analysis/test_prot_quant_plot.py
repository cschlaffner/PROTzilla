from backend.protzilla.data_analysis.plots import *
from backend.tests.protzilla.data_analysis.test_clustering import *


@pytest.fixture
def wide_4d_df():
    return pd.DataFrame(
        np.array(
            [
                [4, 10, 3, 2],
                [8, 2, 4, 7],
                [2, 7, 1, 4],
                [13, 5, 7, 1],
            ]
        ),
        columns=["Protein1", "Protein2", "Protein3", "Protein4"],
        index=["Sample1", "Sample2", "Sample3", "Sample4"],
    )


def test_prot_quant_plot(show_figures, wide_4d_df):
    # TODO: there should be more tests that also check the error handling
    outputs = prot_quant_plot(wide_4d_df, "Protein1")
    assert "plots" in outputs
    fig = outputs["plots"][0]
    if show_figures:
        fig.show()
    return
