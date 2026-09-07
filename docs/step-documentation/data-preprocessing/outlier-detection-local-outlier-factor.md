# Outlier Detection: Local Outlier Factor

Represents each sample $s$ by its protein-intensity vector $x_s=(x_{s,1},\ldots,x_{s,m})$. Because missing intensities are not accepted, distances between samples are calculated using the Euclidean distance:

$$
d(s,t) = \sqrt{\sum_{p=1}^{m}\left(x_{s,p}-x_{t,p}\right)^2}.
$$

For each sample $s$, the $k$ other samples with the smallest distances to $s$ form its neighborhood $N_k(s)$. The selected number of neighbors defines $k$ and defaults to $20$. Its local density $\rho_k(s)$ is derived from the distances to these neighbors. More precisely, $\rho_k(s)$ is the reciprocal of the mean reachability distance $\max\{d(s,t),d_k(t)\}$ for $t\in N_k(s)$, where $d_k(t)$ is the distance from $t$ to its $k$th nearest sample.

The Local Outlier Factor compares this density with the average local density of the neighboring samples:

$$
\operatorname{LOF}_k(s)
=
\frac{\frac{1}{|N_k(s)|}\sum_{t\in N_k(s)}\rho_k(t)}{\rho_k(s)},
\qquad
a_s=-\operatorname{LOF}_k(s).
$$

$\operatorname{LOF}_k(s)=1$ means that both densities are equal; values greater than $1$ mean that $s$ has a lower local density than its neighbors. A sample is classified as an outlier iff

$$
a_s < -1.5.
$$

Outlier samples are removed from the protein table and returned together with all scores. The calculation fails if the input contains missing intensities. For the exact definition of the local density, see the [scikit-learn User Guide](https://scikit-learn.org/stable/modules/outlier_detection.html#local-outlier-factor).

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/outlier_detection.py:by_local_outlier_factor"
```
