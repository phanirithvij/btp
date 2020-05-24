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
from flask_caching import Cache
from flask_jwt_extended import (JWTManager, create_access_token,
                                create_refresh_token, get_current_user,
                                get_jwt_identity, jwt_refresh_token_required,
                                jwt_required)
from flask_session import Session
from flask_socketio import SocketIO, disconnect, emit, join_room, leave_room
from werkzeug.utils import secure_filename

from server.auth import auth
from server.db.user import *


@auth.route('/login', methods=['POST', 'GET'])
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



@auth.route('/new', methods=['GET', 'POST'])
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


@auth.route('/refresh')
@jwt_refresh_token_required
def post(self):
    print("user", session['user'])
    current_user = session['user'][0]
    # return a non-fresh token for the user
    new_token = create_access_token(current_user)
    return {'access_token': new_token}, 200
