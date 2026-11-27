# PTMs per Sample

Counts the occurrences of each modification listed in the given PSM table separately for every sample. Let $a_{r,m}$ be the number of occurrences of modification $m$ recorded for PSM row $r$. For sample $s$, the reported count is

$$
n_{s,m}=\sum_{r:\,s(r)=s}a_{r,m}.
$$

Entries such as `2 Oxidation (M)` contribute two occurrences. The result contains one row per sample, one column per observed modification type, and a `Total Amount of Peptides` column containing the total number of PSM rows for that sample.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/ptm_analysis.py:ptms_per_sample"
```
