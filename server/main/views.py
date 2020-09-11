import calendar
import datetime
import json
import os
import random
import sys
import time
from pathlib import Path

from flask import (current_app, jsonify, redirect, render_template, request,
                   send_from_directory, session, url_for)
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

import server.tasks.batch as batch
from server import cache
from server.db import UserFileSystem
from server.db.user import *
from server.main import main

DB = Database("data/data.db")

# here it should be parents[2]
up_one = Path(__file__).parents[2]
# print(up_one)
folder = up_one / 'web_app' / 'src'


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/login')
def login_alt():
    return redirect(url_for('auth.login'))


@main.route('/signup')
def signup_alt():
    return redirect(url_for('auth.new_user'))


# TODO
# https://stackoverflow.com/a/51013358/8608146

@main.route('/files')
@jwt_required
def all_files():
    items = []
    for i in Path(current_app.config['UPLOAD_FOLDER']).iterdir():
        path = str(i)
        items.append({
            'date': i.split('.')[0][4:],
            'size': os.stat(path).st_size,
            'id': i
        })
    return render_template("files.html", items=items)  # , as_attachment=True)


@main.route('/logout')
def logout():
    return redirect('/')


@main.route('/dashboard')
def dashboard_home():
    # print('x' not in cache)
    running = cache.get('running_zip_tasks')
    print(running)

    session['x'] = (0, 1, 2, 3)
    print(session['x'])
    users = DB.get_users()
    for x in users:
        audiofiles = UserFileSystem(x['username']).get_audio_files()
        x['count'] = len(audiofiles)
    newlist = sorted(users, key=lambda k: k['count'], reverse=True)
    return render_template('dashboard.html', users=newlist)

@main.route('/settings', methods=['GET', 'POST'])
def dashboard_settings():
    if request.method == 'GET':
        datasets = []
        for file in (up_one / 'corpora' / 'uploads').iterdir():
            if file.is_file():
                datasets.append({'name': str(file.name), 'current': False})
        datasets[0]['current'] = True

        return render_template('settings.html', datasets=datasets)
    else:
        print(request.form)
        if 'file' not in request.files:
            # return redirect(request.url)
            return jsonify({'status': 'failed', 'msg': 'No file uploaded try again'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'failed', 'msg': 'No file selected for uploading'})
        if file and allowed_settings_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = up_one / 'corpora' / 'uploads' / filename
            try:
                os.makedirs(filepath.parents[0])
            except Exception as e:
                print(e)

            file.save(filepath)
            size = os.stat(filepath).st_size
            return jsonify({
                'status': 'ok',
                'msg': None, 'path': filename, 'size': size
            })
        else:
            return jsonify({
                'status': 'failed',
                'msg': f'invalid file type {file.filename} ' + 'only ' + ", ".join(ALLOWED_SETTINGS_EXTENSIONS) + ' file types are allowed'
                }), 403


def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False


@main.route('/_cache')
def export_cache():
    k_prefix = cache.cache.key_prefix
    keys = cache.cache._write_client.keys(k_prefix + '*')
    keys = [k.decode('utf8') for k in keys]
    keys = [k.replace(k_prefix, '') for k in keys]
    values = cache.get_many(*keys)
    ret = {}
    for k, v in zip(keys, values):
        if is_jsonable(v):
            ret[k] = v
    return jsonify(ret)


@main.route('/users')
def users_home():
    users = DB.get_users()
    for x in users:
        audiofiles = UserFileSystem(x['username']).get_audio_files()
        x['count'] = len(audiofiles)
    newlist = sorted(users, key=lambda k: k['count'], reverse=True)
    return render_template('users.html', users=newlist)


@main.route('/user/<string:username>')
def user_page(username: str):
    userinfo = DB.get_user(username)
    sens = UserFileSystem(username).get_sentences()
    return render_template('user.html', user=userinfo, sentences=sens)


@main.route('/search', methods=['POST'])
def search():
    print(request.json)

    return jsonify({})


@main.route('/userfile/<string:filename>')
def user_file(filename: str):
    # filename is username_sid.wav
    # username can be x_yayya_xx
    username = "_".join(filename.split('_')[:-1])
    dirname = (up_one / 'data')
    print("User name is ", username, secure_filename(username))
    for d in dirname.iterdir():
        d = os.path.basename(d)
        safeusername = secure_filename(str(d))
        if safeusername == username:
            print(safeusername)
            dirname = (up_one / 'data' / d)
            break
    return send_from_directory(str(dirname), filename)


@main.route('/upload', methods=['POST'])
@jwt_required
def upload_file():
    # TODO in the app when logged out
    # 401 code is sent so this method is not called
    # Show failed message
    # user = (User(session['user'][0]).attach_DB(DB))
    print(session['user'])  # tuple (username, age, gender)
    print("-"*(200))
    sys.stdout.flush()

    if request.method == 'POST':
        # check if the post request has the file part
        # print(request)
        if 'file' not in request.files:
            # return redirect(request.url)
            return jsonify({'status': 'failed', 'msg': 'No file uploaded try again'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'failed', 'msg': 'No file selected for uploading'})
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = Path(current_app.config['UPLOAD_FOLDER']
                            ) / session['user'][0] / filename
            try:
                os.makedirs(filepath.parents[0])
            except Exception as e:
                print(e)

            file.save(filepath)
            size = os.stat(filepath).st_size
            return jsonify({
                'status': 'ok',
                'msg': None, 'path': filename, 'size': size
            })
        else:
            return jsonify({'status': 'failed', 'msg': f'invalid file type {file.filename}'})


@main.route('/data')
@jwt_required
def random_corpa():
    # print("Data bros")
    # print(session['user'])
    data_dir: Path = up_one / 'corpora' / 'split'
    x = 0
    for filename in data_dir.iterdir():
        if filename.is_file():
            x += 1
    return send_from_directory(
        str(data_dir),
        "out{}.txt".format(random.randint(1, x))
    )


@main.route('/skipped', methods=['POST'])
@jwt_required
def handle_skip():

    sentence_ids = request.json['ids']
    username = session['user'][0]

    with open('corpora/split/skipped.txt', 'a+') as skipper:
        for sentence_id in sentence_ids:
            skipper.write(f"{sentence_id}||{username}\n")

    return 'ok', 200


@main.route('/files/<path:filename>', methods=['GET', 'DELETE', 'PUT'])
@jwt_required
def download_file(filename):
    print(session['user'])
    if request.method == 'GET':
        print("accessing file: " + filename, time.asctime())
        print((request.headers))
        return send_from_directory(current_app.config['UPLOAD_FOLDER'],
                                   filename)  # , as_attachment=True)
    elif request.method == 'DELETE':
        # TODO
        # check if client has the ownership
        print("Delete", filename)
        try:
            os.remove(os.path.join(
                current_app.config['UPLOAD_FOLDER'], filename))
        except FileNotFoundError as e:
            return jsonify({'status': 'failed', 'msg': str(e)})
        return jsonify({'status': 'ok'})
    elif request.method == 'PUT':
        # https://pythonise.com/series/learning-flask/flask-http-methods
        return jsonify({'status': 'ok'})


# file upload
ALLOWED_EXTENSIONS = set(['wav', 'mp3', 'ogg', 'webm', 'aac'])

# Settings dashboard file upload
ALLOWED_SETTINGS_EXTENSIONS = set(['txt', 'csv'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_settings_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_SETTINGS_EXTENSIONS
