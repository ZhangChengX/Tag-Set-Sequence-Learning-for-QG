# coding: utf-8

from allennlp.predictors.predictor import Predictor
# import allennlp_models.syntax.srl
# from collections import OrderedDict
import config
import re


class SemanticRoleLabeling(object):

    predictor = None

    def __init__(self):
        self.predictor = Predictor.from_path(archive_path=config.SRL_model)

    def predict(self, sentence):
        raw_dict = self.predictor.predict(sentence)

        # import pprint
        # pprint.pprint(raw_dict)

        labels = []
        pattern = r'\[.[^\[\]]*: .[^\[\]]*\]'
        for verb_item in raw_dict['verbs']:
            description = verb_item['description']
            items = re.findall(pattern, description)

            # od = OrderedDict()
            label = []
            for item in items:
                l = item[1:-1].split(': ')
                # od[l[0]] = l[1]
                label.append((l[0], l[1]))

            # labels.append(od)
            labels.append(label)
            
        # print(labels)
        return labels

