# PTM Diff. Exp.: Kruskal-Wallis Test

First normalizes each PTM value $x_{s,j}$ by the total number of peptides $T_s$ in sample $s$:

$$
r_{s,j}=\frac{x_{s,j}}{T_s}.
$$

A Kruskal-Wallis H test is then performed independently for each PTM $j$ across the selected metadata groups. For $k$ groups, the null hypothesis is

$$
H_0:F_{1,j}=F_{2,j}=\dots=F_{k,j},
$$

where $F_{g,j}$ is the distribution of the normalized PTM values in group $g$. All normalized values of the PTM are ranked jointly. [`scipy.stats.kruskal`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kruskal.html) calculates the tie-corrected statistic $H_j$ from the group rank sums and its p-value $p_j$. PTMs for which no valid p-value can be calculated are excluded.

The selected multiple-testing correction produces the value $q_j$ and significance threshold $\alpha^*$:

- **None:** $q_j=p_j$ and $\alpha^*=\alpha$.
- **Benjamini-Hochberg:** $q_j$ is the adjusted p-value and $\alpha^*=\alpha$.
- **Bonferroni:** $q_j=p_j$ and $\alpha^*=\alpha/m$, where $m$ is the number of valid PTMs tested.

A PTM is considered significant iff

$$
q_j \leq \alpha^*.
$$

The test compares all selected groups simultaneously. It does not determine which individual groups differ.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/differential_expression_kruskal_wallis.py:kruskal_wallis_test_on_ptm_data"
```
