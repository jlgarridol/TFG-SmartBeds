from flask_login import UserMixin
from smartbeds.api.api import (API, BadCredentialsError)
from smartbeds.utils import get_secret_key


class User(UserMixin):

    def __init__(self, data):
        self._data = data
        self.id = None

    def is_authenticated(self):
        if self._token is not None:
            return True
        return False

    def is_active(self):
        return self.is_authenticated()

    def is_anonymous(self):
        if self._token is None:
            return True
        return False

    def get_token(self):
        return self.get_id()

    def get_username(self):
        return self._data['nickname']

    def get_role(self):
        return self._data['role']


def user_loader(token):
    if token is not None:
        try:
            user = User(API.get_instance().get_user_intern(token, get_secret_key()))
            user.id = token
            return user
        except BadCredentialsError:
            return None
    return None
