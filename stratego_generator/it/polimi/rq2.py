import configparser
import json
import os
import sys
import time
from bisect import bisect_left
from typing import List, Dict

import matplotlib.pyplot as plt
import scipy.stats as ss
import seaborn as sns
from tqdm import tqdm

from it.polimi.model.params import Design_Parameter, get_permutations


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


config = configparser.ConfigParser()
config.read('./resources/config/config.ini')

with open(config['UPPAAL SETTINGS']['uppaal.time.log'].format(os.getcwd()), 'w') as log_file:
    log_file.truncate(0)

template_path = config['TEMPLATES SETTING']['TEMPLATES_PATH']

if len(sys.argv) > 2:
    with open('./resources/config/{}.json'.format(sys.argv[2])) as model_config_file:
        model_params = json.load(model_config_file)
else:
    with open('./resources/config/model_config.json') as model_config_file:
        model_params = json.load(model_config_file)

N_V = int(model_params['n_victims'])
N_S = int(model_params['n_survivors'])
if len(sys.argv) > 4:
    N = int(sys.argv[4])
else:
    N = -1

try:
    # Chooses which version of the model to use (either with history, multiple victims, or multiple survivors).
    if sys.argv[1] == 'hist':
        model_name = 'sar_hist.xml'
    elif sys.argv[1] == 'multi_victim':
        model_name = 'sar_multi_victim.xml'
    elif sys.argv[1] == 'multi_survivor':
        model_name = 'sar_pi_multi_survivor.xml'
except IndexError:
    print("First argument either 'hist', 'multi_victim', or 'multi_survivor'.")
else:
    FIXED_PARAMS: Dict[str, int] = {'timebound': int(sys.argv[3]), 'rat_deg': 0.75, 'dist_fr': model_params['dist_fr'],
                                    'speed': model_params['survivor_speed'], 'dist_s': 0}

    # Processes parameters search space
    with open('./resources/config/model_params.json') as json_file:
        params_ss = json.load(json_file)
        design_params: List[Design_Parameter] = []
        for key in params_ss:
            if "S{}" in params_ss[key]["key"]:
                for i in range(N_S):
                    design_params.append(
                        Design_Parameter(key, params_ss[key]["key"].format(i + 1), params_ss[key]["type"],
                                         params_ss[key]["min"], params_ss[key]["max"]))
            elif "V{}" in params_ss[key]["key"]:
                for i in range(N_V):
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

    # For each configuration --->
    for conf in tqdm(configurations[:N]):
        start_time = time.time()

        with open(template) as template_file:
            tplt_content = template_file.read()
            for i, param in enumerate(conf):
                tplt_content = tplt_content.replace(design_params[i].key, str(param))

            # FIXME: should be configurable
            if model_name in ['sar_multi_victim.xml', 'sar_hist.xml']:
                tplt_content = tplt_content.replace("**N_V**", str(N_V))
                tplt_content = tplt_content.replace("**PI_S**", '{' + ','.join(
                    ['{' + ','.join([str(x) for x in model_params['pi_survivors'][v]]) + '}' for v in
                     model_params['pi_survivors']]) + '}')
                tplt_content = tplt_content.replace("**PI_V**", '{' + ','.join(
                    ['{' + ','.join([str(x) for x in model_params['pi_victims'][v]]) + '}' for v in
                     model_params['pi_victims']]) + '}')
                tplt_content = tplt_content.replace("**PSI**", model_params['property'])

        new_model = config['TEMPLATES SETTING']['MODEL_PATH'].format(os.getcwd()) + model_name
        with open(new_model, 'w') as new_model_file:
            new_model_file.write(tplt_content)

        # ---> performs verification with Uppaal
        uppaal_path = config['UPPAAL SETTINGS']['UPPAAL_PATH']
        script_path = config['UPPAAL SETTINGS']['UPPAAL_SCRIPT_PATH'].format(os.getcwd())
        out_path = config['UPPAAL SETTINGS']['UPPAAL_OUT_PATH'].format(os.getcwd(),
                                                                       model_name.replace('.xml', '') +
                                                                       '_' + str(FIXED_PARAMS['timebound']) + '_' +
                                                                       '_'.join([str(x) for x in conf[15:-2]]))
        os.system("{} {} {} {}".format(script_path, uppaal_path, new_model, out_path))

        with open(out_path) as out_file:
            lines = out_file.readlines()
            EXP_VALUE_PRE = " -- Formula: E[<=TAU;10000](max: {})\n".format(model_params['exp_value'])
            EXP_VALUE_POST = " -- Formula: E[<=TAU;10000](max: {}) under {}\n".format(model_params['exp_value'],
                                                                                      model_params['strat_name'])
            indexes = [i for i, line in enumerate(lines) if line in [EXP_VALUE_PRE, EXP_VALUE_POST]]
            est = []
            for i in indexes:
                try:
                    est.append(float(lines[i + 2].split(' = ')[1].split(' (')[0].split(' ')[0]))
                except ValueError:
                    est.append(float(lines[i + 2].split(' ')[-1]))
            try:
                exp_values.append((est[0], est[1], (est[1] - est[0]) / est[0] * 100))
            except ZeroDivisionError:
                exp_values.append(0)

            PROPERTY = " -- Formula: Pr[<=TAU](<> {})\n".format(model_params['property'])
            line = [i for i, l in enumerate(lines) if l == PROPERTY][0]
            pr = [float(x) for x in lines[line + 2].split('[')[1].split(']')[0].split(',')]
            pr_property_pre.append(pr[0] + (pr[1] - pr[0]) / 2)

            PROPERTY = " -- Formula: Pr[<=TAU](<> {}) under {}\n".format(model_params['property'],
                                                                         model_params['strat_name'])
            line = [i for i, l in enumerate(lines) if l == PROPERTY][0]
            pr = [float(x) for x in lines[line + 2].split('[')[1].split(']')[0].split(',')]
            pr_property_post.append(pr[0] + (pr[1] - pr[0]) / 2)

        # RQ3: logs wall-clock time necessary to perform the verification
        with open(config['UPPAAL SETTINGS']['uppaal.time.log'].format(os.getcwd()), 'a') as log_file:
            log_file.write('{},{},{},{}\n'.format(out_path.split('/')[-1], conf[model_params["plot_dim_1"]],
                                                  conf[model_params["plot_dim_2"]], time.time() - start_time))

    fig, axs = plt.subplots(ncols=2, figsize=(7, 3))

    colors = ['lightyellow', 'lightgreen']
    metrics = {'r_payoff': "Task Duration", 'fr_usage': "FR Calls"}

    data_1 = [[x[0] for x in exp_values], [x[1] for x in exp_values]]
    sns.boxplot(data=data_1, ax=axs[0], showmeans=True, palette=colors,
                meanprops={'marker': '^', 'markerfacecolor': 'white', 'markeredgecolor': 'black', 'markersize': '9'})

    data_2 = [pr_property_pre, pr_property_post]
    sns.boxplot(data=data_2, ax=axs[1], showmeans=True, palette=colors,
                meanprops={'marker': '^', 'markerfacecolor': 'white', 'markeredgecolor': 'black', 'markersize': '9'})

    stat, pvalue = ss.mannwhitneyu(data_1[0], data_1[1])
    pvalue = '{:.1e}'.format(pvalue) if pvalue > 0.05 else '<0.05'
    est, mag = VD_A(data_1[0], data_1[1])
    axs[0].set_title('Exp. Value of {}\np-value: {},\n'
                     'effect size: {}'.format(metrics[model_params['exp_value']], pvalue, mag), fontsize=12)
    axs[0].set_xticklabels(['BL', 'FormIDEAble'], fontsize=12)

    stat, pvalue = ss.mannwhitneyu(data_2[0], data_2[1])
    pvalue = '{:.1e}'.format(pvalue) if pvalue > 0.05 else '<0.05'
    est, mag = VD_A(data_2[0], data_2[1])
    axs[1].set_title('Pr. of psi holding\np-value: {},\n'
                     'effect size: {}'.format(pvalue, mag), fontsize=12)
    axs[1].set_xticklabels(['BL', 'FormIDEAble'], fontsize=12)

    plt.savefig("rq2_box_{}_{}.pdf".format(sys.argv[2], sys.argv[3]), bbox_inches="tight")
