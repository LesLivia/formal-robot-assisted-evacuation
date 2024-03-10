import os
import sys

import numpy as np

curr_path = os.getcwd()
SUBMODULE_PATHS = ['submodules/gi_estimator', 'submodules/StrategyViz', '']

for sub in SUBMODULE_PATHS:
    PROJECT_PATH = 'stratego_generator/' + sub

    if 'impact' in curr_path:
        sub_path = os.getcwd().replace('impact2.10.7', PROJECT_PATH)
    else:
        sub_path = os.getcwd().replace('it/polimi/controllers', sub)

    # necessary to access 'controller' in NetLogo
    sys.path.extend([sub_path])

# necessary to suppress tensorflow logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from controller import GI_Estimator
from src.strategyviz.strategy2pta.opt_strategy import OptimizedStrategy
from it.polimi.mgrs.strategy_mgr import parse_strategy
from it.polimi.controllers.utils import process_regressors

# Processes the current state of the scenario into input parameters for
# the model estimating the GI probability
sensor_data = np.array([int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]),
                        int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7])])
# ,float(sys.argv[8]), float(sys.argv[9])])
sensor_data = sensor_data.reshape(1, -1)

# Estimates the probability of having developed a Group Identity
manager = GI_Estimator()
encoded_data = manager.encoder.transform(sensor_data)
gi_prob = manager.get_shared_identity_probability(encoded_data)

# Parses Uppaal Stratego verified strategy
strategy: OptimizedStrategy = parse_strategy()
decisions = process_regressors(strategy.regressors)

# Selects best decision based on strategy and current state

calibrated_decisions = dict()
calibrated_decisions['GI'] = (decisions['GI'][0], decisions['GI'][1] * gi_prob)
calibrated_decisions['NOT_GI'] = (decisions['NOT_GI'][0], decisions['NOT_GI'][1] * (1 - gi_prob))

if calibrated_decisions['GI'][1] > calibrated_decisions['NOT_GI'][1]:
    print(calibrated_decisions['GI'][0])
else:
    print(calibrated_decisions['NOT_GI'][0])
