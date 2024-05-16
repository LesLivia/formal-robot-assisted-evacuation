import configparser
import os

from it.polimi.logger.logger import Logger
from src.strategyviz.strategy2pta.stratego_parser import parse_optimized_strategy

LOGGER = Logger('Strategy Manager')

config = configparser.ConfigParser()
curr_path = os.getcwd()
if 'impact' in curr_path:
    config.read(curr_path.replace('impact2.10.7', 'stratego_generator/resources/config/config.ini'))
else:
    config.read('./resources/config/config.ini')
config.sections()


def generate_strategy():
    LOGGER.info(config['UPPAAL SETTINGS']['UPPAAL_SCRIPT_PATH'])


def parse_strategy(strat_name):
    STRATEGY_PATH = config['STRATEGY SETTINGS']['STRATEGY_PATH'].format(strat_name)
    if 'impact' in curr_path:
        STRATEGY_PATH = curr_path.replace('impact2.10.7', 'stratego_generator' + STRATEGY_PATH[1:])

    with open(STRATEGY_PATH) as opt_strategy_file:
        data: str = opt_strategy_file.read()
        optimized_strategy = parse_optimized_strategy(strat_name, data)

    return optimized_strategy
