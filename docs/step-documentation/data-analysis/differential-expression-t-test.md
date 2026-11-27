# Diff. Expression: t-Test

Performs an independent two-sample t-test separately for each protein $p$ between the two selected metadata groups. Student's t-test assumes equal group variances, whereas Welch's t-test does not. Each group must contain at least two non-missing intensities for the protein; otherwise, the protein is excluded. The test is equivalent to [`scipy.stats.ttest_ind`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html).

Let $p_p$ be the resulting two-sided p-value. The selected multiple-testing correction produces the value $q_p$ and significance threshold $\alpha^*$:

- **None:** $q_p=p_p$ and $\alpha^*=\alpha$.
- **Benjamini-Hochberg:** $q_p$ is the adjusted p-value and $\alpha^*=\alpha$.
- **Bonferroni:** $q_p=p_p$ and $\alpha^*=\alpha/m$, where $m$ is the number of valid proteins tested.

Without the optional fold-change filter, a protein is considered significant iff

$$
q_p \leq \alpha^*.
$$

Let $\tilde{x}_{1,p}$ and $\tilde{x}_{2,p}$ be the median intensities of protein $p$ in groups 1 and 2. The log2 fold change is

$$
\operatorname{log2FC}_p=
\begin{cases}
\log_2\left(\dfrac{\tilde{x}_{2,p}}{\tilde{x}_{1,p}}\right), & \text{for untransformed data},\\
(\tilde{x}_{2,p}-\tilde{x}_{1,p})\log_2(b), & \text{for data transformed with logarithm base }b.
\end{cases}
$$

A positive value indicates a higher median intensity in group 2; a negative value indicates a higher median intensity in group 1.

If **Fold-change Z-score significance** is enabled, the fold changes are standardized relative to their median using separate scales below and above the median. The resulting upper-tail probability $c_p$ must additionally satisfy

$$
c_p \leq \alpha_{\mathrm{FC}}.
$$

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/differential_expression_t_test.py:t_test"
```
