# Filter Samples: Sum of Intensities

For each sample $s$, calculates the total protein intensity $S_s$ in the active intensity column:

$$
S_s = \sum_i I_{i,s}.
$$

Let $\tilde{S}$ be the median and $\sigma$ the standard deviation of these sums across all samples. The sample is retained iff

$$
\left|S_s - \tilde{S}\right| \leq \tau \cdot \sigma,
$$

where $\tau$ is the selected maximum deviation from the median in units of standard deviations.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/filter_samples.py:by_protein_intensity_sum"
```
