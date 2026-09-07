# PTM Visualisation: Overview Plot

Maps post-translational modifications from the given PSM table to the protein sequence in the given FASTA file. A modified PSM row $r$ is considered iff

$$
\operatorname{PEP}_r < \tau,
$$

where $\tau$ is the selected evidence-file threshold. The peptide sequence and its modified residues are aligned to the corresponding protein isoform, and each detected PTM is shown at its resulting amino-acid position.

The regions file divides the sequence into named regions, while the PTM visualisation settings determine which modification types and residue sites are displayed. The plot therefore shows the positions and types of the detected PTMs in the context of the protein sequence, its isoforms, and its annotated regions.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/ptm_visualization/ptm_overview_plot.py:create_overview_ptm_visualization"
```
