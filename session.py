from enum import Enum
from flask import session


class SessionKeys:
    PLAYER_ID = 'player'
    GAME_KEY = 'game'


class SessionHelper:
    def __init__(self):
        pass

    @staticmethod
    def __convert_key__(key):
        return key

    @staticmethod
    def get(key, default=None):
        if not SessionHelper.has(key):
            return default
        key = SessionHelper.__convert_key__(key)
        return session[key]

    @staticmethod
    def set(key, value):
        key = SessionHelper.__convert_key__(key)
        session[key] = value

    @staticmethod
    def has(key):
        key = SessionHelper.__convert_key__(key)
        return key in session

    @staticmethod
    def delete(key):
        if not SessionHelper.has(key):
            return
        key = SessionHelper.__convert_key__(key)
        del session[key]
