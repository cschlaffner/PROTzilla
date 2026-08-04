# Outlier Detection: Isolation Forest

Uses an Isolation Forest to identify outlier samples through random splits. Samples in dense regions generally require many splits to be isolated, while unusual samples can often be isolated with only a few splits.

The fewer splits a sample requires, the more likely it is to be classified as an outlier. The `number of estimators` parameter controls how many random decision trees are generated.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/outlier_detection.py:by_isolation_forest"
```
