"""Module interface.py"""

import pandas as pd

import config
import src.elements.s3_parameters as s3p
import src.elements.text_attributes as txa
import src.functions.streams


class Interface:
    """
    Notes<br>
    ------<br>

    Reads-in the data in focus.
    """

    def __init__(self, s3_parameters: s3p.S3Parameters):
        """

        :param s3_parameters: The overarching S3 parameters settings of this project, e.g., region code
                              name, buckets, etc.
        """

        self.__s3_parameters = s3_parameters

        # Instances
        self.__streams = src.functions.streams.Streams()
        self.__configurations = config.Config()

    def __get_data(self, uri: str) -> pd.DataFrame:
        """

        :param uri: A data sets' uniform resource identifier.
        :return:
        """

        text = txa.TextAttributes(uri=uri, header=0)

        frame = self.__streams.read(text=text)
        frame['week_ending_date'] = pd.to_datetime(
            frame['week_ending_date'].astype(dtype=str), errors='coerce', format='%Y-%m-%d')

        return frame[self.__configurations.fields]

    def exc(self, stamp: str) -> pd.DataFrame:
        """

        :param stamp:
        :return:
        """

        # The data sets' uniform resource identifier
        uri = ('s3://' + self.__s3_parameters.internal + '/' +
                self.__s3_parameters.path_internal_data + f'raw/{stamp}.csv')

        # Reading, and enhancing, the data set.
        data = self.__get_data(uri=uri)

        return data
