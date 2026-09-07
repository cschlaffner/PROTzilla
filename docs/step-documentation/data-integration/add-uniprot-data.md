# Add UniProt Data

Adds selected fields from a local UniProt database to the given protein table. Each semicolon-separated protein group is split into individual identifiers, and isoform or variant suffixes are removed before lookup.

For every selected field, the values of all members of a protein group are collected. If all members have the same value, that value is stored once; otherwise, the member values are joined with semicolons. For a `Gene Names` field, only the first space-separated gene name of each database entry is used. Selecting `Links` adds one UniProt URL for every member of the protein group.

The original rows and `Protein ID` values are retained, and the enriched protein table is returned.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_integration/database_integration.py:add_uniprot_data"
```
