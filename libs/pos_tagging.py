# coding: utf-8

from nltk import word_tokenize, pos_tag


class PosTagging(object):

    # predictor = None

    # def __init__(self):
    #     self.predictor = Predictor.from_path(config.CP_model)

    def predict(self, sentence):
        tokens = word_tokenize(sentence)
        return pos_tag(tokens)


# def get_pos_tags(text):
#     tokens = word_tokenize(text)
#     return pos_tag(tokens)
