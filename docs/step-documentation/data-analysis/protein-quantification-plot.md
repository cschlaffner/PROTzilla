# Protein Quantification Plot

Plots the intensity $x_{s,p}$ of a selected protein group $p$ across all samples $s$. The shaded region spans the minimum and maximum protein intensity in each sample.

To identify protein groups with a similar profile, every protein group is standardized across samples:

$$
z_{s,p}=\frac{x_{s,p}-\bar{x}_p}{\sigma_p}.
$$

For a selected reference group $r$, another group $p$ is shown as similar iff either its Euclidean distance

$$
d(p,r)=\sqrt{\sum_s\left(z_{s,p}-z_{s,r}\right)^2}
$$

is at most the selected threshold, or its cosine similarity

$$
c(p,r)=\frac{\sum_s z_{s,p}z_{s,r}}{\sqrt{\sum_s z_{s,p}^2}\sqrt{\sum_s z_{s,r}^2}}
$$

is at least the selected threshold. The plotted profiles retain their original intensity scale.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/plots.py:prot_quant_plot"
```
