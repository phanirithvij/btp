from server.db.schema.adminq import CREATE_ADMIN_TABLE, INSERT_ADMIN_USER
from server.db.schema.queries import MALE
from server.db.user import User
from server.scripts.passwd import create_strong_password


class Admin(User):

    def __init__(self, *args, **kwargs):
        super.__init__(*args, **kwargs)
        self.is_admin = True


def initial_admin():
    """
    username: str,
    age: int = None,
    gender: int = None,
    password: str = None
    """
    passwd = create_strong_password()
    admin = Admin("admin", 100, MALE, passwd)
    admin.save_to_db()
