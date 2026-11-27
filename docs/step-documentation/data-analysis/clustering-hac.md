# Clustering: HAC

Performs hierarchical agglomerative clustering on the sample intensity vectors. Initially, each sample forms a separate cluster. The pair of clusters with the smallest selected linkage distance is repeatedly merged until the selected number of clusters remains.

For a pointwise distance $d(a,b)$ between samples $a$ and $b$, the available linkage criteria are:

- **Single:** $D(A,B)=\min_{a\in A,\,b\in B}d(a,b)$.
- **Complete:** $D(A,B)=\max_{a\in A,\,b\in B}d(a,b)$.
- **Average:** $D(A,B)=\dfrac{1}{|A||B|}\sum_{a\in A}\sum_{b\in B}d(a,b)$.
- **Ward:** merges the pair that causes the smallest increase in within-cluster sum of squares and requires Euclidean distance.

The selected metadata labels are used only to evaluate the resulting assignments and to select parameters during grid or randomized search. The step returns the fitted model, the cluster assigned to each sample, and the evaluation results. Missing intensities must be handled before clustering.

The calculation uses [`sklearn.cluster.AgglomerativeClustering`](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.AgglomerativeClustering.html).

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/clustering.py:hierarchical_agglomerative_clustering"
```
