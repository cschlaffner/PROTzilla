# PTM Diff. Exp.: Mann-Whitney Test

First normalizes each PTM value $x_{s,j}$ by the total number of peptides $T_s$ in sample $s$:

$$
r_{s,j}=\frac{x_{s,j}}{T_s}.
$$

A two-sided Mann-Whitney U test is then performed independently for each PTM $j$ between the two selected metadata groups. The null hypothesis is

$$
H_0:F_{1,j}=F_{2,j},
$$

where $F_{1,j}$ and $F_{2,j}$ are the distributions of the normalized PTM values in groups 1 and 2. Let $n_{1,j}$ be the number of observations in group 1 and $R_{1,j}$ their rank sum within the pooled observations. The reported statistic for group 1 is

$$
U_{1,j}=R_{1,j}-\frac{n_{1,j}(n_{1,j}+1)}{2}.
$$

The test is calculated with [`scipy.stats.mannwhitneyu`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html). The selected **Exact**, **Asymptotic**, or **Auto** method determines how its two-sided p-value $p_j$ is calculated. PTMs for which no valid p-value can be calculated are excluded.

The selected multiple-testing correction produces the value $q_j$ and significance threshold $\alpha^*$:

- **None:** $q_j=p_j$ and $\alpha^*=\alpha$.
- **Benjamini-Hochberg:** $q_j$ is the adjusted p-value and $\alpha^*=\alpha$.
- **Bonferroni:** $q_j=p_j$ and $\alpha^*=\alpha/m$, where $m$ is the number of valid PTMs tested.

A PTM is considered significant iff

$$
q_j \leq \alpha^*.
$$

Let $\bar{r}_{1,j}$ and $\bar{r}_{2,j}$ be the arithmetic means of the normalized PTM values in groups 1 and 2. The log2 fold change is

$$
\operatorname{log2FC}_j=
\begin{cases}
\log_2\left(\dfrac{\bar{r}_{2,j}}{\bar{r}_{1,j}}\right), & \text{for untransformed data},\\
\log_2\left(\dfrac{\overline{b^r}_{2,j}}{\overline{b^r}_{1,j}}\right), & \text{for data transformed with logarithm base }b.
\end{cases}
$$

Here, $\overline{b^r}_{g,j}$ is the arithmetic mean after transforming the normalized PTM values of group $g$ back with base $b$. A positive fold change indicates a higher mean in group 2; a negative value indicates a higher mean in group 1.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/differential_expression_mann_whitney.py:mann_whitney_test_on_ptm_data"
```
