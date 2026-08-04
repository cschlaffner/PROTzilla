# Filter Proteins: Missing Samples

Filters the given protein table by the proportion of samples containing a non-missing intensity for each protein. A protein is retained only if this proportion is at least the selected percentage.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/filter_proteins.py:by_samples_missing"
```
