import configparser

from it.polimi.logger.logger import Logger

LOGGER = Logger('Strategy Manager')

config = configparser.ConfigParser()
config.read('./resources/config/config.ini')
config.sections()


def generate_strategy():
    LOGGER.info(config['UPPAAL SETTINGS']['UPPAAL_SCRIPT_PATH'])


def parse_strategy():
    return