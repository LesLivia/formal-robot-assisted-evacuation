from typing import List, Dict

from src.strategyviz.strategy2pta.opt_strategy import Regressor

CHAN_TO_ACT: Dict[str, str] = {'help_victim!': 'do-help', 'contact_first_responder!': 'call-staff'}


def process_action(act: str):
    upp_chan = act.split(', ')[1]
    return CHAN_TO_ACT[upp_chan]


def process_regressors(regressors: List[Regressor]):
    return {reg.state.state.locs[1].label: (process_action(reg.best_actions[0]), reg.payoff) for reg in regressors}
