"""Module main.py"""
import logging
import os
import sys

import boto3


def main():
    """

    :return:
    """

    logger: logging.Logger = logging.getLogger(__name__)
    stamp = config.Config().stamp
    logger.info('Latest Tuesday: %s', stamp)

    '''
    Set up
    '''
    setup: bool = src.setup.Setup(service=service, s3_parameters=s3_parameters, stamp=stamp).exc()
    if not setup:
        src.functions.cache.Cache().exc()
        sys.exit('No Executions')

    '''
    Steps
    src.modelling.interface.Interface().exc()
    '''
    training, testing = src.data.interface.Interface(s3_parameters=s3_parameters).exc(stamp=stamp)

    '''
    Cache
    '''
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
    import config
    import src.data.interface
    import src.functions.cache
    import src.functions.service
    import src.modelling.interface
    import src.s3.s3_parameters
    import src.setup

    # S3 S3Parameters, Service Instance
    connector = boto3.session.Session()
    s3_parameters = src.s3.s3_parameters.S3Parameters(connector=connector).exc()
    service = src.functions.service.Service(connector=connector, region_name=s3_parameters.region_name).exc()

    main()
