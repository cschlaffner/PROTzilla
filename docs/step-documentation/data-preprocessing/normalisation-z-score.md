# Normalisation: Z-Score

For each sample $s$, calculates the mean $\mu_s$ and standard deviation $\sigma_s$ of its measured protein intensities. Each measured intensity is then standardised by

$$
\hat{x}_{s,p} = \frac{x_{s,p} - \mu_s}{\sigma_s}.
$$

Consequently, the standardised intensities of each sample have mean $0$ and standard deviation $1$. If $\sigma_s=0$, all measured intensities of the affected sample are set to zero. Missing intensities remain missing.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/normalisation.py:by_z_score"
```
