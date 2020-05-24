from flask import request, session, current_app
from flask_socketio import SocketIO, disconnect, emit, join_room, leave_room

from server import socketio

import uuid

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
