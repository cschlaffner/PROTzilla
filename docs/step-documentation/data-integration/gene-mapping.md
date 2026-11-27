# Gene Mapping

Maps the `Protein ID` values of the given protein table to gene symbols. Semicolon-separated protein groups are split into individual UniProt identifiers, and isoform or variant suffixes are removed before lookup.

The selected local UniProt databases are queried in order. The primary gene name is used when available; otherwise, the first entry in `Gene Names` is used. If BioMart is enabled, identifiers not resolved by the local databases are additionally mapped online to HGNC symbols through the human Ensembl dataset.

The resulting table contains one `(Protein ID, Gene)` row for every mapped member while preserving the original protein-group identifier. Protein groups for which no member can be mapped are returned separately as `filtered_protein_ids`.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_integration/database_integration.py:gene_mapping"
```
