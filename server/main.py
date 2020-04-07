import os

from flask import Flask, jsonify, render_template, request, send_from_directory, send_file
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename

# current directory is server/
# Set static folder to be ../web_app/src
up_one = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
folder = os.path.abspath(os.path.join(up_one, 'web_app', 'src'))

app = Flask(__name__, static_folder=folder)
app.config['SECRET_KEY'] = 'secret!'
# print(app.static_folder)

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
ALLOWED_EXTENSIONS = set(['wav', 'mp3', 'ogg', 'webm'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/files')
def all_files():
    items = []
    for i in os.listdir(app.config['UPLOAD_FOLDER']):
        path = os.path.join(app.config['UPLOAD_FOLDER'], i)
        items.append(
            {'date': i.split('.')[0][4:], 'size': os.stat(path).st_size, 'id': i})
    return render_template("files.html", items=items)  # , as_attachment=True)

# TODO
# https://stackoverflow.com/a/51013358/8608146


@app.route('/files/<path:filename>', methods=['GET', 'DELETE', 'PUT'])
def download_file(filename):
    if request.method == 'GET':
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
    run_app(app, 'localhost', 3000, debug=True)
