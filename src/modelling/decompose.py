"""Module decompose.py"""
import os

import pandas as pd
import statsmodels.tsa.seasonal as stsl

import config
import src.elements.codes as ce
import src.elements.master as mr
import src.functions.streams


class Decompose:
    """
    Notes<br>
    ------<br>

    This class decomposes the <i># of attendances series</i>.
    """

    def __init__(self, arguments: dict):
        """

        :param arguments: The modelling arguments
        """

        self.__arguments: dict = arguments
        self.__decompose: dict = self.__arguments.get('decompose')

        # The parent path of modelling data
        self.__root = os.path.join(config.Config().artefacts_, 'data')

    def __add_components(self, frame: pd.DataFrame) -> pd.DataFrame:
        """

        :param frame:
        :return:
        """

        components: stsl.DecomposeResult = stsl.STL(
            frame['n_attendances'], period=self.__arguments.get('seasons'),
            seasonal=self.__decompose.get('smoother_seasonal'),
            trend_deg=self.__decompose.get('degree_trend'),
            seasonal_deg=self.__decompose.get('degree_seasonal'),
            robust=True).fit()

        frame['trend'] = components.trend
        frame['residue'] = components.resid
        frame['seasonal'] = components.seasonal

        return frame

    def exc(self, master: mr.Master, code: ce.Codes) -> mr.Master:
        """

        :param master:
        :param code:
        :return:
        """

        frame = master.training.copy()

        # Decomposition Components
        frame = self.__add_components(frame=frame.copy())

        # Save
        blob = frame.copy().reset_index(drop=False)
        src.functions.streams.Streams().write(
            blob=blob, path=os.path.join(self.__root, code.hospital_code, 'features.csv' ))

        # Update/Replace
        master = master._replace(training=frame)

        return master
