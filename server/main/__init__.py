from flask import Blueprint

main = Blueprint('main', __name__)

from server.main import views
from server.main import stats