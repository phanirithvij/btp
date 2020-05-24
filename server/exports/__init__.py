from flask import Blueprint

exports = Blueprint('exports', __name__)

from server.exports import views
