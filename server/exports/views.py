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
from server.config import Config
from server.db.user import *
from server.exports import exports
from server.main import main

DB = Database("data/data.db")

# here it should be parents[2]
up_one = Path(__file__).parents[2]
# print(up_one)
folder = up_one / 'web_app' / 'src'


@exports.route('/', methods=['GET', 'POST'])
# TODO add @jwt admin
# @jwt_required
def exports_page():
    print('--'*100)
    if request.method == 'GET':
        exportfiles = {}
        for x in Path(Config.TEMP_DIR).iterdir():
            # print(x)
            name = os.path.basename(x)
            username = name.split('_')[0]
            running = cache.get('running_zip_tasks')
            print("running", running)
            export_this = False
            if running is not None:
                if username not in list([x['username'] for x in running.values()]):
                    export_this = True
            else:
                export_this = True
            if export_this:
                exportfiles[username] = {
                    'file': name, 'size': os.stat(x).st_size}

        users = DB.get_users()
        for x in users:
            dirname = (up_one / 'data' / x['username'])
            audiofiles = []
            if dirname.is_dir():
                audiofiles = list(dirname.iterdir())
                audiofiles = [str(x) for x in audiofiles]
                # print(audiofiles)
            x['count'] = len(audiofiles)
            if x['username'] not in exportfiles.keys():
                exportfiles[x['username']] = {'file': None, 'size': 0}
        newlist = sorted(users, key=lambda k: k['count'], reverse=True)
        return render_template('exports.html', files=exportfiles, users=newlist)
    else:
        print(request.args)
        print(request.form)
        user_id = request.json['userid']
        print(request.json)
        print(url_for('exports.progress', _external=True))

        username = request.json['username']
        # username = 'rhodio'

        task = batch.zip_files.delay(
            out_filepath=Config.TEMP_DIR,
            dir_name=str((up_one / 'data' / username).resolve()),
            username=username,
            user_id=user_id,
            update_url=url_for('exports.progress', _external=True),
            # str((up_one / 'data' / 'taskmaster').resolve()),
        )
        return jsonify({'taskid': task.id})


socketio = None

# INTERNAL route


@exports.route('/progress', methods=['POST'])
def progress():
    # for now progress gets update progress of all celery tasks
    # TODO need to forward this to any connected clients
    data = request.json
    print(data)
    userid = data['userid']
    # print(data)
    # room = cache.get('clients')[userid]
    # print('room', room)
    # if ns and data:
    # must specify both namespace and room
    # room is for this single user
    global socketio
    if socketio is None:
        from server import socketio as socker
        socketio = socker
    socketio.emit('celerystatus', data, namespace='/events')
    # socketio.emit('celerystatus', data,
    #               room=room, namespace='/events')
    print(request.data)
    return 'ok'


@exports.route('/export/<string:filename>')
def download_zipfile(filename: str):
    return send_from_directory(
        Config.TEMP_DIR,
        filename,
        as_attachment=True,
        attachment_filename=filename.split("_")[0] + ".zip"
    )


@exports.route('/info/<string:filename>')
def info_zipfile(filename: str):
    filepath = Path(Config.TEMP_DIR) / filename
    err = "No such file {} found".format(filename)
    if filepath.is_file():
        err = None
    size = os.stat(filepath).st_size
    return jsonify({"error": err, "size": size})
