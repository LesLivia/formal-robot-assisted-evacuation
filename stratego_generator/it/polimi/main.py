from it.polimi.logger.logger import Logger
from it.polimi.mgrs.param_mgr import parse_params
from it.polimi.mgrs.model_mgr import generate_model
from it.polimi.mgrs.strategy_mgr import generate_strategy, parse_strategy
from it.polimi.mgrs.code_mgr import generate_code

LOGGER = Logger('main')

LOGGER.info('Parsing input parameters...')

params = parse_params()

LOGGER.info('Generating Uppaal Stratego model...')

generate_model()

LOGGER.info('Generating Strategy...')

generate_strategy()

LOGGER.info('Parsing Strategy...')

parse_strategy()

LOGGER.info('Generating Decision-making Script...')

generate_code()

LOGGER.info('Done.')
