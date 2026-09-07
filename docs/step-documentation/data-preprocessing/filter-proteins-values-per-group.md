# Filter Proteins: #Values / Group

Filters the given protein table using the group assignments from the given metadata table.

For each protein $i$ and group $g$, calculates:

$$
n_{i,g} =
\text{number of distinct, non-missing intensities for protein } i
\text{ in group } g.
$$

The protein is retained iff

$$
\min_{g \in G} n_{i,g} \geq m,
$$

where $m$ is the selected minimum number of values per group.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/filter_proteins.py:by_number_of_values_per_group"
```
