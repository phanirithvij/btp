import atexit
import os
from server.config import Config
from server.main.utils import get_session, store_session
import time
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler

from server import app, run_app

up_one = Path(__file__).parents[1]
folder = up_one / 'web_app' / 'src'

# print(up_one, Path(__file__), folder)


def send_ping_req():
    if not Config.USE_CENTRAL_SERVER:
        return
    print("[INFO] Make self online", time.strftime(
        "%A, %d. %B %Y %I:%M:%S %p"))
    try:
        sess = get_session()
        r = sess.post(Config.CENTRAL_SERVER_PING_URL, json={
            "message": "ping"
        })
        print(r.json(), r.status_code)
        # TODO deal with status code
        # if status code is badrequest json is invalid not sure when this can occur
        # if status code is unauthorized try getting session again
        # if the next status code is unauthorized as well we are probably
        # banned or suspended or deleted
        # check based on the message in the response

    except Exception as e:
        # TODO check in config if this org wants the central_server feature
        print("[WARNING] Failed to PING central server")

# TODO argparse or config
DEBUG = Config.FLASK_DEBUG
# DEBUG = True


def shutdown_sched(scheduler: BackgroundScheduler):
    print("[INFO] Shutting down BG scheduler")
    scheduler.shutdown()


# https://stackoverflow.com/a/25519547/8608146
if not DEBUG or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    # store the session once
    store_session()
    # send very first ping request
    send_ping_req()

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=send_ping_req, trigger="interval", seconds=60)
    print("[INFO] Starting Background Scheduler...")
    scheduler.start()
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: shutdown_sched(scheduler))


if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = os.path.join(up_one, 'data')
    print(app.config['UPLOAD_FOLDER'], app.static_folder, app.static_url_path)
    app.debug = True
    run_app(app=app, host='0.0.0.0', port=8080, debug=DEBUG)
