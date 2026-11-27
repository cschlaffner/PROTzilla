# Imputation: Min per Protein

For each protein $p$, replaces every missing intensity with $\lambda \cdot x_{\min,p}$, where $x_{\min,p}$ is the smallest measured intensity of protein $p$ across all samples and $\lambda$ is the selected shrinking value, which defaults to $1$.

Proteins without a measured intensity in any sample are removed before imputation.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/imputation.py:by_min_per_protein"
```
