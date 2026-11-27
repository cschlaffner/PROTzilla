# Clustering: KMeans

Partitions the samples according to their protein-intensity vectors. Let $x_s=(x_{s,p})_p$ be the vector of protein intensities for sample $s$. For a selected number of clusters $k$, K-means determines clusters $C_1,\ldots,C_k$ and centroids

$$
\mu_j=\frac{1}{|C_j|}\sum_{s\in C_j}x_s
$$

that minimize the within-cluster sum of squares

$$
\sum_{j=1}^{k}\sum_{s\in C_j}\left\|x_s-\mu_j\right\|_2^2.
$$

Each sample is assigned to its nearest centroid. The calculation is repeated with the selected number of initializations, and the result with the smallest within-cluster sum of squares is retained. The initialization strategy, maximum number of iterations, convergence tolerance, and random seed can be configured.

The selected metadata labels are not used to form the clusters. They are used to evaluate the resulting assignments and, during grid or randomized search, to select parameters according to the selected score. The step returns the fitted model, the cluster assigned to each sample, the cluster centroids, and the evaluation results. Missing intensities must be handled before clustering.

The calculation uses [`sklearn.cluster.KMeans`](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html).

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/clustering.py:k_means"
```
