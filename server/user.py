import sqlite3
import time

from werkzeug.security import check_password_hash, generate_password_hash
from typing import Union

from .queries import *


# https://stackoverflow.com/a/3300514/8608146
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class UserFileSystem(object):
    pass


def auth_handler(username, password):
    user = User(username)
    try:
        user.populate()
    except Exception:
        print("No user named", username)
    if user.verify_password(password):
        return user


def identity(payload):
    user_id = payload['identity']
    return User(user_id).populate()


class Database:

    def __init__(self, filename="../data/data.db"):
        self.instance = sqlite3.connect(filename)
        self.instance.row_factory = dict_factory
        self._cursor = self.instance.cursor()

        # Init users table
        self.init_db()

    def execute(self, query, args=()):
        # Init users table
        self._cursor.execute(query, args)
        return self._cursor.fetchall()

    def init_db(self):
        self._cursor.execute(CREATE_USER_TABLE)
        self.instance.commit()

    def close(self):
        self.instance.close()

    def commit(self):
        self.instance.commit()

    def get_users(self):
        self._cursor.execute(GET_ALL_USERS)
        _data = self._cursor.fetchall()
        return _data


class User:
    def __init__(
            self,
            username: str,
            age: int = None,
            gender: int = None,
            password: str = None
    ):
        self.DB: Database = None
        self.username = username
        self.age = age
        self.gender = gender
        self.pwhash = None
        if password is not None:
            self.pwhash = generate_password_hash(password)
        self.id = username  # get this from the database

    def delete_self(self):
        self._ensure_db_exists()

        self.DB.execute(DELETE_USER, (self.username,))
        print("Deleted user", self.username)
        # TODO delete user files

    def verify_password(self, password: str) -> bool:
        return check_password_hash(self.pwhash, password)

    def save_to_db(self) -> tuple:
        self._ensure_db_exists()
        valid = (self.gender is not None and self.age is not None)
        if not valid:
            return False, None
        try:
            self.DB.execute(
                INSERT_USER, (
                    self.username,
                    self.age,
                    self.gender,
                    self.pwhash
                )
            )
        except sqlite3.IntegrityError:
            return False, None
        self.DB.commit()
        return True, self._fecth_id()

    def populate(self):
        """Populates the user based on the username"""
        self._ensure_db_exists()
        users = self.DB.execute(GET_USER, (self.username,))
        if len(users) == 0:
            raise Exception
        self.username = users[0]["username"]
        self.age = users[0]["age"]
        self.gender = users[0]["gender"]
        self.pwhash = users[0]["password"]
        self.id = self.username
        return self

    def attach_DB(self, DB: Database) -> None:
        """Attaches the given DB to this user"""
        self.DB = DB
        return self

    def _ensure_db_exists(self) -> None:
        """This ensures DB is initialized"""
        if self.DB is None:
            self.DB = Database()
        return self

    def _fecth_id(self) -> int:
        """Last inserted ROW id (row number)"""
        self._ensure_db_exists()
        return self.DB.execute(GET_LAST_ID)[0]

    def dispose(self):
        """Disposes the sqlite3 instance"""
        self._ensure_db_exists()
        self.DB.cursor.close()
        self.DB.close()


if __name__ == "__main__":
    user = User("Rithvij",  "viz" + str(time.time()), 19, MALE, 'encrypted')
    user.save_to_db()
