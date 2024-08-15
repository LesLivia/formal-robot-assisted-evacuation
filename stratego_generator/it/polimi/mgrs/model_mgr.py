import configparser
import os
from typing import Dict, Any

from it.polimi.logger.logger import Logger

LOGGER = Logger('Model Manager')

config = configparser.ConfigParser()
curr_path = os.getcwd()
if 'impact' in curr_path:
    config.read(curr_path.replace('impact2.10.7', 'stratego_generator/resources/config/config.ini'))
else:
    config.read('./resources/config/config.ini')
config.sections()

if 'impact' in curr_path:
    to_format = curr_path.replace('impact2.10.7', 'stratego_generator')
else:
    to_format = '.'

TPLT_PATH = config['TEMPLATES SETTING']['TEMPLATES_PATH'].format(to_format)
MODEL_PATH = config['TEMPLATES SETTING']['MODEL_PATH'].format(to_format)
QUERY_PATH = config['TEMPLATES SETTING']['QUERY_PATH'].format(to_format)
STRAT_PATH = config['STRATEGY SETTINGS']['STRATEGY_PATH']
SCRIPT_PATH = config['UPPAAL SETTINGS']['UPPAAL_SCRIPT_PATH'].format(to_format)

TPLT_EXT = config['TEMPLATES SETTING']['TEMPLATES_EXT']
TPLT_NAME = config['TEMPLATES SETTING']['TEMPLATE_NAME']
TPLT = TPLT_PATH + TPLT_NAME + TPLT_EXT
QUERY_EXT = config['TEMPLATES SETTING']['QUERY_EXT']

QUERY_TPLT = """strategy EndOptR = minE (r_payoff) [<=TAU] : <> s.__end__
saveStrategy(\"{}\", EndOptR)"""

UPP_PATH = config['UPPAAL SETTINGS']['UPPAAL_PATH']


def generate_model(params: Dict[str, Any], strat_name: str):
    # Generate Uppaal model
    with open(TPLT) as tplt:
        tplt_lines = tplt.readlines()
        for i, line in enumerate(tplt_lines):
            if '**TIME_BOUND**' in line:
                tplt_lines[i] = line.replace('**TIME_BOUND**', str(params['TIME_BOUND']))
            if '**RAT_DEG**' in line:
                tplt_lines[i] = tplt_lines[i].replace('**RAT_DEG**', str(params['RAT_DEG']))
            if '**SPEED**' in line:
                tplt_lines[i] = tplt_lines[i].replace('**SPEED**', str(params['WALKING_SPEED']))
            if '**VICTIM_DIST**' in line:
                tplt_lines[i] = tplt_lines[i].replace('**VICTIM_DIST**', str(params['DIST_V']))
            if '**FR_DIST**' in tplt_lines[i]:
                tplt_lines[i] = tplt_lines[i].replace('**FR_DIST**', str(params['DIST_FR']))

    MODEL_FILE = MODEL_PATH + strat_name + TPLT_EXT
    with open(MODEL_FILE, 'w+') as model_file:
        model_file.writelines(tplt_lines)

    # Generate Uppaal query file to calculate strategy and export it
    QUERY_FILE = QUERY_PATH + strat_name + QUERY_EXT
    with open(QUERY_FILE, 'w+') as query_file:
        QUERY = QUERY_TPLT.format(to_format + STRAT_PATH[1:].format(strat_name))
        query_file.writelines(QUERY)

    # Run Uppaal experiment
    os.system('{} {} {} {}'.format(SCRIPT_PATH, UPP_PATH, MODEL_FILE, QUERY_FILE))
    return MODEL_FILE, QUERY_FILE
