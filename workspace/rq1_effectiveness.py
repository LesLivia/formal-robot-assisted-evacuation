import configparser
import csv
import os
import statistics as st
from bisect import bisect_left
from typing import List, Tuple, Dict, Any, Union

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as ss
import seaborn as sns
from tqdm import tqdm

from idea_logs_processor import process_decisions

config = configparser.ConfigParser()
config.read('./resources/config.ini')
config.sections()

CSV_PATH = './data'
csv_prefix = 'exp_'

out_prefix = 'out_'
out_cols = ['number_of_passengers', 'number_of_staff_members', 'seed', 'helper-gender',
            'helper-culture', 'helper-age', 'fallen-gender', 'fallen-culture',
            'fallen-age', 'helper-fallen-distance', 'staff-fallen-distance', 'decision']
GAMBIT_PATH = './data/gambit/IDEA-no-teleporting/formideable_gambit/exp_rvar_0.5_50_50_{}_gambit_results_from_IDEA.csv'
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


COUNT = 1
STRAT = 'idea_0.12_50'


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

    gambit_times: List[Union[float, None]] = []
    with open(GAMBIT_PATH.format(file.split('_')[-1].replace('.csv', ''))) as g_file:
        reader = csv.reader(g_file)
        for row in reader:
            try:
                gambit_times.append(float(row[1]))
            except ValueError:
                gambit_times.append(None)

    with open(CSV_PATH + '/' + file) as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            if i == 0:
                for key in row[2:]:
                    metrics[key] = []
                    titles.append(key)
            else:
                seeds_with_time[row[1]] = {'strategy_name': strat_name}
                if COUNT > 0 and count_decisions(row[1]) < COUNT:
                    continue

                for j, value in enumerate(row[2:]):
                    try:
                        metrics[titles[j]].append(float(value))
                        seeds_with_time[row[1]][titles[j]] = float(value)
                    except ValueError:
                        pass

    def get_metric(x):
        try:
            return st.median(x)
        except st.StatisticsError:
            return None

    processed_metrics = {key: get_metric(metrics[key]) for key in metrics}

    metrics['gambit-support_evacuation_time'] = gambit_times

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

configurations = ['no-support', 'staff-support', 'passenger-support', 'gambit-support', 'adaptive-support']
metrics_keys = ['evacuation_time', 'victims', 'staff_requests']

fig, axs = plt.subplots(ncols=2, figsize=(25, 7), gridspec_kw={'width_ratios': [2, 1]})

t_evac = []
fr_calls = [[], [], []]

IDEA_decisions = process_decisions(STRAT)
fr_calls[1] = [sum([dec == 'call-staff' for dec in IDEA_decisions[k]]) for k in IDEA_decisions]

for t_fall in all_times[STRAT]:

    for i, conf in enumerate(configurations):
        if len(t_evac) > i:
            t_evac[i].extend(t_fall[2][conf + '_evacuation_time'])
        else:
            t_evac.append(t_fall[2][conf + '_evacuation_time'])

    fr_calls[0].extend(t_fall[2]['staff-support' + '_staff_requests'])
    fr_calls[2].extend(t_fall[2]['adaptive-support' + '_staff_requests'])

# colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:purple', 'tab:red']
colors = ['lightyellow', 'lightyellow', 'lightyellow', 'lightcyan', 'lightgreen']

sns.boxplot(data=t_evac, ax=axs[0], showmeans=True, palette=colors, linewidth=1.5, linecolor='black', width=0.5,
            meanprops={'marker': '^', 'markerfacecolor': 'black', 'markeredgecolor': 'black', 'markersize': '14'})
sns.boxplot(data=fr_calls, ax=axs[1], showmeans=True, palette=[colors[1], colors[3], colors[4]],
            linewidth=1.5, linecolor='black', width=0.5,
            meanprops={'marker': '^', 'markerfacecolor': 'black', 'markeredgecolor': 'black', 'markersize': '14'})

fontsize = 22
axs[0].set_ylim(150, 700)
axs[0].set_xticks(np.arange(len(configurations)))
axs[0].set_xticklabels(['no-support', 'staff-support', 'survivor-support', 'IDEA', 'FormIDEAble'], fontsize=fontsize)
axs[0].set_yticklabels(labels=[str(x) for x in range(100, 800, 100)], fontsize=fontsize - 4)
axs[0].set_ylabel('T_evac', fontsize=fontsize)

stat, pvalue = ss.mannwhitneyu(fr_calls[0], fr_calls[2])
stat_2, pvalue_2 = ss.mannwhitneyu(fr_calls[1], fr_calls[2])
est, mag = VD_A(fr_calls[0], fr_calls[2])
est_2, mag_2 = VD_A(fr_calls[1], fr_calls[2])
title = ('(staff-support vs. FormIDEAble) p-value: {:.1E}, eff. size: {}\n '
         '(IDEA vs. FormIDEAble) p-value: {:.1E}, eff. size: {}').format(
    pvalue, mag, pvalue_2, mag_2)
print(title)
# axs[1].set_title(title ,fontsize=fontsize)
axs[1].set_xticklabels(['staff-support', 'IDEA', 'FormIDEAble'], fontsize=fontsize)
axs[1].set_yticklabels(labels=[str(x) for x in range(0, 45, 5)], fontsize=fontsize - 4)
axs[1].set_ylabel('FR calls', fontsize=fontsize)

plt.savefig('./rq1_box_{}_10_{}.pdf'.format(STRAT, COUNT), bbox_inches='tight')
plt.show()

pairs = [(c1, c2) for i, c1 in enumerate(configurations) for c2 in configurations[i + 1:]]

for pair in pairs:
    i = configurations.index(pair[0])
    j = configurations.index(pair[1])

    stat, pvalue = ss.mannwhitneyu(
        [t for i_t, t in enumerate(t_evac[i]) if
         t is not None and len(t_evac[j]) > i_t and t_evac[j][i_t] is not None],
        [t for j_t, t in enumerate(t_evac[j]) if
         t is not None and len(t_evac[i]) > j_t and t_evac[i][j_t] is not None])
    est, mag = VD_A([t for i_t, t in enumerate(t_evac[i]) if
                     t is not None and len(t_evac[j]) > i_t and t_evac[j][i_t] is not None],
                    [t for j_t, t in enumerate(t_evac[j]) if
                     t is not None and len(t_evac[i]) > j_t and t_evac[i][j_t] is not None])

    print('{} vs. {}: p-value {:.1E}, eff. size {}'.format(pair[0], pair[1], pvalue, mag))
