import logging
import os
import typing

import boto3
import jax
import numpyro
import pytensor

import src.data.interface
import src.elements.s3_parameters as s3p
import src.elements.service as sr
import src.functions.cache
import src.functions.service
import src.modelling.interface
import src.preface.environment
import src.s3.configurations
import src.s3.s3_parameters
import src.setup
import src.transfer.interface


class Interface:
    """
    Interface
    """

    def __init__(self):
        """

        """

        self.__connector = boto3.session.Session()
        self.__s3_parameters: s3p.S3Parameters = src.s3.s3_parameters.S3Parameters(connector=self.__connector).exc()
        self.__service: sr.Service = src.functions.service.Service(
            connector=self.__connector, region_name=self.__s3_parameters.region_name).exc()

        pytensor.config.blas__ldflags = '-llapack -lblas -lcblas'

        # Logging
        logging.basicConfig(level=logging.INFO,
                            format='\n\n%(message)s\n%(asctime)s.%(msecs)03d',
                            datefmt='%Y-%m-%d %H:%M:%S')

        self.__logger: logging.Logger = logging.getLogger(__name__)

    def __get_arguments(self) -> dict:
        """

        :return:
        """

        key_name = 'artefacts' + '/' + 'architecture' + '/' + 'single' + '/' + 'futures' + '/' + 'arguments.json'

        return src.s3.configurations.Configurations(connector=self.__connector).objects(key_name=key_name)

    @staticmethod
    def __compute(arguments: dict):
        """

        :param arguments:
        :return:
        """

        jax.config.update('jax_platform_name', 'cpu')
        jax.config.update('jax_enable_x64', True)

        numpyro.set_platform('cpu')
        numpyro.set_host_device_count(os.cpu_count())

        src.preface.environment.Environment(arguments=arguments)

    @staticmethod
    def __setting_up(service: sr.Service, s3_parameters: s3p.S3Parameters):
        """

        :param service:
        :param s3_parameters:
        :return:
        """

        src.setup.Setup(service=service, s3_parameters=s3_parameters).exc()

    def exc(self) -> typing.Tuple[boto3.session.Session, s3p.S3Parameters, sr.Service, dict]:
        """

        :return:
        """

        arguments: dict = self.__get_arguments()
        self.__compute(arguments=arguments)
        self.__setting_up(service=self.__service, s3_parameters=self.__s3_parameters)
        self.__logger.info('BLAS: %s', pytensor.config.blas__ldflags)

        return self.__connector, self.__s3_parameters, self.__service, arguments
