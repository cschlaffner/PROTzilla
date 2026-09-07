# Diff. Expression: Kruskal-Wallis Test

Performs a Kruskal-Wallis H test independently for each protein $p$ across the selected metadata groups. For $k$ groups, the null hypothesis is

$$
H_0:F_{1,p}=F_{2,p}=\dots=F_{k,p}.
$$

All intensities of the protein are ranked jointly. [`scipy.stats.kruskal`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kruskal.html) calculates the tie-corrected statistic $H_p$ from the group rank sums and its p-value $p_p$. Proteins for which no valid p-value can be calculated are excluded.

The selected multiple-testing correction produces the value $q_p$ and significance threshold $\alpha^*$:

- **None:** $q_p=p_p$ and $\alpha^*=\alpha$.
- **Benjamini-Hochberg:** $q_p$ is the adjusted p-value and $\alpha^*=\alpha$.
- **Bonferroni:** $q_p=p_p$ and $\alpha^*=\alpha/m$, where $m$ is the number of valid proteins tested.

A protein is considered significant iff

$$
q_p \leq \alpha^*.
$$

The test compares all selected groups simultaneously. It does not determine which individual groups differ.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/differential_expression_kruskal_wallis.py:kruskal_wallis_test_on_intensity_data"
```
