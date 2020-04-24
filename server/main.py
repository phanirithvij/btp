import datetime
import os
import random
import time
from pathlib import Path

from flask import (Flask, jsonify, render_template, request, send_file,
                   send_from_directory, session)
from flask_jwt_extended import (JWTManager, create_access_token,
                                create_refresh_token, get_current_user,
                                get_jwt_identity, jwt_refresh_token_required,
                                jwt_required)
from werkzeug.utils import secure_filename

from .user import *

# current directory is server/
# Set static folder to be ../web_app/src
up_one = Path(__file__).parent
folder = up_one / 'web_app' / 'src'


DB = Database("data/data.db")
app = Flask(__name__, static_folder=str(folder))

# https://stackoverflow.com/a/53152394/8608146
# app.config.from_object(__name__)
# random key
# app.config['SECRET_KEY'] = 'FTYFUH@E^@%R%^#!V#HUFEDGVQGV'
app.secret_key = r'<çDÒ\x88\r/Ò\x9dµ\x90k!a|RÈ\x96#ÇÔ^1à'

# app.config['SESSION_TYPE'] = 'filesystem'
# Session(app)

jwt = JWTManager()


@app.route('/')
def index():
    return render_template('index.html')


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

# Routes


@app.route('/auth/login', methods=['POST'])
def login():

    error = ''
    status = 'error'
    user, error = auth_handler(
        request.json['username'],
        request.json['password']
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
        access_token = None
        refresh_token = None
        user_id = None
        if success:
            print("New user added", _username)
            # custom success status instead of 'ok'
            status = 'new'
            err = ''
            session['user'] = user.pickle_instance()
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
        return "Web UI Not Implemented", 404


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


@app.route('/upload', methods=['POST'])
@jwt_required
def upload_file():

    print(session['user'])

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


@app.route('/data')
@jwt_required
def random_corpa():
    print("Data bros")
    print(session['user'])
    data_dir: Path = up_one / '..' / 'corpora' / 'split'
    x = 0
    for filename in data_dir.iterdir():
        if filename.is_file():
            x += 1
    return send_from_directory(
        str(data_dir),
        "out{}.txt".format(random.randint(1, x))
    )


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
    jwt.init_app(app)
    app.run(*args, **kwargs)


if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = os.path.join(up_one, 'data')
    app.debug = True
    run_app(app, host='0.0.0.0', port=3000, debug=True)
