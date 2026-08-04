# Imputation: Min per Dataset

Replaces missing values with the smallest measured intensity in the complete dataset, multiplied by the selected shrinking value.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/imputation.py:by_min_per_dataset"
```
