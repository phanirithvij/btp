import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(), verbose=True)

class Config:
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CELERY_ACCEPT_CONTENT = ['pickle', 'json']
    Unnamed_MAIL_SUBJECT_PREFIX = '[Unnamed]'
    Unnamed_MAIL_SENDER = 'Unnamed Admin <admin@unnamed.com>'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
