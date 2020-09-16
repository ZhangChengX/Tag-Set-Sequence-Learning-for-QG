# coding: utf-8


from allennlp.predictors.predictor import Predictor
import allennlp_models.structured_prediction
import config


class DependencyParsing(object):

    predictor = None

    def __init__(self):
        self.predictor = Predictor.from_path(config.DP_model)

    def predict(self, sentence):
        raw_dict = self.predictor.predict(sentence)
        # print(raw_dict)
        return raw_dict['hierplane_tree']
