#!/usr/bin/env python
# coding: utf-8

import requests
import config


def preprocess(sentence):
    r = requests.get(url = 'http://localhost:' + str(config.port) + '/preprocess?sentence=' + sentence)
    return r.json()

def pipeline(sentence):
    r = requests.get(url = 'http://localhost:' + str(config.port) + '/pipeline?sentence=' + sentence)
    return r.json()

def loadrules():
    r = requests.get(url = 'http://localhost:' + str(config.port) + '/loadrules')
    return r.json()


if __name__ == "__main__":
    pass
