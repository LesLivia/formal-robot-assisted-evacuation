import os
import sys

import numpy as np

curr_path = os.getcwd()
SUBMODULE_PATH = 'submodules/gi_estimator'
PROJECT_PATH = 'stratego_generator/' + SUBMODULE_PATH

if 'impact' in curr_path:
    sub_path = os.getcwd().replace('impact2.10.7', PROJECT_PATH)
else:
    sub_path = os.getcwd().replace('resources/robot_controllers', SUBMODULE_PATH)

# necessary to access 'controller' in NetLogo
sys.path.extend([sub_path])

# necessary to suppress tensorflow logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from controller import AutonomicManagerController

manager = AutonomicManagerController()
sample_sensor_reading = np.zeros(shape=(1, 30))  # type: np.ndarray
gi_prob = manager.get_shared_identity_probability(sample_sensor_reading)

print(gi_prob)

if sys.argv[1] == '1':
    print('do-help')
else:
    print('call-staff')
