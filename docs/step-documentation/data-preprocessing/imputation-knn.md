# Imputation: kNN

Imputes missing protein intensities using the k-nearest neighbors method. For each sample containing missing values, the method identifies the `k` most similar samples based on the available intensities. The corresponding protein intensities from these neighboring samples are then averaged to estimate the missing value.

Only proteins measured in both the current sample and the neighboring samples are used to determine similarity. The number of neighbors is controlled by `number_of_neighbours`, which defaults to `5`.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/imputation.py:by_knn"
```
