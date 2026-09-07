# Protein Coverage Plot

Matches the peptide sequences in the given peptide table to the selected protein sequence from the given FASTA table. A separate plot is created for each selected value of the metadata grouping.

For group $g$ and amino-acid position $r$, the sequence coverage is the number of distinct matched peptide sequences covering that position:

$$
c_{g,r}=\sum_{j\in J_g}\mathbf{1}\{a_j\leq r<b_j\},
$$

where $J_g$ is the set of matched peptide sequences in group $g$, and $a_j$ and $b_j$ are the start and end positions of peptide $j$. Each peptide is drawn at its position in the protein sequence. Its color represents the log2-transformed intensity, aggregated across the group by the selected mean or median.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/protein_coverage.py:plot_protein_coverage"
```
