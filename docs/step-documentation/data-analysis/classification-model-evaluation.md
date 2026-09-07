# Classification Model Evaluation

Applies a fitted classification model to the given feature table and compares the predicted labels $\hat{y}_s$ with the given true labels $y_s$. For binary classification, the available evaluation measures are based on true positives (TP), true negatives (TN), false positives (FP), and false negatives (FN):

$$
\operatorname{Accuracy}=\frac{\mathrm{TP}+\mathrm{TN}}{\mathrm{TP}+\mathrm{TN}+\mathrm{FP}+\mathrm{FN}},
$$

$$
\operatorname{Precision}=\frac{\mathrm{TP}}{\mathrm{TP}+\mathrm{FP}},
\qquad
\operatorname{Recall}=\frac{\mathrm{TP}}{\mathrm{TP}+\mathrm{FN}},
$$

and


$$
\operatorname{MCC}=\frac{\mathrm{TP}\cdot\mathrm{TN}-\mathrm{FP}\cdot\mathrm{FN}}{\sqrt{(\mathrm{TP}+\mathrm{FP})(\mathrm{TP}+\mathrm{FN})(\mathrm{TN}+\mathrm{FP})(\mathrm{TN}+\mathrm{FN})}}.
$$

The step returns one score for each selected metric. It should be applied to data that was not used to fit or select the model, such as the test tables returned by a classification step.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/model_evaluation.py:evaluate_classification_model"
```
