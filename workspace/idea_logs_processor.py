out_path_1 = './data/gambit/IDEA-no-teleporting/formideable_gambit/experiment_output.txt'
out_path_2 = './data/gambit/IDEA-no-teleporting/formideable_gambit_TOSEM/experiment_output.txt'


def process_decisions(strat_name):
    idea_decisions = []

    if 'TOSEM' in strat_name:
        path = out_path_2
    else:
        path = out_path_1

    with open(path, 'r') as f:
        lines = f.readlines()
        idea_decisions = [(int(line.split('seed_')[1].split('_')[0]), line.split('\\n\\n')[1].split(' ')[0])
                          for line in lines if '[OUT] Response from controller' in line]

    decisions_dict = dict()
    for dec in idea_decisions:
        if dec[0] in decisions_dict:
            decisions_dict[dec[0]].append(dec[1])
        else:
            decisions_dict[dec[0]] = [dec[1]]

    return decisions_dict
