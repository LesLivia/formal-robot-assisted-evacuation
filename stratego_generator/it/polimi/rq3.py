import csv
from bisect import bisect_left
from typing import List

import matplotlib.pyplot as plt
import scipy.stats as ss
import seaborn as sns


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


data = []

# RQ1-related wall-clock plots

files_rq1 = {1: ['./resources/logs/wallclocktimes.csv']}

for i, model_size in enumerate(files_rq1):
    for file in files_rq1[model_size]:
        with open(file, 'r') as f:
            reader = csv.reader(f)
            if len(data) > i:
                data[i].extend([float(row[0]) for row in reader])
            else:
                data.append([float(row[0]) for row in reader])

baseline = [0] * len(data[0])

stat, pvalue = ss.mannwhitneyu(baseline, data[0])
est, mag = VD_A(baseline, data[0])

print(pvalue, mag)

# RQ2-related wall-clock plots

files_rq2 = {2: ['./resources/logs/multi_survivor_time.csv', './resources/logs/multi_victim_time.csv'],
             4: ['./resources/logs/hist_x2_time.csv'], 9: ['./resources/logs/hist_x3_time.csv'],
             16: ['./resources/logs/hist_x4_time.csv'], 25: ['./resources/logs/hist_x5_time.csv']}

for i, model_size in enumerate(files_rq2):
    for file in files_rq2[model_size]:
        with open(file, 'r') as f:
            reader = csv.reader(f)
            if len(data) > i + 1:
                data[i + 1].extend([float(row[3]) for row in reader])
            else:
                data.append([float(row[3]) for row in reader])

plt.figure(figsize=(15, 7))

pvalues = []
eff_sizes = []
for v in data:
    baseline = [0] * len(v)

    stat, pvalue = ss.mannwhitneyu(baseline, v)
    est, mag = VD_A(baseline, v)

    pvalues.append(pvalue)
    eff_sizes.append(mag)

print(pvalues, eff_sizes)

sns.boxplot(data=data, showmeans=True, palette=['white'] * len(data), linewidth=1, linecolor='black', width=0.5,
            meanprops={'marker': '^', 'markerfacecolor': 'white', 'markeredgecolor': 'black', 'markersize': '9'})
sns.pointplot(data=[sum(v) / len(v) for v in data], color='black', linewidth=1)

fontsize=18

# plt.title('RQ1', fontsize=fontsize)
plt.xlabel('N_s x N_v', fontsize=fontsize)
plt.ylabel('Wall-clock time [s]', fontsize=fontsize)
files_rq1.update(files_rq2)
plt.xticks(ticks=range(6), labels=[str(key) for key in files_rq1], fontsize=fontsize-2)
plt.yticks(fontsize=fontsize-2)

plt.savefig('./rq3.pdf', bbox_inches='tight')
plt.show()
