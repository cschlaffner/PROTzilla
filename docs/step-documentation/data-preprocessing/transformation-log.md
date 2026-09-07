# Transformation: Log

Applies the selected logarithm to every intensity $x$ in the given protein table and, if provided, peptide table:

$$
\hat{x}=\log_b(x),
\qquad b\in\{2,10\}.
$$

The default base is $b=2$. Only positive intensities produce finite real values: zero is transformed to $-\infty$, negative intensities to `NaN`, and missing intensities remain missing. All other columns remain unchanged.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/transformation.py:by_log"
```
