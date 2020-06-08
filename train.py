#!/usr/bin/env python
# coding: utf-8

import config
import helper
import json
import sys


def train_file(filename):
    declarative_list = []
    interrogative_list = []
    rules = {}
    i = 0
    with open(config.rules_path + filename) as file:
        lines = file.readlines()
        for line in lines:
            if '' == line.strip():
                continue
            i = i + 1
            pair = line.split('|')
            print(line)
            decla_tags_list = helper.preprocess(pair[0])
            for decla_tags in decla_tags_list:
                interro_tags_list = helper.preprocess(pair[1])
                if len(interro_tags_list) > 1:
                    print('### Length of interro_tags_list > 1 ###')
                    interro_tags = interro_tags_list[-1]
                    print(pair[0])
                    print(decla_tags_list)
                    print(pair[1])
                    print(interro_tags_list)
                    continue
                elif len(interro_tags_list) == 1:
                    interro_tags = interro_tags_list[0]
                else:
                    continue
                declarative_list.append(decla_tags)
                new_interro_tags = helper.get_new_interro_tags_by_decla_interro_tags(decla_tags, interro_tags)
                interrogative_list.append(new_interro_tags)
                rule = {' '.join([tag['POS'] + ':' + tag['NE'] + ':' + tag['SR'] for tag in decla_tags]): \
                    ' '.join([tag['POS'] + ':' + tag['NE'] + ':' + tag['SR'] for tag in new_interro_tags])}
                rules.update(rule)
                print(rule)
                print('')
    print('Total lines: ' + str(i))
    print('Total rules: ' + str(len(rules)))
    print('Generating data file.')
    with open(config.rules_path + filename.replace('.txt', '') + '.rules', 'w') as file:
        json.dump(rules, file)
        # print('Don\'t forget to rename file. Wh.txt.rules to Wh.rules')
    reload_rules()
    print('Generating analysis file.')
    with open(config.rules_path + filename + '.analysis.txt', 'w') as file:
        i = 0
        for i in range(len(declarative_list)):
            file.write('\n')
            file.write(str(i))
            file.write('\n')
            file.write(' '.join([tag['W'] for tag in declarative_list[i]]))
            file.write('\n')
            file.write(' '.join([tag['W'] for tag in interrogative_list[i]]))
            file.write('\n')
            file.write(str([tag['POS'] + ':' + tag['NE'] + ':' + tag['SR'] for tag in declarative_list[i]]))
            file.write('\n')
            file.write(str([tag['POS'] + ':' + tag['NE'] + ':' + tag['SR'] for tag in interrogative_list[i]]))
            file.write('\n')
            file.write(' '.join([tag['POS'] + ':' + tag['NE'] + ':' + tag['SR'] for tag in declarative_list[i]]))
            file.write('\n')
            file.write(' '.join([tag['POS'] + ':' + tag['NE'] + ':' + tag['SR'] for tag in interrogative_list[i]]))
            file.write('\n')
            file.write(str(declarative_list[i]))
            file.write('\n')
            file.write(str(interrogative_list[i]))
            file.write('\n')
        file.write('\n----------\n')
    return rules

def train_pair(ques_word, declarative, interrogative):
    filename = config.rules_path + ques_word + '.rules'
    rules = None
    with open(filename) as file:
        rules = json.load(file)
        decla_tags_list = helper.preprocess(declarative)
        for decla_tags in decla_tags_list:
            interro_tags_list = helper.preprocess(interrogative)
            if len(interro_tags_list) > 1:
                print('### Length of interro_tags_list > 1 ###')
                interro_tags = interro_tags_list[-1]
                print(pair[0])
                print(decla_tags_list)
                print(pair[1])
                print(interro_tags_list)
                continue
            else:
                interro_tags = interro_tags_list[0]
            new_interro_tags = helper.get_new_interro_tags_by_decla_interro_tags(decla_tags, interro_tags)
            rule = {' '.join([tag['POS'] + ':' + tag['NE'] + ':' + tag['SR'] for tag in decla_tags]): \
                    ' '.join([tag['POS'] + ':' + tag['NE'] + ':' + tag['SR'] for tag in new_interro_tags])}
            print(rule)
            rules.update(rule)
    with open(filename, 'w') as file:
        json.dump(rules, file)
    reload_rules()
    incremental_file = config.rules_path + ques_word + '.incremental.txt'
    with open(incremental_file, 'a') as file:
        file.write(declarative + ' | ' + interrogative + '\n')

def train_pair_test(ques_word, declarative, interrogative):
    # filename = config.rules_path + ques_word + '.rules'
    # rules = None
    # with open(filename) as file:
        # rules = json.load(file)
        decla_tags_list = helper.preprocess(declarative)
        # print(decla_tags_list)
        for decla_tags in decla_tags_list:
            interro_tags_list = helper.preprocess(interrogative)
            # print(interro_tags_list)
            if len(interro_tags_list) > 1:
                print('### Length of interro_tags_list > 1 ###')
                interro_tags = interro_tags_list[-1]
                print(pair[0])
                print(decla_tags_list)
                print(pair[1])
                print(interro_tags_list)
                continue
            else:
                interro_tags = interro_tags_list[0]
            new_interro_tags = helper.get_new_interro_tags_by_decla_interro_tags(decla_tags, interro_tags)
            rule = {' '.join([tag['POS'] + ':' + tag['NE'] + ':' + tag['SR'] for tag in decla_tags]): \
                    ' '.join([tag['POS'] + ':' + tag['NE'] + ':' + tag['SR'] for tag in new_interro_tags])}
            print(rule)
    #         rules.update(rule)
    # with open(filename, 'w') as file:
    #     json.dump(rules, file)
    # incremental_file = config.rules_path + ques_word + '.incremental.txt'
    # with open(incremental_file, 'a') as file:
    #     file.write(declarative + ' | ' + interrogative + '\n')

def reload_rules():
    helper.loadrules()
    print('Rules reloaded.')


if __name__ == "__main__":
    argv = sys.argv
    arguments = ' '.join(argv[1:])
    if '|' in arguments:
        pair = arguments.split('|')
        # train_pair(pair[1].split()[0].capitalize(), pair[0], pair[1])
        train_pair_test(pair[1].split()[0].capitalize(), pair[0], pair[1])
    elif '.txt' in arguments:
        train_file(arguments)
    elif 'all' in arguments:
        train_file('What.txt')
        train_file('When.txt')
        train_file('Where.txt')
        train_file('Who.txt')
    else:
        print('Usage:')
        print('python train.py all')
        print('python train.py filename.txt')
        print('python train.py "Declarative sentence. | Interrogative question?"')
