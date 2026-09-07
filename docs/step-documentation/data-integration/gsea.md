# GSEA

Performs Gene Set Enrichment Analysis for two groups from the selected metadata column. Only samples assigned to either selected group are retained. Protein groups are mapped to gene symbols using the given gene-mapping table; unmapped groups are excluded. If one protein group maps to multiple genes, its intensity profile is assigned to each gene. If multiple protein groups map to the same gene, their intensities are averaged separately for every sample.

The selected ranking method orders the genes according to their differences between the two groups. For each gene set, GSEA calculates a weighted running sum along this ranking. The enrichment score is its greatest signed deviation from zero; positive and negative scores indicate enrichment at opposite ends of the ranking. Only gene sets whose overlap with the data lies between the selected minimum and maximum size are analyzed.

The selected permutations estimate the nominal p-value and normalize the enrichment score to the NES. The result contains the ES, NES, nominal p-value, FDR q-value, leading-edge genes, corresponding protein groups, and the calculated gene ranking. The formal method and interpretation are described in the [GSEA User Guide](https://docs.gsea-msigdb.org/GSEA/GSEA_User_Guide/#gsea-statistics).

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_integration/enrichment_analysis_gsea.py:gsea"
```
