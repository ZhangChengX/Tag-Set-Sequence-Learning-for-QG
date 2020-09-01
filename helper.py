# coding: utf-8

import os
import json
import requests
import config
from nltk.metrics.distance import edit_distance
from nltk.tree import Tree


def preprocess(sentence):
    r = requests.get(url = 'http://localhost:' + str(config.port) + '/preprocess?sentence=' + sentence)
    return r.json()

def preprocess_learning(sentence):
    r = requests.get(url = 'http://localhost:' + str(config.port) + '/preprocess_learning?sentence=' + sentence)
    return r.json()

def pos(sentence):
    r = requests.get(url = 'http://localhost:' + str(config.port) + '/pos?sentence=' + sentence)
    return r.json()

def ner(sentence):
    r = requests.get(url = 'http://localhost:' + str(config.port) + '/ner?sentence=' + sentence)
    return r.json()

def srl(sentence):
    r = requests.get(url = 'http://localhost:' + str(config.port) + '/srl?sentence=' + sentence)
    return r.json()

def ctree(sentence):
    r = requests.get(url = 'http://localhost:' + str(config.port) + '/ctree?sentence=' + sentence)
    return Tree.fromstring(r.json())

def dtree(sentence):
    r = requests.get(url = 'http://localhost:' + str(config.port) + '/dtree?sentence=' + sentence)
    return r.json()

def segment_by_sentence(text, tokenizer):
    # from nltk.tokenize import sent_tokenize
    # sentence_list = sent_tokenize(text)
    sentences = []
    sentence_list = tokenizer.tokenize(text)
    for sent in sentence_list:
        sentences.extend([s for s in sent.split('\n') if s])
    return sentences

def load_rules(path):
    rules = {}
    for filename in os.listdir(path):
        if filename[-6:] == '.rules':
            with open(path + filename) as file:
                rules[filename[:-6]] = json.load(file)
    return rules

def get_sub_trees(tree:Tree, labels = ['NP']):
    ''' The height of a tree
        containing no children is 1; the height of a tree
        containing only leaves is 2; and the height of any other
        tree is one plus the maximum of its children's
        heights. '''
    # Get subtrees that only contain one level subtree
    # print(list(tree.subtrees()))
    subtrees = list(tree.subtrees(filter=lambda x: x.label() in labels and x.height()<=3 ))
    return [subtree.leaves() for subtree in subtrees]

def get_new_interro_tags_by_decla_interro_tags(decla_tags:list, interro_tags:list):
    new_interro_tags = []
    is_in_sr_tag = False
    last_word = ''
    current_word = ''
    word_list = [tag['W'].lower() for tag in decla_tags] # Using lower() to avoid John = john
    i = 0
    for i in range(len(interro_tags)):
        # Check if w is any of decla word, append w of decla to new list
        if interro_tags[i]['W'].lower() in word_list:
            index = word_list.index(interro_tags[i]['W'].lower())
            new_interro_tags.append(decla_tags[index])
        else:
            # Check if w with previous or next w is a part of any SR labeled word
            for word in word_list:
                if i > 0 and interro_tags[i-1]['W'].lower() + ' ' + interro_tags[i]['W'].lower() in word:
                    is_in_sr_tag = True
                if len(interro_tags) > i+1 and interro_tags[i]['W'].lower() + ' ' + interro_tags[i+1]['W'].lower() in word:
                    is_in_sr_tag = True
            if is_in_sr_tag:
                if i >= len(decla_tags):
                    index = len(decla_tags) - 1
                else:
                    index = i
                # if current tag and previous tag are same SR tag, remove previous and add new one.
                current_word = decla_tags[index]['W']
                if current_word == last_word:
                    new_interro_tags.pop()
                new_interro_tags.append(decla_tags[index])
                last_word = decla_tags[index]['W']
            else:
                # tmp = interro_tags[i].copy()
                # # tmp['SR'] = tmp['SR'] + 'NEW'
                # tmp['ADD'] = 'NEW'
                new_interro_tags.append(interro_tags[i])
            is_in_sr_tag = False
        i = i + 1
    # k = ' '.join([tag['POS'] + ':' + tag['NE'] + ':' + tag['SR'] for tag in decla_tags])
    # v = ' '.join([tag['POS'] + ':' + tag['NE'] + ':' + tag['SR'] for tag in new_interro_tags])
    return new_interro_tags
    

def adjust_order(new_seq, based_seq):
    rst_seq = []
    for b_tag in based_seq:
        tmp_is_match = False
        for n_tag in new_seq:
            if is_tag_match(b_tag, n_tag):
                rst_seq.append(n_tag)
                new_seq.remove(n_tag)
                tmp_is_match = True
                break
        if not tmp_is_match:
            if len(new_seq) > 0:
                rst_seq.append(new_seq[0])
                new_seq.pop()
    return rst_seq
        

def find_lcs(x:list, y:list, m:int, n:int): 
    # https://www.geeksforgeeks.org/longest-common-substring-dp-29/
    # Create a table to store lengths of longest common suffixes of substrings.  
    # Note that LCSuff[i][j] contains the length of longest common suffix of  
    # X[0...i-1] and Y[0...j-1]. The first row and first column entries have no 
    # logical meaning, they are used only for simplicity of the program. 
    # LCSuff is the table with zero value initially in each cell 
    lcsuff = [[0 for k in range(n+1)] for l in range(m+1)]
    # To store the length of longest common substring 
    result = 0
    # Following steps to build LCSuff[m+1][n+1] in bottom up fashion 
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:
                lcsuff[i][j] = 0
            elif is_tag_match(x[i-1], y[j-1]):
                lcsuff[i][j] = lcsuff[i-1][j-1] + 1
                result = max(result, lcsuff[i][j])
            else:
                lcsuff[i][j] = 0
    return result

# def find_lcs(a:list, i:int, b:list, j:int):
#     if i == len(a) or j == len(b):
#         return 0
#     # if a[i]['POS'] + a[i]['NE'] + a[i]['SR'] == b[j]['POS'] + b[j]['NE'] + b[j]['SR']:
#     # if a[i] == b[j]:
#     if is_tag_match(a[i], b[j]):
#         return 1 + find_lcs(a, i + 1, b, j + 1)
#     else:
#         return max(find_lcs(a, i + 1, b, j), find_lcs(a, i, b, j + 1))

def is_tag_match(tag1, tag2):
    if tag1 == tag2:
        return True
    # NN == NNS
    elif 'NN' in tag1 and 'NN' in tag2 and 'ARGM' not in tag1 and 'ARGM' not in tag2:
        is_same_arg = False
        if 'ARG0' in tag1 and 'ARG0' in tag2:
            is_same_arg = True
        elif 'ARG1' in tag1 and 'ARG1' in tag2:
            is_same_arg = True
        elif 'ARG2' in tag1 and 'ARG2' in tag2:
            is_same_arg = True
        elif 'ARG3' in tag1 and 'ARG3' in tag2:
            is_same_arg = True
        elif 'ARG4' in tag1 and 'ARG4' in tag2:
            is_same_arg = True
        elif 'ARG5' in tag1 and 'ARG5' in tag2:
            is_same_arg = True
        noun_list = ['NN', 'NNP', 'NNS', 'NNPS']
        if is_same_arg and tag1.split(':')[0] in noun_list and tag2.split(':')[0] in noun_list:
            return True
        else:
            return False
    # VBP == VBZ, VBZ::V != VBZ::
    elif 'VB' in tag1 and 'VB' in tag2:
        verb_list = ['VBP', 'VBZ']
        if tag1.split(':')[2] == tag2.split(':')[2]:
            if tag1.split(':')[0] in verb_list and tag2.split(':')[0] in verb_list:
                return True
            else:
                return False
        else:
            return False
    # IN == TO
    elif tag1.split(':')[2] in ['IN', 'TO'] and tag2.split(':')[2] in ['IN', 'TO']:
        return True
    # NNP(S):LOC:ARG1 == NNP(S):LOC:ARGM-DIR
    elif 'LOC:ARG' in tag1 and 'LOC:ARG' in tag2 and 'ARGM' not in tag1 and 'ARGM' not in tag2:
        return True
    # # PER:ARG0
    # elif 'PER:ARG0' in tag1 and 'PER:ARG0' in tag2:
    #     return True
    # # PER:ARG1
    # elif 'PER:ARG1' in tag1 and 'PER:ARG1' in tag2:
    #     return True
    # # PER:ARG2
    # elif 'PER:ARG2' in tag1 and 'PER:ARG2' in tag2:
    #     return True
    # ARG0, ARG1, ARG2
    elif 'PER:ARG' in tag1 and 'PER:ARG' in tag2 and edit_distance(tag1, tag2) == 1:
        return True
    else:
        return False

def get_question_seq_by_rule(decla_seq:list, rule:dict):
    # 已知：
    # Xd = [A, B, C, G]
    # Xi = [W, Y, A, C, G]
    # 
    # Yd = [A, B, C, D, E]
    # 未知：
    # Yi = [W, Y, A, C, D, E]

    # Xd和Yd有共同子序列
    # Xi和Yi有共同子序列
    # Xd和Xi有共同子序列
    # 根据Xd->Xi的转换规则 由Yd转换成Yi

    # 先把Xi 复制到Yi
    # Yi中去掉Yd没有但是在Xd和Xi都有的 G
    # 得到Yd有，Xi没有的 B D E
    # 找到Xd有，Xi没有的 B
    # BDE 中去掉 B， 加入到Yi中
    # Xd有，Xi没有的元素一般是待生成问题的答案

    # 先把Xi 复制到Yi
    new_seq = rule['v'].copy()
    # Xd和Xi都有的元素集合去掉Yd有的
    in_k_v_but_not_in_decla_seq = set(rule['k']).intersection(set(rule['v'])) - set(decla_seq)
    # Yi中去掉Yd没有但是在Xd和Xi都有的
    new_seq = [s for s in new_seq if s not in in_k_v_but_not_in_decla_seq]
    # Yd 去掉 Xi
    in_decla_but_not_in_rule_v = set(decla_seq) - set(rule['v'])
    # Xd 去掉 Xi
    in_rule_k_but_not_in_rule_v = set(rule['k']) - set(rule['v'])
    # append_list 是将要加入到Yi的
    append_list = list(in_decla_but_not_in_rule_v - in_rule_k_but_not_in_rule_v)
    # 待生成问题的答案
    in_rule_k_but_not_in_rule_v = list(in_rule_k_but_not_in_rule_v)
    # if 1 < len(in_rule_k_but_not_in_rule_v):
    #     print('########## answer tag more than 1 ##########')
    #     print(decla_seq)
    #     print(rule['k'])
    #     print(rule['v'])
    #     print('########## answer tag more than 1 ##########')
    #     print('')
    if 0 == len(in_rule_k_but_not_in_rule_v):
        print('########## answer tag is 0 ##########')
        print(decla_seq)
        print(rule['k'])
        print(rule['v'])
        print('########## answer tag is 0 ##########')
        print('')

    # Re-sort append_list
    order = [decla_seq.index(tag) for tag in append_list]
    tmp_append_list = sorted(zip(order, append_list))
    append_list = [tag[1] for tag in tmp_append_list]
    if config.debug:
        print('new_seq:')
        print(new_seq)
        print('append_list:')
        print(append_list)
        print('')
    wh_tag = rule['v'][0].split(':')[0]
    for tag in append_list:

        if ',::' == tag:
            continue
        tagl = tag.split(':')
        # Remove tag if the tag match answer tag
        is_break = False
        for tag1 in in_rule_k_but_not_in_rule_v:
            if is_tag_match(tag, tag1):
                is_break = True
        if is_break: continue
        # Append_list and new_seq may have duplicated tag, e.g. NNS::ARG1 and NN::ARG1
        is_break = False
        for tag2 in new_seq:
            if is_tag_match(tag, tag2):
                index = new_seq.index(tag2)
                new_seq.pop(index)
                new_seq.insert(index, tag)
                is_break = True
        if is_break: continue

        if config.debug:
            print('Processing current append tag: ')
            print(tag)

        if 'V' in tagl[2]:
            sr_neg_newseq = [t.split(':')[2][:8] for t in new_seq]
            # If NEG in new_seq, insert the verb tag to the next element of NEG of new_seq
            # if the next element of NEG is V, insert the verb tag to the next element of V
            if 'ARGM-NEG' in sr_neg_newseq:
                neg_index = sr_neg_newseq.index('ARGM-NEG')
                if len(new_seq) > neg_index + 1 and new_seq[neg_index + 1].split(':')[2] == 'V':
                    index = new_seq.index(new_seq[neg_index + 1])
                else:
                    index = new_seq.index(new_seq[neg_index])
                new_seq.insert(index + 1, tag)
            else:
                # If the V tag of append_list in new_seq, replace the V in new_seq with the V in append_list. otherwise append the V to new_seq
                sr_rule_v = [t.split(':')[2] for t in new_seq]
                if tagl[2] in sr_rule_v:
                    index = sr_rule_v.index(tagl[2])
                    new_seq.pop(index)
                    new_seq.insert(index, tag)
                else:
                    new_seq.append(tag)
            continue
        # Add a verb into new_seq, if no verb in there
        if 'VB' == tagl[0][:2]:
            new_seq_pos_vb = [t[:2] for t in new_seq]
            new_seq_sr_v = [t.split(':')[2] for t in new_seq]
            if 'VB' not in new_seq_pos_vb or 'V' not in new_seq_sr_v:
                for seq in new_seq:
                    if 'ARG0' == seq.split(':')[2] or 'ARG1' == seq.split(':')[2]:
                        index = new_seq.index(seq) + 1
                        new_seq.insert(index, tag)
                        break

        # VBP and VBZ can not in question seq togehter
        if tagl[0] in ['VBZ', 'VBP']:
            for seq in new_seq:
                if seq[:3] in ['VBZ', 'VBP']:
                    index = new_seq.index(seq)
                    new_seq.pop(index)
                    new_seq.insert(index, tag)
                    # print(new_seq)
                    break
            continue
        # Append ARG to new_seq if ARG not in new_seq and not in Answer_tags
        if 'ARG' == tagl[2][:3] and 'ARGM' != tagl[2][:4]:
            arg_new_seq = [s.split(':')[2] for s in new_seq if s.split(':')[0][:1] != 'W']
            arg_answer_seq = [s.split(':')[2] for s in in_rule_k_but_not_in_rule_v]
            # print(arg_new_seq)
            # print(arg_answer_seq)
            if tagl[2] not in arg_new_seq and tagl[2] not in arg_answer_seq:
                new_seq.append(tag)
            continue

        # Append NNP:LOC:ARG to new_seq if it in rule_v
        if 'LOC' == tagl[1] and 'WRB' == wh_tag:
            is_append = False
            for rule_v_tag in rule['v']:
                if 'LOC' in rule_v_tag:
                    is_append = True
                    continue
            if is_append:
                decla_seq_ner = [t.split(':')[1] for t in decla_seq]
                index = decla_seq_ner.index('LOC')
                new_seq.insert(index, tag)
            else:
                # Update LOC tag in in_rule_k_but_not_in_rule_v
                # NNP:LOC:ARG is not in rule_v, the LOC tag is answer_tag, replace the LOC tag
                tmp_i = 0
                for tmp_i in range(len(in_rule_k_but_not_in_rule_v)):
                    if 'LOC:ARG' in in_rule_k_but_not_in_rule_v[tmp_i]:
                        in_rule_k_but_not_in_rule_v[tmp_i] = tag
            continue
        # If NEG
        if tagl[2][:8] == 'ARGM-NEG':
            # If one or more verb, put NEG behind the first verb
            # index() returns the first one
            vb_new_seq = [t[:2] for t in new_seq]
            if 'MD' in vb_new_seq:
                index = vb_new_seq.index('MD')
            elif 'VB' in vb_new_seq:
                index = vb_new_seq.index('VB')
            else:
                # there is no VB in the new_seq, append VB and set index to the last one
                new_seq.append('VB::')
                index = len(new_seq) - 1
            # If more than one verb, and ARG is behind verb, put NEG behind the ARG
            # Apply to Where Why How questions
            if 'WRB' == wh_tag:
                srl_new_seq = [t.split(':')[2][:3] for t in new_seq]
                if len(srl_new_seq) > index + 1 and 'ARG' == srl_new_seq[index + 1]:
                    index = index + 1
            new_seq.insert(index + 1, tag)
            continue
        # If the tag is the second element in decla_seq, 
        # it must be a verb and insert the it to the second element of the new_seq.
        previous_in_decla = decla_seq[decla_seq.index(tag) - 1]
        if previous_in_decla not in new_seq and previous_in_decla == decla_seq[0]:
            new_seq.insert(1, tag)
            continue
        new_seq.append(tag)

    # Ajdust order of new_seq according to rule['v']
    new_seq = adjust_order(new_seq, rule['v'])

    # Ajdust order, move ARGM-TMP to the end
    arg_append_list = [t[-8:] for t in append_list]
    for seq in new_seq.copy():
        if 'ARGM-TMP' in seq and 'ARGM-TMP' in arg_append_list and 'WRB' not in seq:
            tmp_seq = seq
            new_seq.remove(tmp_seq)
            new_seq.append(tmp_seq)

    return new_seq, in_rule_k_but_not_in_rule_v

def generate_question_by_seq(ques_word:str, decla_tags:list, interro_seq:list, answer_tags:list, wordnet):
    question = []
    verb_list = []
    decla_seq = [tag['POS'] + ':' + tag['NE'] + ':' + tag['SR'] for tag in decla_tags]
    decla_sr_tag = [tag['SR'] for tag in decla_tags]
    decla_pos_tag = [tag['POS'] for tag in decla_tags]
    # print(decla_seq)

    for tag in interro_seq:
        # print(tag)
        tagl = tag.split(':')
        if tag in decla_seq:
            index = decla_seq.index(tag)
            question.append(decla_tags[index]['W'])
            if tagl[0][:2] == 'VB':
                verb_list.append((decla_tags[index]['W'], tag))
        else:
            if tagl[0] in ['WDT', 'WP', 'WP$', 'WRB', 'WHM']: # WHM: How many/much
                question.insert(0, ques_word)
                continue
            if tagl[0] in decla_pos_tag:
                index = decla_pos_tag.index(tagl[0])
                question.append(decla_tags[index]['W'])
                if tagl[0][:2] == 'VB':
                    verb_list.append((decla_tags[index]['W'], tag))
                continue
            else:
                print('####################')
                print('处理不存在的tag')
                print(tag)
                print([tag['W'] for tag in decla_tags])
                print(decla_seq)
                print(interro_seq)
                print('####################')
                print('')
                # IN::NEW, VB::NEW, NN::ARG2NEW
                # If current is VB, and next tag is V, then current tag is be
                if tagl[0][:2] == 'VB':
                    next_index = interro_seq.index(tag) + 1
                    if len(interro_seq) > next_index and 'V' in interro_seq[next_index].split(':')[2]:
                        question.append('be')
                        verb_list.append(('be', tag))
                    else:
                        # singular or plural, will be changed in reverse verb
                        if answer_tags[0].split(':')[0] in ['NN', 'NNP']:
                            question.append('does')
                            verb_list.append(('does', tag))
                            # verb_list.append(('does', 'singular'))
                        else:
                            question.append('do')
                            verb_list.append(('do', tag))
                            # verb_list.append(('do', 'plural'))
                elif tagl[0] == 'IN':
                    # Get prep in ARG
                    arg_word = ''
                    arg_tag = ''
                    # Check which ARG(ARG0 or ARG1) tag contained in answer tag
                    for answer_tag in answer_tags:
                        if 'ARG' in answer_tag:
                            arg_tag = answer_tag.split(':')[2]
                            break
                    # Get the word corresponding to the answer tag
                    for decla_tag in decla_tags:
                        if decla_tag['SR'] == arg_tag:
                            arg_word = decla_tag['W']
                            break
                    if ' ' in arg_word:
                        tmp_words = arg_word.split()
                        if tmp_words[1] in ['in', 'to', 'on', 'by', 'for', 'out', 'below']:
                            question.append(tmp_words[1])
                        elif tmp_words[0] in ['in', 'to', 'on', 'by', 'for', 'out', 'below']:
                            question.append(tmp_words[0])
                        else:
                            # In most case, prep is first word
                            # check the first word is prep
                            for t in decla_tags:
                                if tmp_words[0] == t['W']:
                                    if 'IN' == t['POS']:
                                        question.append(tmp_words[0])
                                        break
                    # if ARG is a phrase, then ignore the IN, no need append tag
                    # else:
                    #     # TODO
                    #     question.append(tag)
                elif 'ARG' in tagl[2] and 'ARGM' not in tagl[2]:
                    if tagl[2] in decla_sr_tag:
                        index = decla_sr_tag.index(tagl[2])
                        question.append(decla_tags[index]['W'])
                    else:
                        # TODO
                        question.append(tag)
                else:
                    if config.debug:
                        print('### Tag can not be found. ###')
                        print(tag)
                    # TODO
                    # question.append(tag)

    # Check verb tense
    # # Apply to Where question
    # if 'WRB' == interro_seq[0].split(':')[0]:
    # 1. verb_list 不少于一个, 2. 句子不是 be about to 和 be able to 结构, 3. verb_list 中没有进行时(VBG), 4. verb_list中第一个verb是['is', 'are', 'do', 'does'], 5. 不是will/can do(MD)结构, 6. 不是has have been(VBN)结构, 7. 不是否定句(NEG)
    # 满足1.2.3.4.条件时, 尝试修正verb的时态
    # 满足1.2.3.5.6.7.条件时 并且verb_list中第一个verb是['VBD', 'VBZ']，才需要颠倒两个verb的顺序
    is_verb_flag = True
    is_replace_verb = False
    is_replace_first_verb = False
    is_reverse_verb = False
    new_verb_list = []

    if len(verb_list) > 1:
        tmp_ques = ' '.join(question)
        verb_pos_list = [v[1].split(':')[0] for v in verb_list]
        # 如果是进行时就不进行verb操作
        if 'VBG' in verb_pos_list or \
            'about to' in tmp_ques or 'able to' in tmp_ques:
            is_verb_flag = False
        # 如果第一个verb属于is are do does中的任意一个，则执行替换操作
        if is_verb_flag and verb_list[0][0] in ['is', 'are', 'do', 'does']:
            is_replace_verb = True
        # 如果两个verb相等，则执行替换第一个verb操作
        if is_verb_flag and verb_list[0][0] == verb_list[1][0]:
            is_replace_first_verb = True
        # 没有过去分词并且没有情态动词，并且第一个verb属于vbd，vbz，且不是否定句，则互换2个verb位置
        # 只有出现匹配不到的SSU，且第一个动词的POS是VBD或者VBZ，才需要交换位置。
        if is_verb_flag and 'VBN' not in verb_pos_list and \
            'MD' not in verb_pos_list and verb_list[0][1][:3] in ['VBD', 'VBZ'] and \
                'not' not in question:
            is_reverse_verb = True
    
    if config.debug:
        print('####################')
        print('处理动词')
        print('verb_list: ')
        print(verb_list)
        print('is_replace_verb: ')
        print(is_replace_verb)
        print('is_replace_first_verb: ')
        print(is_replace_first_verb)
        print('is_reverse_verb: ')
        print(is_reverse_verb)
        print('Before: ')
        print(' '.join(question))
        print('')
    
    if is_replace_verb:
        for i, v in enumerate(verb_list):
            if 'VBD' == v[1][:3]:
                new_verb_list.append(('did', v[1]))
            elif 'VBP' == v[1][:3]:
                new_verb_list.append(('do', v[1]))
            elif 'VBZ' == v[1][:3]:
                new_verb_list.append(('does', v[1]))
            else:
                new_verb_list.append((v[0], v[1]))
        for i, q in enumerate(question):
            for j, v in enumerate(verb_list):
                if q == v[0]:
                    question[i] = new_verb_list[j][0]
                    break

    if is_replace_first_verb:
        tmp_v = ''
        if 'VBD' == verb_list[0][1][:3]:
            tmp_v = 'did'
        elif 'VBP' == verb_list[0][1][:3]:
            tmp_v = 'do'
        elif 'VBZ' == verb_list[0][1][:3]:
            tmp_v = 'does'
        else:
            tmp_v = verb_list[0][0]

        for i, q in enumerate(question):
            if q == verb_list[0][0]:
                question[i] = tmp_v
                break

    # print('new_verb_list:')
    # print(new_verb_list)

    # Reverse the order of 2 verbs.
    if is_reverse_verb:
        verb1 = wordnet.get_base_verb(verb_list[0][0])
        if 'VBD' == verb_list[0][1][:3]:
            verb0 = 'did'
        elif 'VBG' == verb_list[0][1][:3]:
            verb0 = 'UNKNOWN'
        elif 'VBN' == verb_list[0][1][:3]:
            verb0 = 'UNKNOWN'
        elif 'VBP' == verb_list[0][1][:3]:
            verb0 = 'do'
        elif 'VBZ' == verb_list[0][1][:3]:
            verb0 = 'does'
        elif 'VB:' == verb_list[0][1][:3]:
            verb0 = 'UNKNOWN'
        else:
            verb0 = 'UNKNOWN'
        for i, q in enumerate(question):
            if q == verb_list[0][0]:
                question[i] = verb0
            if q == verb_list[1][0]:
                question[i] = verb1

    if config.debug:
        print('After: ')
        print(' '.join(question))
        print('####################')
        print('')

    return ' '.join(question) + '?'



