# Normalisation: Reference Protein

Normalises each sample relative to a selected reference protein. Every protein intensity is divided by the intensity of the reference protein in the same sample:

$$
I_{\text{norm}} = \frac{I}{I_{\text{ref, Sample}}}
$$

Here, $I$ is the original protein intensity and $I_{\text{ref, Sample}}$ is the intensity of the selected reference protein in that sample.

Samples in which the reference protein has an intensity of zero or is not measured are excluded from the normalisation and reported separately. An example reference protein identifier is `A0A0B4J1V0`.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/normalisation.py:by_reference_protein"
```
