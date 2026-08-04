# Normalisation: Median

Normalises the intensities of each sample by dividing every value by a selected quantile of that sample. The median, corresponding to the 50th percentile, is used by default. A different quantile can be selected through the `percentile` parameter.

For each sample, the calculation is:

$$
I_{\text{norm}} = \frac{I}{Q_p(\text{Sample})}
$$

Here, $I$ is the original intensity and $Q_p(\text{Sample})$ is the selected quantile of the intensities in that sample.

If the selected quantile is zero, all intensities of the affected sample are set to zero and a warning is returned.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/normalisation.py:by_median"
```
