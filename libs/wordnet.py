# coding: utf-8

from nltk.stem.wordnet import WordNetLemmatizer

class WordNet:

    wnl = None

    def __init__(self):
        self.wnl = WordNetLemmatizer()

    def get_base_verb(self, verb):
        return self.wnl.lemmatize(verb,'v')

