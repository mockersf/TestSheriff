from TestSheriff_flask import app

import os

from flask import Flask, send_from_directory, jsonify, request, abort


ui_root = '/ui'


@app.route(ui_root, methods=['GET'])
def ui_index():
    return send_file('index.html')

@app.route(ui_root + '/js/<path:filename>')
def sf_js(filename):
    return send_file(filename, 'js')

@app.route(ui_root + '/css/<path:filename>')
def sf_css(filename):
    return send_file(filename, 'css')

def send_file(filename, subfolder=None):
    rootdir = os.path.abspath(os.path.dirname(__file__))
    dir = os.path.join(rootdir, 'ui')
    if subfolder is not None:
        dir = os.path.join(dir, subfolder)
    return send_from_directory(dir, filename)
