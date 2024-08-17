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


# RQ1-related wall-clock plots

files = {2: ['./resources/logs/multi_survivor_time.csv', './resources/logs/multi_victim_time.csv'],
         4: ['./resources/logs/hist_x2_time.csv'], 9: ['./resources/logs/hist_x3_time.csv'],
         16: ['./resources/logs/hist_x4_time.csv'], 25: ['./resources/logs/hist_x5_time.csv']}

data = []

for i, model_size in enumerate(files):
    for file in files[model_size]:
        with open(file, 'r') as f:
            reader = csv.reader(f)
            if len(data) > i:
                data[i].extend([float(row[3]) for row in reader])
            else:
                data.append([float(row[3]) for row in reader])

fig, axs = plt.subplots(figsize=(9, 6))

pvalues = []
eff_sizes = []
for v in data:
    baseline = [0] * len(v)

    stat, pvalue = ss.mannwhitneyu(baseline, v)
    est, mag = VD_A(baseline, v)

    pvalues.append(pvalue)
    eff_sizes.append(mag)

print(pvalues, eff_sizes)

sns.boxplot(data=data, showmeans=True,
            meanprops={'marker': '^', 'markerfacecolor': 'white', 'markeredgecolor': 'black', 'markersize': '9'})
sns.pointplot(data=[sum(v) / len(v) for v in data], color='black', linewidth=1)

axs.set_xlabel('N_s x N_v', fontsize=14)
axs.set_ylabel('Wall-clock time [s]', fontsize=14)
axs.set_xticklabels([str(key) for key in files], fontsize=14)

plt.savefig('./rq3_uppaal_only_times.pdf', bbox_inches='tight')
plt.show()
