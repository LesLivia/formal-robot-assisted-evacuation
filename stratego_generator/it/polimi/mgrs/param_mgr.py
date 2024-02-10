import configparser
import sys
from typing import Dict

from it.polimi.logger.logger import Logger

LOGGER = Logger('Parameters Manager')

config = configparser.ConfigParser()
config.read('./resources/config/config.ini')
config.sections()


def parse_params():
    # TODO
    params: Dict[str, str] = dict()

    LOGGER.info(sys.argv[1])

    return params
