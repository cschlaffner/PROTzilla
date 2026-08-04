# Diff. Expression: ANOVA

Performs a one-way ANOVA independently for each protein using the active intensity column. Samples are assigned to groups using the selected metadata column, and only the selected groups are included in the analysis.

PROTzilla performs the test using [`scipy.stats.f_oneway`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f_oneway.html). For a formal explanation of one-way ANOVA, its assumptions, and the interpretation of its results, see the [NIST One-Way ANOVA overview](https://www.itl.nist.gov/div898/handbook/prc/section4/prc431.htm).

Proteins for which the ANOVA does not produce a valid p-value are excluded from the result and reported as filtered proteins.

After testing all valid proteins, PROTzilla applies the selected multiple-testing correction:

- **None:** the original p-values and alpha threshold are used.
- **Benjamini-Hochberg:** the p-values are adjusted while the selected alpha threshold is retained.
- **Bonferroni:** the original p-values are compared with a corrected alpha threshold.

A protein is included in `significant_proteins_df` when its resulting p-value is below the resulting alpha threshold.

The step returns:

- the differential-expression results for all valid proteins,
- the subset of significant proteins,
- the p-values used for the final significance decision,
- the resulting alpha threshold,
- and the identifiers of proteins excluded because no valid test result could be calculated.

This step tests all selected groups simultaneously. It does not perform a post-hoc analysis to determine which individual groups differ.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/differential_expression_anova.py:anova"
```
