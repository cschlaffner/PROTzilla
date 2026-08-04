# Imputation: per Protein

Replaces missing values using a central value calculated separately for each protein. The available strategies are:

- **Mean:** arithmetic mean of the measured intensities
- **Median:** median of the measured intensities
- **Most frequent:** most frequently occurring intensity

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/imputation.py:by_simple_imputer"
```
