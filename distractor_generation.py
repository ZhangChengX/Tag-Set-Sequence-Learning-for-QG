#!/usr/bin/env python
# coding: utf-8

import math
import nltk
import random
import helper
import config
import requests
from nltk.corpus import wordnet as wn
from nltk.metrics import edit_distance

class DistractorGeneration:

    _text = None
    # _noun_list = None
    _ne = {} # {'ORG': ['The Times', 'BBC'], 'PER': [], 'LOC': [], 'MISC': ['Oxford English Dictionary']}


    def __init__(self, text:str):
        super().__init__()
        # self._noun_list = self.extract_noun(text)
        self._ne = self.extract_named_entity(text)
    
    def distractors(self, answer:str, pos_tags:list):
        if config.debug:
            print('### Distractors')
            print('')
        n = 3 # number of distractors to be generated
        distractors = []
        correct_tags = []
        # correct_tags = self.merge_answer(correct_tags)

        # pos_tags = helper.pos(sentence)
        pos_tags_word_list = [t[0] for t in pos_tags]
        for word in answer.split(' '):
            index = pos_tags_word_list.index(word)
            pos_tag = pos_tags[index][1]
            ne_tag = ''
            for k, v in self._ne.items():
                if word in v:
                    ne_tag = k
            correct_tags.append({'W': word, 'POS': pos_tag, 'NE': ne_tag})

        correct_tags.reverse()
        
        # Collect distracted words
        candidates_dict = {} 
        antonym_candidates_list = []
        # candidates_dict = {'target_word': [('candidate', word2vec, WUP, edit_distance)]}
        
        # by NE
        for d in correct_tags:
            if d['NE'] == 'PER' and 'PER' in self._ne and len(self._ne['PER']) > 0:
                candidates_dict[d['W']] = [(t, 1, 1, 1) for t in self.get_ramdom_words(self._ne['PER'], [d['W']], 3)]
            if d['NE'] == 'ORG' and 'ORG' in self._ne and  len(self._ne['ORG']) > 0:
                candidates_dict[d['W']] = [(t, 1, 1, 1) for t in self.get_ramdom_words(self._ne['ORG'], [d['W']], 3)]
            if d['NE'] == 'LOC' and 'LOC' in self._ne and  len(self._ne['LOC']) > 0:
                candidates_dict[d['W']] = [(t, 1, 1, 1) for t in self.get_ramdom_words(self._ne['LOC'], [d['W']], 3)]
            # if d['NE'] == 'MISC' and 'MISC' in self._ne and  len(self._ne['MISC']) > 0:
            #     candidates_dict[d['W']] = [(t, 1, 1, 1) for t in self.get_ramdom_words(self._ne['MISC'], [d['W']], 3)]
        if config.debug:
            print('NE: ', candidates_dict)
        
        # by POS CD numeral
        if len([j for i in candidates_dict.values() for j in i]) < n:
            # TODO
            word2digit = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', \
                    6: 'six', 7: 'seven', 8: 'eight', 9:'nine', 10: 'ten', \
                    11: 'eleven', 12: 'twelve', 13: 'thirteen', 14: 'fourteen', 15: 'fifteen', \
                    20: 'twenty', 30: 'thirty', 40: 'fourty', 50: 'fifty', \
                    100: 'hundred', 1000: 'thousand'}
            for d in correct_tags:
                if d['POS'] == 'CD':
                    if d['W'].isdigit():
                        cd_list = [str(int(d['W']) + 1), str(int(d['W']) + 1), str(int(d['W']) + 10)]
                    elif d['W'] in word2digit.values():
                        digit = list(word2digit.keys())[list(word2digit.values()).index(d['W'])]
                        cd_list = []
                        for i in [digit + 1, digit - 1, digit + 2]:
                            if i in word2digit.keys():
                                cd_list.append(list(word2digit.values())[list(word2digit.keys()).index(i)])
                            else:
                                cd_list.append(str(i))
                    else:
                        cd_list = ['one', 'two', 'three']

                    if d['W'] in candidates_dict.keys():
                        candidates_dict[d['W']] = candidates_dict[d['W']] + [(t, 1, 1, 1) for t in cd_list]
                    else:
                        candidates_dict[d['W']] = [(t, 1, 1, 1) for t in cd_list]
        
            if config.debug:
                print('POS CD: ', candidates_dict)

        if len([j for i in candidates_dict.values() for j in i]) < n:
            # by Word2vec
            for d in correct_tags:
                if d['POS'][:2] == 'NN' or d['POS'][:2] == 'VB':
                    similar_words = self.get_most_similar_words(d, 'positive')
                    if len(similar_words) > 0:
                        similar_words.reverse()
                        if d['W'] in candidates_dict.keys():
                            candidates_dict[d['W']] = candidates_dict[d['W']] + [similar_words[j] for j in range(n) if len(similar_words) > j]
                        else:
                            candidates_dict[d['W']] = [similar_words[j] for j in range(n) if len(similar_words) > j]
                    # break if the number of result greater than n * 2
                    if len([j for i in candidates_dict.values() for j in i]) >= n * 2:
                        break
            if config.debug:
                print('Word2vec: ', candidates_dict)

            # by POS NN and VB
            for d in correct_tags:
                if d['POS'][:2] == 'NN' or d['POS'][:2] == 'VB':
                    synonyms, antonyms, hypernyms = self.get_synonyms_antonyms(d)
                    for t in antonyms:
                        antonym_candidates_list.append(t[0])
                    if len(synonyms + antonyms + hypernyms) > 0:
                        if d['W'] in candidates_dict.keys():
                            candidates_dict[d['W']] = candidates_dict[d['W']] + synonyms + antonyms + hypernyms
                        else:
                            candidates_dict[d['W']] = synonyms + antonyms + hypernyms
                    if len([j for i in candidates_dict.values() for j in i]) >= n:
                        break
            if config.debug:
                print('WordNet POS: ', candidates_dict)
                print('Antonyms: ', antonym_candidates_list)

        if len([j for i in candidates_dict.values() for j in i]) < 1:
            return []

        # Ranking
        candidates_dict = self.ranking(candidates_dict, antonym_candidates_list)
        if config.debug:
            print('Candidates with ranking:')
            for k, v in candidates_dict.items():
                print(k)
                for c in v:
                    print(c[0], c[4])

        # Build distractors
        correct_tags.reverse()
        for k, v in candidates_dict.items():
            correct_tags_str = ' '.join([w['W'] for w in correct_tags])
            for t in v:
                distractor = correct_tags_str.replace(k, t[0])
                distractors.append(distractor)
        
        return distractors

    # def distractors(self, correct_answer:list):
    #     n = 3 # number of distractors to be generated
    #     distractors = []
    #     # correct_answer = self.merge_answer(correct_answer)
    #     if config.debug:
    #         print('New answer: ', correct_answer)
    #     correct_answer.reverse()
        
    #     # Collect distracted words
    #     candidates_dict = {} 
    #     antonym_candidates_list = []
    #     # candidates_dict = {'target_word': [('candidate', word2vec, WUP, edit_distance)]}
        
    #     # by NE
    #     for d in correct_answer:
    #         if d['NE'] == 'PER' and 'PER' in self._ne and len(self._ne['PER']) > 0:
    #             candidates_dict[d['W']] = [(t, 1, 1, 1) for t in self.get_ramdom_words(self._ne['PER'], [d['W']], 3)]
    #         if d['NE'] == 'ORG' and 'ORG' in self._ne and  len(self._ne['ORG']) > 0:
    #             candidates_dict[d['W']] = [(t, 1, 1, 1) for t in self.get_ramdom_words(self._ne['ORG'], [d['W']], 3)]
    #         if d['NE'] == 'LOC' and 'LOC' in self._ne and  len(self._ne['LOC']) > 0:
    #             candidates_dict[d['W']] = [(t, 1, 1, 1) for t in self.get_ramdom_words(self._ne['LOC'], [d['W']], 3)]
    #         # if d['NE'] == 'MISC' and 'MISC' in self._ne and  len(self._ne['MISC']) > 0:
    #         #     candidates_dict[d['W']] = [(t, 1, 1, 1) for t in self.get_ramdom_words(self._ne['MISC'], [d['W']], 3)]
    #     if config.debug:
    #         print('NE: ', candidates_dict)
        
    #     # by POS CD numeral
    #     if len([j for i in candidates_dict.values() for j in i]) < n:
    #         # TODO
    #         word2digit = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', \
    #                 6: 'six', 7: 'seven', 8: 'eight', 9:'nine', 10: 'ten', \
    #                 11: 'eleven', 12: 'twelve', 13: 'thirteen', 14: 'fourteen', 15: 'fifteen', \
    #                 20: 'twenty', 30: 'thirty', 40: 'fourty', 50: 'fifty', \
    #                 100: 'hundred', 1000: 'thousand'}
    #         for d in correct_answer:
    #             if d['POS'] == 'CD':
    #                 if d['W'].isdigit():
    #                     cd_list = [str(int(d['W']) + 1), str(int(d['W']) + 1), str(int(d['W']) + 10)]
    #                 elif d['W'] in word2digit.values():
    #                     digit = list(word2digit.keys())[list(word2digit.values()).index(d['W'])]
    #                     cd_list = []
    #                     for i in [digit + 1, digit - 1, digit + 2]:
    #                         if i in word2digit.keys():
    #                             cd_list.append(list(word2digit.values())[list(word2digit.keys()).index(i)])
    #                         else:
    #                             cd_list.append(str(i))
    #                 else:
    #                     cd_list = ['one', 'two', 'three']

    #                 if d['W'] in candidates_dict.keys():
    #                     candidates_dict[d['W']] = candidates_dict[d['W']] + [(t, 1, 1, 1) for t in cd_list]
    #                 else:
    #                     candidates_dict[d['W']] = [(t, 1, 1, 1) for t in cd_list]
        
    #         if config.debug:
    #             print('POS CD: ', candidates_dict)

    #     if len([j for i in candidates_dict.values() for j in i]) < n:
    #         # by Word2vec
    #         for d in correct_answer:
    #             if d['POS'][:2] == 'NN' or d['POS'][:2] == 'VB':
    #                 similar_words = self.get_most_similar_words(d, 'positive')
    #                 if len(similar_words) > 0:
    #                     similar_words.reverse()
    #                     if d['W'] in candidates_dict.keys():
    #                         candidates_dict[d['W']] = candidates_dict[d['W']] + [similar_words[j] for j in range(n) if len(similar_words) > j]
    #                     else:
    #                         candidates_dict[d['W']] = [similar_words[j] for j in range(n) if len(similar_words) > j]
    #                 # break if the number of result greater than n * 2
    #                 if len([j for i in candidates_dict.values() for j in i]) >= n * 2:
    #                     break
    #         if config.debug:
    #             print('Word2vec: ', candidates_dict)

    #         # by POS NN and VB
    #         for d in correct_answer:
    #             if d['POS'][:2] == 'NN' or d['POS'][:2] == 'VB':
    #                 synonyms, antonyms, hypernyms = self.get_synonyms_antonyms(d)
    #                 for t in antonyms:
    #                     antonym_candidates_list.append(t[0])
    #                 if len(synonyms + antonyms + hypernyms) > 0:
    #                     if d['W'] in candidates_dict.keys():
    #                         candidates_dict[d['W']] = candidates_dict[d['W']] + synonyms + antonyms + hypernyms
    #                     else:
    #                         candidates_dict[d['W']] = synonyms + antonyms + hypernyms
    #                 if len([j for i in candidates_dict.values() for j in i]) >= n:
    #                     break
    #         if config.debug:
    #             print('WordNet POS: ', candidates_dict)
    #             print('Antonyms: ', antonym_candidates_list)

    #     if len([j for i in candidates_dict.values() for j in i]) < 1:
    #         return []

    #     # Ranking
    #     candidates_dict = self.ranking(candidates_dict, antonym_candidates_list)
    #     if config.debug:
    #         print('Candidates with ranking:')
    #         for k, v in candidates_dict.items():
    #             print(k)
    #             for c in v:
    #                 print(c[0], c[4])

    #     # Build distractors
    #     correct_answer.reverse()
    #     for k, v in candidates_dict.items():
    #         correct_answer_str = ' '.join([w['W'] for w in correct_answer])
    #         for t in v:
    #             distractor = correct_answer_str.replace(k, t[0])
    #             distractors.append(distractor)
        
    #     return distractors

    # def merge_answer(self, answer):
    #     # answer = [{'W': 'John', 'POS': 'NN', 'NE': 'U-PER'}, {'W': 'Wick', 'POS': 'NN', 'NE': 'U-PER'}]
    #     # Merge continuous words with same NE tag
    #     new_answer = []
    #     skip_index = []
    #     total = len(answer)
    #     for i in range(total):
    #         if i in skip_index:
    #             continue

    #         # Looking for continuous words with same NE tag
    #         is_loop = True
    #         k = i
    #         while is_loop:
    #             if total > k + 1:
    #                 if answer[i]['NE'][2:] == answer[k + 1]['NE'][2:] and \
    #                     (answer[i]['NE'] != 'O' and answer[k + 1]['NE'] != 'O'):
    #                     k = k + 1
    #                     skip_index.append(k)
    #                 else:
    #                     is_loop = False
    #             else:
    #                 is_loop = False

    #         if k > i:
    #             phrase = ' '.join([answer[j]['W'] for j in range(i, k+1)])
    #             candidates_dict = {'W': phrase, 'POS': answer[i]['POS'], 'NE': answer[i]['NE'][2:]}
    #         else:
    #             candidates_dict = answer[i].copy()
    #             candidates_dict['NE'] = candidates_dict['NE'][2:]
            
    #         new_answer.append(candidates_dict)
    #     return new_answer

    # def extract_noun(self, text):
    #     pos_tag = nltk.pos_tag(nltk.word_tokenize(text))
    #     return list(set([word for (word, pos) in pos_tag if pos[0] == 'N' and len(word) > 3]))

    def extract_named_entity(self, text):
        ne_list = helper.ner(text)
        data = {}
        skip_index = []
        total = len(ne_list)
        for i in range(total):
            if ne_list[i][0] == 'O':
                continue
            if i in skip_index:
                continue

            # Looking for continuous words with same NE tag
            is_loop = True
            k = i
            while is_loop:
                if total > k + 1:
                    if ne_list[i][0][2:] == ne_list[k + 1][0][2:]:
                        k = k + 1
                        skip_index.append(k)
                    else:
                        is_loop = False
                else:
                    is_loop = False

            if k > i:
                phrase = ' '.join([ne_list[j][1] for j in range(i, k+1)])
            else:
                phrase = ne_list[i][1]

            if not phrase.isalpha() or len(phrase) < 3:
                continue
            
            if ne_list[i][0][2:] in data.keys():
                if phrase not in data[ne_list[i][0][2:]]:
                    data[ne_list[i][0][2:]].append(phrase)
            else:
                data[ne_list[i][0][2:]] = [phrase]

        # print(data)
        return data

    def get_ramdom_words(self, word_list:list, used_words=[], n=3):
        # Get 3 ramdom answer words from word_list
        data = []
        for i in range(n):
            if i >= len(word_list):
                break
            k = 0
            is_loop = True
            while is_loop:
                if k > 100: break
                tmp_noun = random.choice(word_list)
                k = k + 1
                if tmp_noun not in used_words:
                    data.append(tmp_noun)
                    used_words.append(tmp_noun)
                    is_loop = False
        return data
    
    def get_synonyms_antonyms(self, word):
        synonyms = [] 
        antonyms = [] 
        hypernyms = []
        # hyponyms = []
        pos = word['POS']
        word = word['W']
        for syn in wn.synsets(word):
            # print(syn)
            # print(syn.lemmas())
            if syn.lemmas()[0].name() != word:
                synonyms.append(syn.lemmas()[0].name())
            for lemma in syn.lemmas():
                # synonyms.append(lemma.name().replace('_', ' ')) # more synonyms
                if lemma.antonyms() and lemma.antonyms()[0].name() != word:
                    antonyms.append(lemma.antonyms()[0].name())
            for hypernym in syn.hypernyms():
                hypernyms.append(hypernym.name().split('.')[0])
            # for hyponym in syn.hyponyms():
            #     hyponyms.append(hyponym.name().split('.')[0].replace('_', ' '))
        synonyms = list(set(synonyms))
        antonyms = list(set(antonyms))
        hypernyms = list(set(hypernyms))
        # print('Synonyms:')
        # print(synonyms)
        # print('Antonyms:')
        # print(antonyms)
        # print('Hypernyms:')
        # print(hypernyms)
        # print('Hyponyms:')
        # print(hyponyms)
        synonyms_t = []
        antonyms_t = []
        hypernyms_t = []
        for w in synonyms:
            wup = self.get_WUP_similarity(word, w)
            w2v = self.get_word2vec_similarity(word.replace('_', '-'), w, wup)
            edscore = self.get_edit_distance_score(word, w)
            synonyms_t.append((w.replace('_', ' '), w2v, wup, edscore))
        for w in antonyms:
            wup = self.get_WUP_similarity(word, w)
            w2v = self.get_word2vec_similarity(word.replace('_', '-'), w, wup)
            edscore = self.get_edit_distance_score(word, w)
            antonyms_t.append((w.replace('_', ' '), w2v, wup, edscore))
        for w in hypernyms:
            wup = self.get_WUP_similarity(word, w)
            w2v = self.get_word2vec_similarity(word.replace('_', '-'), w, wup)
            edscore = self.get_edit_distance_score(word, w)
            hypernyms_t.append((w.replace('_', ' '), w2v, wup, edscore))
        # print('Synonyms:')
        # print(synonyms_t)
        # print('Antonyms:')
        # print(antonyms_t)
        # print('Hypernyms:')
        # print(hypernyms_t)
        # print('Hyponyms:')
        # print(hyponyms)
        synonyms_t = self.word_filter(word, pos, synonyms_t)
        antonyms_t = self.word_filter(word, pos, antonyms_t)
        hypernyms_t = self.word_filter(word, pos, hypernyms_t)
        # hyponyms = self.word_filter(word, pos, list(set(hyponyms)))

        return synonyms_t, antonyms_t, hypernyms_t
    
    def get_most_similar_words(self, word, argu='positive', n=100):
        pos = word['POS']
        word = word['W']
        # argu = 'positive' or 'negative'
        word2vec_api = config.word2vec_api + 'most_similar'
        params = {argu: word, 'topn': n}
        try:
            response = requests.get(word2vec_api, params=params)
        except Exception as e:
            # raise e
            return []
        data = []
        if response.status_code == 200:
            responsejson = response.json()
            if responsejson != None:
                # j = 0
                for i in range(len(responsejson)):
                    if responsejson[i][1] > 0.9 or responsejson[i][1] < 0.6:
                        continue
                    wup = self.get_WUP_similarity(word, responsejson[i][0])
                    edscore = self.get_edit_distance_score(word, responsejson[i][0])
                    data.append((responsejson[i][0], responsejson[i][1], wup, edscore))
            else:
                if config.debug:
                    print('Ignored candidate word2vec ', word)
                    print('responsejson is empty')

        return self.word_filter(word, pos, data)

    def get_WUP_similarity(self, word1, word2):
        # w1 = wn.synsets('stories')[0]
        # w2 = wn.synsets('news')[0]
        # print(w1.wup_similarity(w2))
        w1 = wn.synsets(word1)
        w2 = wn.synsets(word2)
        if len(w1) > 0 and len(w2) > 0:
            score = w1[0].wup_similarity(w2[0])
            if score:
                return score
        return 0.1

    def get_word2vec_similarity(self, word1, word2, default_score=0.1):
        word2vec_api = config.word2vec_api + 'similarity'
        params = {'w1': word1, 'w2': word2}
        try:
            response = requests.get(word2vec_api, params=params)
        except Exception as e:
            # raise e
            return default_score

        if response.status_code == 200:
            responsejson = response.json()
            if responsejson != None:
                return float(responsejson)

        return default_score

    def get_edit_distance_score(self, word1, word2):
        return 1 - 1 / (1 + math.exp(edit_distance(word1, word2)))

    def word_filter(self, word, pos, word_list):
        # words filter
        new_word_list = []
        for w in word_list:
            # remove phrase
            if '-' in w[0]:
                continue
            if ' ' in w[0]:
                continue
            # contained
            if word.lower() in w[0].lower():
                continue
            max_len = len(word) if len(word) > len(w[0]) else len(w[0])
            if word.lower()[:max_len-3] == w[0].lower()[:max_len-3]:
                continue
            if edit_distance(word.lower(), w[0].lower()) < 2:
                continue
            # remove both pos of word are different
            # is_append = True
            # for syn in wn.synsets(w[0]):
            #     if syn.name().split('.')[0] == w[0]:
            #         is_append = False
            #     if syn.pos() != pos[0].lower():
            #         is_append = False
            is_append = False
            for syn in wn.synsets(w[0]):
                if syn.name().split('.')[0] != w[0] and syn.pos() == pos[0].lower():
                    is_append = True
            if is_append:
                new_word_list.append(w)
        return new_word_list

    def ranking(self, candidates_dict, antonym_candidates_list=[]):
        data = {}
        for k, v in candidates_dict.items():
            # Remove duplicate
            tmp_list = []
            tmp_tup = []
            for t in v:
                if t[0] in tmp_list:
                    continue
                # if t[0] == k:
                #     continue
                tmp_list.append(t[0])
                if t[0] in antonym_candidates_list:
                    ranking_score = (t[1]  + t[2] + t[3]) / 3
                else:
                    ranking_score = (t[1] + t[2] + t[3]) / 3
                tmp_tup.append((t[0], t[1], t[2], t[3], ranking_score))
            # Sorting
            data[k] = sorted(tmp_tup, key = lambda x: x[4], reverse=True)
        return data



