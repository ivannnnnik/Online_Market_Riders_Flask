from flask_login import UserMixin
from app.db_util import Database

dbase = Database()

class UserLogin(UserMixin):
    def __init__(self):
        self.__user = None

    def from_db(self, user_id, db):
        self.__user = db.get_user(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user[0]['id'])

    def get_user(self, db, user_id):
        self.__user = db.select(f"SELECT * FROM users WHERE id=%s LIMIT 1, (user_id,)")
        return self

    def is_admin(self):
        user_status = self.__user[0]['role']
        if user_status == 'admin':
            return True
