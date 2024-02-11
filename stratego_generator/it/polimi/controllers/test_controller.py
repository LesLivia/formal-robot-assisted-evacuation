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

sensor_data = np.array([int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]),
                        int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7]),
                        float(sys.argv[8]), float(sys.argv[9])])
sensor_data = sensor_data.reshape(1, -1)

manager = GI_Estimator()
sample_sensor_reading_0 = np.zeros(shape=(1, 30))
sample_sensor_reading_1 = np.ones(shape=(1, 30))
sample_sensor_reading = sample_sensor_reading_1 if sys.argv[2] == '1' else sample_sensor_reading_0
gi_prob = manager.get_shared_identity_probability(sample_sensor_reading)

parsed_strategy: OptimizedStrategy = parse_strategy()

if gi_prob > 0.2:
    print('do-help')
else:
    print('call-staff')
