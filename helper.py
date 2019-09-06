# coding: utf-8

import re
from nltk.data import load
from nltk.tokenize import sent_tokenize
from nltk.stem.wordnet import WordNetLemmatizer

# sentence_delimiters_en = ['?', '!', '...', '\n']

stop_list = ['a', 'by', 'in', 'the']

def remove_stop_word(word_list):
    return [w for w in word_list if w.lower() not in stop_list]

def strip_multi_space(text):
    return re.sub(' +', ' ', text)

def segment_by_sentence(text):
    tokenizer = load('tokenizers/punkt/{0}.pickle'.format('english'))
    sentences = []
    paragraphs = [p for p in text.split('\n') if p]
    for paragraph in paragraphs:
        sentences.extend(tokenizer.tokenize(paragraph))
    return sentences

def get_named_entity_by_word(word, tags):
    for tag in tags:
        if word == tag[1]:
            return tag[0]

def get_phrase_by_consecutive_tags(tag_key, tags):
    # Given tag_key = 'PER' and tags = [('B-PER', 'Barack'), ('L-PER', 'Obama'), ('O', 'is'), ('O', 'the'), ('O', 'president'), ('O', 'of'), ('O', 'The'), ('B-LOC', 'United'), ('I-LOC', 'States'), ('I-LOC', 'of'), ('L-LOC', 'America'), ('O', '.')]
    # Find Barack Obama
    phrase = ''
    consecutive = True
    for tag in tags:
        if not consecutive:
            break
        if tag_key == tag[0][2:]:
            phrase = phrase + tag[1] + ' '
            consecutive = True
        else:
            consecutive = False
    return phrase.rstrip()

def combine_verb(verb, tags):
    for i in range(len(tags)):
        if tags[i][1] == verb and tags[i-1][1] in ['am', 'is', 'are']:
            return tags[i-1][1], 'is ' + verb
    return '', verb

def get_base_verb(verb):
    # stemming verb
    # TODO single instance
    return WordNetLemmatizer().lemmatize(verb,'v')

def get_verb_tense(verb, pos_tags):
    # VBD past, VBN Past participle
    for tag in pos_tags:
        if tag[0] == verb:
            return tag[1] 

def lower_case_first_letter(labels):
    if labels[list(labels)[0]] != 'I':
        labels[list(labels)[0]] = labels[list(labels)[0]].lower()
    return labels


