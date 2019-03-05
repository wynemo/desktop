import sys

rule_path = sys.argv[1]
with open(rule_path, 'r') as f:
    for line in f.readlines():
        print(line)
