# Imputation: Normal Distribution Sampling

Replaces each missing protein intensity by a value drawn from a normal distribution that is derived from the measured intensities of a group. The strategy determines what a group is: a protein $p$ (per protein), a sample $s$ (per sample), or the complete dataset.

By default the intensities are $\log_{10}$-transformed before sampling, so that each missing intensity $x_{g,i}$ of group $g$ is replaced with

$$
\hat{x}_{g,i} = 10^{Z_{g,i}}, \qquad Z_{g,i} \sim \mathcal{N}\left(\mu_g + d \cdot \sigma_g,\;(c \cdot \sigma_g)^2\right),
$$

where $\mu_g$ and $\sigma_g$ are the mean and standard deviation of the measured $\log_{10}$ intensities of that group, $d$ is the selected downshift and $c$ is the selected scaling factor. The form defaults are $d=-1$ and $c=0.5$; a negative downshift moves the sampled distribution below the measured one.

## Data that is already on a log scale

The $\log_{10}$ transformation assumes positive measured intensities. Data that has already been log-transformed, for example by a preceding transformation step, generally contains negative values and cannot be transformed again. For such data, disable **log-transform intensities before sampling**. The values are then drawn on the scale of the input data,

$$
\hat{x}_{g,i} \sim \mathcal{N}\left(\mu_g + d \cdot \sigma_g,\;(c \cdot \sigma_g)^2\right),
$$

with $\mu_g$ and $\sigma_g$ calculated from the measured values as they are. Imputed values may then be negative, as the data itself is.

To reproduce the Perseus default of replacing missing values separately for each column, select the per-sample strategy with $d=-1.8$ and $c=0.3$ and disable the log transformation.

## Strategies

| Strategy | Group | Requirement |
| --- | --- | --- |
| Per protein | one protein group across all samples | at least two measured intensities for that protein |
| Per sample | one sample across all protein groups | at least two measured intensities in that sample |
| Per dataset | all measured intensities | at least two measured intensities in total |

Groups that do not meet the requirement offer no standard deviation to sample from and are left unchanged, so missing values remain. These are reported as a warning and can be identified in the imputation summary.

Only for the per-dataset strategy, and only while the log transformation is enabled, PROTzilla keeps the sampled distribution on the positive side by using $\max(0, \mu + d \cdot \sigma)$ as its mean and reflecting negative sampled values.

## Reproducibility

Values are sampled randomly, so repeated calculations produce different results. Setting a non-negative random seed makes a calculation reproducible. The seed is used for a generator local to this step, so it does not influence the randomness of any other step. Groups that cannot be imputed consume no random values, meaning their presence does not change the values drawn for the other groups.

## Imputation summary

Besides the imputed dataframe, the step returns an `imputation_summary_df` with one row per group, describing how it was imputed:

| Column | Description |
| --- | --- |
| `strategy`, `group_type`, `group` | the selected strategy and the group the row describes |
| `n_observed`, `n_missing`, `n_imputed` | how many values were measured, missing, and actually imputed; `n_imputed` is 0 for a skipped group |
| `observed_mean`, `observed_sd` | $\mu_g$ and $\sigma_g$, on the scale that was sampled on |
| `impute_mean`, `impute_sd` | the mean and standard deviation of the sampled distribution |
| `down_shift`, `scaling_factor`, `log_transform`, `seed` | the parameters the calculation was run with |

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/imputation.py:by_normal_distribution_sampling"
```
