# Group Replicates

Let $S_g$ be the set of samples assigned to group $g$. For each protein $p$, the intensities $x_{s,p}$ of all samples $s\in S_g$ are combined using the selected method.

If **`sum`** is selected, the intensities are added:

$$
\hat{x}_{g,p}=\sum_{s\in S_g}x_{s,p}.
$$

If **`mean`** is selected, their arithmetic mean is calculated.

If **`median`** is selected, their median is calculated.

If **`min`** is selected, the smallest intensity is selected.

If **`max`** is selected, the largest intensity is selected.

Each group value becomes the new `Sample` identifier. Samples without a matching metadata row are excluded. The resulting protein table contains the `Protein ID`, new `Sample`, and aggregated intensity columns.

Missing intensities are ignored during aggregation. If every replicate intensity in a group is missing, `sum` returns zero, while the other methods return a missing value.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/simplification.py:group_replicates"
```
