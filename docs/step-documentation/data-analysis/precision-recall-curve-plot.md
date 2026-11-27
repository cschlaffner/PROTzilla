# Precision Recall Curve Plot

Evaluates a fitted binary classification model on the given test data. For every decision threshold $t$, samples with a predicted positive-class probability of at least $t$ are classified as positive. The curve plots

$$
\operatorname{Precision}(t)=\frac{\operatorname{TP}(t)}{\operatorname{TP}(t)+\operatorname{FP}(t)}
$$

against

$$
\operatorname{Recall}(t)=\frac{\operatorname{TP}(t)}{\operatorname{TP}(t)+\operatorname{FN}(t)}.
$$

The displayed AUC is the area under the precision-recall curve. The calculation uses [`sklearn.metrics.precision_recall_curve`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_curve.html).

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/plots.py:precision_recall_plot"
```
