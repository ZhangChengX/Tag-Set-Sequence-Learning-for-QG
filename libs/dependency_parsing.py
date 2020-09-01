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
        print(raw_dict)
        # return raw_dict
        tags = list(zip(raw_dict['words'], raw_dict['pos'], raw_dict['predicted_dependencies'], raw_dict['predicted_heads']))
        print(tags)
        # raw_dict['words']
        # raw_dict['pos']
        tags = list(zip(raw_dict['words'], raw_dict['pos']))
        return tags