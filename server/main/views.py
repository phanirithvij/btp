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
from server.db.user import *
from server.main import main

TEMP_DIR = '/tmp/storage'
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
    return redirect('/auth/login')


@main.route('/signup')
def signup_alt():
    return redirect('/auth/new')


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
    cache.set('pokepoke', {'s': [1, 2, 3, 4, 4, 5], "sx": list(range(100))})
    print(cache.__dir__(), cache.get('pokepoke'))
    return redirect('/')


@main.route('/dashboard')
def dashboard_home():
    # print('x' not in cache)
    if 'running_tasks' not in session:
        session['running_tasks'] = {}

    session['x'] = (0, 1, 2, 3)
    print(session['x'])
    users = []
    for i in range(108):
        users.append({'name': f"user{i}", 'count': (100 - i) * 10})
    return render_template('dashboard.html', users=users)


@main.route('/_cache')
def export_cache():
    ret = {}
    for k, v in cache.get_many('pokepoke'):
        ret[k] = v
    return jsonify(ret)


@main.route('/users')
def users_home():
    users = []
    for i in range(108):
        users.append({'name': f"user{i}", 'count': (100 - i) * 10})
    return render_template('users.html', users=users)

# TODO in the app when logged out
# 401 code is sent so this method is not called
# Show failed message


@main.route('/upload', methods=['POST'])
@jwt_required
def upload_file():

    # exit(-1)
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
    print("Data bros")
    print(session['user'])
    data_dir: Path = up_one / 'corpora' / 'split'
    x = 0
    for filename in data_dir.iterdir():
        if filename.is_file():
            x += 1
    return send_from_directory(
        str(data_dir),
        "out{}.txt".format(random.randint(1, x))
    )


@main.route('/exports', methods=['GET', 'POST'])
# TODO add @jwt admin
# @jwt_required
def exports_page():
    print('--'*100)
    if request.method == 'GET':
        exportfiles = {}
        for x in Path(TEMP_DIR).iterdir():
            print(x)
            name = os.path.basename(x)
            username = name.split('_')[0]
            if 'running_tasks' not in session:
                session['running_tasks'] = {}
            if username not in session['running_tasks']:
                exportfiles[username] = {
                    'file': name, 'size': os.stat(x).st_size}
        users = DB.get_users()
        for x in users:
            dirname = (up_one / 'data' / x['username'])
            audiofiles = []
            if dirname.is_dir():
                audiofiles = list(dirname.iterdir())
                audiofiles = [str(x) for x in audiofiles]
                print(audiofiles)
            x['count'] = len(audiofiles)
            if x['username'] not in exportfiles.keys():
                exportfiles[x['username']] = {'file': None, 'size': 0}
        return render_template('exports.html', files=exportfiles, users=users)
    else:
        print(request.args)
        print(request.form)
        user_id = request.json['userid']
        print(request.json)
        print(url_for('main.progress', _external=True))
        # Using this on linux so /tmp is the best
        # place to store files
        try:
            os.makedirs(TEMP_DIR)
        except Exception as e:
            print(str(e))

        username = request.json['username']
        # username = 'rhodio'

        task = batch.zip_files.delay(
            TEMP_DIR,
            str((up_one / 'data' / username).resolve()),
            # str((up_one / 'data' / 'taskmaster').resolve()),
            username,
            user_id,
            url_for('main.progress', _external=True),
        )
        return jsonify({'taskid': task.id})

socketio = None

# INTERNAL route
@main.route('/progress', methods=['POST'])
def progress():
    # for now progress gets update progress of all celery tasks
    # TODO need to forward this to any connected clients
    data = request.json
    print(data)
    userid = data['userid']
    # print(data)
    room = current_app.clients.get(userid)
    # print('room', room)
    # if ns and data:
    # must specify both namespace and room
    # room is for this single user
    global socketio
    if socketio is None:
        from server import socketio as socker
        socketio = socker
    socketio.emit('celerystatus', data,
                  room=room, namespace='/events')
    print(request.data)
    return 'ok'


@main.route('/export/<string:filename>')
def download_zipfile(filename: str):
    return send_from_directory(
        TEMP_DIR,
        filename,
        as_attachment=True,
        attachment_filename=filename.split("_")[0] + ".zip"
    )


@main.route('/info/<string:filename>')
def info_zipfile(filename: str):
    filepath = Path(TEMP_DIR) / filename
    err = "No such file {} found".format(filename)
    if filepath.is_file():
        err = None
    size = os.stat(filepath).st_size
    return jsonify({"error": err, "size": size})


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
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        except FileNotFoundError as e:
            return jsonify({'status': 'failed', 'msg': str(e)})
        return jsonify({'status': 'ok'})
    elif request.method == 'PUT':
        # https://pythonise.com/series/learning-flask/flask-http-methods
        return jsonify({'status': 'ok'})
