import pandas as pd

from backend.protzilla.data_analysis.classification_helper import (
    evaluate_with_scoring,
)


# --8<-- [start:evaluate_classification_model]
def evaluate_classification_model(model, protein_df, metadata_df, scoring):
    """
    Function that asseses an already trained classification model on separate testing
    data using widely used scoring metrics

    :param model: The trained classification model instance to be evaluated.
    :type model: BaseEstimator
    :param protein_df: The input features of the testing data as a DataFrame.
    :type protein_df: pd.DataFrame
    :param metadata_df: The true labels of the testing data as a DataFrame.
    :type metadata_df: pd.DataFrame
    :param scoring: The scoring metric to be used for evaluation. It can be a string
        representing a predefined metric e.g. accuracy, precision, recall, matthews_corrcoef
    :type scoring: str or callable
    :return: A dataframe with the metric name and its corresponding score.
    :rtype: dict
    """

    y_pred = model.predict(protein_df)
    scores = evaluate_with_scoring(scoring, metadata_df, y_pred)

    scores_df = pd.DataFrame.from_dict(scores, orient="index", columns=["Score"])
    scores_df = scores_df.reset_index().rename(columns={"index": "Metric"})
    return dict(scores_df=scores_df)
# --8<-- [end:evaluate_classification_model]
