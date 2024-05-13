import matplotlib

matplotlib.use('Agg')

import math
import time
import traceback
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
from pathlib import Path
from pyNetLogo import NetLogoException
import pyNetLogo
from scipy.stats import mannwhitneyu
from typing import List, Dict
import configparser

config = configparser.ConfigParser()
config.read('./resources/config.ini')
config.sections()

WORKSPACE_FOLDER = os.getcwd() + '/'

PLOT_STYLE = 'seaborn-darkgrid'

NETLOGO_PROJECT_DIRECTORY = config['NETLOGO']['netlogo.project']  # type:str
NETLOGO_MODEL_FILE = NETLOGO_PROJECT_DIRECTORY + "v2.11.0.nlogo"  # type:str
NETLOGO_CONFIG_FILE = NETLOGO_PROJECT_DIRECTORY + "config.nls"
NETLOGO_HOME = config['NETLOGO']['netlogo.home']  # type:str
RESULTS_CSV_FILE = WORKSPACE_FOLDER + "data/{}_fall_{}_samples_experiment_results.csv"  # type:str

NETLOGO_VERSION = "5"  # type:str

TURTLE_PRESENT_REPORTER = "count turtles"  # type:str
EVACUATED_REPORTER = "number_passengers - count agents + 1"  # type:str
DEAD_REPORTER = "count agents with [ st_dead = 1 ]"  # type:str
SEED_SIMULATION_REPORTER = "seed-simulation"
FALL_LENGTH_REPORTER = "fall-length-simulation"
SET_STARTING_SEED_COMMAND = "set starting-seed {}"
SET_SIMULATION_ID_COMMAND = 'set SIMULATION_ID "{}"'  # type:str

# SET_STAFF_SUPPORT_COMMAND = "set REQUEST_STAFF_SUPPORT {}"  # type: str
# SET_PASSENGER_SUPPORT_COMMAND = "set REQUEST_BYSTANDER_SUPPORT {}"  # type: str
# SET_FALL_LENGTH_COMMAND = "set DEFAULT_FALL_LENGTH {}"  # type:str
#
# ENABLE_STAFF_COMMAND = SET_STAFF_SUPPORT_COMMAND.format("TRUE")  # type:str
# ENABLE_PASSENGER_COMMAND = SET_PASSENGER_SUPPORT_COMMAND.format("TRUE")  # type:str

# NO_SUPPORT_COLUMN = "no-support"  # type:str
# ONLY_STAFF_SUPPORT_COLUMN = "staff-support"  # type:str
# ONLY_PASSENGER_SUPPORT_COLUMN = "passenger-support"  # type:str
# ADAPTIVE_SUPPORT_COLUMN = "adaptive-support"

# SIMULATION_SCENARIOS = {NO_SUPPORT_COLUMN: [],
#                         ONLY_STAFF_SUPPORT_COLUMN: [ENABLE_STAFF_COMMAND],
#                         ONLY_PASSENGER_SUPPORT_COLUMN: [ENABLE_PASSENGER_COMMAND],
#                         ADAPTIVE_SUPPORT_COLUMN: [ENABLE_PASSENGER_COMMAND,
#                                                   ENABLE_STAFF_COMMAND]}  # type: Dict[str, List[str]]

MAX_NETLOGO_TICKS = 2000  # type: int


# Using https://www.stat.ubc.ca/~rollin/stats/ssize/n2.html
# And https://www.statology.org/pooled-standard-deviation-calculator/


# function to calculate Cohen's d for independent samples
# Inspired by: https://machinelearningmastery.com/effect-size-measures-in-python/

def cohen_d_from_metrics(mean_1, mean_2, std_dev_1, std_dev_2):
    # type: (float, float, float, float) -> float
    pooled_std_dev = np.sqrt((std_dev_1 ** 2 + std_dev_2 ** 2) / 2)
    return (mean_1 - mean_2) / pooled_std_dev


def calculate_sample_size(mean_1, mean_2, std_dev_1, std_dev_2, alpha=0.05, power=0.8):
    # type: (float, float, float, float, float, float) -> float
    analysis = sm.stats.TTestIndPower()  # type: sm.stats.TTestIndPower
    effect_size = cohen_d_from_metrics(mean_1, mean_2, std_dev_1, std_dev_2)
    result = analysis.solve_power(effect_size=effect_size,
                                  alpha=alpha,
                                  power=power,
                                  alternative="two-sided")
    return result


def start_experiments(experiment_configurations, results_file, samples, random_seeds):
    start_time = time.time()  # type: float

    experiment_data = {}  # type: Dict[str, List[float]]
    experiment_data['random_seed'] = random_seeds
    for experiment_name, experiment_commands in experiment_configurations.items():
        scenario_times = run_simulations(experiment_name, samples,
                                         post_setup_commands=experiment_commands,
                                         random_seeds=random_seeds)  # type:List[float]
        experiment_data[experiment_name] = scenario_times

    end_time = time.time()  # type: float
    print("Simulation finished after {} seconds".format(end_time - start_time))

    experiment_results = pd.DataFrame(experiment_data)  # type:pd.DataFrame
    experiment_results.to_csv(results_file)

    print("Data written to {}".format(results_file))


def run_simulation(netlogo_link, simulation_id, post_setup_commands, random_seed):
    try:
        netlogo_link.command("setup")

        starting_seed_cmd = SET_STARTING_SEED_COMMAND.format(random_seed)
        netlogo_link.command(starting_seed_cmd)

        netlogo_link.command(SET_SIMULATION_ID_COMMAND.format(simulation_id))

        current_seed = netlogo_link.report(SEED_SIMULATION_REPORTER)  # type:str
        print("id:{} seed:{} {} executed".format(simulation_id, current_seed, starting_seed_cmd))

        if len(post_setup_commands) > 0:
            for post_setup_command in post_setup_commands:
                netlogo_link.command(post_setup_command)
                print("id:{} seed:{} {} executed".format(simulation_id, current_seed, post_setup_command))
        else:
            print("id:{} seed:{} no post-setup commands".format(simulation_id, current_seed))

        metrics_dataframe = netlogo_link.repeat_report(
            netlogo_reporter=[TURTLE_PRESENT_REPORTER, EVACUATED_REPORTER, DEAD_REPORTER],
            reps=MAX_NETLOGO_TICKS)  # type: pd.DataFrame

        evacuation_finished = metrics_dataframe[
            metrics_dataframe[TURTLE_PRESENT_REPORTER] == metrics_dataframe[DEAD_REPORTER]]

        evacuation_time = evacuation_finished.index.min()  # type: float
        print("id:{} seed:{} evacuation time {}".format(simulation_id, current_seed, evacuation_time))
        if math.isnan(evacuation_time):
            metrics_dataframe.to_csv("data/nan_df.csv")
            print("DEBUG!!! info to data/nan_df.csv")

        # generate_video(simulation_id=simulation_id)
        return evacuation_time
    except NetLogoException:
        traceback.print_exc()
        raise
    except Exception:
        traceback.print_exc()

    return None


def initialize(gui, random_seed):
    netlogo_link = pyNetLogo.NetLogoLink(netlogo_home=NETLOGO_HOME,
                                         netlogo_version=NETLOGO_VERSION,
                                         gui=gui)

    with open('./resources/netlogo_config_tplt.txt') as config_tplt:
        lines = config_tplt.readlines()
        for i, line in enumerate(lines):
            if 'starting-seed' in line:
                lines[i] = SET_STARTING_SEED_COMMAND.format(random_seed) + '\n'
                break

    with open(NETLOGO_CONFIG_FILE, "w") as config_file:
        config_file.writelines(lines)

    netlogo_link.load_model(NETLOGO_MODEL_FILE)
    return netlogo_link


def run_simulations(experiment_name, samples, post_setup_commands, gui=False, random_seeds=None):
    simulation_parameters = [{"simulation_id": "{}_{}".format(experiment_name, simulation_index),
                              "post_setup_commands": post_setup_commands,
                              "random_seed": random_seeds[simulation_index]}
                             for simulation_index in range(samples)]

    results = []  # type: List[float]
    for exp, params in enumerate(simulation_parameters):
        link = initialize(gui, params['random_seed'])
        simulation_output = run_simulation(link, params['simulation_id'], params['post_setup_commands'],
                                           params['random_seed'])
        if simulation_output:
            results.append(simulation_output)

        link.kill_workspace()

    return results


def get_dataframe(csv_file):
    # type: (str) -> pd.DataFrame
    results_dataframe = pd.read_csv(csv_file, index_col=[0])  # type: pd.DataFrame
    results_dataframe = results_dataframe.dropna()

    return results_dataframe


def plot_results(csv_file, samples_in_title=False):
    # type: (str, bool) -> None
    file_description = Path(csv_file).stem  # type: str
    results_dataframe = get_dataframe(csv_file)  # type: pd.DataFrame
    results_dataframe = results_dataframe.loc[:, results_dataframe.columns != 'random_seed']
    # results_dataframe = results_dataframe.rename(columns={
    #     NO_SUPPORT_COLUMN: "No Support",
    #     ONLY_STAFF_SUPPORT_COLUMN: "Proself-Oriented",
    #     ONLY_PASSENGER_SUPPORT_COLUMN: "Prosocial-Oriented",
    #     ADAPTIVE_SUPPORT_COLUMN: "Adaptive"
    # })

    print(results_dataframe.describe())

    title = ""
    # order = ["No Support", "Prosocial-Oriented", "Proself-Oriented", "Adaptive"]  # type: List[str]
    order = None

    if samples_in_title:
        title = "{} samples".format(len(results_dataframe))
    _ = sns.violinplot(data=results_dataframe, order=order).set_title(title)
    plt.savefig(WORKSPACE_FOLDER + "img/" + file_description + "_violin_plot.png", bbox_inches='tight', pad_inches=0)
    plt.savefig(WORKSPACE_FOLDER + "img/" + file_description + "_violin_plot.eps", bbox_inches='tight', pad_inches=0)
    plt.show()
    plt.clf()

    _ = sns.stripplot(data=results_dataframe, order=order, jitter=True).set_title(title)
    plt.savefig(WORKSPACE_FOLDER + "img/" + file_description + "_strip_plot.png", bbox_inches='tight', pad_inches=0)
    plt.savefig(WORKSPACE_FOLDER + "img/" + file_description + "_strip_plot.eps", bbox_inches='tight', pad_inches=0)
    plt.show()


def test_hypothesis(first_scenario_column, second_scenario_column, csv_file, alternative="two-sided"):
    # type: (str, str, str, str) -> None
    print("CURRENT ANALYSIS: Analysing file {}".format(csv_file))
    results_dataframe = get_dataframe(csv_file)  # type: pd.DataFrame

    first_scenario_data = results_dataframe[first_scenario_column].values  # type: List[float]
    first_scenario_mean = np.mean(first_scenario_data).item()  # type:float
    first_scenario_stddev = np.std(first_scenario_data).item()  # type:float

    second_scenario_data = results_dataframe[second_scenario_column].values  # type: List[float]
    second_scenario_mean = np.mean(second_scenario_data).item()  # type:float
    second_scenario_stddev = np.std(second_scenario_data).item()  # type:float

    print("{}-> mean = {} std = {} len={}".format(first_scenario_column, first_scenario_mean, first_scenario_stddev,
                                                  len(first_scenario_data)))
    print("{}-> mean = {} std = {} len={}".format(second_scenario_column, second_scenario_mean, second_scenario_stddev,
                                                  len(second_scenario_data)))
    print("Recommended Sample size: {}".format(
        calculate_sample_size(first_scenario_mean, second_scenario_mean, first_scenario_stddev,
                              second_scenario_stddev)))

    null_hypothesis = "MANN-WHITNEY RANK TEST: " + \
                      "The distribution of {} times is THE SAME as the distribution of {} times".format(
                          first_scenario_column, second_scenario_column)  # type: str
    alternative_hypothesis = "ALTERNATIVE HYPOTHESIS: the distribution underlying {} is stochastically {} than the " \
                             "distribution underlying {}".format(first_scenario_column, alternative,
                                                                 second_scenario_column)  # type:str

    threshold = 0.05  # type:float
    u, p_value = mannwhitneyu(x=first_scenario_data, y=second_scenario_data, alternative=alternative)
    print("U={} , p={}".format(u, p_value))
    if p_value > threshold:
        print("FAILS TO REJECT NULL HYPOTHESIS: {}".format(null_hypothesis))
    else:
        print("REJECT NULL HYPOTHESIS: {}".format(null_hypothesis))
        print(alternative_hypothesis)


def simulate_and_store(simulation_scenarios, results_file_name, samples, random_seeds):
    updated_simulation_scenarios = {scenario_name: commands
                                    for scenario_name, commands in
                                    simulation_scenarios.items()}  # type: Dict[str, List[str]]
    start_experiments(updated_simulation_scenarios, results_file_name, samples, random_seeds)


def get_current_file_metrics(simulation_scenarios, current_file):
    results_dataframe = get_dataframe(current_file)
    metrics_dict = {}

    for scenario in simulation_scenarios.keys():
        metrics_dict["{}_mean".format(scenario)] = results_dataframe[scenario].mean()
        metrics_dict["{}_std".format(scenario)] = results_dataframe[scenario].std()
        metrics_dict["{}_median".format(scenario)] = results_dataframe[scenario].median()
        metrics_dict["{}_min".format(scenario)] = results_dataframe[scenario].min()
        metrics_dict["{}_max".format(scenario)] = results_dataframe[scenario].max()

    return metrics_dict


def perform_analysis(target_scenario, simulation_scenarios, current_file):
    plot_results(csv_file=current_file)
    current_file_metrics = get_current_file_metrics(simulation_scenarios, current_file)

    for alternative_scenario in simulation_scenarios.keys():
        if alternative_scenario != target_scenario:
            test_hypothesis(first_scenario_column=target_scenario,
                            second_scenario_column=alternative_scenario,
                            alternative="less",
                            csv_file=current_file)

    return current_file_metrics
