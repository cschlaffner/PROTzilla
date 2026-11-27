# Filter PSMs: Existing Proteins

Filters the given PSM table against the given protein table. A PSM row is retained iff its `Protein ID` occurs in the protein table.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/filter_peptides_or_psm.py:by_existing_proteins"
```
