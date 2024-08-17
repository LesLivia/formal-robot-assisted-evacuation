import configparser
import csv
import os
import statistics as st
from bisect import bisect_left
from typing import List, Tuple, Dict, Any

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as ss
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
from tqdm import tqdm

config = configparser.ConfigParser()
config.read('./resources/config.ini')
config.sections()

CSV_PATH = './data'
csv_prefix = 'exp_'

out_prefix = 'out_'
out_cols = ['number_of_passengers', 'number_of_staff_members', 'seed', 'helper-gender',
            'helper-culture', 'helper-age', 'fallen-gender', 'fallen-culture',
            'fallen-age', 'helper-fallen-distance', 'staff-fallen-distance', 'decision']
gambit_metric = 'gambit-support_evacuation_time'
missing_gambit_metrics = ['gambit-support_victims', 'gambit-support_staff_requests']
decisions_const = {'ask-help': 1, 'call-staff': 2}
colors = {'ask-help': 'red', 'call-staff': 'blue'}
out_data: List[Dict[str, float]] = []


def VD_A(treatment: List[float], control: List[float]):
    m = len(treatment)
    n = len(control)
    # if m != n:
    #    raise ValueError("Data d and f must have the same length")
    r = ss.rankdata(treatment + control)
    r1 = sum(r[0:m])
    # Compute the measure
    # A = (r1/m - (m+1)/2)/n # formula (14) in Vargha and Delaney, 2000
    A = (2 * r1 - m * (m + 1)) / (2 * n * m)  # equivalent formula to avoid accuracy errors
    levels = [0.147, 0.33, 0.474]  # effect sizes from Hess and Kromrey, 2004
    magnitude = ["negligible", "small", "medium", "large"]
    scaled_A = (A - 0.5) * 2
    magnitude = magnitude[bisect_left(levels, abs(scaled_A))]
    estimate = A
    return estimate, magnitude


def get_fall_length(tup):
    return tup[1]


COUNT = 10
STRAT = 'tosem_1.0_100'


def count_decisions(seed):
    for file in os.listdir(CSV_PATH):
        if file.startswith(out_prefix):
            with open(CSV_PATH + '/' + file) as csv_file:
                lines = csv_file.readlines()
                lines = [l for l in lines if seed in l]
                if len(lines) > 0:
                    return len(lines)
    return 0


def process_csv(file, strat_name):
    metrics: Dict[str, List[float]] = {}
    titles: List[str] = []
    seeds_with_time: Dict[str, Dict[str, Any]] = {}
    gambit_times: Dict[str, float] = {}

    try:
        with open(CSV_PATH + '/gambit_' + file) as gambit_file:
            reader = csv.reader(gambit_file)
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                gambit_times[row[4]] = float(row[1])
    except FileNotFoundError:
        pass

    with open(CSV_PATH + '/' + file) as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            if i == 0:
                for key in row[2:]:
                    metrics[key] = []
                    titles.append(key)
                if len(gambit_times) > 0:
                    metrics[gambit_metric] = []
                    for miss in missing_gambit_metrics:
                        metrics[miss] = []
            else:
                seeds_with_time[row[1]] = {'strategy_name': strat_name}
                if COUNT > 0 and count_decisions(row[1]) < COUNT:  # if the robot makes less than 3 decisions
                    continue

                for j, value in enumerate(row[2:]):
                    try:
                        metrics[titles[j]].append(float(value))
                        seeds_with_time[row[1]][titles[j]] = float(value)
                    except ValueError:
                        pass

                if row[1] in gambit_times:
                    metrics[gambit_metric].append(gambit_times[row[1]])
                    for miss in missing_gambit_metrics:
                        metrics[miss].append(0.0)

    def get_metric(x):
        try:
            return st.median(x)
        except st.StatisticsError:
            return None

    processed_metrics = {key: get_metric(metrics[key]) for key in metrics}

    return processed_metrics, seeds_with_time, metrics


exp_metrics: Dict[str, List[Tuple[int, int, Dict[str, float]]]] = {}
evac_times: Dict[str, Dict[str, Any]] = {}
all_times: Dict[str, List[Tuple[int, int, Dict[str, List[float]]]]] = {}

for file in tqdm(os.listdir(CSV_PATH)):
    if file.startswith(csv_prefix):
        fields = file.replace(csv_prefix, '').split('_')
        strat_name = '_'.join(fields[:3])
        median, seeds_w_time, all_metrics = process_csv(file, strat_name)
        evac_times.update(seeds_w_time)
        if strat_name in exp_metrics:
            exp_metrics[strat_name].append((int(fields[3]), int(fields[4].replace('.csv', '')), median))
        else:
            exp_metrics[strat_name] = [(int(fields[3]), int(fields[4].replace('.csv', '')), median)]
        if strat_name in all_times:
            all_times[strat_name].append((int(fields[3]), int(fields[4].replace('.csv', '')), all_metrics))
        else:
            all_times[strat_name] = [(int(fields[3]), int(fields[4].replace('.csv', '')), all_metrics)]

for key in exp_metrics:
    exp_metrics[key].sort(key=get_fall_length)

configurations = ['no-support', 'staff-support', 'passenger-support', 'adaptive-support', 'gambit-support']
metrics_keys = ['evacuation_time', 'victims', 'staff_requests']

aggregate_score = False
for key in exp_metrics:
    print('\n\n\n-- RESULTS for strategy:{} --'.format(key))

    if aggregate_score:
        print('\n\t\t\t\t\t\t\t{}'.format('AGGREGATE SCORE'))
        print('fall-length\t' + '\t'.join(configurations))

        for length_value in exp_metrics[key]:
            row = '{}\t\t\t'.format(length_value[1])

            scores = []
            for key_i, metric_key in enumerate(metrics_keys):
                scores.append([])
                for conf_i, conf in enumerate(configurations):
                    try:
                        scores[key_i][0] = min(scores[key_i][0], float(length_value[2][conf + '_' + metric_key]))
                    except IndexError:
                        scores[key_i].append(float(length_value[2][conf + '_' + metric_key]))
                    try:
                        scores[key_i][1] = max(scores[key_i][1], float(length_value[2][conf + '_' + metric_key]))
                    except IndexError:
                        scores[key_i].append(float(length_value[2][conf + '_' + metric_key]))
                    try:
                        scores[key_i][2].append(float(length_value[2][conf + '_' + metric_key]))
                    except IndexError:
                        scores[key_i].append([float(length_value[2][conf + '_' + metric_key])])

            for conf_i, conf in enumerate(configurations):
                aggr_score = sum(
                    [(metric[2][conf_i] - metric[0]) / max((metric[1] - metric[0]), 1) for metric in scores])
                row += '{:.1f}\t\t\t'.format(aggr_score)
            print(row)

    for metric_key in metrics_keys:
        print('\n\t\t\t\t\t\t\t{}'.format(metric_key))
        print('fall-length\t' + '\t'.join(configurations))
        for length_value in exp_metrics[key]:
            row = '{}\t\t\t'.format(length_value[1])
            for conf in configurations:
                try:
                    row += '{:.1f}\t\t\t'.format(length_value[2][conf + '_' + metric_key])
                except TypeError:
                    row += 'None\t\t\t'
                except KeyError:
                    row += 'None\t\t\t'
            print(row)

fig, axs = plt.subplots(ncols=2, figsize=(12, 7), gridspec_kw={'width_ratios': [2, 1]})

t_evac = []
fr_calls = [[], []]

for t_fall in all_times[STRAT]:

    for i, conf in enumerate(configurations[:-1]):
        if len(t_evac) > i:
            t_evac[i].extend(t_fall[2][conf + '_evacuation_time'])
        else:
            t_evac.append(t_fall[2][conf + '_evacuation_time'])

    fr_calls[0].extend(t_fall[2]['staff-support' + '_staff_requests'])
    fr_calls[1].extend(t_fall[2]['adaptive-support' + '_staff_requests'])

sns.boxplot(data=t_evac, ax=axs[0], showmeans=True,
            meanprops={'marker': '^', 'markerfacecolor': 'white', 'markeredgecolor': 'black', 'markersize': '9'})
sns.boxplot(data=fr_calls, ax=axs[1], showmeans=True,
            meanprops={'marker': '^', 'markerfacecolor': 'white', 'markeredgecolor': 'black', 'markersize': '9'})

axs[0].set_ylim(200, 700)
axs[0].set_xticks(np.arange(len(configurations[:-1])))
axs[0].set_xticklabels(['no-support', 'staff-support', 'survivor-support', 'FormIdeAble'], fontsize=12)
axs[0].set_ylabel('T_evac', fontsize=14)

stat, pvalue = ss.mannwhitneyu(fr_calls[0], fr_calls[1])
est, mag = VD_A(fr_calls[0], fr_calls[1])
axs[1].set_title('p-value: {:.1E}, eff. size: {}'.format(pvalue, mag), fontsize=12)
axs[1].set_xticklabels(['staff-support', 'FormIdeAble'], fontsize=12)
axs[1].set_ylabel('FR calls', fontsize=14)

plt.savefig('./rq2_box_{}_10_{}.pdf'.format(STRAT, COUNT), bbox_inches='tight')
plt.show()

pairs = [(c1, c2) for i, c1 in enumerate(configurations[:-1]) for c2 in configurations[i + 1:-1]]

for pair in pairs:
    i = configurations.index(pair[0])
    j = configurations.index(pair[1])

    stat, pvalue = ss.mannwhitneyu(t_evac[i], t_evac[j])
    est, mag = VD_A(t_evac[i], t_evac[j])

    print('{} vs. {}: p-value {:.1E}, eff. size {}'.format(pair[0], pair[1], pvalue, mag))

extra_plots = False


def map_value(x):
    try:
        return float(x)
    except ValueError:
        return float(decisions_const[x.replace('\n', '')])


for file in os.listdir(CSV_PATH):
    if not extra_plots:
        break

    if file.startswith(out_prefix):
        out_data = []
        with open(CSV_PATH + '/' + file) as csv_file:
            lines = csv_file.readlines()
            for line in lines:
                values = line.split(' ')

                try:
                    evac_times[values[2]]['number_of_passengers'] = int(values[0])
                    evac_times[values[2]]['number_of_staff_members'] = int(values[1])
                except KeyError:
                    pass

                out_data.append({out_cols[i]: map_value(v) for i, v in enumerate(values)})
                genders = (out_data[-1]['helper-gender'], out_data[-1]['fallen-gender'])
                cultures = (out_data[-1]['helper-culture'], out_data[-1]['fallen-culture'])
                ages = (out_data[-1]['helper-age'], out_data[-1]['fallen-age'])
                out_data[-1]['rat_deg'] = 0.33 * (genders[0] == genders[1]) + 0.33 * (
                        cultures[0] == cultures[1]) + 0.33 * (ages[0] == ages[1])

            if extra_plots:
                _dummy = Axes3D
                fig = plt.figure(figsize=[10, 10])
                axs = fig.add_subplot(projection='3d')
                labels = ['helper-fallen-distance', 'staff-fallen-distance', 'rat_deg']
                for decision in decisions_const:
                    color = colors[decision]
                    axs.scatter(
                        [x[labels[0]] for x in out_data if x['decision'] == decisions_const[decision]],
                        [x[labels[1]] for x in out_data if x['decision'] == decisions_const[decision]],
                        [x[labels[2]] for x in out_data if x['decision'] == decisions_const[decision]],
                        color=color, s=2.0)
                # ax.view_init(elev=20, azim=120)
                axs.set_xlabel(labels[0])
                axs.set_ylabel(labels[1])
                axs.set_zlabel(labels[2])
                axs.set_title(file.replace(out_prefix, ''))
                plt.show()

colors = ['red', 'green', 'orange', 'blue']
exclude_confs = ['no-support', 'passenger-support']

if extra_plots:
    for strategy in exp_metrics:
        if 'var' not in strategy:
            continue

        fig = plt.figure(figsize=[10, 10])
        axs = fig.add_subplot()
        labels = ['number_of_passengers', 'evacuation_time']

        for i, conf in enumerate(configurations):
            if conf in exclude_confs:
                continue
            try:
                x_values = [evac_times[seed][labels[0]] for seed in evac_times
                            if evac_times[seed]['strategy_name'] == strategy and labels[0] in evac_times[seed]]
                times = [evac_times[seed][conf + '_' + labels[1]] for seed in evac_times
                         if evac_times[seed]['strategy_name'] == strategy and labels[0] in evac_times[seed]]
                axs.scatter(x_values, times, color=colors[i], s=3.0)
            except KeyError:
                pass

        axs.set_xlabel(labels[0])
        axs.set_ylabel(labels[1])
        axs.set_title(strategy)
        plt.ylim(200, 350)
        plt.show()
