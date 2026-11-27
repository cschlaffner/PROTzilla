# GO Results: Bar Plot

Creates a horizontal bar plot from selected gene-set categories of a GO enrichment result. Terms are shown on the y-axis, and bars are colored by gene-set category.

In `fdr` mode, only STRING results are accepted. Terms with $\operatorname{FDR}\leq\tau$ are retained and plotted by

$$
-\log_{10}(\operatorname{FDR}),
$$

where $\tau$ is the selected cutoff. The selected number of terms with the greatest transformed values is shown per category.

In `p-value` mode, STRING results use the raw p-value and Enrichr or offline results use the adjusted p-value. The current implementation does not apply the selected cutoff or a $-\log_{10}$ transformation in this mode; it sorts the raw values in descending order and retains the selected number of rows per category.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_integration/di_plots.py:GO_enrichment_bar_plot"
```
