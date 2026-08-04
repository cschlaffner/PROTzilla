# Filter Proteins: #Values / Group

Filters the given protein table using the group assignments from the given metadata table. A protein is retained only if every group contains at least the selected minimum number of distinct, non-missing intensity values for that protein.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/filter_proteins.py:by_number_of_values_per_group"
```
