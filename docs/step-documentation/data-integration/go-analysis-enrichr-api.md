# GO Analysis (Enrichr API)

Performs an online over-representation analysis through GSEApy and the Enrichr API. Let $v_i$ be the value in the selected differential-expression column for protein group $i$, and let $\tau$ be the selected threshold. If the column name contains `log`, the analyzed sets are

$$
U=\{i\mid v_i>\tau\},
\qquad
D=\{i\mid v_i<-\tau\}.
$$

Otherwise, $U=\{i\mid v_i>\tau\}$ and $D=\{i\mid v_i<\tau\}$. Depending on the selected direction, $U$, $D$, or both sets are analyzed separately.

Protein groups are mapped to gene symbols using the given gene-mapping table. Groups without a mapping are excluded and returned separately. For query genes $Q$, background genes $B$, and gene set $G$, enrichment is tested from the overlap $x=|Q\cap G|$ using the upper tail of the hypergeometric distribution:

$$
p_G=\Pr(X\geq x),
\qquad
X\sim\operatorname{Hypergeom}(|B|,|G\cap B|,|Q\cap B|).
$$

Gene sets may be uploaded or selected from Enrichr. The background may be supplied as a gene list, a gene count, a BioMart dataset, or the union of all genes in the uploaded gene sets. When an Enrichr library is selected, the custom background settings are ignored. If both directions are analyzed, matching terms are combined and the current implementation retains the statistics with the greater adjusted p-value.

See the [GSEApy Enrichr documentation](https://gseapy.readthedocs.io/en/latest/run.html#enrichr-api) for details about the analysis and background options.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_integration/enrichment_analysis.py:GO_analysis_with_Enrichr"
```
