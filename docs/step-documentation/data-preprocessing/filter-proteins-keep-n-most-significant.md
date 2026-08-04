# Filter Proteins: Keep n Most Significant

Filters the given differential-expression table to retain the selected number of most significant proteins. Proteins are ranked by `corrected_p_value` in ascending order, so smaller values are considered more significant. Duplicate `Protein ID` entries are removed, keeping the entry with the smallest corrected p-value.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/filter_proteins.py:keep_n_most_significant_proteins"
```
