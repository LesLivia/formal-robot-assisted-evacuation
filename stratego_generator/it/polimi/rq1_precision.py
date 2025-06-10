import sys
from typing import List, Tuple, Dict

from tqdm import tqdm

from it.polimi.controllers.rq2_controller import pick_best_decision


def process_line(l):
    fields = l.split(' ')
    return ([int(fields[3]), int(fields[4]), int(fields[5])], [int(fields[6]), int(fields[7]), int(fields[8])], float(
        fields[9]), float(fields[10]),
            int(fields[2]), int(fields[14].replace(')', '')), int(fields[12].replace(')', '')))


def viol_key(line):
    fields = line.split(' ')
    return (int(fields[0]), int(fields[3]), int(fields[6].replace(')', '')))


def viol_value(line):
    fields = line.split(' ')
    return int(fields[8].replace('\n', ''))


INPUT_PARAMS = '../workspace/data/out_rq4_5.txt'
params: List[Tuple[List[int], List[int], float, float, int, int, int]] = []
with open(INPUT_PARAMS, 'r') as in_f:
    lines = in_f.readlines()
    params.extend([process_line(line) for line in tqdm(lines)])

IN_SIM_VIOLATIONS = '../workspace/data/verification_rq4_5.txt'
occ: Dict[Tuple[int, int, int], int] = dict()
with open(IN_SIM_VIOLATIONS, 'r') as in_f:
    lines = in_f.readlines()
    occ.update({viol_key(line): viol_value(line) for line in tqdm(lines) if 'in' in line})
    non_violations = {key: occ[key] for key in occ if occ[key] <= int(sys.argv[1])}
    violations = {key: occ[key] for key in occ if occ[key] > int(sys.argv[1])}

params = [p for p in params if (p[4], p[5], p[6]) in occ]

P = len([p for p in params if (p[4], p[5], p[6]) in non_violations])
N = len([p for p in params if (p[4], p[5], p[6]) in violations])

PP = 0
PN = 0
TP = 0
TN = 0

for p in tqdm(params):
    if pick_best_decision(p[0], p[1], p[2], p[3]) == 'violation':
        PN += 1
        if (p[4], p[5], p[6]) in violations:
            TN += 1
    else:
        PP += 1
        if (p[4], p[5], p[6]) not in violations:
            TP += 1

print(f'P: {P}, N: {N}, PP: {PP}, PN:{PN}, TP: {TP}, TN: {TN}')
print('Precision: {:.3f}, Recall: {:.3f}'.format((TP + TN) / (P + N), TP / P))
