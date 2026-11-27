# Scatter Plot

Plots each sample as a point using the two or three numeric columns of the given table as coordinates. Two columns produce a two-dimensional scatter plot; three columns produce a three-dimensional scatter plot. If a metadata column is provided, points are colored by its value for the corresponding sample.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/plots.py:scatter_plot"
```
