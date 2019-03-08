# coding=utf-8
import os
import re
import sys

import xlwt

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
                    #print('ignore rule line', line)
                    pass
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
                    #print('ignore config line', line)
                    pass
            else:
                #print('ignore line', line)
                pass
    return configs


def check_result(calc, standard, result):
    if not standard.isdigit():
        standard = '\'' + standard + '\''
    if not result.isdigit():
        result = '\'' + result + '\''
    s = result + calc + standard
    return eval(s)


def read_file(file_path, configs):
    pattern = '\<[\w-]+?\>(.+)'
    current_rule = None
    info = []
    with open(file_path, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if not line:
                continue
            o = re.search(pattern, line)
            if o is not None:
                rule = o.group(1)
                rule = rule.strip()
                if rule in configs:
                    current_rule = rule
                else:
                    current_rule = None
            else:
                if current_rule is not None:
                    check_rules = configs[current_rule]
                    for check_rule in check_rules:
                        keyword = check_rule['keyword']
                        o = re.match(keyword, line)
                        if o is not None:
                            keyword_result = o.group()
                            splitword_pattern = check_rule['splitword']
                            o = re.search(splitword_pattern, line)
                            if o is not None:
                                splitword = o.group()
                                pos = line.find(splitword)
                                result = line[pos + len(splitword):]
                                result = result.strip()
                                if check_rule['standard']:
                                    standard = check_rule['standard']
                                    result = check_result(check_rule['calc'], standard, result)
                                s = 'path is %s, rule is %s, keyword is %s, result is %s' % (file_path, current_rule, keyword_result, result)
                                info.append((file_path, current_rule, keyword_result, result))
                                if sys.platform == 'win32':
                                    try:
                                        print(s.decode('gbk').encode('utf-8'))
                                    except:
                                        print(s)
                                else:
                                    print(s)
        return info


def create_csv():
    book = xlwt.Workbook()
    sheet = book.add_sheet('Sheet1')
    return book, sheet


def try_to_get_unicode(s):
    if sys.platform == 'win32':
        try:
            return s.decode('gbk')
        except:
            return s
    else:
        return s


def write_sheet(info, row):
    for file_path1, current_rule, keyword_result, result in info:
        file_path1 = try_to_get_unicode(file_path1)
        current_rule = try_to_get_unicode(current_rule)
        keyword_result = try_to_get_unicode(keyword_result)
        result = try_to_get_unicode(result)
        col = 0
        sheet.write(row, col, file_path1)
        col += 1
        sheet.write(row, col, current_rule)
        col += 1
        sheet.write(row, col, keyword_result)
        col += 1
        sheet.write(row, col, result)
        row += 1


if __name__ == '__main__':
    rule_path = sys.argv[1]
    configs = read_config(rule_path)
    file_path = sys.argv[2]
    book, sheet = create_csv()
    row = 0
    sheet.write(row, 0, u'路径')
    sheet.write(row, 1, u'命令')
    sheet.write(row, 2, u'规则')
    sheet.write(row, 3, u'检查结果')
    row = 1
    if os.path.isfile(file_path):
        info = read_file(file_path, configs)
        if info:
            write_sheet(info, row)
            row += 1
    elif os.path.isdir(file_path):
        for each in os.listdir(file_path):
            sub_path = os.path.join(file_path, each)
            info = read_file(sub_path, configs)
            if info:
                write_sheet(info, row)
                row += 1
    path = './results.xls'
    print(os.path.abspath(path))
    book.save(path)
