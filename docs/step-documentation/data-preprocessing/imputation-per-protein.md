# Imputation: per Protein

For each protein $p$, the replacement value is calculated from the measured intensities of that protein, depending on the selected method.

If **Mean** is selected, missing values are replaced with the arithmetic mean:

$$
\hat{x}_{s,p} = \frac{1}{|O_p|}\sum_{s' \in O_p}x_{s',p},
$$

where $O_p$ is the set of samples in which protein $p$ has a measured intensity.

If **Median** is selected, missing values are replaced with the median of the measured intensities of protein $p$.

If **Most frequent** is selected, missing values are replaced with the most frequently occurring measured intensity of protein $p$.

Proteins without a measured intensity in any sample are removed before imputation.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/imputation.py:by_simple_imputer"
```
