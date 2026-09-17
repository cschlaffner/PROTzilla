# Filter Proteins: #Values / Group

Filters the given protein table using the group assignments from the selected column of the given metadata table.

For each protein $i$ and group $g$, calculates:

$$
n_{i,g} =
\text{number of non-missing intensities for protein } i
\text{ in group } g.
$$

Depending on the selected mode, the protein is retained iff

$$
\min_{g \in G} n_{i,g} \geq m
\quad\text{(in every group)}
\qquad\text{or}\qquad
\max_{g \in G} n_{i,g} \geq m
\quad\text{(in at least one group)},
$$

where $m$ is the selected minimum number of values per group.

Samples that are missing from the metadata contribute to no group, so a protein that is only
measured in such samples counts as $n_{i,g} = 0$ everywhere and is filtered out.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/filter_proteins.py:by_number_of_values_per_group"
```
