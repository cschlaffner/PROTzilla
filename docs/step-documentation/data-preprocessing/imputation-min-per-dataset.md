# Imputation: Min per Dataset

Replaces every missing protein intensity with $\lambda \cdot x_{\min}$, where $x_{\min}$ is the smallest measured intensity in the complete dataset and $\lambda$ is the selected shrinking value, which defaults to $1$.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/imputation.py:by_min_per_dataset"
```
