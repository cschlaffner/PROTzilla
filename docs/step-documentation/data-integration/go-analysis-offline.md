# GO Analysis (Offline)

Performs a local over-representation analysis against uploaded gene sets. Protein groups are selected from the given differential-expression column exactly as in the online GO steps: for a column containing `log`, $v_i>\tau$ defines the upregulated set and $v_i<-\tau$ the downregulated set; otherwise, the conditions are $v_i>\tau$ and $v_i<\tau$, respectively.

Protein groups are mapped to gene symbols using the given gene-mapping table. Groups without a mapping are excluded and returned separately. For query genes $Q$, background genes $B$, and gene set $G$, GSEApy calculates

$$
p_G=\Pr(X\geq |Q\cap G|),
\qquad
X\sim\operatorname{Hypergeom}(|B|,|G\cap B|,|Q\cap B|).
$$

The background may be provided as a gene list or as the number of expressed genes. If no explicit background is selected, the union of all genes in the uploaded gene sets is used. Upregulated and downregulated proteins can be analyzed separately or together. Matching terms from both directions are combined, and the current implementation retains the statistics with the greater adjusted p-value.

The calculation uses GSEApy's local `enrich` function and therefore does not submit the analysis to Enrichr. See the [GSEApy documentation](https://gseapy.readthedocs.io/en/latest/gseapy_example.html#over-representation-analysis-offline-hypergeometric-test) for details.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_integration/enrichment_analysis.py:GO_analysis_offline"
```
