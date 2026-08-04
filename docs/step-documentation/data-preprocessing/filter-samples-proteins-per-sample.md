# Filter Samples: #Proteins / Sample

Filters the given protein table based on the number of unique proteins with a non-missing intensity in each sample. The median and standard deviation of these protein counts are calculated across all samples. A sample is retained only if its protein count lies within the following range:

$$
\left[
\text{Median} - (\text{Threshold} \cdot \sigma),
\;
\text{Median} + (\text{Threshold} \cdot \sigma)
\right]
$$


The threshold specifies the maximum allowed deviation from the median in units of standard deviations.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/filter_samples.py:by_protein_count"
```
