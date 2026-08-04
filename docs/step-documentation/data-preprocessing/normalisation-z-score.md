# Normalisation: Z-Score

Standardises the intensities in each sample so that they have a mean of zero and a standard deviation of one:

$$
I_{\text{norm}} =
\frac{I - \mu_{\text{Sample}}}{\sigma_{\text{Sample}}}
$$

Here, $I$ is the original intensity, $\mu_{\text{Sample}}$ is the arithmetic mean, and $\sigma_{\text{Sample}}$ is the standard deviation of the intensities in the sample.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/normalisation.py:by_z_score"
```
