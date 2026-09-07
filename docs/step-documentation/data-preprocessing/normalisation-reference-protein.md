# Normalisation: Reference Protein

Given a reference protein identifier, identifies the protein group $g$ containing it. For each sample $s$, every protein-group intensity is normalised by the intensity of $g$ in the same sample:

$$
\hat{x}_{s,p} = \frac{x_{s,p}}{x_{s,g}}.
$$

Consequently, the normalised intensity of the reference group $g$ equals $1$ in every retained sample. A `Protein ID` may represent a semicolon-separated protein group, such as `P12345;Q67890`; entering either member selects this group as the reference.

Samples in which the reference intensity is missing, zero, or negative are removed and reported separately. If the selected reference identifier does not occur in the protein table, the calculation fails.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/normalisation.py:by_reference_protein"
```
