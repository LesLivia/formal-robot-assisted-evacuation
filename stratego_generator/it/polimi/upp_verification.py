import configparser
import json
import os
import sys
from typing import List, Dict

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from tqdm import tqdm

from it.polimi.model.params import Design_Parameter, get_permutations

config = configparser.ConfigParser()
config.read('./resources/config/config.ini')

template_path = config['TEMPLATES SETTING']['TEMPLATES_PATH']

# TODO: can be customisable
N_V = 1
N_S = 2
N = -1

try:
    # Chooses which version of the model to use (either with history, multiple victims, or multiple survivors).
    if sys.argv[1] == 'hist':
        model_name = 'sar_hist.xml'
    elif sys.argv[1] == 'multi_victim':
        model_name = 'sar_multi_victim.xml'
    elif sys.argv[1] == 'multi_survivor':
        model_name = 'sar_multi_survivor.xml'
except IndexError:
    print("First argument either 'hist', 'multi_victim', or 'multi_survivor'.")
else:
    FIXED_PARAMS: Dict[str, int] = {'timebound': 20, 'rat_deg': 1.0, 'dist_fr': 15, 'speed': 1}

    # Processes parameters search space
    with open('./resources/config/params.json') as json_file:
        params_ss = json.load(json_file)
        design_params: List[Design_Parameter] = []
        for key in params_ss:
            if "S{}" in params_ss[key]["key"]:
                for i in range(N_S):
                    design_params.append(
                        Design_Parameter(key, params_ss[key]["key"].format(i + 1), params_ss[key]["type"],
                                         params_ss[key]["min"], params_ss[key]["max"]))
            else:
                design_params.append(Design_Parameter(key, params_ss[key]["key"], params_ss[key]["type"],
                                                      params_ss[key]["min"], params_ss[key]["max"]))

    configurations = get_permutations(design_params, FIXED_PARAMS)

    template = template_path.format(os.getcwd()) + model_name
    exp_values = []
    pr_property_pre = []
    pr_property_post = []

    for conf in tqdm(configurations[:N]):
        with open(template) as template_file:
            tplt_content = template_file.read()
            for i, param in enumerate(conf):
                tplt_content = tplt_content.replace(design_params[i].key, str(param))

        new_model = config['TEMPLATES SETTING']['MODEL_PATH'].format(os.getcwd()) + model_name
        with open(new_model, 'w') as new_model_file:
            new_model_file.write(tplt_content)

        # Runs verification with Uppaal
        uppaal_path = config['UPPAAL SETTINGS']['UPPAAL_PATH']
        script_path = config['UPPAAL SETTINGS']['UPPAAL_SCRIPT_PATH'].format(os.getcwd())
        out_path = config['UPPAAL SETTINGS']['UPPAAL_OUT_PATH'].format(os.getcwd(), sys.argv[1])
        os.system("{} {} {} {}".format(script_path, uppaal_path, new_model, out_path))

        with open(out_path) as out_file:
            lines = out_file.readlines()
            EXP_VALUE = " -- Formula: E[<=TAU;10000](max: r_payoff)"
            indexes = [i for i, line in enumerate(lines) if EXP_VALUE in line]
            est = []
            for i in indexes:
                try:
                    est.append(float(lines[i + 2].split(' = ')[1].split(' (')[0].split(' ')[0]))
                except ValueError:
                    est.append(float(lines[i + 2].split(' ')[-1]))
            try:
                exp_values.append((est[1] - est[0]) / est[0])
            except ZeroDivisionError:
                exp_values.append(0)

            PROPERTY = " -- Formula: Pr[<=TAU](<> s1.__end__ or s2.__end__)\n"
            line = [i for i, l in enumerate(lines) if l == PROPERTY][0]
            pr = [float(x) for x in lines[line + 2].split('[')[1].split(']')[0].split(',')]
            pr_property_pre.append(pr[0] + (pr[1] - pr[0]) / 2)

            PROPERTY = " -- Formula: Pr[<=TAU](<> s1.__end__ or s2.__end__) under EndOptR\n"
            line = [i for i, l in enumerate(lines) if l == PROPERTY][0]
            pr = [float(x) for x in lines[line + 2].split('[')[1].split(']')[0].split(',')]
            pr_property_post.append(pr[0] + (pr[1] - pr[0]) / 2)

    fig, axs = plt.subplots(ncols=3, figsize=(15, 5))

    data_1 = pd.DataFrame(data={'dist1': [conf[4] for conf in configurations[:N]],
                                'dist2': [conf[5] for conf in configurations[:N]],
                                'pr': pr_property_pre})
    data_1 = data_1.pivot(index='dist2', columns='dist1', values='pr')
    sns.heatmap(data_1, cmap="Reds", ax=axs[0], vmin=0.0, vmax=1.0)

    axs[0].set_title('Pr. ending within {}'.format(FIXED_PARAMS['timebound']), fontsize=10)

    data_2 = pd.DataFrame(data={'dist1': [conf[4] for conf in configurations[:N]],
                                'dist2': [conf[5] for conf in configurations[:N]],
                                'gain': exp_values})
    data_2 = data_2.pivot(index='dist2', columns='dist1', values='gain')
    sns.heatmap(data_2, cmap="Blues", ax=axs[1])

    axs[1].set_title('Covered dist. decrease under strategy\n'
                     '(rat.deg:{}, tb: {}, speeds:{})'.format(FIXED_PARAMS['rat_deg'], FIXED_PARAMS['timebound'],
                                                              FIXED_PARAMS['speed']), fontsize=10)

    data_3 = pd.DataFrame(data={'dist1': [conf[4] for conf in configurations[:N]],
                                'dist2': [conf[5] for conf in configurations[:N]],
                                'pr': pr_property_post})
    data_3 = data_3.pivot(index='dist2', columns='dist1', values='pr')
    sns.heatmap(data_3, cmap="Reds", ax=axs[2], vmin=0.0, vmax=1.0)

    axs[2].set_title('Pr. ending within {} under strategy'.format(FIXED_PARAMS['timebound']), fontsize=10)

    plt.show()
