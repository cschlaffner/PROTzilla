# ROC Curve Plot

Evaluates a fitted binary classification model on the given test data. For every decision threshold $t$, samples with a predicted positive-class probability of at least $t$ are classified as positive. The receiver operating characteristic curve plots

$$
\operatorname{TPR}(t)=\frac{\operatorname{TP}(t)}{\operatorname{TP}(t)+\operatorname{FN}(t)}
$$

against

$$
\operatorname{FPR}(t)=\frac{\operatorname{FP}(t)}{\operatorname{FP}(t)+\operatorname{TN}(t)}.
$$

The displayed AUC is the area under this curve. The calculation uses [`sklearn.metrics.roc_curve`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_curve.html).

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/plots.py:roc_plot"
```
