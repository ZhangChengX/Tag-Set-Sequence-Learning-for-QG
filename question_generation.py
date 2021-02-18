#!/usr/bin/env python
# coding: utf-8

# import warnings
# warnings.simplefilter('ignore')

import config
import helper
from nltk.data import load
from libs.wordnet import WordNet
from distractor_generation import DistractorGeneration
from train import train_pair


class QuestionGeneration:

    # ner = None
    # srl = None
    # pos = None
    # cr = None
    # ss = None
    wn = None
    rules = None
    tokenizer = None
    preprocess_instance = None
    generate_filling_in_question = True
    generate_cloze_question = True
    generate_distractor = True

    def __init__(self):
        self.wn = WordNet()
        self.rules = self.load_rules()
        self.tokenizer = load('tokenizers/punkt/{0}.pickle'.format('english'))
        if config.dev_mode:
            self.preprocess_instance = type('', (object,), {'preprocess': lambda s: helper.preprocess(s), 'ctree': lambda s: helper.ctree(s), 'pos': lambda s: helper.pos(s)})
        else:
            from preprocess import Preprocess
            self.preprocess_instance = Preprocess()
            
    def load_rules(self):
        self.rules = helper.load_rules(config.rules_path)
        if config.debug:
            for k, v in self.rules.items():
                print('Rule ' + k + ': ' + str(len(v)))
        return self.rules

    def learn_rule(self, rule_pair:str):
        if '|' in rule_pair:
            declarative = rule_pair.split('|')[0].strip()
            interrogative = rule_pair.split('|')[1].strip()
            ques_word = interrogative.split()[0].capitalize()
            train_pair(ques_word, declarative, interrogative)
            self.load_rules()
            return True
        return False

    def generate(self, text):
        rst = []

        text = text.replace('-', ' - ')
        
        # Coreference Resolution
        # text = self.cr.predict(text)

        # Sentence Simplification
        # sentences = self.ss.simplify(text)

        # # Split sentences
        # sentences = helper.segment_by_sentence(text)
        sentences = helper.segment_by_sentence(text, self.tokenizer)

        # Generate Cloze Question
        if self.generate_cloze_question:
            rst = self.generate_cloze_question(sentences)

        # Generate distractors
        if self.generate_distractor:
            dg = DistractorGeneration(text)

        for sentence in sentences:
            # Generate Questions
            qaps = self.pipeline(sentence)
            # Generate Distractors
            if self.generate_distractor:
                if len(qaps) > 0: pos_tags = helper.pos(qaps[0]['sentence'])
                for qap in qaps:
                    # Filter useless answer
                    if qap['answer'].lower() in ['i', 'me', 'it', 'its', 'you', 'he', 'she', 'him', 'her', 'they', 'them', 'our', 'us']:
                        continue
                    qap['distractors'] = dg.distractors(qap['answer'], pos_tags)
                    # Filter if the distractors are not enough
                    if self.generate_distractor:
                        if len(qap['distractors']) < 3:
                            continue
                    rst.append(qap)
            else:
                rst = rst + qaps

        return rst

    def pipeline(self, sentence:str):
        question_list = []

        if config.debug:
            print('### Sentence: ')
            print(sentence)

        # Get merged tags list
        decla_tags_list = self.preprocess_instance.preprocess(sentence)

        # # Previous version, rules based QG
        # import rule_based_rules as rulebased
        # if config.rule_based:
        #     for tags_list in decla_tags_list:
        #         labels = {}
        #         ne_tags = []
        #         pos_tags = []
        #         for tags in tags_list:
        #             if tags['SR']:
        #                 labels[tags['SR']] = tags['W']
        #             ne_tags.append((tags['NE'], tags['W']))
        #             pos_tags.append((tags['W'], tags['POS']))
        #         rbqg = rulebased.who(labels, ne_tags, pos_tags)
        #         if rbqg:
        #             rbqg['Sentence'] = sentence
        #             question_list.append(rbqg)
        #         rbqg = rulebased.why(labels, ne_tags)
        #         if rbqg:
        #             rbqg['Sentence'] = sentence
        #             question_list.append(rbqg)
        #     # Remove duplicates
        #     ques_list = []
        #     for tmp in question_list.copy():
        #         if tmp['Question'] in ques_list:
        #             question_list.remove(tmp)
        #         else:
        #             ques_list.append(tmp['Question'])
        # # Previous version, rules based QG

        for decla_tags in decla_tags_list:

            if len(decla_tags) < 3:
                continue

            decla_seq = [tag['POS'] + ':' + tag['NE'] + ':' + tag['SR'] for tag in decla_tags]
            ne_decla_seq = [tag['NE'] for tag in decla_tags]
            sr_decla_seq = [tag['SR'] for tag in decla_tags]
            pos_decla_seq = [tag['POS'] for tag in decla_tags]

            if config.debug:
                print('### After Preprocess')
                print('Sub Sentence:')
                print(' '.join([tag['W'] for tag in decla_tags]))
                print(' '.join(decla_seq))
                print('')

            for ques_word, rules in self.rules.items():

                if 'Who' == ques_word and not ('PER' in ne_decla_seq or 'PRP' in pos_decla_seq):
                    continue
                if 'Where' == ques_word and 'LOC' not in ne_decla_seq:
                    continue
                if 'When' == ques_word and 'ARGM-TMP' not in sr_decla_seq:
                    continue
                if 'How_many' == ques_word and 'CD' not in pos_decla_seq:
                    continue

                # Find matching rule
                max_lcs = 0
                max_lcs_rule = {'k': [], 'v': []}
                max_lcs_rule_list = []
                for k, v in rules.items():
                    # lcs = helper.find_lcs(decla_seq, 0, k.split(), 0)
                    lcs = helper.find_lcs(decla_seq, k.split(), len(decla_seq), len(k.split()))
                    # if len(decla_seq) / 3 > lcs:
                    #     continue
                    if lcs < 3:
                        continue
                    # k = 0 表示 匹配到的sequence一定要是输入的陈述句sequence的子集
                    if len(k.split()) - lcs > config.matching_fuzzy:
                        continue
                    # if len(k.split()) == len(decla_seq):
                    #     print('### Perfect Matching')
                    if lcs > max_lcs:
                        max_lcs = lcs
                        max_lcs_rule = {'k': k.split(), 'v': v.split()}
                        max_lcs_rule_list.append(max_lcs_rule)
                    elif lcs == max_lcs:
                        # if len(k.split()) < len(max_lcs_rule['k']):
                        #     max_lcs = lcs
                        max_lcs_rule = {'k': k.split(), 'v': v.split()}
                        max_lcs_rule_list.append(max_lcs_rule)

                if max_lcs < 2:
                    if config.debug:
                        print('No matching rule.')
                        print('Question word: ' + ques_word)
                        print(' '.join([tag['W'] for tag in decla_tags]))
                        print(' '.join(decla_seq))
                        print(max_lcs_rule['k'])
                        print('')
                    continue
                
                for max_lcs_rule in max_lcs_rule_list:

                    if config.debug:
                        print('### Matching ###')
                        print('Question word: ' + ques_word)
                        print('Declarative Sentense:')
                        print(' '.join([tag['W'] for tag in decla_tags]))
                        print('Declarative tags:')
                        print([(tag['POS'] + ':' + tag['NE'] + ':' + tag['SR'], tag['W']) for tag in decla_tags])
                        print('Declarative tag seq:')
                        print(' '.join(decla_seq))
                        print('Matched rule: ')
                        print(max_lcs_rule['k'])
                        print(max_lcs_rule['v'])
                        print('MaxLCS: ' + str(max_lcs) + ' Total: ' + str(len(max_lcs_rule_list)))
                        if len(decla_tags) == len(max_lcs_rule['k']):
                            print('This is Perfect Matching')
                        print('')

                    # Get question seq
                    question_seq, answer_tags = helper.get_question_seq_by_rule(decla_seq, max_lcs_rule)

                    if config.debug:
                        print('### get_question_seq ###')
                        print('Interrogative tag seq:')
                        print(question_seq)
                        print('Answer_tags:')
                        print(answer_tags)
                        print('')

                    # If multi answer tags, choose ARG/LOC/PER as the only one, otherwise select NN.
                    if len(answer_tags) > 1:
                        for t in answer_tags.copy():
                            if 'ARG0' in t or 'ARG1' in t or 'ARG2' in t \
                                 or 'LOC' in t or 'PER' in t or 'TMP' in t or 'CD' in t:
                                answer_tags = [t]
                                break
                        if len(answer_tags) > 1:
                            for t in answer_tags.copy():
                                if 'NN' in t:
                                    answer_tags = [t]
                                    break
                        if config.debug:
                            print('New Answer_tags:')
                            print(answer_tags)
                            print('')

                    if len(answer_tags) != 1:
                        print('####################')
                        print('Answer tags more than one or Empty')
                        print('Answer_tags:')
                        print(answer_tags)
                        print('####################')
                        print('')
                        continue

                    # Generate question according to the seq
                    question = helper.generate_question_by_seq(ques_word, decla_tags, question_seq, answer_tags, self.wn)
                    if config.debug:
                        print('### generate_question ###')
                        if question:
                            print(question)
                        else:
                            print('Empty. No question generated.')
                        print('')
        
                    if not question:
                        continue

                    if 1 == len(answer_tags):
                        if answer_tags[0] in decla_seq:
                            answer = decla_tags[decla_seq.index(answer_tags[0])]['W']
                        else:
                            tmp_tags = [tag for tag in decla_seq if helper.is_tag_match(tag, answer_tags[0])]
                            if len(tmp_tags) > 0:
                                answer = decla_tags[decla_seq.index(tmp_tags[0])]['W']
                            else:
                                print('Can not find answer tag.')
                                continue
                                # answer = answer_tags
                    else:
                        answer = answer_tags
                    
                    if config.debug:
                        print('### generate_answer ###')
                        print(answer)
                        print('')

                    question_list.append({'type':'choice', 'sentence': sentence, 'question': question, 'answer': answer})
            
            if question_list:
                # Filling in Question
                if self.generate_filling_in_question:
                    filling_in_qestions = self.generate_filling_in_question(sentence)
                    question_list = question_list + filling_in_qestions
                    if config.debug:
                        print('### generate_filling_in_question ###')
                        print(filling_in_qestions)
                        print('')

                # Remove duplicated question
                tmp_ques_list = []
                tmp_what_ques_list = []
                tmp_other_ques_list = []
                for question in question_list.copy():
                    if question['question'] in tmp_ques_list:
                        question_list.remove(question)
                    elif question['question'][:4].lower() == 'what' and \
                        'Who' + question['question'][4:] in [q['question'] for q in question_list]:
                        # Remove duplicated What question
                        question_list.remove(question)
                        if config.debug:
                            print('### Removed duplicated What question ###')
                            print(question)
                            print('')
                    else:
                        tmp_ques_list.append(question['question'])

        return question_list

    def generate_filling_in_question(self, sentence):
        # Generate gap question
        ctree = self.preprocess_instance.ctree(sentence.strip())
        entities = helper.get_tree_nodes(ctree, ['NP'])
        # Build candidate questions
        candidates = []
        # if len(entities) > 7:
        #     return False
        for entity in entities:
            candidate_q = {}
            candidate_gap = str(' '.join(entity))
            # Replace sentence candidate_gap with ___
            gap_question = sentence.replace(candidate_gap, '______')
            if gap_question == sentence:
                continue
            if candidate_gap == sentence:
                continue
            candidate_q['type'] = 'choice'
            candidate_q['sentence'] = sentence
            candidate_q['question'] = gap_question
            candidate_q['answer'] = candidate_gap
            candidates.append(candidate_q)
        # print(candidates)
        return candidates

    def generate_cloze_question(self, sentences):
        cloze_qestion = {}
        cloze_qestion['type'] = 'cloze'
        cloze_qestion['answer'] = ''
        cloze_qestion['distractors'] = []
        max_len = 10 if len(sentences) > 10 else len(sentences)
        tmp_text = ''
        if len(sentences) > 3:
            tmp_text = ' '.join(sentences[0:max_len])
        else:
            return []
        pos_text_seq = self.preprocess_instance.pos(tmp_text)
        cloze_qestion['sentence'] = tmp_text
        tmp_text = ''
        for pos_tag in pos_text_seq:
            if pos_tag[1] == 'IN' and pos_tag[0] not in ['that', 'of']:
                tmp_text = tmp_text + ' <{' + pos_tag[0] + '}>'
            elif pos_tag[1][:2] == 'VB' and len(pos_tag[1]) == 3 and pos_tag[0] not in ['am', 'is', 'are', 'be']:
                base_verb = self.wn.get_base_verb(pos_tag[0])
                if base_verb == pos_tag[0]:
                    tmp_text = tmp_text + ' ' + pos_tag[0]
                else:
                    tmp_text = tmp_text + ' <{' + pos_tag[0] + '|' + base_verb + '}>'
            elif pos_tag[0] in [',', '.', '!', '?', '\'']:
                tmp_text = tmp_text  + pos_tag[0]
            else:
                tmp_text = tmp_text + ' ' + pos_tag[0]
        cloze_qestion['question'] = tmp_text
        return [cloze_qestion]


if __name__ == "__main__":
    qg = QuestionGeneration()
    while True:
        sentence = input('\nType in a sentence: \n')
        if sentence == '':
            continue
        if sentence == 'exit' or sentence == 'q':
            exit()
        if sentence == 'learn':
            learn_rule = input('\nType in a rule: declarative_sentence | interrogative_sentence \n')
            qg.learn_rule(learn_rule)
        questions_list = qg.pipeline(sentence)
        for question in questions_list:
            print('Sentence: ' + question['sentence'])
            print('Question: ' + question['question'])
            print('Answer: ' + question['answer'])
            print('')
        print('')
    