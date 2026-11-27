# GO Analysis (STRING API)

Performs an online functional over-representation analysis through the STRING API. Let $v_i$ be the value in the selected differential-expression column for protein group $i$, and let $\tau$ be the selected threshold. If the column name contains `log`, the analyzed sets are

$$
U=\{i\mid v_i>\tau\},
\qquad
D=\{i\mid v_i<-\tau\}.
$$

Otherwise, $U=\{i\mid v_i>\tau\}$ and $D=\{i\mid v_i<\tau\}$. Depending on the selected direction, $U$, $D$, or both sets are analyzed separately.

Semicolon-separated protein groups are split into individual UniProt identifiers and cleaned before they are submitted to STRING. The selected NCBI taxonomy identifier specifies the organism. An optional file defines the statistical background; without one, STRING uses the entire proteome. Results are restricted to the selected STRING knowledge bases.

If both directions are analyzed, equal `(Gene_set, term)` results are combined. Their proteins and gene names are merged, while the current implementation retains the statistics of the result with the greater p-value. See the [STRING API documentation](https://string-db.org/help/api/) for details about the enrichment service.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_integration/enrichment_analysis.py:GO_analysis_with_STRING"
```
