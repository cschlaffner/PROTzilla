# Outlier Detection: Isolation Forest

Transforms the given protein table into a matrix with samples as rows and proteins as columns, then fits an Isolation Forest with the selected number of estimators. Each tree is trained on $\lfloor n/2 \rfloor$ randomly selected samples, where $n$ is the total number of samples.

Each sample $s$ receives a decision score $a_s$, where lower values indicate stronger anomalies. A sample is classified as an outlier iff

$$
a_s < 0.
$$

Outlier samples are removed from the protein table and returned together with all decision scores. The fixed random seed makes repeated calculations with the same input and parameters reproducible. For details about the algorithm, see the [scikit-learn Isolation Forest documentation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html).

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/outlier_detection.py:by_isolation_forest"
```
