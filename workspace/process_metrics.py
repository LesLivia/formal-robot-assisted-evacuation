import configparser
import csv
import os
import statistics as st
from typing import List, Tuple, Dict

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

    processed_metrics = {key: st.mean(metrics[key]) for key in metrics}

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
    print('-- RESULTS for strategy:{} --'.format(key))

    for metric_key in metrics_keys:
        print('\n\t\t\t\t\t\t\t{}'.format(metric_key))
        print('fall-length\t' + '\t'.join(configurations))
        for length_value in exp_metrics[key]:
            row = '{}\t\t\t'.format(length_value[1])
            for conf in configurations:
                row += '{:.1f}\t\t\t'.format(length_value[2][conf + '_' + metric_key])
            print(row)
