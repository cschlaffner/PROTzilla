# Clustering: EM

Models the sample intensity vectors as a mixture of $k$ multivariate Gaussian distributions:

$$
p(x_s)=\sum_{j=1}^{k}\pi_j\,\mathcal{N}(x_s\mid\mu_j,\Sigma_j),
$$

where $\pi_j$ is the weight, $\mu_j$ the mean vector, and $\Sigma_j$ the covariance matrix of component $j$. Expectation maximization iteratively estimates the membership probabilities

$$
\gamma_{s,j}=\frac{\pi_j\mathcal{N}(x_s\mid\mu_j,\Sigma_j)}{\sum_{l=1}^{k}\pi_l\mathcal{N}(x_s\mid\mu_l,\Sigma_l)}
$$

and updates the component parameters to increase the data likelihood. Sample $s$ is assigned to the component with the greatest $\gamma_{s,j}$.

The selected covariance type determines whether components use full, diagonal, spherical, or shared covariance matrices. The covariance regularization is added to their diagonals for numerical stability. The initialization method, maximum number of iterations, and random seed can also be configured.

The selected metadata labels are used only for evaluation and parameter selection, not to fit the mixture components. The step returns the fitted model, the assigned component and membership probabilities for each sample, and the evaluation results. Missing intensities must be handled before clustering.

The calculation uses [`sklearn.mixture.GaussianMixture`](https://scikit-learn.org/stable/modules/generated/sklearn.mixture.GaussianMixture.html).

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_analysis/clustering.py:expectation_maximisation"
```
