# Filter Proteins: Keep n Most Significant

Sorts the given differential-expression table by `corrected_p_value` in ascending order. Duplicate `Protein ID` entries are removed, retaining the entry with the smallest corrected p-value. The first $n$ proteins of the resulting ranked table are retained, where $n$ is the selected number of proteins.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/filter_proteins.py:keep_n_most_significant_proteins"
```
