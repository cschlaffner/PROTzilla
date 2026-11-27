# Transformation: Inversion

Replaces every intensity $x$ in the given protein table and, if provided, peptide table with its reciprocal:

$$
\hat{x}=\frac{1}{x}.
$$

This transformation can, for example, convert ratios from H/L to L/H. If either table contains an intensity of zero, the calculation fails. Missing intensities remain missing, and all other columns remain unchanged.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/transformation.py:by_inversion"
```
