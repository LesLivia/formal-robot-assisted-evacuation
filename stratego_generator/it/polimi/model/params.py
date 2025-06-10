import itertools
import sys
from typing import List, Union, Dict

import numpy as np


class Design_Parameter:
    def __init__(self, name, key, type, min, max):
        self.name = name
        self.key = key
        self.type = type
        self.min = min
        self.max = max


STEP_FLOAT = 0.5
STEP_INT = 10 if sys.argv[1] == 'hist' else 2


def get_permutations(params: List[Design_Parameter], fixed_params: Dict[str, Union[float, int]]):
    values: List[List[Union[float, int]]] = []
    for param in params:
        if param.name in fixed_params:
            values.append([fixed_params[param.name]])
        elif param.type == 'int':
            values.append(list(range(param.min, param.max + STEP_INT, STEP_INT)))
        elif param.type == 'float':
            values.append(list(np.arange(param.min, param.max + STEP_FLOAT, STEP_FLOAT)))

    return list(itertools.product(*values))
