# Normalisation: Width Adjustment

For each sample $s$, calculates the first quartile $q_{1,s}$, median $q_{2,s}$, and third quartile $q_{3,s}$. The lower and upper quartile widths are

$$
l_s = q_{2,s} - q_{1,s}
\qquad\text{and}\qquad
u_s = q_{3,s} - q_{2,s}.
$$

The target widths $l^*$ and $u^*$ are the medians of all positive lower and upper sample widths, respectively. Each intensity is then centred around the sample median:

$$
y_{s,p} = x_{s,p} - q_{2,s}.
$$

For intensities above the median with $u_s>0$, the centred value is scaled by

$$
\hat{x}_{s,p} = y_{s,p} \cdot \frac{u^*}{u_s}.
$$

For intensities at or below the median with $l_s>0$, it is scaled by

$$
\hat{x}_{s,p} = y_{s,p} \cdot \frac{l^*}{l_s}.
$$

Consequently, every sample is centred at zero and its lower and upper quartile widths are adjusted to common target widths. If one width of an individual sample is zero, that side is not rescaled. If no positive lower or upper width exists across all samples, the calculation fails.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/normalisation.py:by_width_adjustment"
```
