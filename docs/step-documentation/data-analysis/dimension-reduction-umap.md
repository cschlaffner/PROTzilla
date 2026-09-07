# Dimension Reduction: UMAP

Embeds the sample intensity vectors into a selected number of dimensions. UMAP constructs a weighted nearest-neighbor graph from the samples using the selected distance metric and optimizes the embedded coordinates to preserve these local graph relationships.

The number of neighbors controls the scale of the structure considered: smaller values emphasize local neighborhoods, while larger values include broader relationships between samples. The minimum distance controls how closely neighboring points may be placed in the embedding; smaller values permit more compact groups.

The result contains one row per sample and one column per generated component. The component axes have no inherent biological meaning, and the stochastic embedding can vary with the selected random seeds. It can be visualized with a subsequent Scatter Plot step. Missing intensities must be handled before calculation.

The calculation uses [`umap.UMAP`](https://umap-learn.readthedocs.io/en/latest/api.html#umap.umap_.UMAP).

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/dimension_reduction.py:umap"
```
