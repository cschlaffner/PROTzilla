# Filter Samples: Missing Proteins

For each sample $s$, calculates the fraction $r_s$ of unique proteins with a non-missing intensity:

$$
r_s =
\frac{\text{number of unique proteins with a non-missing intensity in sample } s}
{\text{total number of unique proteins}}.
$$

The sample is retained iff $r_s \geq \tau$, where $\tau \in [0,1]$ is the selected minimum fraction of proteins.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/filter_samples.py:by_proteins_missing"
```
