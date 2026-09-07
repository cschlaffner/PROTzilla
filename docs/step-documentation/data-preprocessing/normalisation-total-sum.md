# Normalisation: Total Sum

For each sample $s$, calculates the sum of its measured protein intensities:

$$
T_s = \sum_{p \in O_s} x_{s,p},
$$

where $O_s$ is the set of proteins with a measured intensity in sample $s$. Each intensity is then normalised by

$$
\hat{x}_{s,p} = \frac{x_{s,p}}{T_s}.
$$

Consequently, the normalised measured intensities of each sample sum to $1$. If $T_s=0$, all normalised intensities of the affected sample are set to zero and a warning is returned.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/normalisation.py:by_totalsum"
```
