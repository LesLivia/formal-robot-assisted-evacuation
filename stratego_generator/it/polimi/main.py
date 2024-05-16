from it.polimi.logger.logger import Logger
from it.polimi.mgrs.param_mgr import parse_params
from it.polimi.mgrs.model_mgr import generate_model
from it.polimi.mgrs.strategy_mgr import generate_strategy, parse_strategy
from it.polimi.mgrs.code_mgr import generate_code
from src.strategyviz.strategy2pta.opt_strategy import OptimizedStrategy

LOGGER = Logger('main')

LOGGER.info('Parsing input parameters...')

params = parse_params()

LOGGER.info('Generating Uppaal Stratego model...')

test_params = {'TIME_BOUND': 50, 'WALKING_SPEED': 6, 'DIST_V': 50, 'DIST_FR': 40, 'RAT_DEG': 1.0}
generate_model(test_params, 'end_min_t')

LOGGER.info('Generating Strategy...')

generate_strategy()

LOGGER.info('Parsing Strategy...')

parsed_strategy: OptimizedStrategy = parse_strategy()

LOGGER.info('Generating Decision-making Script...')

generate_code()

LOGGER.info('Done.')
