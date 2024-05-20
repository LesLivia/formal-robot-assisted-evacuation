import configparser
import csv
import os
import statistics as st
from typing import List, Tuple, Dict

import matplotlib.pyplot as plt

config = configparser.ConfigParser()
config.read('./resources/config.ini')
config.sections()

CSV_PATH = './data'
csv_prefix = 'exp_'

NaN_fake_value = 800


def get_fall_length(tup):
    return tup[1]


def process_csv(file):
    metrics: Dict[str, List[float]] = {}
    titles: List[str] = []

    with open(CSV_PATH + '/' + file) as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            if i == 0:
                for key in row[2:]:
                    metrics[key] = []
                    titles.append(key)
            else:
                for j, value in enumerate(row[2:]):
                    try:
                        metrics[titles[j]].append(float(value))
                    except ValueError:
                        pass

    processed_metrics = {key: st.median(metrics[key]) for key in metrics}

    return processed_metrics


exp_metrics: Dict[str, List[Tuple[int, int, Dict[str, float]]]] = {}

for file in os.listdir(CSV_PATH):
    if file.startswith(csv_prefix):
        fields = file.replace(csv_prefix, '').split('_')
        strat_name = '_'.join(fields[:3])
        if strat_name in exp_metrics:
            exp_metrics[strat_name].append((int(fields[3]), int(fields[4].replace('.csv', '')),
                                            process_csv(file)))
        else:
            exp_metrics[strat_name] = [(int(fields[3]), int(fields[4].replace('.csv', '')),
                                        process_csv(file))]

for key in exp_metrics:
    exp_metrics[key].sort(key=get_fall_length)

configurations = ['no-support', 'staff-support', 'passenger-support', 'adaptive-support']
metrics_keys = ['evacuation_time', 'victims', 'staff_requests']

for key in exp_metrics:
    print('\n\n\n-- RESULTS for strategy:{} --'.format(key))

    for metric_key in metrics_keys:
        print('\n\t\t\t\t\t\t\t{}'.format(metric_key))
        print('fall-length\t' + '\t'.join(configurations))
        for length_value in exp_metrics[key]:
            row = '{}\t\t\t'.format(length_value[1])
            for conf in configurations:
                row += '{:.1f}\t\t\t'.format(length_value[2][conf + '_' + metric_key])
            print(row)

out_prefix = 'out_'
out_cols = ['number_of_passengers', 'number_of_staff_members', 'seed', 'helper-gender',
            'helper-culture', 'helper-age', 'fallen-gender', 'fallen-culture',
            'fallen-age', 'helper-fallen-distance', 'staff-fallen-distance', 'decision']
decisions_const = {'ask-help': 1, 'call-staff': 2}
colors = {'ask-help': 'red', 'call-staff': 'blue'}
out_data: List[Dict[str, float]] = []


def map_value(x):
    try:
        return float(x)
    except ValueError:
        return float(decisions_const[x.replace('\n', '')])


for file in os.listdir(CSV_PATH):
    if file.startswith(out_prefix):
        out_data = []
        with open(CSV_PATH + '/' + file) as csv_file:
            lines = csv_file.readlines()
            for line in lines:
                values = line.split(' ')
                out_data.append({out_cols[i]: map_value(v) for i, v in enumerate(values)})
            fig = plt.figure()
            ax = fig.add_subplot()
            for decision in decisions_const:
                color = colors[decision]
                ax.scatter(
                    [x['helper-fallen-distance'] for x in out_data if x['decision'] == decisions_const[decision]],
                    [x['staff-fallen-distance'] for x in out_data if x['decision'] == decisions_const[decision]],
                    color=color, s=0.5)
            ax.set_title(file.replace(out_prefix, ''))
            plt.show()
