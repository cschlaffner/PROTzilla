# GSEA Results: Dot Plot

Creates a dot plot from a GSEA or preranked-GSEA result. A term is shown iff its selected significance value satisfies

$$
q_G\leq\tau,
$$

where $q_G$ is either the FDR q-value or the nominal p-value and $\tau$ is the selected cutoff. The x-axis shows either the enrichment score or normalized enrichment score, while dot color represents $-\log_{10}(q_G)$.

Dot area is proportional to the `Tag %` ratio: the fraction of members of the gene set that occur before the running-score peak for a positive ES or after the peak for a negative ES. Library-name prefixes separated from term names by `__` can optionally be removed.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_integration/di_plots.py:gsea_dot_plot"
```
