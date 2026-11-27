# Classification: SVM

Trains a support-vector classifier to predict the selected metadata label from each sample's protein-intensity vector $x_s$. For binary labels $y_s\in\{-1,1\}$, the soft-margin objective is

$$
\min_{w,b,\xi}\frac{1}{2}\lVert w\rVert^2+C\sum_s\xi_s
$$

subject to

$$
y_s\left(w^T\phi(x_s)+b\right)\geq 1-\xi_s,\qquad \xi_s\geq0.
$$

The selected kernel defines the feature mapping $\phi$. The parameter $C$ controls the trade-off between a wider margin and classification errors; larger values penalize errors more strongly. Optional class weights scale this penalty separately for each class.

The data is first divided into separate training and test sets. Validation and optional grid or randomized parameter search are performed on the training set using the selected strategy and scores. Samples without a value in the selected labels column are excluded, and the selected positive class is encoded as $1$. The current implementation trains the model without probability estimation.

The step returns the fitted model, validation results, and the feature and label tables for the training and test sets. The calculation uses [`sklearn.svm.SVC`](https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html).

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/classification.py:svm"
```
