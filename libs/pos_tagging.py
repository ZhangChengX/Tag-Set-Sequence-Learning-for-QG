# coding: utf-8

from nltk import word_tokenize, pos_tag


class PosTagging(object):

    # predictor = None

    # def __init__(self):
    #     pass

    def predict(self, sentence):
        tokens = word_tokenize(sentence)
        return pos_tag(tokens)

