from typing import List, Dict

from src.strategyviz.strategy2pta.opt_strategy import Regressor

CHAN_TO_ACT: Dict[str, str] = {'help_victim!': 'do-help', 'contact_first_responder!': 'call-staff'}


def process_tf_out(line):
    if 'Prob=' in line:
        return float(line.split('Prob=')[1].split(')')[0])
    else:
        return None


def process_giprob_log(file):
    params = ['helper-gender', 'helper-culture', 'helper-age', 'fallen-gender', 'fallen-culture', 'fallen-age']

    with open(file) as giprob_file:
        lines = giprob_file.readlines()
        tf_inputs = [i for i, l in enumerate(lines) if '[OUT] Input parameters' in l]
        tf_params = [tuple([int(lines[i].split(p + ' ')[1].split(' ')[0]) for p in params]) for i in tf_inputs]
        tf_outputs = [process_tf_out(lines[i + 1]) for i in tf_inputs]
        return {p: tf_outputs[i] for i, p in enumerate(tf_params) if tf_outputs[i] is not None}


def process_action(act: str):
    upp_chan = act.split(', ')[1]
    return CHAN_TO_ACT[upp_chan]


def process_regressors(regressors: List[Regressor], prob_gi: float, fallen_dist: float,
                       staff_dist: float, adhoc_strat: bool):
    calibrated_decisions = dict()

    if not adhoc_strat:
        D_TH = 5
        f_label = 'fu' if fallen_dist <= D_TH else 'fo'
        s_label = 'su' if staff_dist <= D_TH else 'so'
        gi_label = 'GI_{}_{}'.format(f_label, s_label)
    else:
        gi_label = 'GI'

    ngi_label = 'NOT_' + gi_label

    for reg in regressors:
        if reg.state.state.locs[1].label not in [gi_label, ngi_label]:
            continue

        if reg.state.state.locs[1].label == gi_label:
            if process_action(reg.best_actions[0]) in calibrated_decisions:
                calibrated_decisions[process_action(reg.best_actions[0])] += reg.payoff * prob_gi
            else:
                calibrated_decisions[process_action(reg.best_actions[0])] = reg.payoff * prob_gi
        else:
            if process_action(reg.best_actions[0]) in calibrated_decisions:
                calibrated_decisions[process_action(reg.best_actions[0])] += reg.payoff * (1 - prob_gi)
            else:
                calibrated_decisions[process_action(reg.best_actions[0])] = reg.payoff * (1 - prob_gi)

    return calibrated_decisions
