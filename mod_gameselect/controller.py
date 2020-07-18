from flask import request, render_template, \
                  flash, g, session, redirect, url_for

from flask import Blueprint
from session import SessionKeys, SessionHelper
mod_gameselect = Blueprint('gameselect', __name__)


@mod_gameselect.route('/')
def index():
    game_key = SessionHelper.get(SessionKeys.GAME_KEY, '')
    g.game_key = game_key
    return render_template("index.html")