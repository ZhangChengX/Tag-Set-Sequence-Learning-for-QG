#!/usr/bin/env python
# coding: utf-8

from libs.semantic_role_labeling import SemanticRoleLabeling
from libs.named_entity_recognition import NamedEntityRecognition
from libs.pos_tagging import get_pos_tags
import config
import helper
import rules


class QuestionGeneration:

    ner = None
    srl = None

    def __init__(self):
        pass
        self.ner = NamedEntityRecognition()
        self.srl = SemanticRoleLabeling()

    def generate(self, text):
        rst = []
        # split sentences
        sentences = helper.segment_by_sentence(text)
        for sentence in sentences:
            rst.append(self.pipeline(sentence))
        # TODO question filter
        return rst

    def pipeline(self, sentence):
        # Simplify the complex sentences

        # Preprocess
        # didn't -> did not, haven't -> have not, can't -> can not
        if "can't" in sentence:
            sentence = sentence.replace("'t", ' not', )
        sentence = sentence.replace("n't", ' not', )

        # Pos tag
        pos_tags = get_pos_tags(sentence)

        # Named Entity Information
        ne_tags = self.ner.predict(sentence)

        # Semantic Role Labeling
        labels = self.srl.predict(sentence)
        labels = helper.preprocess_labels(labels, pos_tags)

        # if config.debug:
        #     print('pos_tags = ' + str(pos_tags))
        #     print('ne_tags = ' + str(ne_tags))
        #     print('labels = ' + str(labels))
        #     print(sentence)
        
        # pos_tags = [('Tom', 'NNP'), ('has', 'VBZ'), ('been', 'VBN'), ('in', 'IN'), ('Boston', 'NNP'), ('.', '.')]
        # ne_tags = [('U-PER', 'Tom'), ('O', 'has'), ('O', 'been'), ('O', 'in'), ('U-LOC', 'Boston'), ('O', '.')]
        # labels = [{'V': 'has'}, {'ARG1': 'Tom', 'V': 'been', 'ARG2': 'in Boston'}]

        question_list = []
        for label in labels:
            question_list.append(rules.who(label, ne_tags, pos_tags))
            # question_list.append(rules.what(label, ne_tags, pos_tags))
            # question_list.append(rules.where(label, ne_tags))
            # question_list.append(rules.why(label, ne_tags))
            # question_list.append(rules.when(label, ne_tags))
            # question_list.append(rules.how(label, ne_tags))
            # question_list.append(rules.arg1_is_argx(label, ne_tags))
            # question_list.append(rules.arg1_is_arg2(label, ne_tags))
        # remove empty []
        return [x for x in question_list if x]


if __name__ == "__main__":
    qg = QuestionGeneration()
    while True:
        text = input('\nType in a sentence: \n')
        if text == 'exit' or text == 'q':
            exit()
        if text == '':
            continue
        questions_list = qg.pipeline(text)
        print('')
        print(questions_list)

    