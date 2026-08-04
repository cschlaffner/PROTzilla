# Filter Peptides: PEP Threshold

Removes peptides whose posterior error probability (PEP) is greater than the selected threshold.

The PEP value is the probability that an identified peptide was assigned incorrectly:

$$
\text{PEP} = P(\text{false-positive identification} \mid \text{given match})
$$

For example, a PEP value of `0.01` represents a 1% probability of a false-positive match. Lower PEP values indicate more reliable peptide identifications.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/filter_peptides_or_psm.py:by_pep_value"
```
