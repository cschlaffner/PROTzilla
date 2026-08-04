# Filter Samples: Missing Proteins

Filters the given protein table by the proportion of unique proteins with a non-missing intensity in each sample. A sample is retained only if this proportion is at least the selected percentage of all unique proteins in the table.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/filter_samples.py:by_proteins_missing"
```
