import configparser
import math
import os
import random
import sys

curr_path = os.getcwd()
SUBMODULE_PATHS = ['submodules/gi_estimator', 'submodules/StrategyViz', '']

config = configparser.ConfigParser()
config.read('./resources/config/config.ini')
config.sections()
LOG_FILE = config['GENERAL SETTINGS']['controller.log.file'].format(curr_path)
VIOL_FILE = config['STRATEGY SETTINGS']['violations.log.file'].format(curr_path)

LOGGING = config['GENERAL SETTINGS']['controller.logging'] == 'True'

for sub in SUBMODULE_PATHS:
    PROJECT_PATH = 'stratego_generator/' + sub

    sub_path = curr_path.replace('it/polimi/controllers', sub)

    # necessary to access 'controller' in NetLogo
    sys.path.extend([sub_path])

from src.strategyviz.strategy2pta.opt_strategy import OptimizedStrategy
from it.polimi.mgrs.strategy_mgr import parse_strategy
from it.polimi.mgrs.model_mgr import generate_model
from it.polimi.controllers.utils import process_regressors

gi_prob_distr = config['STRATEGY SETTINGS']['GI_PROB_DISTR'].lower()

if gi_prob_distr == 'uniform':
    gi_prob_min = float(config['STRATEGY SETTINGS']['GI_PROB_MIN'])
    gi_prob_max = float(config['STRATEGY SETTINGS']['GI_PROB_MAX'])
    gi_prob = random.uniform(gi_prob_min, gi_prob_max)
else:
    gi_prob = float(config['STRATEGY SETTINGS']['GI_PROB'])

walking_speed = config['STRATEGY SETTINGS']['WALKING_SPEED']
time_bound = config['STRATEGY SETTINGS']['TIME_BOUND']

# Parses Uppaal Stratego verified strategy
ADHOC_STRAT = config['STRATEGY SETTINGS']['ADHOC_STRAT'].lower() == 'true'
ADD_PI = config['STRATEGY SETTINGS']['ADD_PI'].lower() == 'true'


def pick_best_decision(pi1, pi2, dist_v, dist_fr):
    if ADHOC_STRAT:
        if ADD_PI:
            rat_deg = 0.33 * (pi1[0] == pi2[0]) + 0.33 * (pi1[1] == pi2[1]) + 0.33 * (pi1[2] == pi2[2])
        else:
            rat_deg = config['STRATEGY SETTINGS']['RAT_DEG']

        strategy_name = 'end_min_t_{}_{}'.format(rat_deg, time_bound)
        params = {'TIME_BOUND': time_bound, 'WALKING_SPEED': walking_speed, 'RAT_DEG': rat_deg,
                  'DIST_V': int(math.ceil(float(dist_v * 10))), 'DIST_FR': int(math.ceil(float(dist_fr * 10))),
                  'GI_PROB': gi_prob}

        STRATEGY_PATH = config['STRATEGY SETTINGS']['STRATEGY_PATH'].format(strategy_name)
        if os.path.exists(STRATEGY_PATH):
            os.remove(STRATEGY_PATH)

        generate_model(params, strategy_name)
    else:
        strategy_name = config['STRATEGY SETTINGS']['STRATEGY_NAME']

    try:
        strategy: OptimizedStrategy = parse_strategy(strategy_name)
    except FileNotFoundError:
        new_line = "{},{},{},{},{},{},{},{},{}\n".format(pi1[0], pi1[1], pi1[2], pi2[0], pi2[1], pi2[2],
                                                         dist_v, dist_fr, int(time_bound) / 10)
        with open(VIOL_FILE, 'a') as violations_file:
            violations_file.write(new_line)

        return 'violation'
    else:
        decisions = process_regressors(strategy.regressors, gi_prob, dist_v, dist_fr, ADHOC_STRAT)

        # Selects best decision based on strategy and current state
        minimize = config['STRATEGY SETTINGS']['MINIMIZE'].lower() == 'true'
        if (not minimize and decisions.get('call-staff', 0) >= decisions.get('do-help', 0)) or (
                minimize and decisions.get('call-staff', int(time_bound)) <= decisions.get('do-help', int(time_bound))):
            return 'call-staff'
        else:
            return 'ask-help'
