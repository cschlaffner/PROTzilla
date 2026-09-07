# Imputation: Normal Distribution Sampling

Replaces each missing protein intensity $x_{s,p}$ with

$$
\hat{x}_{s,p} = 10^{Z_{s,p}},
$$

where $Z_{s,p}$ is sampled on the $\log_{10}$ scale. For the per-protein strategy,

$$
Z_{s,p} \sim \mathcal{N}\left(\mu_p + d \cdot \sigma_p,\;(c \cdot \sigma_p)^2\right),
$$

where $\mu_p$ and $\sigma_p$ are the mean and standard deviation of the measured $\log_{10}$ intensities of protein $p$. For the per-dataset strategy, the corresponding statistics $\mu$ and $\sigma$ are calculated across the complete dataset; PROTzilla uses $\max(0, \mu + d \cdot \sigma)$ as the sampling mean and reflects negative sampled values to the positive side.

Here, $d$ is the selected downshift and $c$ is the selected scaling factor. The form defaults are $d=-1$ and $c=0.5$. Per-protein imputation requires at least two measured intensities for the respective protein; otherwise, its missing values remain unchanged. Since values are sampled randomly, repeated calculations can produce different results. This method assumes positive measured intensities because the calculations use a $\log_{10}$ transformation.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/imputation.py:by_normal_distribution_sampling"
```
