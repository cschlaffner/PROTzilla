# Filter Peptides: PEP Threshold

Filters peptide identifications by their posterior error probability (PEP). The PEP of a peptide identification is the posterior probability that the identification is incorrect. For the formal definition of posterior probability, see [JCGM 106:2012, Section 6.2](https://www.bipm.org/en/doi/10.59161/jcgm106-2012).

Peptide identification $i$ is retained iff

$$
\operatorname{PEP}_i \leq \tau,
$$

where $\tau \in [0,1]$ is the selected maximum PEP value. Lower PEP values indicate more reliable identifications.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/filter_peptides_or_psm.py:by_pep_value"
```
