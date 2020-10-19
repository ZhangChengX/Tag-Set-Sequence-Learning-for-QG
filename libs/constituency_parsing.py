# coding: utf-8


from allennlp.predictors.predictor import Predictor
import allennlp_models.structured_prediction
import config


class ConstituencyParsing(object):

    predictor = None

    def __init__(self):
        self.predictor = Predictor.from_path(config.CP_model)

    def predict(self, sentence):
        raw_dict = self.predictor.predict(sentence)
        # print(raw_dict)
        # from nltk.tree import Tree
        # return Tree.fromstring(raw_dict['trees'])
        return raw_dict['trees']

