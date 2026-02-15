import pytest

from backend.protzilla.data_preprocessing import imputation
from backend.protzilla.data_preprocessing.plots import *
from backend.tests.protzilla.data_preprocessing.test_imputation import *

# this tests will build some Figures and display them if show_figures==True
# it tests only for occurring errors


@pytest.mark.order(1)
@pytest.mark.dependency()
def test_create_pie_plot(show_figures):
    fig = create_pie_plot(
        names_of_sectors=["Non-imputed values", "Imputed values"],
        values_of_sectors=[10, 21],
        heading="Number of Imputed Values",
    )
    if show_figures:
        fig.show()

    # should throw Value Error
    with pytest.raises(ValueError):
        create_pie_plot(
            names_of_sectors=["", ""],
            values_of_sectors=[-10, 21],
        )


@pytest.mark.order(1)
@pytest.mark.dependency()
def test_create_bar_plot(show_figures):
    fig = create_bar_plot(
        names_of_sectors=["Non-imputed values", "Imputed values"],
        values_of_sectors=[10, 21],
        heading="Number of Imputed Values",
    )
    if show_figures:
        fig.show()


@pytest.mark.order(1)
@pytest.mark.dependency()
def test_create_box_plots(
    show_figures, input_imputation_df, assertion_df_knn, assertion_df_min_value_per_df
):
    fig = create_box_plots(
        dataframe_a=input_imputation_df,
        dataframe_b=assertion_df_knn,
        name_a="Before Transformation",
        name_b="After Transformation",
        heading="Distribution of Protein Intensities",
        group_by="None",
    )
    if show_figures:
        fig.show()

    # should throw Value Error
    with pytest.raises(ValueError):
        create_box_plots(
            dataframe_a=input_imputation_df,
            dataframe_b=assertion_df_knn,
            group_by="wrong_group_by",
        )
    return


@pytest.mark.order(1)
@pytest.mark.dependency()
def test_create_histograms(
    show_figures, input_imputation_df, assertion_df_knn, assertion_df_min_value_per_df
):
    fig = create_histograms(
        dataframe_a=input_imputation_df,
        dataframe_b=assertion_df_knn,
        name_a="input_imputation_df",
        name_b="assertion_df_knn",
        heading="heading",
    )
    if show_figures:
        fig.show()

    fig = create_histograms(
        dataframe_a=input_imputation_df,
        dataframe_b=assertion_df_knn,
        name_a="input_imputation_df",
        name_b="assertion_df_knn",
        heading="heading",
        overlay=True,
    )
    if show_figures:
        fig.show()

    # should throw Value Error
    with pytest.raises(ValueError):
        create_histograms(
            dataframe_a=input_imputation_df,
            dataframe_b=assertion_df_knn,
            visual_transformation="wrong_visual_transformation",
        )
    return


def test_create_histograms_one_bin_per_int_is_true():

    df_a = pd.DataFrame({"value": [1.2, 2.7, 3.5]})
    df_b = pd.DataFrame({"value": [2.1, 4.6, 5.9]})

    fig = create_histograms(
        dataframe_a=df_a,
        dataframe_b=df_b,
        relevant_column_a="value",
        relevant_column_b="value",
        name_a="A",
        name_b="B",
        one_bin_per_int=True,
    )

    trace_a = fig.data[0]
    trace_b = fig.data[1]

    # Check bin size is 1
    assert trace_a.xbins["size"] == 1
    assert trace_b.xbins["size"] == 1

    # Check min and max are rounded correctly
    # min_value should be floor(min(values_a.min(), values_b.min())) = floor(1.2) = 1
    # max_value should be ceil(max(values_a.max(), values_b.max())) = ceil(5.9) = 6
    assert trace_a.xbins["start"] == 1
    assert trace_a.xbins["end"] == 6
    assert trace_b.xbins["start"] == 1
    assert trace_b.xbins["end"] == 6


def test_create_histograms_with_empty_dataframe():
    df_empty = pd.DataFrame({"value": []})
    df_nonempty = pd.DataFrame({"value": [1, 2, 3]})

    fig = create_histograms(
        dataframe_a=df_empty,
        dataframe_b=df_nonempty,
        relevant_column_a="value",
        relevant_column_b="value",
        name_a="Empty",
        name_b="NonEmpty",
        one_bin_per_int=True,
    )

    trace_empty = fig.data[0]
    trace_nonempty = fig.data[1]

    # Ensure the function did not crash and returned a Figure
    assert isinstance(fig, Figure)

    # Even if dataframe_a is empty, trace_a should exist with default bin size 1
    assert trace_empty.xbins["size"] == 1

    # trace_b should have correct start/end bin values
    assert trace_nonempty.xbins["start"] == 1  # floor(min(values_b)) = 1
    assert trace_nonempty.xbins["end"] == 3  # ceil(max(values_b)) = 3
    assert trace_nonempty.xbins["size"] == 1


@pytest.mark.order(2)
@pytest.mark.dependency(
    depends=[
        "test_create_pie_plot",
        "test_create_bar_plot",
        "test_create_box_plots",
        "test_create_histograms",
    ]
)
def test_build_box_hist_plot(
    show_figures, input_imputation_df, assertion_df_knn, assertion_df_min_value_per_df
):
    fig1, fig2 = imputation._build_box_hist_plot(
        input_imputation_df,
        assertion_df_knn,
        "Boxplot",
        "Bar chart",
        "Sample",
        "linear",
    )
    fig3, fig4 = imputation._build_box_hist_plot(
        input_imputation_df,
        assertion_df_min_value_per_df,
        "Histogram",
        "Pie chart",
        "Protein ID",
        "linear",
    )

    if show_figures:
        fig1.show()
        fig2.show()
        fig3.show()
        fig4.show()
    return
