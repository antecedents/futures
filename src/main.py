"""Module main.py"""
import logging
import os
import sys

import boto3
import jax
import numpyro
import pytensor


def main():
    """

    :return:
    """

    logger: logging.Logger = logging.getLogger(__name__)
    logger.info('BLAS: %s', pytensor.config.blas__ldflags)

    # Setting up
    src.setup.Setup(service=service, s3_parameters=s3_parameters).exc()

    # Data
    data = src.data.interface.Interface(s3_parameters=s3_parameters).exc()

    # Modelling
    masters = src.modelling.interface.Interface(
      data=data, arguments=arguments).exc()

    # Transfer
    src.transfer.interface.Interface(
       connector=connector, service=service, s3_parameters=s3_parameters).exc()

    # Cache
    src.functions.cache.Cache().exc()


if __name__ == '__main__':

    root = os.getcwd()
    sys.path.append(root)
    sys.path.append(os.path.join(root, 'src'))

    # Logging
    logging.basicConfig(level=logging.INFO,
                        format='\n\n%(message)s\n%(asctime)s.%(msecs)03d',
                        datefmt='%Y-%m-%d %H:%M:%S')

    # Classes
    import environment
    import src.data.interface
    import src.functions.cache
    import src.functions.service
    import src.modelling.interface
    import src.s3.s3_parameters
    import src.s3.configurations
    import src.setup
    import src.transfer.interface

    # Vis-à-vis Amazon & Development: Connector, S3 Parameters, Platform Services, Configurations
    connector = boto3.session.Session()
    s3_parameters = src.s3.s3_parameters.S3Parameters(connector=connector).exc()
    service = src.functions.service.Service(connector=connector, region_name=s3_parameters.region_name).exc()
    arguments: dict = src.s3.configurations.Configurations(connector=connector).objects(
        key_name=('artefacts' + '/' + 'architecture' + '/' + 'single' + '/' + 'futures' + '/' + 'arguments.json'))

    pytensor.config.blas__ldflags = '-llapack -lblas -lcblas'

    jax.config.update('jax_platform_name', 'cpu')
    jax.config.update('jax_enable_x64', True)

    numpyro.set_platform('cpu')
    numpyro.set_host_device_count(os.cpu_count())

    # Environment Variables
    environment.Environment(arguments=arguments)

    main()
