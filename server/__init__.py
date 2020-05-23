import datetime
import logging
import os
import random
import sys
import time
import uuid
from pathlib import Path

from celery import Celery
from flask import (Flask, current_app, jsonify, redirect, render_template,
                   request, send_file, send_from_directory, session, url_for)
from flask_jwt_extended import (JWTManager, create_access_token,
                                create_refresh_token, get_current_user,
                                get_jwt_identity, jwt_refresh_token_required,
                                jwt_required)
from flask_socketio import SocketIO, disconnect, emit, join_room, leave_room
from werkzeug.utils import secure_filename

import server.tasks.batch as batch
from server.config import Config
from server.db.schema.queries import FEMALE, MALE
from server.db.user import *
from server.tasks import celery

LOG_FILENAME = 'logs/mylogs.log'

# Set up a specific logger with our desired output level
my_logger = logging.getLogger('MyLogger')
my_logger.setLevel(logging.DEBUG)


handler = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=1024*6, backupCount=5)

my_logger.addHandler(handler)


# current directory is server/
# Set static folder to be ../web_app/src
up_one = Path(__file__).parents[1]
folder = up_one / 'web_app' / 'src'

TEMP_DIR = '/tmp/storage'

DB = Database("data/data.db")
jwt = JWTManager()
socketio = SocketIO()


def create_app():
    app = Flask(__name__, static_folder=str(folder), static_url_path='/static')
    app.config.from_object(Config)
    jwt.init_app(app)
    socketio.init_app(app)
    celery.conf.update(app.config)
    return app


app: Flask = create_app()
app.clients = {}
app.running_tasks = {}

# https://stackoverflow.com/a/53152394/8608146
# app.config.from_object(__name__)
# random key
# app.config['SECRET_KEY'] = 'FTYFUH@E^@%R%^#!V#HUFEDGVQGV'
app.secret_key = r'<çDÒ\x88\r/Ò\x9dµ\x90k!a|RÈ\x96#ÇÔ^1à'

# app.config['SESSION_TYPE'] = 'filesystem'
# Session(app)

# file upload
ALLOWED_EXTENSIONS = set(['wav', 'mp3', 'ogg', 'webm', 'aac'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# JWT methods


@jwt.user_loader_error_loader
def customized_error_handler(error):
    return jsonify({
        'message': error.description,
        'code': error.status_code
    }), error.status_code


# Socket io
@socketio.on('status', namespace='/events')
def events_message(message):
    emit('status', {'status': message['status']})


@socketio.on('disconnect request', namespace='/events')
def disconnect_request():
    emit('status', {'status': 'Disconnected!'})
    disconnect()


@socketio.on('connect', namespace='/events')
def events_connect():
    print(request.namespace)
    userid = str(uuid.uuid4())
    session['userid'] = userid
    # https://stackoverflow.com/questions/39423646/flask-socketio-emit-to-specific-user
    current_app.clients[userid] = request.sid
    join_room(request.sid, namespace='/events')
    emit('userid', {'userid': userid})
    emit('status', {'status': 'Connected user', 'userid': userid})


@socketio.on('disconnect', namespace='/events')
def events_disconnect():
    leave_room(current_app.clients[session['userid']], namespace='/events')
    del current_app.clients[session['userid']]
    print('Client %s disconnected' % session['userid'])


# Routes


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login_alt():
    return redirect('/auth/login')


@app.route('/signup')
def signup_alt():
    return redirect('/auth/new')


@app.route('/auth/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username: str = None
        password: str = None

        try:
            # TODO this needs to be removed soon
            # write js fecth call to request instead of form POST
            username = request.json['username']
            password = request.json['password']
        except:
            username = request.form['username']
            password = request.form['password']

        error = ''
        status = 'error'
        user, error = auth_handler(
            username,
            password
        )
        print('user', user)
        if error is None:
            error = ''
            status = 'ok'
            session['user'] = user.pickle_instance()
            print(session['user'])

        access_token = None
        refresh_token = None
        user_id = None
        username = None
        # https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
        code = 401
        if user is not None:
            expires = datetime.timedelta(hours=3)
            user_id = user.id
            username = user.username
            access_token = create_access_token(user_id, expires_delta=expires)
            refresh_token = create_refresh_token(user_id)
            code = 200

        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'status': status,
            'error': error,
            'userId': user_id,
            'name': username,
        }), code
    elif request.method == 'GET':
        return render_template('auth/login.html')


# TODO
# https://stackoverflow.com/a/51013358/8608146

@app.route('/files')
@jwt_required
def all_files():
    items = []
    for i in Path(app.config['UPLOAD_FOLDER']).iterdir():
        path = str(i)
        items.append({
            'date': i.split('.')[0][4:],
            'size': os.stat(path).st_size,
            'id': i
        })
    return render_template("files.html", items=items)  # , as_attachment=True)


@app.route('/logout')
def logout():
    return redirect('/')


@app.route('/dashboard')
def dashboard_home():
    users = []
    for i in range(108):
        users.append({'name': f"user{i}", 'count': (100 - i) * 10})
    return render_template('dashboard.html', users=users)


@app.route('/users')
def users_home():
    users = []
    for i in range(108):
        users.append({'name': f"user{i}", 'count': (100 - i) * 10})
    return render_template('users.html', users=users)


@app.route('/auth/new', methods=['GET', 'POST'])
def new_user():
    # TODO register
    if request.method == 'POST':

        _username: str = request.form.get('username')
        _password: str = request.form.get('password')

        # TODO remove this field from the form after we done with forntend
        # Or make this only feild only valid when accessed via email.
        # After master gives access to the user's account
        # So this feild will not exist in register form
        _admin: bool = request.form.get('admin') == 'yes'

        if _username is None:
            return jsonify({'error': 'Username was empty'}), 403

        _age: int = request.form.get('age')
        _gender: str = request.form.get('gender')
        _gender = MALE if _gender == 'm' else FEMALE
        user = User(_username, _age, _gender, _password)

        user.is_admin = _admin
        user.attach_DB(DB)
        success, err = user.save_to_db()

        print(success, err)

        status = 'error'
        # err = f'A user named {_username} exists'
        access_token = None
        refresh_token = None
        user_id = None
        if success:
            print("New user added", _username)
            # custom success status instead of 'ok'
            status = 'new'
            err = ''
            session['user'] = user.pickle_instance()
            user_id = _username
            access_token = create_access_token(user_id)
            refresh_token = create_refresh_token(user_id)

        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'status': status,
            'error': err,
            'userId': user_id,
            'name': _username
        })
    else:
        # Register page from web app
        # return "Web UI Not Implemented", 404
        return render_template('auth/signup.html')


@app.route('/refresh')
@jwt_refresh_token_required
def post(self):
    print("user", session['user'])
    current_user = session['user'][0]
    # return a non-fresh token for the user
    new_token = create_access_token(current_user)
    return {'access_token': new_token}, 200


@app.route('/files/<path:filename>', methods=['GET', 'DELETE', 'PUT'])
@jwt_required
def download_file(filename):
    print(session['user'])
    if request.method == 'GET':
        print("accessing file: " + filename, time.asctime())
        print((request.headers))
        return send_from_directory(app.config['UPLOAD_FOLDER'],
                                   filename)  # , as_attachment=True)
    elif request.method == 'DELETE':
        # TODO
        # check if client has the ownership
        print("Delete", filename)
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        except FileNotFoundError as e:
            return jsonify({'status': 'failed', 'msg': str(e)})
        return jsonify({'status': 'ok'})
    elif request.method == 'PUT':
        # https://pythonise.com/series/learning-flask/flask-http-methods
        return jsonify({'status': 'ok'})


# TODO in the app when logged out
# 401 code is sent so this method is not called
# Show failed message
@app.route('/upload', methods=['POST'])
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
            filepath = Path(app.config['UPLOAD_FOLDER']
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


@app.route('/data')
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


@app.route('/exports', methods=['GET', 'POST'])
# TODO add @jwt admin
# @jwt_required
def exports_page():
    if request.method == 'GET':
        exportfiles = {}
        for x in Path(TEMP_DIR).iterdir():
            name = os.path.basename(x)
            username = name.split('_')[0]
            print(app.running_tasks)
            if username not in app.running_tasks:
                exportfiles[username] = {'file': name, 'size': os.stat(x).st_size}
        users = DB.get_users()
        for x in users:
            dirname = (up_one / 'data' / x['username'])
            audiofiles = []
            if dirname.is_dir():
                audiofiles = list(dirname.iterdir())
                audiofiles = [ str(x) for x in audiofiles ]
            x['count'] = len(audiofiles)
            if x['username'] not in exportfiles.keys():
                exportfiles[x['username']] = {'file': None, 'size': 0}
        return render_template('exports.html', files=exportfiles, users=users)
    else:
        print(request.args)
        print(request.form)
        user_id = request.json['userid']
        print(request.json)
        print(url_for('progress', _external=True))
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
            url_for('progress', _external=True),
        )
        return jsonify({'taskid': task.id})


# INTERNAL route
@app.route('/progress', methods=['POST'])
def progress():
    # for now progress gets update progress of all celery tasks
    # TODO need to forward this to any connected clients
    data = request.json
    print(data)
    userid = data['userid']
    # print(data)
    room = app.clients.get(userid)
    # print('room', room)
    # if ns and data:
    # must specify both namespace and room
    # room is for this single user
    socketio.emit('celerystatus', data,
                  room=room, namespace='/events')
    print(request.data)
    return 'ok'


@app.route('/export/<string:filename>')
def download_zipfile(filename: str):
    return send_from_directory(
        TEMP_DIR,
        filename,
        as_attachment=True,
        attachment_filename=filename.split("_")[0] + ".zip"
    )


@app.route('/info/<string:filename>')
def info_zipfile(filename: str):
    filepath = Path(TEMP_DIR) / filename
    err = "No such file {} found".format(filename)
    if filepath.is_file():
        err = None
    size = os.stat(filepath).st_size
    return jsonify({"error": err, "size": size})


@app.route('/skipped', methods=['POST'])
@jwt_required
def handle_skip():

    sentence_ids = request.json['ids']
    username = session['user'][0]

    with open('corpora/split/skipped.txt', 'a+') as skipper:
        for sentence_id in sentence_ids:
            skipper.write(f"{sentence_id}||{username}\n")

    return 'ok', 200


def run_app(*args, **kwargs):
    app = kwargs['app']
    del kwargs['app']
    # app.run(*args, **kwargs)
    socketio.run(app, *args, **kwargs)


if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = os.path.join(up_one, 'data')
    app.debug = True
    run_app(app=app, host='0.0.0.0', port=3000, debug=True)
