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
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.utils.validation import check_X_y
from sklearn.exceptions import NotFittedError
from tqdm.auto import tqdm


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
        """
        Fits the (LOESS) curve using lowess.

        :param X: The training input samples. Must be sorted in ascending order.
        :param y: the intensity values of the input samples corresponding to X

        :return:  the fitted estimator instance
        """

        # Check that X and y have correct shape
        X, y = check_X_y(X, y)
        # Store the classes seen during fit
        x = X.flatten()
        y_fit = lowess(y, x, frac=self.frac, is_sorted=True, return_sorted=False)
        fill = (y_fit[0], y_fit[-1])
        self.interpolator_ = interp1d(x, y_fit, fill_value=fill, bounds_error=False)
        return self

    def predict(self, X):
        """
        Takes the input samples and predicts the intensity values for them with the fitted LOESS curve.

        :param X: the input samples

        :return: the predicted values for the input samples
        """
        if self.interpolator_ is None:
            raise NotFittedError
        xf = X.flatten()
        x_interp = self.interpolator_(xf)
        return x_interp


def correct_intra_batch_with_loess(
    batch_wide_protein_df: pd.DataFrame,
    qc_samples_in_order: np.ndarray,
    qc_samples_values: np.ndarray,
    all_samples_in_order: np.ndarray,
    all_samples_values: np.ndarray,
    frac: float,
) -> dict:
    """
    Applies LOESS correction on each feature (protein) within the given batch.

    :param batch_wide_protein_df: dataframe that contains the protein data for one batch in wide format
    :param qc_samples_in_order: list of quality samples in order (within the batch)
    :param qc_samples_values: list of quality samples values in order (within the batch)
    :param all_samples_in_order: list of all samples in order (within the batch)
    :param all_samples_values: list of all samples values in order (within the batch)
    :param frac: fraction of samples around a point to fit the curve at this specific point

    :return: dictionary with the adjusted batch protein data and, if there are any, messages
    """
    # I decided to use a global fraction for all proteins to reduce computation time (from minutes to seconds) and reduce the probability of overfitting
    corrector = _LoessCorrector(frac=frac)

    # for now I use tqdm to keep track of the progress. Currently, loading times are several minutes. I could think about parallelizing this.
    for protein in tqdm(
        batch_wide_protein_df.columns, desc="Progress in fitting proteins: "
    ):

        y_qc = qc_samples_values[protein].values
        y_all = all_samples_values[protein].values

        valid_mask = ~np.isnan(y_qc)
        if valid_mask.sum() < MIN_LOESS_SIZE:
            continue

        # filter out NaNs
        valid_y_qc = y_qc[valid_mask]
        valid_qc_samples_in_order = qc_samples_in_order[valid_mask]
        corrector.fit(valid_qc_samples_in_order, valid_y_qc)

        qc_mean = np.nanmean(y_qc)
        x_qc = corrector.predict(all_samples_in_order)

        # different from the tidyms implementation because we expect our data to be log transformed already
        factor = x_qc - qc_mean
        corrected = y_all - factor

        batch_wide_protein_df[protein] = corrected
    return {"protein_df": batch_wide_protein_df, "messages": []}
