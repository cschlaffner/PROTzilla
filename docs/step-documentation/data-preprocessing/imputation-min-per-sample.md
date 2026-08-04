# Imputation: Min per Sample

Determines the smallest measured intensity separately for each sample. Missing values are replaced with the minimum intensity of the corresponding sample, multiplied by the selected shrinking value.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/imputation.py:by_min_per_protein"
```
