# Filter Samples: #Proteins / Sample

For each sample $s$, calculates the number $c_s$ of unique proteins with a non-missing intensity:

$$
c_s = \text{number of unique proteins with a non-missing intensity in sample } s.
$$

Let $\tilde{c}$ be the median and $\sigma$ the standard deviation of these counts across all samples. The sample is retained iff

$$
\left|c_s - \tilde{c}\right| \leq \tau \cdot \sigma,
$$

where $\tau$ is the selected maximum deviation from the median in units of standard deviations.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/filter_samples.py:by_protein_count"
```
