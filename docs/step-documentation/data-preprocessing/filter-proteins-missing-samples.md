# Filter Proteins: Missing Samples

For each protein $i$, calculates the fraction $r_i$ of samples with a non-missing intensity:

$$
r_i =
\frac{\text{number of samples with a non-missing intensity for protein } i}
{\text{total number of samples}}.
$$

The protein is retained if $r_i \geq \tau$, where $\tau \in [0,1]$ is the selected minimum fraction of samples.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/filter_proteins.py:by_samples_missing"
```
