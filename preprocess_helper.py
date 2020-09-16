# coding: utf-8


interrogative_word = ['who', 'whose', 'what', 'where', 'when', 'which', 'why', 'how', 'am', 'is', 'are', 'be', 'do', 'did', 'does', 'have', 'has']


def preprocess_sr_tags(sr_tags_list:list, sentence:str):

    def reformat(sr_tags_list):
        rst = []
        for sr_dict in sr_tags_list:
            # Re-format
            sr_tags = []
            for k, v in sr_dict.items():
                sr_tags.append((k, v))
            rst.append(sr_tags)
        return rst

    if len(sr_tags_list) == 1:
        return reformat(sr_tags_list)
    verbs = []
    new_sr_tags_list = []
    for sr_tags in sr_tags_list:
        # ignore if len(sr_tags) is 0 or 2
        if len(sr_tags) == 1 and 'V' in sr_tags:
            verbs.append(sr_tags['V'])
        if len(sr_tags) > 2:
            # # sr_tags must contain 2 ARGs, e.g. ARG0 and ARG1, not include ARGM.
            # # arg_tag >= 2 means sr_tags contains at least 3 tags, 2 for ARGs, 1 for V
            # def is_complete_clause(sr_tags):
            #     arg_tag = 0
            #     if len(sr_tags) >= 3:
            #         for k in sr_tags.keys():
            #             if k[:4] != 'ARGM' and k[:3] == 'ARG':
            #                 arg_tag = arg_tag + 1
            #     return True if len(arg_tag) >=2 else False
            verb_phrase = ''
            clause = ' '.join([t for t in sr_tags.values()])
            # len(verbs) may be 0
            for verb in verbs:
                # only merge the verb if it not appears in current clause
                left_index = clause.find(sr_tags['V']) - len(verb) - 5
                right_index = left_index + len(sr_tags['V']) + len(verb) + 5
                if left_index < 0: left_index = 0
                seg_s = clause[left_index:right_index]
                if verb in seg_s:
                    continue
                verb_phrase = verb_phrase + ' ' + verb
            if verb_phrase != '':
                sr_tags['V'] = verb_phrase.strip() + ' ' + sr_tags['V']
            # only process previous V tags, empty the list after the current done.
            verbs = []
            # check if there is any preposition word missing in the V
            # check if any missing prep inside of the V 
            if ' ' in sr_tags['V'] and sr_tags['V'] not in sentence:
                v_list = sr_tags['V'].split(' ')
                left_index = sentence.find(v_list[0], 0)
                right_index = sentence.find(v_list[-1], left_index)
                new_verb_phrase = sentence[left_index:right_index+len(v_list[-1])]
                sr_tags['V'] = new_verb_phrase
            # check if any missing prep surround the V
            # check left
            # seg_sentences = sentence.split(sr_tags['V'])
            # left_words = seg_sentences.split(' ')
            # TODO 
            # Bob agreed to take out the trash which was thrown by Tom.
            # V: agreed to take, missing: out
            new_sr_tags_list.append(sr_tags)
    return reformat(new_sr_tags_list)


# def preprocess_sr_tags2(sr_tags_list:list, sentence:str):

#     verb_phrase = ''

#     if len(sr_tags_list) == 2:
#         for sr_dict in sr_tags_list.copy():
#             if 1 == len(sr_dict) and 'V' in sr_dict:
#                 sr_tags_list.remove(sr_dict)
#                 verb_phrase = sr_dict['V']
#             elif 0 == len(sr_dict):
#                 sr_tags_list.remove(sr_dict)
    
#     if len(sr_tags_list) > 2:
#         # Check if there is any short tag list contain V need to be merged in
#         # to_be_merged_list = []
#         for sr_dict in sr_tags_list.copy():
#             arg3_list = [k[:3] for k in sr_dict.keys()]
#             arg4_list = [k[:4] for k in sr_dict.keys()]
#             if 1 == len(sr_dict) and 'V' in sr_dict:
#                 # to_be_merged_list.append(sr_dict)
#                 sr_tags_list.remove(sr_dict)
#                 verb_phrase = verb_phrase + ' ' + sr_dict['V']
#             elif 2 == len(sr_dict) and 'ARG' in arg3_list and 'ARGM' not in arg4_list:
#                 sr_tags_list.remove(sr_dict)
#                 continue
#             elif 2 == len(sr_dict):
#                 # to_be_merged_list.append(sr_dict)
#                 sr_tags_list.remove(sr_dict)
#                 verb_phrase = verb_phrase + ' ' + list(sr_dict.values())[0] + ' ' + list(sr_dict.values())[1]
#             elif 0 == len(sr_dict):
#                 sr_tags_list.remove(sr_dict)
#         verb_phrase = verb_phrase.strip()
#         # print(verb_phrase)

#     if verb_phrase:
#         # If more than one long tag list, check which tag list need to be merged with V
#         for sr_dict in sr_tags_list:
#             if 'V' not in sr_dict:
#                 continue

#             if verb_phrase in list(sr_dict.values()):
#                 continue

#             # rewrite V tag
#             if 'going' == verb_phrase[-5:]:
#                 # be going to
#                 verb_phrase = verb_phrase + ' ' + 'to'

#             if len(sr_dict) == 2: # {'V': 'shingled', 'ARG1': 'hair'} 
#                 sr_dict['V1'] = sr_dict['V']
#                 sr_dict['V'] = verb_phrase
#             else:
#                 tmp_phrase1 = verb_phrase + ' ' + sr_dict['V']
#                 tmp_phrase2 = sr_dict['V'] + ' ' + verb_phrase

#                 if tmp_phrase1 in sentence:
#                     sr_dict['V'] = tmp_phrase1.strip()
#                 elif tmp_phrase2 in sentence:
#                     sr_dict['V'] = tmp_phrase2.strip()

#     rst = []
#     for sr_dict in sr_tags_list:
#         # Re-format
#         sr_tags = []
#         for k, v in sr_dict.items():
#             sr_tags.append((k, v))
#         rst.append(sr_tags)

#     return rst


def merge_tags(pos_tags:list, ne_tags:list, sr_tags:list):
    pos_w_list = [t[0] for t in pos_tags]
    pos_t_list = [t[1] for t in pos_tags]
    sr_w_list = [t[1] for t in sr_tags]
    sr_t_list = [t[0] for t in sr_tags]

    # 将不及物动词后面的介词IN或TO分离
    sr_t = None
    sr_t_index = None
    if 'V' in sr_t_list:
        # print('has V')
        sr_t_index = sr_t_list.index('V') + 1
        if len(sr_t_list) > sr_t_index:
            # print('has target_sr_tag')
            target_sr_tag = sr_tags[sr_t_index]
            if ' ' in target_sr_tag[1]:
                # print('is phrase')
                # print(target_sr_tag)
                target_w = target_sr_tag[1].split(' ')[0]
                target_w_pos = None
                for p in pos_tags:
                    if p[0] == target_w:
                        target_w_pos = p
                # print(target_w_pos)
                if target_w_pos and target_w_pos[1] in ['TO', 'IN', 'RP']:
                    sr_t = (target_w_pos[1], target_w_pos[0])
    if sr_t:
        sr_tags[sr_t_index] = (sr_tags[sr_t_index][0], sr_tags[sr_t_index][1].replace(sr_t[1] + ' ', ''))
        if sr_t[1] not in ['that', 'who', 'whom', 'where', 'which', 'what']:
            sr_tags.insert(sr_t_index, sr_t)
    
    # # 将第一个不在ARGM中的CD分离
    # pos_t = None
    # pos_t_index = None
    # if 'CD' in pos_t_list:
    #     pos_t_index = pos_t_list.index('CD')
    #     for sr_tag in sr_tags:
    #         if pos_tags[pos_t_index][0] in sr_tag[1] and 'ARGM' not in sr_tag[0]:
    #             pos_t = (pos_tags[pos_t_index][1], pos_tags[pos_t_index][0])
    #             pos_t_index = sr_tags.index(sr_tag)
    # if pos_t:
    #     sr_tags[pos_t_index] = (sr_tags[pos_t_index][0], sr_tags[pos_t_index][1].replace(pos_t[1] + ' ', ''))
    #     sr_tags.insert(pos_t_index, pos_t)

    # # 统计VB和NN
    # word_amount_pos_tags = len(pos_tags)
    # word_amount_sr_tags = len(' '.join([t[1] for t in sr_tags]).split(' '))
    # vb_amount = 0
    # nn_amount = 0
    # for t in pos_tags:
    #     if 'VB' == t[1][:2]:
    #         vb_amount = vb_amount + 1
    #     if 'NN' == t[1][:2]:
    #         nn_amount = nn_amount + 1
    # if vb_amount >= 3 and nn_amount >= 3 and (word_amount_pos_tags - word_amount_sr_tags) >= 3:
    #     print('# merge_tags_SR_based() ')
    #     return merge_tags_sr_based(pos_tags, ne_tags, sr_tags)
    # else:
    #     print('# merge_tags_POS_based() ')
    #     return merge_tags_pos_based(pos_tags, ne_tags, sr_tags)

    # if interrogative sentence
    if pos_tags[0][0].lower() in interrogative_word:
        # 将第一个 How many/How much 分离
        sentence = ' '.join(pos_w_list)
        if sentence[:8].lower() == 'how many' or sentence[:8].lower() == 'how much':
            question_word = pos_w_list[0] + ' ' + pos_w_list[1]
            sr_tags[0] = (sr_tags[0][0], sr_tags[0][1].replace(question_word + ' ', ''))
            sr_tags.insert(0, ('WHM', question_word))
            pos_tags[1] = (pos_tags[1][0], 'WHM')
            print('# merge_tags_POS_based() ')
        return merge_tags_pos_based(pos_tags, ne_tags, sr_tags)

    # Check if pos longer than sr, and pos include VBG and TO (be going to), go pos_based
    # print(len(' '.join(pos_w_list)))
    # print(len(' '.join(sr_w_list)))
    # print(len(pos_w_list))
    # print(len(sr_w_list))
    if (len(' '.join(pos_w_list)) - len(' '.join(sr_w_list))) > 2 and \
        len(pos_w_list) / 3 < len(sr_w_list):
        has_VBG = False
        has_TO = False
        tmp_w_list = list(set(pos_w_list) - set(sr_w_list))
        for tmp_w in tmp_w_list:
            if tmp_w in pos_w_list:
                index = pos_w_list.index(tmp_w)
                tag = pos_t_list[index]
                if tag == 'VBG' and 'ing' in tmp_w: 
                    has_VBG = True
                if tag == 'TO': has_TO = True
        if has_TO and has_VBG:
            print('# merge_tags_POS_based() ')
            return merge_tags_pos_based(pos_tags, ne_tags, sr_tags)
    print('# merge_tags_SR_based() ')
    return merge_tags_sr_based(pos_tags, ne_tags, sr_tags)
        
    
def merge_tags_sr_based(pos_tags:list, ne_tags:list, sr_tags:list):
    # How many sr tags, how many merged tags
    tags_list = []
    word_list = [tag[0] for tag in pos_tags]
    for sr_tag in sr_tags: 
        sr_tag_word_list = sr_tag[1].split(' ')
        tmp = {}
        phrase_ne_tag_list = []
        for w in sr_tag_word_list:
            if w in word_list:
                index = word_list.index(w)
                pos_tag = pos_tags[index][1]
                sr_t = sr_tag[0]
                ne_tag = ne_tags[index][0]
                ne_tag = '' if 'O' == ne_tag else ne_tag
                ne_tag = 'PER' if 'PER' == ne_tag[-3:] else ne_tag
                ne_tag = 'LOC' if 'LOC' == ne_tag[-3:] else ne_tag
                ne_tag = 'ORG' if 'ORG' == ne_tag[-3:] else ne_tag
                phrase_ne_tag_list.append(ne_tag)
                # multi-words push into one SR tag, so only keep useful NE tag
                if 'LOC' in phrase_ne_tag_list:
                    ne_tag = 'LOC'
                if 'PER' in phrase_ne_tag_list:
                    ne_tag = 'PER'
                if 'ORG' in phrase_ne_tag_list:
                    ne_tag = 'ORG'
                tmp = {'POS': pos_tag, 'NE': ne_tag, 'SR': sr_t, 'W': sr_tag[1]}
        tags_list.append(tmp)
    # remove the first element if it is ArgM
    if 'ARGM-' == tags_list[0]['SR'][:5]:
        tags_list.pop(0)
    return tags_list

def merge_tags_pos_based(pos_tags:list, ne_tags:list, sr_tags:list):
    # How many pos tags, how many merged tags
    tags_list = []
    last_value = ''
    current_value = ''
    is_in_sr_tag = False
    is_eq_sr_tag = False
    phrase_ne_tag_list = []
    sr_tags_words = [t[1] for t in sr_tags]
    i = 0
    for i in range(len(pos_tags)):
        if pos_tags[i][1] == '.':
            continue
        # Check if any SR label contains tag, SR label could be a phrase.
        for sr_tag in sr_tags:
            if pos_tags[i][0] == sr_tag[1]:
                is_eq_sr_tag = True
                current_value = sr_tag[1]
            if i > 0 and pos_tags[i-1][0] + ' ' + pos_tags[i][0] in sr_tag[1]:
                is_in_sr_tag = True
                current_value = sr_tag[1]
            if len(pos_tags) > i+1 and pos_tags[i][0] + ' ' + pos_tags[i+1][0] in sr_tag[1]:
                is_in_sr_tag = True
                current_value = sr_tag[1]
        ne_tag = '' if 'O' == ne_tags[i][0] else ne_tags[i][0]
        ne_tag = 'PER' if 'PER' == ne_tag[-3:] else ne_tag
        ne_tag = 'LOC' if 'LOC' == ne_tag[-3:] else ne_tag
        ne_tag = 'ORG' if 'ORG' == ne_tag[-3:] else ne_tag
        # print(pos_tags[i][0])
        # print(is_in_sr_tag)
        # print(is_eq_sr_tag)
        # print('')
        if is_in_sr_tag:
            # print(pos_tags[i][0])
            # print(last_value)
            # print(current_value)
            # print('-----')
            # if current tag and previous tag are same SR tag, remove previous and add new one.
            if last_value == current_value:
                tags_list.pop()
                # save each ne_tag to list in a phrase
                phrase_ne_tag_list.append(ne_tag)
            # # Get key by value in dict
            # key = list(sr_tags.keys())[list(sr_tags.values()).index(current_value)]
            index = sr_tags_words.index(current_value)
            # if ne_tag contains more than 1 other tags.
            if len(phrase_ne_tag_list) > 1:
                # multi-words push into one SR tag, so only keep useful NE tag
                if 'LOC' in phrase_ne_tag_list:
                    ne_tag = 'LOC'
                if 'PER' in phrase_ne_tag_list:
                    ne_tag = 'PER'
                if 'ORG' in phrase_ne_tag_list:
                    ne_tag = 'ORG'
            # if phrase_ne_tag_list.count('') > 1:
            #     ne_tag = ''
            tmp = {'POS': pos_tags[i][1], 'NE': ne_tag, 'SR': sr_tags[index][0], 'W': current_value}
            # print(tmp)
            tags_list.append(tmp)
            last_value = current_value
        elif is_eq_sr_tag:
            # Empty the list if the word is not in a phase
            phrase_ne_tag_list = []
            # # Get key by value in dict
            # key = list(sr_tags.keys())[list(sr_tags.values()).index(current_value)]
            index = sr_tags_words.index(current_value)
            tmp = {'POS': pos_tags[i][1], 'NE': ne_tag, 'SR': sr_tags[index][0], 'W': current_value}
            # print(tmp)
            tags_list.append(tmp)
        else:
            # Empty the list if the word is not in a phase
            phrase_ne_tag_list = []

            if pos_tags[i][0] in sr_tags_words:
                index = sr_tags_words.index(pos_tags[i][0])
                sr_t = sr_tags[index][0]
            elif pos_tags[i][0] == 'not':
                sr_t = 'ARGM-NEG'
            else:
                sr_t = ''
            tmp = {'POS': pos_tags[i][1], 'NE': ne_tag, 'SR': sr_t, 'W': pos_tags[i][0]}
            # print(tmp)
            # print(pos_tags[i][0])
            tags_list.append(tmp)
        is_in_sr_tag = False
        is_eq_sr_tag = False
        i = i + 1

    return make_tags_unique(tags_list)

def make_tags_unique(tags):
    seen = []
    i = 0
    for i in range(len(tags)):
        joint_tag = tags[i]['POS'] + ':' + tags[i]['NE'] + ':' + tags[i]['SR']
        if joint_tag in seen:
            tags[i]['SR'] = tags[i]['SR'] + 'ID' + str(i)
        else:
            seen.append(joint_tag)
        i = i + 1
    return tags

def lowercase_first_word(tags_list):
    if len(tags_list) > 0 and tags_list[0]['NE'] == '':
        tags_list[0]['W'] = tags_list[0]['W'].lower()
    return tags_list


