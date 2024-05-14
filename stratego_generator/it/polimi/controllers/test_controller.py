import configparser
import os
import random
import sys

curr_path = os.getcwd()
SUBMODULE_PATHS = ['submodules/gi_estimator', 'submodules/StrategyViz', '']

config = configparser.ConfigParser()
if 'impact' in curr_path:
    config.read(curr_path.replace('impact2.10.7', 'stratego_generator/resources/config/config.ini'))
    config.sections()
    LOG_FILE = config['GENERAL SETTINGS']['controller.log.file'].format(curr_path)
    LOG_FILE = LOG_FILE.replace('impact2.10.7', 'stratego_generator')
else:
    config.read('./resources/config/config.ini')
    config.sections()
    LOG_FILE = config['GENERAL SETTINGS']['controller.log.file'].format(curr_path)

LOGGING = config['GENERAL SETTINGS']['controller.logging'] == 'True'

for sub in SUBMODULE_PATHS:
    PROJECT_PATH = 'stratego_generator/' + sub

    if 'impact' in curr_path:
        sub_path = curr_path.replace('impact2.10.7', PROJECT_PATH)
    else:
        sub_path = curr_path.replace('it/polimi/controllers', sub)

    # necessary to access 'controller' in NetLogo
    sys.path.extend([sub_path])

from src.strategyviz.strategy2pta.opt_strategy import OptimizedStrategy
from it.polimi.mgrs.strategy_mgr import parse_strategy
from it.polimi.controllers.utils import process_regressors

gi_prob_distr = config['STRATEGY SETTINGS']['GI_PROB_DISTR'].lower()

if gi_prob_distr == 'uniform':
    gi_prob_min = float(config['STRATEGY SETTINGS']['GI_PROB_MIN'])
    gi_prob_max = float(config['STRATEGY SETTINGS']['GI_PROB_MAX'])
    gi_prob = random.uniform(gi_prob_min, gi_prob_max)
else:
    gi_prob = float(config['STRATEGY SETTINGS']['GI_PROB'])

# Parses Uppaal Stratego verified strategy
strategy: OptimizedStrategy = parse_strategy()
decisions = process_regressors(strategy.regressors, gi_prob, float(sys.argv[8]), float(sys.argv[9]))

# Logs inputs and outputs
if LOGGING:
    new_line = "\n{},{},{},{},{},{},{},{},{},{:.4f}".format(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]),
                                                            int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]),
                                                            int(sys.argv[7]), float(sys.argv[8]), float(sys.argv[9]),
                                                            gi_prob)
    with open(LOG_FILE, "a") as log_file:
        log_file.write(new_line)

# Selects best decision based on strategy and current state
if decisions.get('call-staff', 0) >= decisions.get('do-help', 0):
    print('call-staff')
else:
    print('ask-help')
