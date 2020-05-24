from flask import Blueprint

socket = Blueprint('socket', __name__)

from server.socket import methods
