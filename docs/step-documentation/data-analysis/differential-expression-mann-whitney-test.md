# Diff. Expression: Mann-Whitney Test

Performs a two-sided Mann-Whitney U test independently for each protein $p$ between the two selected metadata groups. The null hypothesis is that the intensity distributions in both groups are equal:

$$
H_0:F_{1,p}=F_{2,p}.
$$

Let $n_{1,p}$ be the number of observations in group 1 and $R_{1,p}$ their rank sum within the pooled observations. The reported statistic for group 1 is

$$
U_{1,p}=R_{1,p}-\frac{n_{1,p}(n_{1,p}+1)}{2}.
$$

The test is calculated with [`scipy.stats.mannwhitneyu`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html). The selected **Exact**, **Asymptotic**, or **Auto** method determines how its two-sided p-value $p_p$ is calculated. Proteins for which no valid p-value can be calculated are excluded.

The selected multiple-testing correction produces the value $q_p$ and significance threshold $\alpha^*$:

- **None:** $q_p=p_p$ and $\alpha^*=\alpha$.
- **Benjamini-Hochberg:** $q_p$ is the adjusted p-value and $\alpha^*=\alpha$.
- **Bonferroni:** $q_p=p_p$ and $\alpha^*=\alpha/m$, where $m$ is the number of valid proteins tested.

A protein is considered significant iff

$$
q_p \leq \alpha^*.
$$

Let $\bar{x}_{1,p}$ and $\bar{x}_{2,p}$ be the arithmetic mean intensities in groups 1 and 2. The log2 fold change is

$$
\operatorname{log2FC}_p=
\begin{cases}
\log_2\left(\dfrac{\bar{x}_{2,p}}{\bar{x}_{1,p}}\right), & \text{for untransformed data},\\
\log_2\left(\dfrac{\overline{b^x}_{2,p}}{\overline{b^x}_{1,p}}\right), & \text{for data transformed with logarithm base }b.
\end{cases}
$$

Here, $\overline{b^x}_{g,p}$ is the arithmetic mean after transforming the intensities of group $g$ back to their original scale. A positive fold change indicates a higher mean intensity in group 2; a negative value indicates a higher mean intensity in group 1.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/differential_expression_mann_whitney.py:mann_whitney_test_on_intensity_data"
```
