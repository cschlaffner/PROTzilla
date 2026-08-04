# Imputation: Normal Distribution Sampling

Replaces missing values with random values sampled from a normal distribution:

$$
I_{\text{imputed}} \sim
\mathcal{N}\left(
\mu_{\text{ref}} + \text{Downshift},
\sigma_{\text{ref}} \cdot \text{Scaling Factor}
\right)
$$

Here, $\mu_{\text{ref}}$ is the arithmetic mean and $\sigma_{\text{ref}}$ is the standard deviation of the available intensities. Depending on the selected strategy, these values are calculated for the complete dataset or separately for each protein.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/imputation.py:by_normal_distribution_sampling"
```
