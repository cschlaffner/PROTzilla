# Clustergram

Displays the given protein intensities as a heatmap and hierarchically clusters both samples and proteins. The distance between two samples $a$ and $b$ is the Euclidean distance across all proteins,

$$
d(a,b)=\sqrt{\sum_p\left(x_{a,p}-x_{b,p}\right)^2},
$$

and proteins are compared analogously across samples. Complete linkage defines the distance between two clusters $A$ and $B$ as

$$
D(A,B)=\max_{a\in A,\,b\in B}d(a,b).
$$

The heatmap rows and columns are ordered according to the resulting dendrograms. Missing intensities are imputed per protein using the selected strategy before clustering. An optional metadata column annotates the samples, while flipping the axes changes only the plot orientation.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/plots.py:clustergram_plot"
```
