import configparser
import csv
import sys
from random import randint

import pandas as pd

from abm_analysis import simulate_and_store, perform_analysis, WORKSPACE_FOLDER

config = configparser.ConfigParser()
config.read('./resources/config.ini')
config.sections()

MIN_SEED = -2147483648
MAX_SEED = 2147483647

RAND_SEEDS = config['NETLOGO']['random.seeds'] == 'Y'
SEEDS_FILE = config['NETLOGO']['seeds.file']
PASS_MIN = int(config['NETLOGO']['PASS_MIN'])
PASS_MAX = int(config['NETLOGO']['PASS_MAX'])
STAFF_MIN = int(config['NETLOGO']['STAFF_MIN'])
STAFF_MAX = int(config['NETLOGO']['STAFF_MAX'])
NORMAL_STAFF_MIN = int(config['NETLOGO']['NORMAL_STAFF_MIN'])
NORMAL_STAFF_MAX = int(config['NETLOGO']['NORMAL_STAFF_MAX'])

SET_FRAME_GENERATION_COMMAND = "set ENABLE_FRAME_GENERATION {}"
SET_FALL_LENGTH_COMMAND = "set DEFAULT_FALL_LENGTH {}"

SET_STAFF_SUPPORT_COMMAND = "set REQUEST_STAFF_SUPPORT {}"
SET_PASSENGER_SUPPORT_COMMAND = "set REQUEST_BYSTANDER_SUPPORT {}"


def main():
    N_SAMPLES = int(sys.argv[1])
    FALL_DURATION = int(sys.argv[2])
    STRAT_NAME = sys.argv[3]

    simulation_scenarios = {
        "no-support": [SET_FRAME_GENERATION_COMMAND.format("FALSE"),
                       SET_FALL_LENGTH_COMMAND.format(FALL_DURATION)],
        "staff-support": [SET_FRAME_GENERATION_COMMAND.format("FALSE"),
                          SET_FALL_LENGTH_COMMAND.format(FALL_DURATION),
                          SET_STAFF_SUPPORT_COMMAND.format("TRUE")],
        "passenger-support": [SET_FRAME_GENERATION_COMMAND.format("FALSE"),
                              SET_FALL_LENGTH_COMMAND.format(FALL_DURATION),
                              SET_PASSENGER_SUPPORT_COMMAND.format("TRUE")],
        "adaptive-support": [SET_FRAME_GENERATION_COMMAND.format("FALSE"),
                             SET_FALL_LENGTH_COMMAND.format(FALL_DURATION),
                             SET_PASSENGER_SUPPORT_COMMAND.format("TRUE"),
                             SET_STAFF_SUPPORT_COMMAND.format("TRUE")]
    }

    results_file_path = WORKSPACE_FOLDER + "data/"
    results_file_name = "exp_{}_{}_{}.csv".format(STRAT_NAME, N_SAMPLES, FALL_DURATION)

    if RAND_SEEDS:
        random_seeds = [randint(MIN_SEED, MAX_SEED) for i in range(N_SAMPLES)]
        random_passengers = [randint(PASS_MIN, PASS_MAX) for i in range(N_SAMPLES)]
        random_staff = [randint(STAFF_MIN, STAFF_MAX) for i in range(N_SAMPLES)]
        random_normal_staff = [randint(NORMAL_STAFF_MIN, NORMAL_STAFF_MAX) for i in range(N_SAMPLES)]
    else:
        with open(SEEDS_FILE.format(FALL_DURATION)) as seed_file:
            reader = csv.reader(seed_file)
            random_seeds = [int(row[4]) for i, row in enumerate(reader) if i > 0][:N_SAMPLES]
            seed_file.seek(0)
            random_passengers = [int(row[3]) for i, row in enumerate(reader) if i > 0][:N_SAMPLES]
            seed_file.seek(0)
            random_staff = [int(row[5]) for i, row in enumerate(reader) if i > 0][:N_SAMPLES]
            seed_file.seek(0)
            random_normal_staff = [int(row[2]) for i, row in enumerate(reader) if i > 0][:N_SAMPLES]

    simulate_and_store(simulation_scenarios, results_file_path + results_file_name, N_SAMPLES,
                       random_seeds, random_passengers, random_staff, random_normal_staff)
    metrics = pd.DataFrame([perform_analysis("adaptive-support", simulation_scenarios,
                                             results_file_path, results_file_name)])
    metrics.to_csv(WORKSPACE_FOLDER + "data/metrics_{}_{}_{}.csv".format(STRAT_NAME, N_SAMPLES, FALL_DURATION))


if __name__ == "__main__":
    main()
