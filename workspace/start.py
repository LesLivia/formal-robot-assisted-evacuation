import sys
from random import randint

import pandas as pd

from abm_analysis import simulate_and_store, perform_analysis, WORKSPACE_FOLDER

MIN_SEED = -2147483648
MAX_SEED = 2147483647

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
        "adaptive-support": [SET_FRAME_GENERATION_COMMAND.format("TRUE"),
                             SET_FALL_LENGTH_COMMAND.format(FALL_DURATION),
                             SET_PASSENGER_SUPPORT_COMMAND.format("TRUE"),
                             SET_STAFF_SUPPORT_COMMAND.format("TRUE")]
    }

    results_file_path = WORKSPACE_FOLDER + "data/"
    results_file_name = "exp_{}_{}_{}.csv".format(STRAT_NAME, N_SAMPLES, FALL_DURATION)
    random_seeds = [randint(MIN_SEED, MAX_SEED) for i in range(N_SAMPLES)]

    simulate_and_store(simulation_scenarios, results_file_path + results_file_name, N_SAMPLES, random_seeds)
    metrics = pd.DataFrame([perform_analysis("adaptive-support", simulation_scenarios,
                                             results_file_path, results_file_name)])
    metrics.to_csv(WORKSPACE_FOLDER + "data/metrics_{}_{}_{}.csv".format(STRAT_NAME, N_SAMPLES, FALL_DURATION))


if __name__ == "__main__":
    main()
