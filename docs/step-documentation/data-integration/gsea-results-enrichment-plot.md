# GSEA Results: Enrichment Plot

Creates the detailed enrichment plot for one gene set from a GSEA or preranked-GSEA result. The plot combines the running enrichment score across the ranked genes, the positions at which members of the selected gene set occur, and the value of the ranking metric.

The extremum of the running score is the enrichment score. Gene-set members before this extremum for a positive ES, or after it for a negative ES, form the leading-edge subset. Optional phenotype labels identify the positive and negative ends of the ranking. See the [GSEA User Guide](https://docs.gsea-msigdb.org/GSEA/GSEA_User_Guide/#enrichment-score-es) for the interpretation of the plot.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_integration/di_plots.py:gsea_enrichment_plot"
```
