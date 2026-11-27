# Filter Proteins: Specific IDs

Filters the given protein table by a specified list of protein identifiers. Only rows whose `Protein ID` matches one of the provided IDs are retained.

Example identifiers include UniProt IDs such as `P00533`, `Q9Y6K9`, or `A0A0B4J1V0`.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/filter_proteins.py:by_protein_ids"
```
