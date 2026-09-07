# PTM Visualisation: Bar Plot

Maps post-translational modifications from the given PSM table to the protein sequence and compares their occurrence between groups from the selected metadata column. Only modified PSM rows with $\operatorname{PEP}_r < \tau$ are considered, where $\tau$ is the selected evidence-file threshold.

For PTM site $j$ and group $g$, the displayed frequency is

$$
f_{g,j}=\frac{1}{|S_g|}\sum_{s\in S_g}\mathbf{1}\{\text{PTM }j\text{ was detected in sample }s\},
$$

where $S_g$ is the set of samples in group $g$. Each bar represents $f_{g,j}$ on a scale from $0\%$ to $100\%$. PTM positions are shown along the FASTA sequence and the regions defined in the regions file; modification types and residue sites are selected through the PTM visualisation settings.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/ptm_visualization/ptm_bar_plot.py:create_bar_ptm_visualization"
```
