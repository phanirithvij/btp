import sqlite3
import time

from werkzeug.security import check_password_hash, generate_password_hash
from typing import Union

from server.db.schema.queries import *
from server.db.schema.adminq import CREATE_ADMIN_TABLE, CREATE_ROLES_TABLE


# https://stackoverflow.com/a/3300514/8608146
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class UserFileSystem(object):
    pass



class Database:

    def __init__(self, filename="../data/data.db"):
        self.filename = filename
        self.__init_db()

    def execute(self, query, args=()):
        # Init users table
        try:
            self._cursor.execute(query, args)
        except sqlite3.ProgrammingError:
            self.__init_db()
            self._cursor.execute(query, args)
        return self._cursor.fetchall()

    def __init_db(self):
        self.instance = sqlite3.connect(self.filename)
        self.instance.row_factory = dict_factory
        self._cursor = self.instance.cursor()

        # Init users table
        self.init_db()

    def init_db(self):
        self._cursor.execute(CREATE_USER_TABLE)
        self._cursor.execute(CREATE_ADMIN_TABLE)
        self._cursor.execute(CREATE_ROLES_TABLE)
        self.instance.commit()

    def close(self):
        self.instance.close()

    def commit(self):
        self.instance.commit()

    def get_users(self):
        self._cursor.execute(GET_ALL_USERS)
        _data = self._cursor.fetchall()
        return _data
