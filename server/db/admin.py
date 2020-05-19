from server.db.user import User
from server.db.schema.adminq import CREATE_ADMIN_TABLE

class Admin(User):

    def __init__(self, *args, **kwargs):
        super.__init__(*args, **kwargs)
        self.is_admin = True

    def make_user_admin(self, user: User):
        user.is_admin = True
        self.DB.execute(
            INSERT_USER, (
                self.username,
                self.age,
                self.gender,
                self.pwhash
            )
        )

    def _admin_init_db(self):
        pass