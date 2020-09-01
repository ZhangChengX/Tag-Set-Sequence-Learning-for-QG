#!/usr/bin/env python
# coding: utf-8

import os

root_path = os.getcwd() + '/'
SRL_model = root_path + 'models/bert-base-srl-2020.03.24.tar.gz'
NER_model = root_path + 'models/ner-model-2020.02.10.tar.gz'
DP_model = root_path + 'models/biaffine-dependency-parser-ptb-2020.04.06.tar.gz'
CP_model = root_path + 'models/elmo-constituency-parser-2020.02.10.tar.gz'
CR_model = root_path + 'models/coref-model-2020.02.10.tar.gz'
rules_path = root_path + 'rules/'
word2vec_api = 'http://127.0.0.1:8080/w2v/'
rule_based = False
matching_fuzzy = 0
debug = True
dev_mode = True
port = 10081
