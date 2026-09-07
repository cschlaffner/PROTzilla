# Imputation: kNN

Imputes missing protein intensities using the k-nearest neighbors method. For a missing intensity $x_{s,p}$ of protein $p$ in sample $s$, the imputed value is

$$
\hat{x}_{s,p}
=
\frac{1}{|N_k(s,p)|}
\sum_{s' \in N_k(s,p)} x_{s',p},
$$

where $N_k(s,p)$ contains up to `number_of_neighbours` nearest samples in which protein $p$ has a measured intensity. Neighbors are identified from other proteins measured in both samples using the nan-euclidean distance. `number_of_neighbours` defaults to `5`.

Proteins without a measured intensity in any sample are removed before imputation.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/imputation.py:by_knn"
```
