"""Module main.py"""
import logging
import os
import sys


def main():
    """

    :return:
    """

    # Data
    data = src.data.interface.Interface(s3_parameters=s3_parameters).exc()

    # Modelling
    masters = src.modelling.interface.Interface(
      data=data, arguments=arguments).exc()
    logging.info(masters)

    # Transfer
    src.transfer.interface.Interface(
       connector=connector, service=service, s3_parameters=s3_parameters).exc()

    # Cache
    src.functions.cache.Cache().exc()


if __name__ == '__main__':

    root = os.getcwd()
    sys.path.append(root)
    sys.path.append(os.path.join(root, 'src'))

    # Classes
    import src.data.interface
    import src.functions.cache
    import src.modelling.interface
    import src.setup
    import src.transfer.interface
    import src.preface.interface

    connector, s3_parameters, service, arguments = src.preface.interface.Interface().exc()

    main()
