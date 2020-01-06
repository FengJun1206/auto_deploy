from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.sql.functions import current_user

from models import UserProfile, Host, DB
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class UserAdmin(ModelView):
    # def is_accessible(self):
    #     """开启权限"""
    #     if current_user.is_authenticated and current_user.username == 'admin':
    #         return True
    #     return False

    column_list = ('id', 'username', 'password', 'is_superuser', 'created_time')

    def __init__(self, session, **kwargs):
        super(UserAdmin, self).__init__(UserProfile, session, **kwargs)

