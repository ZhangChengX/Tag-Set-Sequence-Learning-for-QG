#!/usr/bin/env python
# coding: utf-8

import os

root_path = os.getcwd() + '/'
SRL_model = root_path + 'models/srl-model-2018.05.25.tar.gz'
NER_model = root_path + 'models/ner-model-2018.12.18.tar.gz'
DP_model = root_path + 'models/biaffine-dependency-parser-ptb-2018.08.23.tar.gz'
CR_model = root_path + 'models/coref-model-2020.02.10.tar.gz'
rules_path = root_path + 'rules/'
rule_based = False
matching_fuzzy = 0
debug = True
dev_mode = True
port = 10081
