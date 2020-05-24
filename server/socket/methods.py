from flask import request, session, current_app
from flask_socketio import SocketIO, disconnect, emit, join_room, leave_room

from server import socketio, cache

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
    existing = cache.get('clients')
    existing[userid] = request.sid
    cache.set('clients', existing)
    join_room(request.sid, namespace='/events')
    emit('userid', {'userid': userid})
    emit('status', {'status': 'Connected user', 'userid': userid})


@socketio.on('disconnect', namespace='/events')
def events_disconnect():
    existing = cache.get('clients')
    userid = session['userid']
    if userid in existing:
        # else user id is gone
        # during development this might happen
        # TODO remove this if and check when this fails
        leave_room(existing[userid], namespace='/events')
        del existing[userid]
    cache.set('clients', existing)
    # del cache.get('clients')[userid]
    print('Client %s disconnected' % userid)
