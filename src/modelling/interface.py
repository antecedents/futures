"""Module interface.py"""
import logging
import os
import sys

import pandas as pd

import config
import src.elements.codes as ce
import src.elements.master as mr
import src.functions.directories
import src.modelling.codes
import src.modelling.core
import src.modelling.initial


class Interface:
    """
    The interface to the seasonal & trend component modelling steps.
    """

    def __init__(self, data: pd.DataFrame, arguments: dict):
        """

        :param data: The weekly accidents & emergency data of institutions/hospitals
        :param arguments: A set of model development, and supplementary, arguments.
        """

        self.__data = data
        self.__arguments = arguments

        # Instances
        self.__configurations = config.Config()
        self.__directories = src.functions.directories.Directories()

    def __set_directories(self, codes: list[ce.Codes]):
        """

        :param codes: The unique set of health board & institution pairings.
        :return:
        """

        directories = [self.__directories.create(os.path.join(self.__configurations.artefacts_, section, c.hospital_code))
                       for section in ['data', 'models'] for c in codes]

        if not all(directories):
            sys.exit('Missing Directories')

    def __get_codes(self) -> list[ce.Codes]:
        """
        The unique set of health board & institution pairings.
        doublets = list(reversed(doublets))

        :return:
        """

        doublets: list[ce.Codes] = src.modelling.codes.Codes().exc(data=self.__data)
        if self.__arguments.get('excerpt') is None:
            codes = doublets
        else:
            state = len(doublets) >= self.__arguments.get('excerpt')
            codes = doublets[:self.__arguments.get('excerpt')] if state else doublets

        return codes

    def exc(self) -> list[str]:
        """
        Each instance of codes consists of the health board & institution/hospital codes of an institution/hospital.
        
        :return: 
        """

        codes = self.__get_codes()
        logging.info('# of institutions in focus: %s', len(codes))

        # Directories: Each institution will have a directory within (a) a data directory, and (b) a models directory
        self.__set_directories(codes=codes)

        # Seasonal Component Modelling
        masters: list[mr.Master] = src.modelling.initial.Initial(
            data=self.__data, codes=codes, arguments=self.__arguments).exc()

        # Trend Component Modelling
        messages = src.modelling.core.Core(
           arguments=self.__arguments).exc(masters=masters)

        return messages
