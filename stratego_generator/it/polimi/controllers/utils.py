from typing import List, Dict

from src.strategyviz.strategy2pta.opt_strategy import Regressor

CHAN_TO_ACT: Dict[str, str] = {'help_victim!': 'do-help', 'contact_first_responder!': 'call-staff'}


def process_action(act: str):
    upp_chan = act.split(', ')[1]
    return CHAN_TO_ACT[upp_chan]


def process_regressors(regressors: List[Regressor], prob_gi: float, fallen_dist: float, staff_dist: float):
    calibrated_decisions = dict()

    D_TH = 5
    f_label = 'fu{}'.format(D_TH) if fallen_dist <= D_TH else 'fo{}'.format(D_TH)
    s_label = 'su{}'.format(D_TH) if staff_dist <= D_TH else 'so{}'.format(D_TH)

    gi_label = 'GI_{}_{}'.format(f_label, s_label)
    ngi_label = 'N' + gi_label

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
