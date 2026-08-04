# Filter Peptides: Existing Proteins

Filters the given peptide table against the given protein table. Only peptide rows whose `Protein ID` occurs in the protein table are retained.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/filter_peptides_or_psm.py:by_existing_proteins"
```
