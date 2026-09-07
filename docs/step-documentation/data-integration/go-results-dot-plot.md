# GO Results: Dot Plot

Creates a dot plot from an Enrichr or offline GO enrichment result. STRING results are not accepted because the plot requires an `Overlap` column. Only selected gene-set categories and terms satisfying

$$
p_{\mathrm{adj}}\leq\tau
$$

are shown, where $\tau$ is the selected cutoff. Dot color represents $-\log_{10}(p_{\mathrm{adj}})$, and dot area is proportional to the overlap ratio

$$
r_G=\frac{|Q\cap G|}{|G|}.
$$

With `Gene Sets` on the x-axis, the selected number of terms with the smallest adjusted p-values is shown separately for each category. With `Combined Score`, exactly one category must be selected; the combined score is then used on the x-axis.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_integration/di_plots.py:GO_enrichment_dot_plot"
```
