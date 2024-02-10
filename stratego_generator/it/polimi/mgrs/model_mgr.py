from it.polimi.logger.logger import Logger
import configparser

LOGGER = Logger('Model Manager')

config = configparser.ConfigParser()
config.read('./resources/config/config.ini')
config.sections()


def generate_model():
    # TODO
    LOGGER.info(config['TEMPLATES SETTING']['MODEL_PATH'])
