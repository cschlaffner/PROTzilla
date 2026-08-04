# Normalisation: Total Sum

Normalises the intensities of each sample by dividing every value by the sum of all intensities in that sample:

$$
I_{\text{norm}} = \frac{I}{\sum I_{\text{Sample}}}
$$

Here, $I$ is the original intensity and $\sum I_{\text{Sample}}$ is the sum of all intensities in the corresponding sample.

If the intensity sum of a sample is zero, all intensities of that sample are set to zero and a warning is returned.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/normalisation.py:by_totalsum"
```
