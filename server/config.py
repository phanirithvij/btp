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
    # CACHE_DEFAULT_TIMEOUT = ""
    SECRET_KEY = r'<çDÒ\x88\r/Ò\x9dµ\x90k!a|RÈ\x96#ÇÔ^1à'
    TEMP_DIR = '/tmp/storage'
