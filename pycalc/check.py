import sys

rule_path = sys.argv[1]
with open(rule_path, 'r') as f:
    for line in f.readlines():
        print(line)
with open('C:/Users/zdb/build/check/2.txt', 'w') as f:
    f.write('123')
