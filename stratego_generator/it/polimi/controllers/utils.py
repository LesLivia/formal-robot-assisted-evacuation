from typing import List, Dict

from src.strategyviz.strategy2pta.opt_strategy import Regressor

CHAN_TO_ACT: Dict[str, str] = {'help_victim!': 'do-help', 'contact_first_responder!': 'call-staff'}


def process_action(act: str):
    upp_chan = act.split(', ')[1]
    return CHAN_TO_ACT[upp_chan]


def process_regressors(regressors: List[Regressor], prob_gi: float):
    calibrated_decisions = dict()
    for reg in regressors:
        if reg.state.state.locs[1].label == 'GI':
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
