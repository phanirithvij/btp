import os
from flask import Flask, send_from_directory, send_file

app = Flask(__name__)


@app.route('/files/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    upload_folder = os.path.join(os.getcwd(), 'files')
    print("Place your files here", upload_folder)
    app.config['UPLOAD_FOLDER'] = upload_folder
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'])
    except Exception as e:
        print(e)
    app.run(host='0.0.0.0', port=3000, debug=True)
