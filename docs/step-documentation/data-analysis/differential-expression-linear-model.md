# Diff. Expression: Linear Model

Fits an ordinary least-squares model independently for each protein $p$ using the two selected metadata groups. For sample $s$, the groups are encoded as $z_s=-1$ for group 1 and $z_s=1$ for group 2:

$$
y_{s,p}=\beta_{0,p}+\beta_{1,p}z_s+\varepsilon_{s,p},
$$

where $y_{s,p}$ is the active intensity. The p-value tests $H_0:\beta_{1,p}=0$. The model is fitted with [`statsmodels.OLS`](https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.OLS.html).

A protein is excluded if either selected group contains a missing intensity, has no measurement, or the model produces no valid p-value. Let $p_p$ be the resulting p-value for each valid protein. The selected multiple-testing correction produces the value $q_p$ and significance threshold $\alpha^*$:

- **None:** $q_p=p_p$ and $\alpha^*=\alpha$.
- **Benjamini-Hochberg:** $q_p$ is the adjusted p-value and $\alpha^*=\alpha$.
- **Bonferroni:** $q_p=p_p$ and $\alpha^*=\alpha/m$, where $m$ is the number of valid proteins tested.

A protein is considered significant iff

$$
q_p \leq \alpha^*.
$$

Let $\bar{y}_{1,p}$ and $\bar{y}_{2,p}$ be the arithmetic mean intensities in groups 1 and 2. The log2 fold change is

$$
\operatorname{log2FC}_p=
\begin{cases}
\log_2\left(\dfrac{\bar{y}_{2,p}}{\bar{y}_{1,p}}\right), & \text{for untransformed data},\\
\log_2\left(\dfrac{\overline{b^y}_{2,p}}{\overline{b^y}_{1,p}}\right), & \text{for data transformed with logarithm base }b.
\end{cases}
$$

Here, $\overline{b^y}_{g,p}$ is the arithmetic mean after transforming the intensities of group $g$ back to their original scale. A positive fold change indicates a higher mean intensity in group 2; a negative value indicates a higher mean intensity in group 1.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/differential_expression_linear_model.py:linear_model"
```
