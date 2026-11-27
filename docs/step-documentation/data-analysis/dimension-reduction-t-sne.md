# Dimension Reduction: t-SNE

Embeds the sample intensity vectors $x_s$ into a selected number of dimensions. t-SNE converts distances between samples in the original space into pairwise similarities $p_{ij}$ and searches for embedded coordinates $y_s$ with similarities $q_{ij}$ that minimize

$$
D_{\mathrm{KL}}(P\parallel Q)=\sum_{i\neq j}p_{ij}\log\left(\frac{p_{ij}}{q_{ij}}\right).
$$

The perplexity controls the effective number of neighbors considered around each sample and must be smaller than the number of samples. The selected metric defines distances in the original protein-intensity space. The exact method evaluates all pairwise interactions, whereas the Barnes-Hut method uses a faster approximation and supports at most three output dimensions.

The result contains one row per sample and one column per generated component. The component axes have no inherent biological meaning; the embedding is intended primarily to represent local sample similarities and can be visualized with a subsequent Scatter Plot step. Missing intensities must be handled before calculation.

The calculation uses [`sklearn.manifold.TSNE`](https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html).

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/dimension_reduction.py:t_sne"
```
