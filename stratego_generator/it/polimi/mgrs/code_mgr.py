import configparser

from it.polimi.logger.logger import Logger

LOGGER = Logger('Code Manager')

config = configparser.ConfigParser()
config.read('./resources/config/config.ini')
config.sections()

def generate_code():
    LOGGER.info(config['STRATEGY SETTINGS']['SCRIPT_PATH'])