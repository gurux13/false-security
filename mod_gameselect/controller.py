from flask import request, render_template, \
                  flash, g, session, redirect, url_for

from flask import Blueprint
from session import SessionKeys, SessionHelper
mod_gameselect = Blueprint('gameselect', __name__)


@mod_gameselect.route('/')
def index():
    if SessionHelper.has(SessionKeys.GAME_KEY):
        return "Welcome back!"
    SessionHelper.set(SessionKeys.GAME_KEY, "meh")
    return "hello"