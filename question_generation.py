#!/usr/bin/env python
# coding: utf-8

import warnings
warnings.simplefilter('ignore')

from libs.semantic_role_labeling import SemanticRoleLabeling
from libs.named_entity_recognition import NamedEntityRecognition
from libs.dependency_parsing import DependencyParsing
# from libs.coreference_resolution import CoreferenceResolution
from libs.sentence_simplification import SentenceSimplification
from libs.wordnet import WordNet
import config
import helper
import rule_based_rules as rulebased


class QuestionGeneration:

    ner = None
    srl = None
    dp = None
    wn = None
    cr = None
    ss = None
    rules = None

    def __init__(self):
        self.ner = NamedEntityRecognition()
        self.srl = SemanticRoleLabeling()
        self.dp = DependencyParsing()
        self.ss = SentenceSimplification()
        # self.cr = CoreferenceResolution()
        self.wn = WordNet()
        self.rules = helper.load_rules(config.rules_path)
        if config.debug:
            for k, v in self.rules.items():
                print('Rule ' + k + ': ' + str(len(v)))

    def generate(self, text):
        rst = []
        # Coreference Resolution
        # text = self.cr.predict(text)
        # Sentence Simplification
        sentences = self.ss.simplify(text)
        # # Split sentences
        # sentences = helper.segment_by_sentence(text)
        for sentence in sentences:
            qgen = self.pipeline(sentence)
            if qgen:
                rst.append(qgen)
        # TODO question filter
        return rst

    def pipeline(self, sentence:str):
        sentence = sentence.strip()
        word_list = sentence.split(' ')
        if len(word_list) < 3: return []
        if sentence[-1:] == '?': return []
        if word_list[0].lower() in ['who', 'whose', 'what', 'where', 'when', 'which', 'why', 'how']:
            return []
        if word_list[0].lower() in ['and', 'but', 'for', 'or', 'plus', 'so', 'therefore']:
            sentence = sentence.replace(word_list[0], '')
        
        question_list = []

        # Get merged tags list
        decla_tags_list = self.preprocess(sentence)

        # Previous version, rules based QG
        if config.rule_based:
            for tags_list in decla_tags_list:
                labels = {}
                ne_tags = []
                pos_tags = []
                for tags in tags_list:
                    if tags['SR']:
                        labels[tags['SR']] = tags['W']
                    ne_tags.append((tags['NE'], tags['W']))
                    pos_tags.append((tags['W'], tags['POS']))
                rbqg = rulebased.who(labels, ne_tags, pos_tags)
                if rbqg:
                    rbqg['Sentence'] = sentence
                    question_list.append(rbqg)
                rbqg = rulebased.why(labels, ne_tags)
                if rbqg:
                    rbqg['Sentence'] = sentence
                    question_list.append(rbqg)
            # Remove duplicates
            ques_list = []
            for tmp in question_list.copy():
                if tmp['Question'] in ques_list:
                    question_list.remove(tmp)
                else:
                    ques_list.append(tmp['Question'])
        # Previous version, rules based QG

        for decla_tags in decla_tags_list:

            decla_seq = [tag['POS'] + ':' + tag['NE'] + ':' + tag['SR'] for tag in decla_tags]
            
            for ques_word, rules in self.rules.items():

                # Find matching rule
                max_lcs = 0
                max_lcs_rule = {'k': [], 'v': []}
                for k, v in rules.items():
                    # lcs = helper.find_lcs(decla_seq, 0, k.split(), 0)
                    lcs = helper.find_lcs(decla_seq, k.split(), len(decla_seq), len(k.split()))
                    if len(decla_seq) / 3 > lcs:
                        continue
                    if len(k.split()) - lcs > config.matching_fuzzy:
                        continue
                    if lcs > max_lcs:
                        max_lcs = lcs
                        max_lcs_rule = {'k': k.split(), 'v': v.split()}
                    elif lcs == max_lcs:
                        if len(k.split()) < len(max_lcs_rule['k']):
                            max_lcs = lcs
                            max_lcs_rule = {'k': k.split(), 'v': v.split()}
                if max_lcs < 2:
                    if config.debug:
                        print('No matching rule. ' + ques_word)
                        print(' '.join([tag['W'] for tag in decla_tags]))
                        print(decla_seq)
                        print('')
                    continue

                if config.debug:
                    print('### Matching')
                    print('Question word: ' + ques_word)
                    print('Declarative Sentense:')
                    print(' '.join([tag['W'] for tag in decla_tags]))
                    print('Declarative tags:')
                    print([(tag['POS'] + ':' + tag['NE'] + ':' + tag['SR'], tag['W']) for tag in decla_tags])
                    print('Declarative tag seq:')
                    print(decla_seq)
                    print('Matched rule: MaxLCS: ' + str(max_lcs))
                    print(max_lcs_rule['k'])
                    print(max_lcs_rule['v'])
                
                # Get question seq
                question_seq, answer_tags = helper.get_question_seq_by_rule(decla_seq, max_lcs_rule)

                if config.debug:
                    print('Interrogative tag seq:')
                    print(question_seq)
                    print('Answer_tags:')
                    print(answer_tags)

                # Generate question according to the seq
                question = helper.generate_question_by_seq(ques_word, decla_tags, question_seq, answer_tags, self.wn)
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
                            answer = answer_tags
                else:
                    answer = answer_tags
                question_list.append({'Sentence': sentence, 'Question': question, 'Answer': answer})
        return question_list
    
    def preprocess(self, sentence:str):
        sentence = sentence.replace("’", "'")
        sentence = sentence.replace("`", "'")
        sentence = sentence.replace('“', '"')
        sentence = sentence.replace('”', '"')
        sentence = sentence.replace("'ve", " have")
        # didn't -> did not, haven't -> have not, can't -> can not
        if "can't" in sentence:
            sentence = sentence.replace("'t", ' not')
        sentence = sentence.replace("n't", ' not')

        # POS Tagging
        pos_tags = self.dp.predict(sentence)

        # Named Entity Information
        ne_tags = self.ner.predict(sentence)

        # Semantic Role Labeling
        sr_tags_list = self.srl.predict(sentence)

        if config.debug:
            print('sr_tags_list before preprocess:')
            print('sr_tags_list = ' + str(sr_tags_list))

        sr_tags_list = helper.preprocess_sr_tags(sr_tags_list, pos_tags)

        if config.debug:
            print('sr_tags_list after preprocess:')
            print('sr_tags_list = ' + str(sr_tags_list))
        
        rst = []
        for sr_tags in sr_tags_list:
            if len(sr_tags) < 3:
                continue
            merged_tags = helper.merge_tags(pos_tags, ne_tags, sr_tags)
            rst.append(merged_tags)

            if config.debug:
                print('### Pre-processing ###')
                print(sentence)
                print('pos_tags = ' + str(pos_tags))
                print('ne_tags = ' + str(ne_tags))
                print('sr_tags = ' + str(sr_tags))
                print('merged_tags = ' + str(merged_tags))
                print([tag['POS'] + ':' + tag['NE'] + ':' + tag['SR'] for tag in merged_tags])
        
        # return [[{'a':'b'}]]
        return rst
    

if __name__ == "__main__":
    qg = QuestionGeneration()
    while True:
        sentence = input('\nType in a sentence: \n')
        if sentence == 'exit' or sentence == 'q':
            exit()
        if sentence == '':
            continue
        sentence = qg.ss.simplify(sentence)
        for sent in sentence:
            questions_list = qg.pipeline(sent)
            for question in questions_list:
                print('Sentence: ' + question['Sentence'])
                print('Question: ' + question['Question'])
                print('Answer: ' + question['Answer'])
        print('')
    