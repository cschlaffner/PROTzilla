# Filter Metadata: Existing Samples

Filters the given metadata table against the given protein table. A metadata row is retained iff the value in the selected sample column occurs in the `Sample` column of the protein table.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/simplification.py:metadata_filter_by_samples"
```
