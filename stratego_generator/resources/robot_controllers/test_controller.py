import sys

import numpy as np

import analyser
from controller import AutonomicManagerController

manager = AutonomicManagerController(analyser.SyntheticTypeAnalyser(model_file="/Users/lestingi/Desktop/phd-workspace/SaR/formal-robot-assisted-evacuation/stratego_generator/submodules/gi_estimator/model/trained_model.h5"))
sample_sensor_reading = np.zeros(shape=(1, 30))  # type: np.ndarray
gi_prob = manager.get_shared_identity_probability(sample_sensor_reading)

if sys.argv[1] == '1':
    print('do-help')
else:
    print('call-staff')
