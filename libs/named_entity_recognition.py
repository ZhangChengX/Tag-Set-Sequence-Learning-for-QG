#!/usr/bin/env python
# coding: utf-8


from allennlp.predictors.predictor import Predictor
import config


class NamedEntityRecognition(object):

    predictor = None

    def __init__(self):
        self.predictor = Predictor.from_path(config.NER_model)

    def predict(self, sentence):
        raw_dict = self.predictor.predict(sentence)
        tags = list(zip(raw_dict['tags'], raw_dict['words']))
        # tags = dict(zip(raw_dict['tags'], raw_dict['words']))
        # tags = {k: v for k, v in tags.items() if k != 'O'}
        return tags

