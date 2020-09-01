#!/usr/bin/env python
# coding: utf-8

import config
import helper_preprocess
from libs.semantic_role_labeling import SemanticRoleLabeling
from libs.named_entity_recognition import NamedEntityRecognition
from libs.pos_tagging import PosTagging
from libs.constituency_parsing import ConstituencyParsing
# from libs.dependency_parsing import DependencyParsing
# from libs.coreference_resolution import CoreferenceResolution
# from libs.sentence_simplification import SentenceSimplification


class Preprocess:

    _ner = None
    _srl = None
    _pos = None
    _ctree = None
    _dtree = None
    _wn = None
    _cr = None
    _ss = None

    def __init__(self):
        self._srl = SemanticRoleLabeling()
        self._pos = PosTagging()
        self._ner = NamedEntityRecognition()
        self._ctree = ConstituencyParsing()
        # self._dtree = DependencyParsing()
        # self._ss = SentenceSimplification()
        # self._cr = CoreferenceResolution()
        # self._wn = WordNet()

    def preprocess(self, sentence:str):
        sentence = sentence.strip()

        # Check sentence
        word_list = sentence.split(' ')
        if len(word_list) < 3: return []
        if sentence[-1:] == '?': return []
        if sentence[-2:] == '?.': return []
        if word_list[0].lower() in helper_preprocess.interrogative_word:
            return []

        # Remove the continuous prep in the begining of the sentence
        is_break = False
        for i, w in enumerate(word_list):
            if is_break:
                break
            if w.lower() in ['and', 'but', 'for', 'or', 'plus', 'so', 'therefore', 'because']:
                word_list.pop(i)
            else:
                is_break = True

        # if word_list[0].lower() in ['and', 'but', 'for', 'or', 'plus', 'so', 'therefore', 'because']:
        #     sentence = sentence.replace(word_list[0], '')

        sentence = sentence.replace("’", "'")
        sentence = sentence.replace("`", "'")
        sentence = sentence.replace('“', '"')
        sentence = sentence.replace('”', '"')
        sentence = sentence.replace("'ve", " have")
        # didn't -> did not, haven't -> have not, can't -> can not
        if "can't" in sentence:
            sentence = sentence.replace("'t", ' not')
        sentence = sentence.replace("n't", ' not')

        # Semantic Role Labeling
        sr_tags_list = self._srl.predict(sentence)
        if not sr_tags_list:
            return []

        # POS Tagging
        pos_tags = self._pos.predict(sentence)

        # Named Entity Information
        ne_tags = self._ner.predict(sentence)

        if config.debug:
            print('### Pre-processing ###')
            print('Before preprocess_sr_tags():')
            print('sr_tags_list = ' + str(sr_tags_list))

        sr_tags_list = helper_preprocess.preprocess_sr_tags(sr_tags_list, pos_tags)

        if config.debug:
            print('After preprocess_sr_tags():')
            print('sr_tags_list = ' + str(sr_tags_list))
            print('')
        
        rst = []
        for sr_tags in sr_tags_list:
            sr_t_list = [t[0][:4] for t in sr_tags if t[0][:4] != 'ARGM']
            if len(sr_t_list) < 2:
                continue
            merged_tags = helper_preprocess.merge_tags(pos_tags, ne_tags, sr_tags)
            rst.append(helper_preprocess.lowercase_first_word(merged_tags))

            if config.debug:
                print('### merged_tags: ###')
                print('Sentence: ' + sentence)
                print('Sub Sentence: ' + str(' '.join([t[1] for t in sr_tags])))
                print('pos_tags = ' + str(pos_tags))
                print('ne_tags = ' + str(ne_tags))
                print('sr_tags = ' + str(sr_tags))
                print('merged_tags = ' + str(merged_tags))
                print([tag['POS'] + ':' + tag['NE'] + ':' + tag['SR'] for tag in merged_tags])
                print('')
        
        # return [[{'a':'b'}]]
        return rst
        
    def preprocess_learning(self, sentence:str):
        sentence = sentence.strip()

        # Check sentence
        word_list = sentence.split(' ')
        if len(word_list) < 3: return []

        sentence = sentence.replace("’", "'")
        sentence = sentence.replace("`", "'")
        sentence = sentence.replace('“', '"')
        sentence = sentence.replace('”', '"')
        sentence = sentence.replace("'ve", " have")
        # didn't -> did not, haven't -> have not, can't -> can not
        if "can't" in sentence:
            sentence = sentence.replace("'t", ' not')
        sentence = sentence.replace("n't", ' not')

        # Semantic Role Labeling
        sr_tags_list = self._srl.predict(sentence)
        if not sr_tags_list:
            return []

        # POS Tagging
        pos_tags = self._pos.predict(sentence)

        # Named Entity Information
        ne_tags = self._ner.predict(sentence)

        if config.debug:
            print('### Pre-processing ###')
            print('Before preprocess_sr_tags():')
            print('sr_tags_list = ' + str(sr_tags_list))

        sr_tags_list = helper_preprocess.preprocess_sr_tags(sr_tags_list, pos_tags)

        if config.debug:
            print('After preprocess_sr_tags():')
            print('sr_tags_list = ' + str(sr_tags_list))
            print('')
        
        rst = []
        for sr_tags in sr_tags_list:
            sr_t_list = [t[0][:4] for t in sr_tags if t[0][:4] != 'ARGM']
            if len(sr_t_list) < 2:
                continue
            merged_tags = helper_preprocess.merge_tags(pos_tags, ne_tags, sr_tags)
            rst.append(helper_preprocess.lowercase_first_word(merged_tags))

            if config.debug:
                print('### merge_tags_pos_based: ###')
                print('Sentence: ' + sentence)
                print('Sub Sentence: ' + str(' '.join([t[1] for t in sr_tags])))
                print('pos_tags = ' + str(pos_tags))
                print('ne_tags = ' + str(ne_tags))
                print('sr_tags = ' + str(sr_tags))
                print('merged_tags = ' + str(merged_tags))
                print([tag['POS'] + ':' + tag['NE'] + ':' + tag['SR'] for tag in merged_tags])
                print('')
        
        return rst

    def srl(self, sentence:str):
        return self._srl.predict(sentence)

    def pos(self, sentence:str):
        return self._pos.predict(sentence)

    def ner(self, sentence:str):
        return self._ner.predict(sentence)

    def ctree(self, sentence:str):
        return self._ctree.predict(sentence)

    def dtree(self, sentence:str):
        return self._dtree.predict(sentence)

