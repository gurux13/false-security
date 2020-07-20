from flask import request, render_template, \
    flash, g, session, redirect, url_for

from flask import Blueprint
from session import SessionKeys, SessionHelper

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired

import random
import string

mod_gameselect = Blueprint('gameselect', __name__)



def get_random_string(length):
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


class GameForm(FlaskForm):
    action = SubmitField()
    player_name = StringField(validators=[DataRequired()])


class JoinForm(GameForm):
    game_key = StringField(validators=[DataRequired()])


class CreateGameForm(GameForm):
    b_falsics = IntegerField(validators=[DataRequired()])


def on_join(form):
    SessionHelper.set(SessionKeys.GAME_KEY, form.game_key.data)
    return redirect('/waitroom')


def on_create(form):
    game_key = get_random_string(6)
    # TODO: Make sure there is no such game already
    # TODO: Create a game
    SessionHelper.set(SessionKeys.GAME_KEY, game_key)
    return redirect('/waitroom')


@mod_gameselect.route('/', methods=['GET', 'POST'])
def index():
    join_form = JoinForm()
    if (join_form.validate_on_submit()):
        return on_join(join_form)
    create_form = CreateGameForm()
    if (create_form.validate_on_submit()):
        return on_create(create_form)

    game_key = SessionHelper.get(SessionKeys.GAME_KEY, '')
    if 'k' in request.args:
        game_key = request.args['k']
        print("Taking from request...")
    g.game_key = game_key
    return render_template("index.html", form=create_form)



@mod_gameselect.route('/test')
def test():
    return 'x'

