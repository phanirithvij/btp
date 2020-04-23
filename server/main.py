import os
import random
import time

from flask import (Flask, jsonify, render_template, request, send_file,
                   send_from_directory)
from flask_jwt import JWT, current_identity, jwt_required
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename

from .user import *

# current directory is server/
# Set static folder to be ../web_app/src
up_one = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
folder = os.path.abspath(os.path.join(up_one, 'web_app', 'src'))


DB = Database("data/data.db")
app = Flask(__name__, static_folder=folder)
# random key
app.config['SECRET_KEY'] = 'FTYFUH@E^@%R%^#!V#HUFEDGVQGV'

jwt = JWT(app, auth_handler, identity)

socketio = SocketIO()


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('my event', namespace='/test')
def test_message(message):
    emit('my response', {'data': message['data']})


@socketio.on('my broadcast event', namespace='/test')
def test_message(message):
    emit('my response', {'data': message['data']}, broadcast=True)


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected'})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


def run_app(*args, **kwargs):
    # init app here so outer configs get registered (??)
    socketio.init_app(app)
    socketio.run(*args, **kwargs)


# file upload
ALLOWED_EXTENSIONS = set(['wav', 'mp3', 'ogg', 'webm', 'aac'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/files')
@jwt_required()
def all_files():
    items = []
    for i in os.listdir(app.config['UPLOAD_FOLDER']):
        path = os.path.join(app.config['UPLOAD_FOLDER'], i)
        items.append(
            {'date': i.split('.')[0][4:], 'size': os.stat(path).st_size, 'id': i})
    return render_template("files.html", items=items)  # , as_attachment=True)

# TODO
# https://stackoverflow.com/a/51013358/8608146


@app.route('/auth/login', methods=['POST'])
def login():

    user = User(request.form.get('username'))
    user.attach_DB(DB)

    error = ''
    status = ''
    try:
        user.populate()
    except Exception:
        error = 'No such user'
        status = 'error'

    error = 'Password is incorrect'
    status = 'error'
    if user.verify_password(request.form.get('password')):
        status = 'ok'
        error = ''

    return jsonify({
        'status': status,
        'error': error,
        'userId': 'test',
        'name': user.username
    })


@app.route('/auth/new', methods=['GET', 'POST'])
def new_user():
    # TODO register
    if request.method == 'POST':

        _username: str = request.form.get('username')
        _password: str = request.form.get('password')
        _age: int = request.form.get('age')
        _gender: str = request.form.get('gender')
        _gender = MALE if _gender == 'm' else FEMALE
        user = User(_username, _age, _gender, _password)
        user.attach_DB(DB)
        success, rowId = user.save_to_db()

        status = 'error'
        err = f'A user named {_username} exists'
        if success:
            print("New user added", _username)
            status = 'ok'
            err = ''

        return jsonify({
            'status': status,
            'error': err,
            'userId': f"{_username}-{rowId}",
            'name': _username
        })
    else:
        # Register page from web app
        return "Not Implemented"


@app.route('/files/<path:filename>', methods=['GET', 'DELETE', 'PUT'])
@jwt_required()
def download_file(filename):
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


@app.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        # print(request)
        if 'file' not in request.files:
            # flash('No file part')
            # return redirect(request.url)
            return jsonify({'status': 'failed', 'msg': 'No file uploaded try again'})
        file = request.files['file']
        if file.filename == '':
            # flash('No file selected for uploading')
            return jsonify({'status': 'failed', 'msg': 'No file selected for uploading'})
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            size = os.stat(filepath).st_size
            # flash('File successfully uploaded')
            # return redirect('/')
            return jsonify({
                'status': 'ok',
                'msg': None, 'path': filename, 'size': size
            })
        else:
            # flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
            # print('my response',)
            return jsonify({'status': 'failed', 'msg': f'invalid file type {file.filename}'})
            # return redirect(request.url)


if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = os.path.join(up_one, 'data')
    app.debug = True
    run_app(app, host='0.0.0.0', port=3000, debug=True)
