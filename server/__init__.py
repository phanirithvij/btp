import logging
import os
import random
import sys
import time
from pathlib import Path

from celery import Celery
from flask import Flask, current_app, jsonify, redirect, session
from flask_caching import Cache
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO

from flask_session import Session
from server.config import Config
from server.db.schema.queries import FEMALE, MALE
# from server.db.user import *
from server.tasks import celery

# LOG_FILENAME = 'logs/mylogs.log'

# # Set up a specific logger with our desired output level
# my_logger = logging.getLogger('MyLogger')
# my_logger.setLevel(logging.DEBUG)


# handler = logging.handlers.RotatingFileHandler(
#     LOG_FILENAME, maxBytes=1024*6, backupCount=5)

# my_logger.addHandler(handler)


# current directory is server/
# Set static folder to be ../web_app/src
up_one = Path(__file__).parents[1]
folder = up_one / 'web_app' / 'src'

jwt = JWTManager()
socketio = SocketIO()
sess = Session()
cache = Cache()


def create_app():
    app = Flask(__name__, static_folder=str(folder), static_url_path='/static')
    app.config.from_object(Config)
    jwt.init_app(app)
    sess.init_app(app)
    cache.init_app(app)
    socketio.init_app(app)
    celery.conf.update(app.config)

    from server.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from server.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from server.exports import exports as exports_blueprint
    app.register_blueprint(exports_blueprint, url_prefix='/exports')

    from server.socket import socket as socket_blueprint
    app.register_blueprint(socket_blueprint)

    return app


app: Flask = create_app()
app.url_map.strict_slashes = False

def init_cache():
    # print('INIT CACHE', '(('*100, '))'*100)
    cache.set('running_zip_tasks', {})
    cache.set('clients', {})
    # Using this on linux so /tmp is the best place to store files
    try:
        os.makedirs(Config.TEMP_DIR)
    except Exception as e:
        print(str(e))
init_cache()

# https://stackoverflow.com/a/53152394/8608146
# app.config.from_object(__name__)
# random key
# app.config['SECRET_KEY'] = 'FTYFUH@E^@%R%^#!V#HUFEDGVQGV'


# JWT methods


@jwt.user_loader_error_loader
def customized_error_handler(error):
    return jsonify({
        'message': error.description,
        'code': error.status_code
    }), error.status_code


def run_app(*args, **kwargs):
    app = kwargs['app']
    del kwargs['app']
    # app.run(*args, **kwargs)
    socketio.run(app, *args, **kwargs)
