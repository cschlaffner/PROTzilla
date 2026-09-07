# Transformation: Scaling

Maps every intensity $x$ from its original range $[x_{\min},x_{\max}]$ to the selected range $[a,b]$:

$$
\hat{x}
=
a+\frac{x-x_{\min}}{x_{\max}-x_{\min}}\cdot(b-a).
$$

Consequently, $x_{\min}$ is mapped to $a$, $x_{\max}$ to $b$, and all intermediate intensities are transformed linearly. Protein and peptide tables are scaled separately using their respective minimum and maximum intensities.

The calculation fails if $x_{\min}=x_{\max}$ or $a\geq b$. Missing intensities remain missing, and all other columns remain unchanged.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/transformation.py:by_scaling"
```
