import sys

state_stopped = 0
state_rule = 1
state_rule_stopped = 2
state_config = 3

rule_prefix = 'rule:'
keyword_prefix = 'keyword:'
splitword_prefix = 'splitword:'
calc_prefix = 'calc:'
standard_prefix = 'standard:'


def read_config(path):
    """
    rule:display version
    keyword:xxx
    splitword:,
    calc:=
    standard:qqqq
    """
    configs = {}
    current_config = {}
    current_name = None
    state = state_stopped
    with open(path, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith(rule_prefix):
                if state in (state_stopped, state_rule_stopped):
                    current_name = line.replace(rule_prefix, '', 1)
                    configs[current_name] = []
                    state = state_rule
                else:
                    print('ignore rule line', line)
            elif line.startswith(keyword_prefix) or line.startswith(splitword_prefix) or line.startswith(
                    calc_prefix) or line.startswith(standard_prefix):
                if state in (state_rule, state_rule_stopped):
                    pos = line.find(':')
                    config_name = line[:pos]
                    current_config[config_name] = line.replace(line[:pos + 1], '', 1)
                    if len(current_config) == 4:
                        state = state_rule_stopped
                        configs[current_name].append(current_config)
                        current_config = {}
                else:
                    print('ignore config line', line)
            else:
                print('ignore line', line)
    return configs


def read_file(file_path):
    pass


if __name__ == '__main__':
    rule_path = sys.argv[1]
    configs = read_config(rule_path)
    print(configs)
