#!/usr/bin/env python
# coding: utf-8

from gevent.pywsgi import WSGIServer
from startup_meta_qg_rur_server import app
import config

# pywsgi.MAX_REQUEST_LINE = 819200
http_server = WSGIServer(('0.0.0.0', config.port), app)
http_server.serve_forever()
