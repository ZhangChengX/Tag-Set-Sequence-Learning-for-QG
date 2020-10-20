#!/usr/bin/env python
# coding: utf-8

from preprocess import Preprocess
from question_generation import QuestionGeneration
from flask import Flask, jsonify, request
import config
# import json

app = Flask(__name__)
p = Preprocess()
qg = QuestionGeneration()

@app.route('/')
def index():
    data = ['Usage: ',\
            'http://localhost:10081/generate?text=Any%20sentence',\
            'http://localhost:10081/pipeline?sentence=Any%20sentence',\
            'http://localhost:10081/preprocess?sentence=Any%20sentence',\
            'http://localhost:10081/preprocess_learning?sentence=',\
            'http://localhost:10081/learn?sentence=',\
            '/srl?sentence=',\
            '/pos?sentence=',\
            '/ner?sentence=',\
            '/ctree?sentence=',\
            '/dtree?sentence=',\
            '/filling_up_qg?sentence='
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

@app.route('/learn')
def learn():
    sentence = request.args.get('sentence')
    data = qg.learn_rule(sentence)
    return jsonify(data)

@app.route('/pipeline')
def pipeline():
    sentence = request.args.get('sentence')
    data = qg.pipeline(sentence)
    return jsonify(data)

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    text = request.args.get('text')
    if not text:
        text = request.form['text']
    data = qg.generate(text)
    return jsonify(data)

@app.route('/filling_up_qg')
def fillingupqg():
    sentence = request.args.get('sentence')
    data = qg.generate_filling_in_question(sentence)
    return jsonify(data)

@app.route('/load_rules_remotely')
def load_rules_remotely():
    qg.load_rules()
    return jsonify('Success')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=config.port, debug=config.debug)
