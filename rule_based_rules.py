# coding: utf-8

import re
import rule_based_helper as helper
import config


def who(labels, ne_tags, pos_tags):
    # Example: arg1 is arg2, arg2 is arg1, arg0 do argx
    if 'V' not in labels:
        return
    question = 'Who'
    subject_key = ''
    subject = helper.get_phrase_by_consecutive_tags('PER', ne_tags)
    if not subject:
        return
    # make sure arg1 is PER
    if 'ARG1' in labels.keys() and labels['ARG1'] == subject:
        subject_key = 'ARG1'
    elif 'ARG0' in labels.keys():
        subject_key = 'ARG0'
        subject = labels['ARG0']
    # Passive, ARG2 may include subject, not equal. e.g. by somebody
    elif 'ARG2' in labels.keys() and subject in labels['ARG2']:
        subject_key = 'ARG2'
    else:
        return
    
    # Eliminate stop word
    if ' ' in subject and subject.count(' ') < 3:
        subject = ' '.join(helper.remove_stop_word(subject.split(' ')))
    
    if subject.lower() in ['he', 'she', 'i', 'you', 'they']:
        return
        
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


# def who_backup(labels, ne_tags, pos_tags):
#     # Example: arg1 is arg2, arg0 do argx
#     # object at the beginning of the sentence
#     # Start to form question
#     question = 'Who'
#     subject_key = ''
#     subject = helper.get_phrase_by_consecutive_tags('PER', ne_tags)
#     # make sure arg1 is PER
#     if 'ARG1' in labels and labels['ARG1'] == subject:
#         subject_key = 'ARG1'
#     # Passive, ARG2 may include subject, not equal. e.g. by somebody
#     elif 'ARG2' in labels and subject in labels['ARG2']:
#         subject_key = 'ARG2'
#     elif 'ARG0' in labels:
#         subject_key = 'ARG0'
#         subject = labels['ARG0']
#     else:
#         return
    
#     # Eliminate stop word
#     if ' ' in subject and subject.count(' ') < 3:
#         subject = ' '.join(helper.remove_stop_word(subject.split(' ')))
#     # Get verb, if subject in ARG2 and passive, done -> have been done
#     if subject_key == 'ARG2' or labels['V'] == 'been':
#         verb = helper.combine_verb(labels['V'], pos_tags)[1]
#     else:
#         verb = labels['V']
#     # Get auxiliary verb
#     auxilverb = helper.get_auxil_verb(labels['V'], labels[subject_key], pos_tags)
    
#     # object at the beginning of the sentence
#     if subject_key == list(labels)[0]:
#         for key, value in labels.items():
#             if subject_key == key:
#                 continue
#             if 'V' == key:
#                 question = question + ' ' + verb
#                 continue
#             if 'ARGM-NEG' == key and verb not in helper.be_verb:
#                 value = 'not'
#                 question = question + ' ' + auxilverb + ' ' + value
#             else:
#                 question = question + ' ' + value
#     # object in the middle or at the end of the sentence
#     else:
#         labels = helper.lower_case_first_letter(labels)
#         question = question + ' ' + verb
#         if 'ARGM-NEG' in labels:
#             if verb in helper.be_verb:
#                 question = question + ' not'
#             else:
#                 question = question + ' ' + auxilverb + ' not'
#         for key, value in labels.items():
#             if key in [subject_key, 'V', 'ARGM-NEG']:
#                 continue
#             question = question + ' ' + value
#     question = question + '?'
#     if config.debug:
#         return {'Question': question, 'Answer': subject, 'Rule': 'who'}
#     return {'Question': question, 'Answer': subject}


# def what(labels, ne_tags, pos_tags):
#     # Example: arg0 do arg1 -> What does arg1 do?
#     question = 'What'
#     if 'ARG0' in labels and 'ARG1' in labels:
#         obj = labels['ARG1']
#         tense = helper.get_verb_tense(labels['V'], pos_tags)
#         if 'VBN' == tense:
#             verb = helper.combine_verb(labels['V'], pos_tags)[1]
#         else:
#             verb = helper.get_base_verb(labels['V'])
#         if 'ARGM-MOD' in labels:
#             question = question + ' ' + labels['ARGM-MOD']
#             excluded_key = ['ARG1', 'ARGM-MOD']
#         else:
#             if 'VBN' != tense:
#                 auxilverb = helper.get_auxil_verb(labels['V'], labels['ARG0'], pos_tags)
#                 question = question + ' ' + auxilverb
#             excluded_key = ['ARG1']
#         labels = helper.lower_case_first_letter(labels)
#         for key, value in labels.items():
#             if key not in excluded_key:
#                 if 'ARGM-NEG' == key: # 'ARGM-NEG' may be "n't"
#                     value = 'not'
#                 if 'V' == key:
#                     question = question + ' ' + verb
#                     continue
#                 question = question + ' ' + value
#         question = question + '?'
#         if config.debug:
#             return {'Question': question, 'Answer': obj, 'Rule': 'what'}
#         return {'Question': question, 'Answer': obj}


def where(labels, ne_tags):
    question = 'Where'
    if 'ARGM-LOC' in labels and ('ARG0' in labels or 'ARG1' in labels):
        labels = helper.lower_case_first_letter(labels)
        verb = helper.combine_verb(labels['V'], ne_tags)[0]
        if verb:
            question = question + ' ' + verb 

        location = ' '.join(helper.remove_stop_word(labels['ARGM-LOC'].split(' ')))
        # arg_subject = 'ARG0' if 'ARG0' in labels else 'ARG1'
        # question = question + ' does ' + labels[arg_subject] + ' ' + labels['V']
        # for key, value in labels.items():
        #     if key in [arg_subject, 'V']:
        #         continue
        #     if 'ARGM-NEG' == key:
        #         question = question + ' does ' + value
        #     else:
        #         question = question + ' ' + value
        for key, value in labels.items():
            if key in ['ARGM-LOC']:
                continue
            question = question + ' ' + value
        question = question + '?'
    
        if config.debug:
            return {'Question': question, 'Answer': location, 'Rule': 'where'}
        return {'Question': question, 'Answer': location}


def why(labels, ne_tags):
    question = 'Why'
    if 'ARGM-CAU' in labels:
        cause = labels['ARGM-CAU']
        for key, value in labels.items():
            if key not in ['ARGM-CAU']:
                if 'ARGM-NEG' == key:
                    question = question + ' does ' + value
                else:
                    question = question + ' ' + value
        question = question + '?'
    
        if config.debug:
            return {'Question': question, 'Answer': cause, 'Rule': 'why'}
        return {'Question': question, 'Answer': cause}


def how(labels, ne_tags):
    # TODO The boy went by bus.
    # Generate: How does the boy went?
    # Should be: How did the boy go? / What did the boy go by?
    question = 'How'
    if 'ARGM-MNR' in labels:
        manner = labels['ARGM-MNR']
        question = question + ' do/did/does'
        labels = helper.lower_case_first_letter(labels)
        for key, value in labels.items():
            if key not in ['ARGM-MNR']:
                # if 'ARGM-MNR' == key:
                #     question = question + ' does ' + value
                # else:
                question = question + ' ' + value
        question = question + '?'
    
        if config.debug:
            return {'Question': question, 'Answer': manner, 'Rule': 'how'}
        return {'Question': question, 'Answer': manner}


def when(labels, ne_tags):
    # TODO He hurriedly left the class in the morning.
    # Generate: When he hurriedly left the class?
    # Should be: When did he hurriedly leave the class?
    question = 'When'
    if 'ARGM-TMP' in labels:
        time = labels['ARGM-TMP']
        be = helper.combine_verb(labels['V'], ne_tags)[0]
        if be:
            question = question + ' ' + be
        labels = helper.lower_case_first_letter(labels)
        for key, value in labels.items():
            if key not in ['ARGM-TMP']:
                if 'ARGM-NEG' == key:
                    question = question + ' does ' + value
                else:
                    question = question + ' ' + value
        question = question + '?'
    
        if config.debug:
            return {'Question': question, 'Answer': time, 'Rule': 'when'}
        return {'Question': question, 'Answer': time}


def which(labels, ne_tags):
    pass


def arg1_is_argx(labels, ne_tags):
    # For structure like arg1 is argX, ask arg1
    question = 'What'
    if 'ARG1' in labels and 'ARG0' not in labels:
        obj = labels['ARG1']

        unknown = helper.get_phrase_by_consecutive_tags('PER', ne_tags)
        if unknown == labels['ARG1']:
            question = 'Who'
            obj = unknown

        unknown = helper.get_phrase_by_consecutive_tags('LOC', ne_tags)
        if unknown == labels['ARG1']:
            question = 'Where'
            obj = unknown
        
        for key, value in labels.items():
            if key in ['ARG1']:
                continue
            # if 'ARGM-NEG' == key:
            #     question = question + ' does ' + value
            # else:
            question = question + ' ' + value
        question = question + '?'

        if config.debug:
            return {'Question': question, 'Answer': obj, 'Rule': 'arg1_is_argx'}
        return {'Question': question, 'Answer': obj}


def arg1_is_arg2(labels, ne_tags):
    # arg1 is arg2, ask arg2
    question = 'What'
    if 'ARG1' in labels and 'ARG2' in labels and 'ARG0' not in labels:
        obj = labels['ARG2']

        unknown = helper.get_phrase_by_consecutive_tags('PER', ne_tags)
        if unknown == labels['ARG2'] or unknown == labels['ARG1']:
            question = 'Who'
            obj = unknown

        unknown = helper.get_phrase_by_consecutive_tags('LOC', ne_tags)
        if unknown == labels['ARG2']:
            question = 'Where'
            obj = unknown

        question = question + ' is'
        for key, value in labels.items():
            if key in ['ARG2', 'V']:
                continue
            question = question + ' ' + value
        question = question + '?'

        if config.debug:
            return {'Question': question, 'Answer': obj, 'Rule': 'arg1_is_arg2'}
        return  {'Question': question, 'Answer': obj}



