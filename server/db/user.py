import sqlite3
import time
from typing import Union

from werkzeug.security import check_password_hash, generate_password_hash

from server.db import Database
from server.db.schema.adminq import CREATE_ADMIN_TABLE, CREATE_ROLES_TABLE
from server.db.schema.queries import *


def auth_handler(username, password):
    print(username, password)
    user = User(username)
    try:
        user.populate()
        if user.verify_password(password):
            return user, None
        else:
            return None, "Password is incorrect"
    except Exception as e:
        print(e)
        print("No user named", username)
        return None, "No user named {}".format(username)


def identity(payload):
    user_id = payload['identity']
    return User(user_id).populate()


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
        self.is_admin = False
        if password is not None:
            self.pwhash = generate_password_hash(password)
        self.id = username  # get this from the database

    def delete_self(self):
        self._ensure_db_exists()

        self.DB.execute(DELETE_USER, (self.username,))
        print("Deleted user", self.username)
        # TODO delete user files

    def verify_password(self, password: str) -> bool:
        print("Verifying password", self.pwhash, password)
        return check_password_hash(self.pwhash, password)

    def save_to_db(self) -> tuple:
        self._ensure_db_exists()

        # admin needs no gender and age
        valid = self.is_admin or (
            self.gender is not None and self.age is not None)
        if not valid:
            return False, 'No gender or age specified'

        ret = True, None
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
            ret = False, 'User already exists with same fields, try login'

        if self.is_admin:
            err = self.make_user_admin()
            ret = err is not None, err

        self.DB.commit()
        return ret

    def populate(self):
        """Populates the user based on the username"""
        self._ensure_db_exists()
        users = self.DB.execute(GET_USER, (self.username,))
        print(users)
        if len(users) == 0:
            raise Exception
        self.username = users[0]["username"]
        self.age = users[0]["age"]
        self.gender = users[0]["gender"]
        self.pwhash = users[0]["password"]
        self.id = self.username
        print(self.pwhash)
        return self

    def pickle_instance(self):
        return (self.username, self.age, self.gender)

    def attach_DB(self, DB: Database) -> None:
        """Attaches the given DB to this user"""
        self.DB = DB
        return self

    def _ensure_db_exists(self) -> None:
        """This ensures DB is initialized"""
        if self.DB is None:
            self.DB = Database("data/data.db")
        print(self.DB)
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

    def make_user_admin(self) -> Exception:
        """
        Makes a given user admin
        TODO add roles to db and also this call
        """
        user = self
        user.is_admin = True
        print(f"Making {user} an admin")
        try:
            user.DB.execute(
                INSERT_ADMIN_USER, (
                    user.username,
                )
            )
        except Exception as e:
            return e
        user.DB.commit()
        return None

    def __repr__(self):
        return f"User {self.username}"


if __name__ == "__main__":
    user = User("Rithvij",  "viz" + str(time.time()), 19, MALE, 'encrypted')
    user.save_to_db()
