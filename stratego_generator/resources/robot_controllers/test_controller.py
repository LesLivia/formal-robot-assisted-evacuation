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

sensor_data = np.array([int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]),
                        int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7]),
                        float(sys.argv[8]), float(sys.argv[9])])
sensor_data = sensor_data.reshape(1, -1)

manager = AutonomicManagerController()
sample_sensor_reading_0 = np.zeros(shape=(1, 30))
sample_sensor_reading_1 = np.ones(shape=(1, 30))
sample_sensor_reading = sample_sensor_reading_1 if sys.argv[2] == '1' else sample_sensor_reading_0
gi_prob = manager.get_shared_identity_probability(sample_sensor_reading)

if gi_prob > 0.2:
    print('do-help')
else:
    print('call-staff')
