# Filter Samples: Sum of Intensities

Filters the given protein table based on the total protein intensity of each sample. First, the protein intensities are summed separately for every sample:

$$
S_{\text{Sample}} = \sum_{i=1}^{n} I_{i,\text{Sample}}
$$

Here, $I_{i,\text{Sample}}$ is the intensity of protein $i$ in the active intensity column, and $S_{\text{Sample}}$ is the resulting intensity sum.

The median and standard deviation of these sums are then calculated across all samples. A sample is retained only if its intensity sum lies within the following range:

$$
\left[
\text{Median} - (\text{Threshold} \cdot \sigma),
\;
\text{Median} + (\text{Threshold} \cdot \sigma)
\right]
$$

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/filter_samples.py:by_protein_intensity_sum"
```
