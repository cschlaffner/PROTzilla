# Classification: Random Forest

Trains a random-forest classifier to predict the selected metadata label from each sample's protein-intensity vector $x_s$. A forest contains $B$ decision trees. For class $c$, their probability estimates are averaged and the class with the greatest mean probability is predicted:

$$
\hat{y}_s=\operatorname*{arg\,max}_{c}\frac{1}{B}\sum_{b=1}^{B}\hat{P}_b(y=c\mid x_s).
$$

Each tree is fitted independently, optionally using a bootstrap sample of the training data. The number and maximum depth of the trees and the criterion used to evaluate candidate splits can be configured.

The data is first divided into separate training and test sets. Validation and optional grid or randomized parameter search are performed on the training set using the selected strategy and scores; the test set remains available for subsequent model evaluation. Samples without a value in the selected labels column are excluded. For binary labels, the selected positive class is encoded as $1$.

The step returns the fitted model, validation results, and the feature and label tables for the training and test sets. The calculation uses [`sklearn.ensemble.RandomForestClassifier`](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html).

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/classification.py:random_forest"
```
