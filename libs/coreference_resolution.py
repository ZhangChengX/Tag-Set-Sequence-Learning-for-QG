# coding: utf-8

from allennlp.predictors.predictor import Predictor
import config

class CoreferenceResolution(object):

    predictor = None

    def __init__(self):
        self.predictor = Predictor.from_path(config.CR_model)

    def predict(self, text):
        raw_dict = self.predictor.predict(text)
        # print(raw_dict['clusters'])
        # for i, c in enumerate(raw_dict['document']):
        #     print(i, c)
        docu_list = raw_dict['document']
        for clusters in raw_dict['clusters']:
            entity = None
            if clusters[0][0] == clusters[0][1]:
                entity = [docu_list[clusters[0][0]]]
            else:
                entity = [docu_list[i] for i in clusters[0]]
            if entity:
                for clu in clusters:
                    if clu[0] == clu[1]:
                        docu_list[clu[0]] = ' '.join(entity)
        docu = ''
        for d in docu_list:
            # e.g.: a word, Co- reference
            if len(d) < 2 and d not in ['a', 'A', 'i', 'I'] or docu[-1:] == '-':
                docu = docu + d
            else:
                docu = docu + ' ' + d
        return docu