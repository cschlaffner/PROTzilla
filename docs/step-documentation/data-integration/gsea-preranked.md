# GSEA (Preranked)

Performs GSEA on a ranking supplied through a numeric column of the given protein table. Protein groups are mapped to gene symbols using the given gene-mapping table; unmapped groups are excluded. If one protein group maps to multiple genes, its ranking value is assigned to each gene.

If several protein groups map to the same gene, the less favorable value is retained: the greatest value for an ascending ranking and the smallest value for a descending ranking. The resulting genes are sorted in the selected direction before GSEA is applied.

For each gene set, the enrichment score is the greatest signed deviation of a weighted running sum along the supplied ranking. Gene sets are restricted by the selected minimum and maximum overlap size, and permutations determine the nominal p-value, NES, and FDR q-value. The result contains the enrichment statistics, leading-edge genes and protein groups, the final ranking, and all protein groups that could not be mapped. See the [GSEA User Guide](https://docs.gsea-msigdb.org/GSEA/GSEA_User_Guide/#using-gseapreranked) for the formal method.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_integration/enrichment_analysis_gsea.py:gsea_preranked"
```
