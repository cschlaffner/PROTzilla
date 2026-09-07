# MultiFLEX-LF

Applies the FLEXIQuant-LF calculation to every protein group with quantified peptides instead of requiring one preselected protein. For each protein, sample, and peptide, it calculates a relative modification score $\operatorname{RM}_{s,p}$ against the selected reference group. Proteins for which FLEXIQuant-LF cannot calculate valid scores are skipped.

Only peptides with RM scores in at least two metadata groups are retained for clustering. Missing scores are imputed from the median scores of at least two peptides whose cosine similarity to the incomplete peptide is at least the selected threshold. Peptides with remaining missing values are removed. Optional DESeq2 normalization is applied across samples before this imputation is repeated.

The retained peptide profiles are hierarchically clustered using average linkage and the cutoff-aware distance

$$
d(u,v)=\sum_i\left(|u_i-v_i|+\mathbf{1}\{u_i<\tau\leq v_i\ \text{or}\ v_i<\tau\leq u_i\}\right),
$$

where $\tau$ is the modification cutoff. Thus, a difference receives an additional penalty of $1$ whenever the two RM scores lie on opposite sides of the cutoff.

The step returns raw and RM scores, modification calls, clustered RM scores, removed peptides, skipped proteins, group-wise score distributions, protein heatmaps, and a clustered heatmap. The method is described in the [MultiFLEX-LF publication](https://doi.org/10.1021/acs.jproteome.1c00669).

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/ptm_quantification/multiflex.py:multiflex_lf"
```
