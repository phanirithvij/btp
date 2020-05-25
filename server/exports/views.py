import json
import os
import random
import sys
import time
from pathlib import Path

from flask import (jsonify, render_template, request, send_from_directory,
                   url_for)
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

import server.tasks.batch as batch
from server import cache
from server.config import Config
from server.db.user import *
from server.db import UserFileSystem
from server.exports import exports
from server.main import main

DB = Database("data/data.db")

# here it should be parents[2]
up_one = Path(__file__).parents[2]
# print(up_one)
folder = up_one / 'web_app' / 'src'


@exports.route('', strict_slashes=False, methods=['GET', 'POST'])
# @exports.route('/', methods=['GET', 'POST'])
# TODO add @jwt admin
# @jwt_required
def exports_page():
    # print('--'*100)
    if request.method == 'GET':
        exportfiles = {}
        for x in Path(Config.TEMP_DIR).iterdir():
            # print(x)
            name = os.path.basename(x)
            username = name.split('_')[0]
            running = cache.get('running_zip_tasks')
            print("running", running)
            ongoing_export = True
            if running is not None:
                if username not in list([x['username'] for x in running.values()]):
                    ongoing_export = False
            else:
                ongoing_export = False
            if not ongoing_export:
                exportfiles[username] = {
                    'file': name, 'size': os.stat(x).st_size}

        users = DB.get_users()
        for x in users:
            audiofiles = UserFileSystem(x['username']).get_audio_files()
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

        task = batch.zip_files.delay(
            out_filepath=Config.TEMP_DIR,
            dir_name=str((up_one / 'data' / username).resolve()),
            username=username,
            user_id=user_id,
            update_url=url_for('exports.progress', _external=True),
        )
        return jsonify({'taskid': task.id})


@exports.route('/partial', methods=['GET', 'POST'])
def partial_export():
    if request.method == "POST":
        print(request.args)
        print(request.form)
        user_id = request.json['userid']
        print(request.json)
        print(url_for('exports.progress', _external=True))

        username = request.json['username']

        task = batch.zip_files_partial.delay(
            files=request.json['files'],
            username=username,
            user_id=user_id,
            update_url=url_for('exports.progress', _external=True),
        )
        return jsonify({'taskid': task.id})

    return render_template('partial.html')


socketio = None


# INTERNAL route
@exports.route('/_progress', methods=['POST'])
def progress():
    # for now progress gets update progress of all celery tasks
    # need to forward this to any connected clients
    data = request.json
    userid = data['userid']
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


@exports.route('/delete', methods=['POST'])
def delete_exports():
    print(request.args)
    print(request.form)
    user_id = request.json['userid']
    print(request.json)

    usernames = request.json['usernames']

    task = batch.delete_zips.delay(
        usernames=usernames,
        user_id=user_id,
        progress_url=url_for('exports.progress', _external=True)
    )
    return jsonify({'taskid': task.id})
