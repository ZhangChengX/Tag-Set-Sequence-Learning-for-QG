# coding: utf-8


from allennlp.predictors.predictor import Predictor
import config


class DependencyParsing(object):

    predictor = None

    def __init__(self):
        self.predictor = Predictor.from_path(config.DP_model)

    def predict(self, sentence):
        raw_dict = self.predictor.predict(sentence)
        # raw_dict['words']
        # raw_dict['pos']
        tags = list(zip(raw_dict['words'], raw_dict['pos']))
        return tags