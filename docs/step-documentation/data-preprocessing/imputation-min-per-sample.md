# Imputation: Min per Sample

For each sample $s$, replaces every missing protein intensity with $\lambda \cdot x_{\min,s}$, where $x_{\min,s}$ is the smallest measured protein intensity in sample $s$ and $\lambda$ is the selected shrinking value, which defaults to $1$.

If a sample contains no measured protein intensity, its missing values remain unchanged.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/imputation.py:by_min_per_sample"
```
