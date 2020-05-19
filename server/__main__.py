import os
from pathlib import Path

from server import app, run_app

up_one = Path(__file__).parents[1]
folder = up_one / 'web_app' / 'src'

# print(up_one, Path(__file__), folder)

if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = os.path.join(up_one, 'data')
    print(app.config['UPLOAD_FOLDER'], app.static_folder, app.static_url_path)
    app.debug = True
    run_app(app=app, host='0.0.0.0', port=3000, debug=True)
