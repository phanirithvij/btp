import os
from pathlib import Path

from server import app, run_app

up_one = Path(__file__).parent
folder = up_one / 'web_app' / 'src'


if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = os.path.join(up_one, 'data')
    app.debug = True
    run_app(app=app, host='0.0.0.0', port=3000, debug=True)
