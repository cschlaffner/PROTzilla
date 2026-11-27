# FLEXIQuant-LF

Estimates the relative modification of unmodified peptide species from one selected protein group. Let $\tilde{x}_{r,p}$ be the median intensity of peptide $p$ in the selected reference group. For each sample $s$, a RANSAC regression through the origin estimates the sample-specific slope $\beta_s$:

$$
x_{s,p}=\beta_s\tilde{x}_{r,p}+\varepsilon_{s,p}.
$$

The regression is repeated with the selected number of initializations, and the model with the greatest inlier $R^2$ is retained. At least five valid peptide pairs are required for a sample. The expected peptide intensity is $\hat{x}_{s,p}=\beta_s\tilde{x}_{r,p}$, giving the raw score

$$
R_{s,p}=1-\frac{\hat{x}_{s,p}-x_{s,p}}{\hat{x}_{s,p}}=\frac{x_{s,p}}{\hat{x}_{s,p}}.
$$

After removing raw-score outliers, each sample is normalized by the median of its three greatest raw scores:

$$
\operatorname{RM}_{s,p}=\frac{R_{s,p}}{\operatorname{median}\left(\operatorname{top3}\{R_{s,q}\}_q\right)}.
$$

An RM score near $1$ indicates the expected relative abundance of the unmodified peptide, while a lower score indicates a greater inferred modification extent. A peptide is classified as differentially modified iff $\operatorname{RM}_{s,p}$ is below the selected modification cutoff.

The step returns raw and RM scores, the modification calls, removed peptides, regression diagnostics, and one regression plot per processed sample. The method is described in the [FLEXIQuant-LF publication](https://elifesciences.org/articles/58783).

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/ptm_quantification/flexiquant.py:flexiquant_lf"
```
