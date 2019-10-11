# coding: utf-8

import re
import helper
import config


def who(labels, ne_tags, pos_tags):
    # Example: arg1 is arg2, arg2 is arg1, arg0 do argx
    question = 'Who'
    subject_key = ''
    subject = helper.get_phrase_by_consecutive_tags('PER', ne_tags)
    # make sure arg1 is PER
    if 'ARG1' in labels and labels['ARG1'] == subject:
        subject_key = 'ARG1'
    elif 'ARG0' in labels:
        subject_key = 'ARG0'
        subject = labels['ARG0']
    # Passive, ARG2 may include subject, not equal. e.g. by somebody
    elif 'ARG2' in labels and subject in labels['ARG2']:
        subject_key = 'ARG2'
    else:
        return

    # Eliminate stop word
    if ' ' in subject and subject.count(' ') < 3:
        subject = ' '.join(helper.remove_stop_word(subject.split(' ')))
    # If object in the middle or at the end of the sentence
    if subject_key != list(labels)[0]:
        labels = helper.lower_case_first_letter(labels)
    
    # Form question
    verb = helper.combine_verb(labels['V'], pos_tags)[1]
    # if config.debug:
    #     print('Verb: ' + str(verb))
    question = question + ' ' + verb
    for key, value in labels.items():
        if key in [subject_key, 'V', 'ARGM-NEG', 'ARGM-MOD']:
            continue
        if 'V' == str(key)[0]: # V1, V2, V3, ...
            continue
        if type(key) is int:
            continue
        question = question + ' ' + value
    question = question + '?'

    if config.debug:
        return {'Question': question, 'Answer': subject, 'Rule': 'who'}
    return {'Question': question, 'Answer': subject}

