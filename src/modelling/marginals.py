"""Module marginals.py"""
import pandas as pd
import pymc


class Marginals:
    """
    Computing auto regressive steps
    """

    def __init__(self):
        pass

    @staticmethod
    def exc(lag_coefficients, n_eqs: int, n_lags: int, segment: pd.DataFrame):
        """

        :param lag_coefficients: A pytensor.tensor.TensorVariable of a pymc distribution
        :param n_eqs: The number of independent variables.
        :param n_lags: Equivalent to the number of non-constant coefficients.
        :param segment: The training data.
        :return:
        """

        ars = []
        for j in range(n_eqs):
            ar = pymc.math.sum(
                [
                    pymc.math.sum(lag_coefficients[j, i] * segment.values[n_lags - (i + 1) : -(i + 1)], axis=-1)
                    for i in range(n_lags)
                ],
                axis=0,
            )
            ars.append(ar)
        beta = pymc.math.stack(ars, axis=-1)

        return beta
