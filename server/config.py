import os
import redis

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
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.from_url("redis://localhost:6379/")
    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = 'redis://localhost:6379/1'
    CACHE_DEFAULT_TIMEOUT = 3
    # TODO os.environ get
    SECRET_KEY = r'<çDÒ\x88\r/Ò\x9dµ\x90k!a|RÈ\x96#ÇÔ^1à'
    TEMP_DIR = '/tmp/storage'
    CENTRAL_SERVER_URL = "http://localhost:9090"
    CENTRAL_SERVER_INFO_URL = CENTRAL_SERVER_URL + "/api/v1/orgs/info"
    CENTRAL_SERVER_TOKEN_URL = CENTRAL_SERVER_URL + "/api/v1/orgs/token"
    CENTRAL_SERVER_PING_URL = CENTRAL_SERVER_URL + "/api/v1/orgs/ping"
    SESSION_DUMP_FILE = ".session.dump.bin"
    USE_CENTRAL_SERVER = True
    # TODO os.environ get
    CENTRAL_SERVER_EMAIL = "main@sample.org"
    CENTRAL_SERVER_PASSWORD = "sample"
    FLASK_DEBUG = False
