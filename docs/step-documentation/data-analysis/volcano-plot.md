# Volcano Plot

Visualizes the corrected p-value $q_i$ and log2 fold change $L_i$ of each protein or PTM $i$ as

$$
(x_i,y_i)=(L_i,-\log_{10}(q_i)).
$$

The horizontal line represents the significance threshold $\alpha$, and the vertical lines represent the selected absolute log2 fold-change threshold $\tau$. Items beyond both thresholds, $q_i<\alpha$ and $|L_i|>\tau$, are highlighted as significant. A positive fold change indicates a higher value in group 2 than in group 1. Selected items of interest are labelled in the plot.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/plots.py:create_volcano_plot"
```
