import os
import sqlite3
import time
from typing import Union
from pathlib import Path

from werkzeug.security import check_password_hash, generate_password_hash

from server.config import Config
from server.db.schema.adminq import CREATE_ADMIN_TABLE, CREATE_ROLES_TABLE
from server.db.schema.queries import *


# https://stackoverflow.com/a/3300514/8608146
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# here it should be parents[2]
up_one = Path(__file__).parents[2]


class UserFileSystem(object):
    def __init__(self, username):
        self.username = username
        self._audiofiles = []

    def user_dir(self):
        """User's data directory"""
        dirname = (up_one / 'data' / self.username)
        return dirname

    @classmethod
    def users_dir(self) -> Path:
        """Users data directory"""
        dirname = (up_one / 'data')
        return dirname


    def get_audio_files(self):
        dirname = (up_one / 'data' / self.username)
        audiofiles = []
        if dirname.is_dir():
            audiofiles = list(dirname.iterdir())
            audiofiles = [os.path.basename(str(x)) for x in audiofiles]
        self._audiofiles = audiofiles
        # print(audiofiles)
        return audiofiles

    def get_exports(self):
        exports = []
        for x in Path(Config.TEMP_DIR).iterdir():
            if self.username in str(x):
                exports.append(os.path.basename(x))

        return exports

    def get_sentences(self):
        if self._audiofiles == []:
            self.get_audio_files()
        sentences = []
        for audfile in self._audiofiles:
            name, _ = os.path.splitext(audfile)
            # print(name, _)
            sid = int(name.split('_')[-1])
            sentences.append((sid, self._get_sentence_fromid(sid), audfile))
        return sentences

    def _get_sentence_fromid(self, sid: int):
        filen = (sid // 1000) + 1
        idx = sid - (filen - 1) * 1000
        data_dir: Path = up_one / 'corpora' / 'split'
        filename = "out{}.txt".format(filen)
        with open(data_dir / filename, 'r') as fil:
            lines = fil.readlines()
            return lines[idx - 1].split('||')[-1]


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
        """Inits Db and creates tables"""
        self._cursor.execute(CREATE_USER_TABLE)
        self._cursor.execute(CREATE_ADMIN_TABLE)
        self._cursor.execute(CREATE_ROLES_TABLE)
        self.instance.commit()

    def close(self):
        """Closes the Database instance"""
        self.instance.close()

    def commit(self):
        """Commit to the Database instance"""
        self.instance.commit()

    def get_users(self):
        """Get all the Users from DB"""
        try:
            self._cursor.execute(GET_ALL_USERS)
        except sqlite3.ProgrammingError as e:
            self.__init_db()
            self._cursor.execute(GET_ALL_USERS)
        _data = self._cursor.fetchall()
        return _data

    def get_user(self, username):
        try:
            self._cursor.execute(GET_USER, (username, ))
        except sqlite3.ProgrammingError as e:
            self.__init_db()
            self._cursor.execute(GET_USER, (username, ))
        _data = self._cursor.fetchone()
        return _data
