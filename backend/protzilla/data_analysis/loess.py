"""
This module contains LOESS batch correction implementations adapted from
the Bioanalytical mass spectrometry group at CIBION-CONICET from their implementation of LOESS in TidyMS.
This is their license:

BSD 3-Clause License

Copyright (c) 2020, Bioanalytical mass spectrometry group at CIBION-CONICET
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from statsmodels.nonparametric.smoothers_lowess import lowess
from sklearn.model_selection import LeaveOneOut, ShuffleSplit, GridSearchCV
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.utils.validation import check_X_y
from sklearn.exceptions import NotFittedError


MIN_LOESS_SIZE = 4


class _LoessCorrector(BaseEstimator, RegressorMixin):
    """
    Intra-batch corrector implementation using sklearn.

    :param frac: number between 0 and 1, default=0.66, it represents the fraction of samples used for local regressions
    """

    def __init__(self, frac: float = 0.66):
        """
        Constructor function.

        :param frac: number between 0 and 1, default=0.66, it represents the fraction of samples used for local regressions
        """

        self.frac = frac
        self.interpolator_ = None

    def fit(self, X, y):
        # TODO: doc string

        # Check that X and y have correct shape
        X, y = check_X_y(X, y)
        # Store the classes seen during fit
        x = X.flatten()
        y_fit = lowess(y, x, frac=self.frac, is_sorted=True, return_sorted=False)
        fill = (y[0], y[-1])
        self.interpolator_ = interp1d(x, y_fit, fill_value=fill, bounds_error=False)
        return self

    def predict(self, X):
        if self.interpolator_ is None:
            raise NotFittedError
        xf = X.flatten()
        x_interp = self.interpolator_(xf)
        return x_interp


def _get_param_grid_loess_corrector(n_qc_samples: int) -> dict:
    """
    Builds a parameter grid for GridSearchCV.

    :param n_qc_samples: number of quality control samples

    :return: the grid parameters in form of a dictionary
    """
    min_frac = min(MIN_LOESS_SIZE / n_qc_samples, 1.0)
    # Limits the number of points in the grid to at most 5
    if n_qc_samples < 9:
        frac = np.arange(MIN_LOESS_SIZE, n_qc_samples + 1) / n_qc_samples
    else:
        n_points = 5
        frac = np.linspace(min_frac, 1.0, n_points)

    grid_params = {"frac": frac}
    return grid_params


def correct_intra_batch_with_loess(
    batch_wide_protein_df,
    qc_samples_in_order,
    qc_samples_values,
    all_samples_in_order,
    all_samples_values,
) -> pd.DataFrame:
    corrector = _LoessCorrector()
    cv = LeaveOneOut()
    grid_params = _get_param_grid_loess_corrector(n_qc_samples=len(qc_samples_in_order))
    scoring = "neg_mean_squared_error"
    grid = GridSearchCV(corrector, grid_params, cv=cv, scoring=scoring)
    grid.fit(qc_samples_in_order, qc_samples_values)
    corrector.set_params(**grid.best_params_)
    corrector.fit(qc_samples_in_order, qc_samples_values)

    qc_mean = qc_samples_values.mean()
    x_qc = corrector.predict(all_samples_in_order)
    factor = np.zeros_like(x_qc)
    # correct nan in zero values and negative values generated during LOESS
    is_positive = x_qc > 0
    factor = np.divide(qc_mean, x_qc, out=factor, where=is_positive)
    corrected = all_samples_values * factor
    batch_wide_protein_df[all_samples_in_order] = corrected
    return batch_wide_protein_df
