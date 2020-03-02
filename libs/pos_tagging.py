# coding: utf-8

from nltk import word_tokenize, pos_tag


def get_pos_tags(text):
    tokens = word_tokenize(text)
    return pos_tag(tokens)