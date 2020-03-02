#!/usr/bin/env python
# coding: utf-8

from question_generation import QuestionGeneration
from flask import Flask, jsonify, request
import config
import json

app = Flask(__name__)
qg = QuestionGeneration()

@app.route('/')
def index():
    data = ['Usage: ',\
            'http://localhost:10080/preprocess?sentence=Any%20sentence',\
            'http://localhost:10080/pipeline?sentence=Any%20sentence',\
            'http://localhost:10080/generate?text=Any%20sentence'
            ]
    return jsonify(data)

@app.route('/preprocess')
def preprocess():
    sentence = request.args.get('sentence')
    data = qg.preprocess(sentence)
    return jsonify(data)

@app.route('/pipeline')
def pipeline():
    sentence = request.args.get('sentence')
    data = qg.pipeline(sentence)
    return jsonify(data)

@app.route('/generate')
def generate():
    text = request.args.get('text')
    data = qg.generate(text)
    return jsonify(data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=config.port, debug=config.debug)
