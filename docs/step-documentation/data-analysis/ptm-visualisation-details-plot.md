# PTM Visualisation: Details Plot

Maps post-translational modifications and proteolytic cleavage sites from the given PSM table to the protein sequence and compares their occurrence between groups from the selected metadata column. Modified PSM rows contribute PTMs iff $\operatorname{PEP}_r < \tau$, where $\tau$ is the selected evidence-file threshold; cleavage sites are derived from all PSM rows matching the FASTA protein.

For site $j$ and group $g$, the displayed frequency is

$$
f_{g,j}=\frac{1}{|S_g|}\sum_{s\in S_g}\mathbf{1}\{\text{site }j\text{ was detected in sample }s\},
$$

where $S_g$ is the set of samples in group $g$. The plot displays these group frequencies for PTMs and cleavage sites alongside the aligned protein sequence and the regions defined in the regions file. PTM types, residue sites, and plot colours are taken from the PTM visualisation settings.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/ptm_visualization/ptm_details_plot.py:create_details_ptm_visualization"
```
