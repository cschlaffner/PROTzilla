# Outlier Detection: PCA

Transforms the given protein table into a matrix with samples as rows and proteins as columns, then projects each sample onto the selected number of principal components. Either two or three components can be used; the default is three.

Each principal component is a weighted linear combination of the centred protein intensities. The first component captures the greatest possible variance between samples; each subsequent component captures the greatest remaining variance while being orthogonal to the preceding components.

Let $z_{s,j}$ be the score of sample $s$ on component $j$, and let $m_j$ and $\sigma_j$ be the median and standard deviation of all scores on that component. For the selected threshold $\tau$, a sample is classified as an outlier iff

$$
\sum_{j=1}^{c}
\left(
\frac{z_{s,j}-m_j}{\tau \cdot \sigma_j}
\right)^2
> 1,
$$

where $c\in\{2,3\}$ is the selected number of components and $\tau$ defaults to $2$. This condition defines an ellipse for two components and an ellipsoid for three components.

Outlier samples are removed from the protein table. The component scores, outlier classifications, and explained-variance ratios are returned. The calculation fails if the input contains missing intensities.

## Implementation in PROTzilla

```python
--8<-- "backend/protzilla/data_preprocessing/outlier_detection.py:by_pca"
```
