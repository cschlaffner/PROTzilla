# Diff. Expression: ANOVA

Performs a one-way ANOVA independently for each protein $p$ across the selected metadata groups using the active intensity column. The test is calculated with [`scipy.stats.f_oneway`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f_oneway.html), which also documents its assumptions.

Let $p_p$ be the resulting p-value for protein $p$. Proteins for which no valid p-value can be calculated are excluded. The selected multiple-testing correction produces the value $q_p$ and significance threshold $\alpha^*$ used for the final decision:

- **None:** $q_p=p_p$ and $\alpha^*=\alpha$.
- **Benjamini-Hochberg:** $q_p$ is the adjusted p-value and $\alpha^*=\alpha$.
- **Bonferroni:** $q_p=p_p$ and $\alpha^*=\alpha/m$, where $m$ is the number of valid proteins tested.

A protein is considered significant iff

$$
q_p < \alpha^*.
$$

The ANOVA tests all selected groups simultaneously. It does not determine which individual groups differ.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/differential_expression_anova.py:anova"
```
