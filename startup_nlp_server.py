#!/usr/bin/env python
# coding: utf-8

from preprocess import Preprocess
from flask import Flask, jsonify, request
import config
# import json

app = Flask(__name__)
p = Preprocess()

@app.route('/')
def index():
    data = ['Usage: ',\
            'http://localhost:10080/generate?text=Any%20sentence',\
            'http://localhost:10080/pipeline?sentence=Any%20sentence',\
            'http://localhost:10080/preprocess?sentence=Any%20sentence',\
            '/preprocess_learning',\
            '/srl',\
            'pos',\
            'ner',\
            'ctree',\
            'gapqg'
            ]
    return jsonify(data)

@app.route('/srl')
def srl():
    sentence = request.args.get('sentence')
    data = p.srl(sentence)
    return jsonify(data)

@app.route('/pos')
def pos():
    sentence = request.args.get('sentence')
    data = p.pos(sentence)
    return jsonify(data)

@app.route('/ner')
def ner():
    sentence = request.args.get('sentence')
    data = p.ner(sentence)
    return jsonify(data)

@app.route('/ctree')
def ctree():
    sentence = request.args.get('sentence')
    data = p.ctree(sentence)
    return jsonify(data)

@app.route('/dtree')
def dtree():
    sentence = request.args.get('sentence')
    data = p.dtree(sentence)
    return jsonify(data)

@app.route('/preprocess')
def preprocess():
    sentence = request.args.get('sentence')
    data = p.preprocess(sentence)
    return jsonify(data)

@app.route('/preprocess_learning')
def preprocess_learning():
    sentence = request.args.get('sentence')
    data = p.preprocess_learning(sentence)
    return jsonify(data)

# @app.route('/pipeline')
# def pipeline():
#     sentence = request.args.get('sentence')
#     data = qg.pipeline(sentence)
#     return jsonify(data)

# @app.route('/generate')
# def generate():
#     text = request.args.get('text')
#     data = qg.generate(text)
#     return jsonify(data)

# @app.route('/gapqg')
# def gapqg():
#     return jsonify([])


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=config.port, debug=config.debug)
