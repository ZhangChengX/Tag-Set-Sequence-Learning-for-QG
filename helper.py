# coding: utf-8

import re
import inflect
from nltk.data import load
from nltk.tokenize import sent_tokenize
from nltk.stem.wordnet import WordNetLemmatizer

# sentence_delimiters_en = ['?', '!', '...', '\n']
stop_list = ['a', 'by', 'in', 'to', 'the']
be_verb = ['am', 'is', 'are', 'was', 'were']
infle = inflect.engine()

def remove_stop_word(word_list):
    return [w for w in word_list if w.lower() not in stop_list]

def strip_multi_space(text):
    return re.sub(' +', ' ', text)

def segment_by_sentence(text):
    tokenizer = load('tokenizers/punkt/{0}.pickle'.format('english'))
    sentences = []
    paragraphs = [p for p in text.split('\n') if p]
    for paragraph in paragraphs:
        sentences.extend(tokenizer.tokenize(paragraph))
    return sentences

def get_named_entity_by_word(word, tags):
    for tag in tags:
        if word == tag[1]:
            return tag[0]

def get_phrase_by_consecutive_tags(tag_key, tags):
    # Given tag_key = 'PER' and tags = [('B-PER', 'Barack'), ('L-PER', 'Obama'), ('O', 'is'), ('O', 'the'), ('O', 'president'), ('O', 'of'), ('O', 'The'), ('B-LOC', 'United'), ('I-LOC', 'States'), ('I-LOC', 'of'), ('L-LOC', 'America'), ('O', '.')]
    # Find Barack Obama
    phrase = ''
    is_break = False
    consecutive = 0
    for tag in tags:
        if is_break:
            break
        if tag_key == tag[0][2:]:
            phrase = phrase + tag[1] + ' '
            consecutive = consecutive + 1
        else:
            if consecutive > 0 and is_break is False:
                is_break = True
    return phrase.rstrip()

def get_base_verb(verb):
    # stemming verb
    # TODO single instance
    return WordNetLemmatizer().lemmatize(verb,'v')

def get_negative_verb(verb, neg):
    # has been -> has not been
    if ' ' in verb:
        vlist = verb.split(' ')
        vlist.insert(1, neg)
        verb = ' '.join(vlist)
    else:
        verb = verb + ' ' + neg
    return verb

def get_verb_tense(verb, pos_tags):
    # VBD past, VBN Past participle
    auxilverb_tense = ''
    for tag in pos_tags:
        # negative sentence, e.g. ('did', 'VBD'), ("n't", 'RB'), ('tell', 'VB')
        if tag[0] in ['do', 'does', 'did', 'have', 'has', 'had']:
            auxilverb_tense = tag[1]
        if tag[0] == verb:
            if auxilverb_tense != '' and tag[1] == 'VB':
                return auxilverb_tense
            else:
                return tag[1] 

def get_auxil_verb(verb, subject, pos_tags):
    tense = get_verb_tense(verb, pos_tags)
    if tense in ['VBD', 'VBN']:
        auxilverb = 'did'
    else:
        if infle.singular_noun(subject) is False:
            auxilverb = 'does'
        else:
            auxilverb = 'do'
    return auxilverb

def lower_case_first_letter(labels):
    if labels[list(labels)[0]] != 'I':
        labels[list(labels)[0]] = labels[list(labels)[0]].lower()
    return labels

# def merge_srl_labels(labels):
#     i = 0
#     auxilverb = ''
#     for i in range(len(labels)):
#         if 1 == len(labels[i]) and 'V' in labels[i]:
#             auxilverb = auxilverb + ' ' + labels[i]['V']
#             auxilverb = auxilverb.lstrip()
#         if len(labels[i]) > 1 and '' != auxilverb:
#             labels[i]['V'] = auxilverb + ' ' + labels[i]['V']
#             if any(string in labels[i]['V'] for string in ['is going ', 'are going ', 'am going ']):
#                 labels[i]['V'] = labels[i]['V'].replace('going', 'going to')
#     return labels

def combine_verb(verb, pos_tags):
    for i in range(len(pos_tags)):
        t1 = pos_tags[i]
        t2 = pos_tags[i-1] if i-1 >= 0 else ['', '']
        t3 = pos_tags[i-2] if i-2 >= 0 else ['', '']
        t4 = pos_tags[i-3] if i-3 >= 0 else ['', '']
        t5 = pos_tags[i-4] if i-4 >= 0 else ['', '']
        # Future, example: be going to do
        if t1[0] == verb and t2[1] == 'TO' and t3[1][0:2] == 'VB' and t4[1][0:2] == 'VB':
            return t4[0], ' '.join([t4[0], t3[0], t2[0], t1[0]])
        if t1[0] == verb and t2[1] == 'TO' and t3[1][0:2] == 'VB' and t4[0] == 'not' and t5[1][0:2] == 'VB':
            return t5[0], ' '.join([t5[0], t4[0], t3[0], t2[0], t1[0]])
        # Future, example: will do, can do
        if t1[0] == verb and t2[1] == 'MD':
            return t2[0], ' '.join([t2[0], t1[0]])
        if t1[0] == verb and t2[0] == 'not' and t3[1] == 'MD':
            return t3[0], ' '.join([t3[0], t2[0], t1[0]])
        # Passive, example: has been done
        if t1[0] == verb and t2[1][0:2] == 'VB' and t3[1][0:2] == 'VB':
            return t3[0], ' '.join([t3[0], t2[0], t1[0]])
        if t1[0] == verb and t2[1][0:2] == 'VB' and t3[0] == 'not' and t4[1][0:2] == 'VB':
            return t4[0], ' '.join([t4[0], t3[0], t2[0], t1[0]])
        # Progressive, example: be doing, does/don't have, have done, was done
        if t1[0] == verb and t2[1][0:2] == 'VB':
            return t2[0], ' '.join([t2[0], t1[0]])
        if t1[0] == verb and t2[0] == 'not' and t3[1][0:2] == 'VB':
            return t3[0], ' '.join([t3[0], t2[0], t1[0]])
        # Negative, never do
        if t1[0] == verb and t2[0] == 'never':
            return t2[0], ' '.join([t2[0], t1[0]])
        # Negative, example: be not
        if t1[0] == verb:
            if len(pos_tags) > i and pos_tags[i+1][0] == 'not': 
                return '', ' '.join([t1[0], pos_tags[i+1][0]])
    return '', verb

def preprocess_labels(labels, pos_tags):
    verb = ''
    labels_list = []
    for label in labels:
        label_dict = {}
        # Ignore if less than 3 elements in labels
        if len(label) < 3:
            if 1 == len(label) and 'V' in label:
                verb = label['V']
            continue
        # Merge tags into labels
        i = 0
        is_in_label = False
        for tag in pos_tags:
            if tag[0] == '.':
                continue
            # Check if any label contains tag
            current_value = ''
            for value in label.values():
                if tag[0] in value:
                    current_value = value
                    is_in_label = True
            if is_in_label:
                # Get key by value in dict
                key = list(label.keys())[list(label.values()).index(current_value)]
                label_dict[key] = label[key]
            else:
                if tag[0] == verb or tag[1][0:2] == 'VB':
                    label_dict['V' + str(i)] = tag[0]
                else:
                    label_dict[i] = tag[0]
            is_in_label = False
            i = i + 1
        labels_list.append(label_dict)
    return labels_list


