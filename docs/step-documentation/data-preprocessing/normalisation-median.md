# Normalisation: Median

For each sample $s$, calculates the selected intensity quantile

$$
q_s = Q_{\tau}\left(\{x_{s,p}\}_p\right),
$$

where $\tau \in [0,1]$ is the selected percentile. The default $\tau=0.5$ corresponds to the median.

If the intensities are not log-transformed, each intensity is normalised by

$$
\hat{x}_{s,p} = \frac{x_{s,p}}{q_s}.
$$

If the intensities were log-transformed before normalisation, division on the original scale is performed as subtraction on the log scale:

$$
\hat{x}_{s,p} = x_{s,p} - q_s.
$$

If $q_s=0$ for non-log-transformed data or $q_s$ is not finite for log-transformed data, all normalised intensities of the affected sample are set to zero and a warning is returned.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/normalisation.py:by_median"
```
