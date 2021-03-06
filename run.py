# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, url_for, redirect, session, jsonify

from app import app
from server.convert import convert
from server.gpu_api import *

app.config['JSON_AS_ASCII'] = False

@app.route('/')
def default():
    return render_template('index.html')

@app.route('/ppt', methods=['POST', 'GET'])
def ppt():
    if request.method == 'POST':
        mdeditorHtmlStr = request.form.to_dict()['html']
        result = convert(mdeditorHtmlStr)
        return jsonify(result)
        
    return render_template('ppt_index.html')


@app.route('/image1', methods=['POST', 'GET'])
def image1():
    if request.method == 'POST':
        inputName = request.form.to_dict()['fileName']
        downloadUrl = backRmvAPI(inputName)
        print(downloadUrl)
        return downloadUrl

    return render_template('img_backRmv_index.html')
    
@app.route('/image2', methods=['POST', 'GET'])
def image2():
    if request.method == 'POST':
        inputName = request.form.to_dict()['fileName']
        downloadUrl = supResolAPI(inputName)
        print(downloadUrl)
        return downloadUrl

    return render_template('img_supResol_index.html')
    
@app.route('/image3', methods=['POST', 'GET'])
def image3():
    if request.method == 'POST':
        inputName = request.form.to_dict()['fileName']
        downloadUrl = iconifyAPI(inputName)
        print(downloadUrl)
        return downloadUrl

    return render_template('img_iconify_index.html')

@app.route('/devinfo')
def devinfo():
    return render_template('devinfo_index.html')
@app.route('/licinfo')
def licinfo():
    return render_template('licinfo_index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
