import calendar
import datetime
import json
import os
import random
import shutil
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

@main.route('/manage/del', methods=['DELETE'])
def dashboard_settings_del_lang():
    langname = request.json['langcode']
    print(f"Warning: {langname} is scheduled for a deletion")
    dirpath = up_one / 'corpora' / 'uploads' / langname
    dest = up_one / 'corpora' / 'trash'
    try:
        os.makedirs(dest)
    except Exception as e:
        print(e)
    shutil.move(str(dirpath), str(dest))
    return jsonify({'success': True, 'error': None})


@main.route('/manage/add', methods=['POST'])
def dashboard_settings_add_lang():
    langname = request.json['langname']
    langs = request.json['langs']
    langtype = request.json['type']
    if not langname or not langs:
        return jsonify({'success': False, 'error': 'Values cannot be empty please try again'}), 403

    langs = [x.strip() for x in langs.split(',')]
    if len(langs) < 1:
        return jsonify({'success': False, 'error': 'Select single if need to have only one language, or a comma is missing please try again'}), 403

    # TODO do something with the langname

    dirname = "-".join(['mix', *langs])
    dirpath = up_one / 'corpora' / 'uploads' / dirname
    try:
        os.makedirs(dirpath)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 403
    print(langname, langs, dirname)
    return jsonify({'success': True})


@main.route('/manage/upload', methods=['POST'])
def dashboard_settings_upload():
    langcode = (request.form['langcode'])
    if not langcode:
        return jsonify({
            'status': 'failed',
            'msg': 'no langcode was specified'
        }), 403
    if 'file' not in request.files:
        # return redirect(request.url)
        return jsonify({'status': 'failed', 'msg': 'No file uploaded try again'}), 404
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'failed', 'msg': 'No file selected for uploading'}), 404
    if file and allowed_settings_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = up_one / 'corpora' / 'uploads' / langcode / filename

        try:
            os.makedirs(filepath.parents[0])
        except Exception as e:
            print(e)

        file.save(filepath)
        size = os.stat(filepath).st_size
        # TODO shedule celery task to split new uploaded dataset

        print(filepath.absolute(), type(filepath.absolute()))

        task = batch.split_corpora.delay(
            file_path=str(filepath.absolute()),
            split_path=f'split-{langcode}'
        )
        return jsonify({
            'status': 'ok',
            'msg': None,
            'path': filename,
            'size': size,
            'taskid': task.id
        })
    else:
        return jsonify({
            'status': 'failed',
            'msg': f'invalid file type {file.filename} ' + 'only ' + ", ".join(ALLOWED_SETTINGS_EXTENSIONS) + ' file types are allowed'
        }), 403


@main.route('/manage', methods=['GET', 'POST'])
def dashboard_settings():
    if request.method == 'GET':
        dataset_types = []
        # dataset_types = ['eng', 'hin', 'tel', 'mix-hin-tel']
        for dire in (up_one / 'corpora' / 'uploads').iterdir():
            if dire.is_dir():
                dataset_types.append(dire.name)

        collections = []
        # TODO store in cache
        config_data = {}
        with open('config.json', 'r') as config:
            config_data = json.load(config)

        print(config_data)

        for dt in dataset_types:
            datasets = []
            selected_index = 0
            index = 0
            for file in (up_one / 'corpora' / 'uploads' / dt).iterdir():
                if file.is_file():
                    new_file = file.stat().st_ctime
                    selected = False
                    if dt in config_data['categories'] and config_data['categories'][dt]:
                        current = config_data['categories'][dt]['current']
                        if current:
                            current = current.strip()
                            if current == str(file.name):
                                selected = True
                                selected_index = index
                    datasets.append(
                        {
                            'name': str(file.name),
                            'current': selected,
                            'new': new_file
                        })
                    index += 1

            collections.append({'dset': datasets, 'type': dt})

        return render_template('settings.html', collections=collections, types=",".join(dataset_types))
    else:
        try:
            selected = request.json['selected']
            langcode = request.json['langcode']
        except:
            return jsonify({
                'success': False,
                'error': 'One of selected and langcode was not provided'
            }), 403
        config_data = {}
        with open('config.json', 'r') as config:
            config_data = json.load(config)

        if 'categories' not in config_data:
            config_data['categories'] = {}

        for k in config_data['categories'].keys():
            config_data['categories'][k]['current'] = None

        config_data['categories'][langcode] = {
            'current': selected
        }

        with open('config.json', 'w+') as config:
            json.dump(config_data, config)

        print(config_data, selected, langcode)

        return jsonify({'success': True})


@main.route('/manage/<string:langcat>', methods=['GET', 'POST'])
def dashboard_settings_lang(langcat: str):
    # TODO check if a valid lang category
    if request.method == 'GET':
        config_data = {}
        with open('config.json', 'r') as config:
            config_data = json.load(config)

        datasets = []
        default_index = None
        selected_index = default_index
        index = 0
        for file in (up_one / 'corpora' / 'uploads' / langcat).iterdir():
            if file.is_file():
                selected = False
                if langcat in config_data['categories'] and config_data['categories'][langcat]:
                    current = config_data['categories'][langcat]['current']
                    if current:
                        current = current.strip()
                        if current == str(file.name):
                            selected = True
                            selected_index = index
                index += 1
                datasets.append({'name': str(file.name), 'current': selected})

        selected = None
        if len(datasets) > 0 and selected_index is not None:
            selected = datasets[selected_index]
            selected['index'] = selected_index

        print(datasets)
        print(selected)
        return render_template(
            'lang-settings.html',
            datasets=datasets,
            langcode=langcat,
            selected=selected
        )
    else:
        langcode = langcat
        if 'file' not in request.files:
            # return redirect(request.url)
            return jsonify({'status': 'failed', 'msg': 'No file uploaded try again'}), 404
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'failed', 'msg': 'No file selected for uploading'}), 404
        if file and allowed_settings_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = up_one / 'corpora' / 'uploads' / langcode / filename

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


@main.route('/_cache/clear')
def clear_cache():
    cache.clear()
    return jsonify(read_cache())


# TODO cahce experimentaion
# Use cache to cache file results (?)
@main.route('/_cache', methods=['GET', 'POST'])
def export_cache():
    if request.method == 'GET':
        return jsonify(read_cache())
    else:
        try:
            print('try')
            session['x']
        except:
            print('except')
            session['x'] = {}
        cache.set('time', datetime.datetime.now())
        cache.set(f'time-{random.randint(1, 100000)}', datetime.datetime.now())
        cache_dat = read_cache()
        ret = {}
        print(session['x'], cache_dat)
        if (len(session['x'].keys()) > len(cache_dat.keys())):
            ret['changes'] = {'x': session['x'], 'new': cache_dat}

        session['x'] = cache_dat
        ret['cache'] = cache_dat
        ret['x'] = session['x']
        return jsonify(ret)


def read_cache():
    k_prefix = cache.cache.key_prefix
    keys = cache.cache._write_client.keys(k_prefix + '*')
    keys = [k.decode('utf8') for k in keys]
    keys = [k.replace(k_prefix, '') for k in keys]
    values = cache.get_many(*keys)
    ret = {}
    for k, v in zip(keys, values):
        if is_jsonable(v):
            ret[k] = v
        else:
            ret[k] = str(v)
    return ret


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
