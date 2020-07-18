from flask import request, render_template, \
    flash, g, session, redirect, url_for

from flask import Blueprint
from session import SessionKeys, SessionHelper
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

mod_gameselect = Blueprint('gameselect', __name__)


class GameForm(FlaskForm):
    action = StringField(validators=[DataRequired()], _name='action')
    game_key = StringField(validators=[DataRequired()], _name='game_key')


def on_form(form):
    if (form.validate()):
        return "Ok"
    else:
        return "Fail"


@mod_gameselect.route('/', methods=['GET', 'POST'])
def index():
    form = GameForm()
    if form.validate_on_submit():
        on_form(form)
    game_key = SessionHelper.get(SessionKeys.GAME_KEY, '')
    g.game_key = game_key
    return render_template("index.html", form)
