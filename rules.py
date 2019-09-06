# coding: utf-8

import re
import helper
import config


def who(labels, ne_tags, pos_tags):
    # Example: arg1 is arg2, arg0 do argx
    # object at the beginning of the sentence
    # Start to form question
    question = 'Who'
    subject_key = ''
    subject = helper.get_phrase_by_consecutive_tags('PER', ne_tags)
    # make sure arg1 in persion
    if 'ARG1' in labels and labels['ARG1'] == subject:
        subject_key = 'ARG1'
    elif 'ARG0' in labels:
        subject_key = 'ARG0'
        subject = labels['ARG0']
    elif 'ARG2' in labels and subject in labels['ARG2']: # ARG2 may include subject, not equal.
        subject_key = 'ARG2'
    else:
        return
    # Eliminate stop word
    if ' ' in subject and subject.count(' ') < 3:
        subject = ' '.join(helper.remove_stop_word(subject.split(' ')))
    # Get verb
    verb = helper.combine_verb(labels['V'], pos_tags)[1]
    auxilverb = helper.get_auxil_verb(labels['V'], labels[subject_key], pos_tags)
    # object at the beginning of the sentence
    if subject_key == list(labels)[0]:
        for key, value in labels.items():
            if subject_key == key:
                continue
            if 'V' == key:
                question = question + ' ' + verb
                continue
            if 'ARGM-NEG' == key:
                question = question + ' ' + auxilverb + ' ' + value
            else:
                question = question + ' ' + value
    # object in the middle or at the end of the sentence
    else:
        labels = helper.lower_case_first_letter(labels)
        question = question + ' ' + verb
        for key, value in labels.items():
            if key in [subject_key, 'V']:
                continue
            if 'ARGM-NEG' == key:
                question = question + ' ' + auxilverb + ' ' + value
            else:
                question = question + ' ' + value
    question = question + '?'
    if config.debug:
        return {'Question': question, 'Answer': subject, 'Rule': 'who'}
    return {'Question': question, 'Answer': subject}

