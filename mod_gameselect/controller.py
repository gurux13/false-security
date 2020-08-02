from flask import request, render_template, \
    flash, g, session, redirect, url_for

from flask import Blueprint
from sqlalchemy.exc import IntegrityError

from Exceptions.hack_attempt import HackAttemptError
from Exceptions.user_error import UserError
from db_models.deckentry import DeckEntry
from game_logic.game_manager import GameManager
from game_logic.player_manager import PlayerManager
from session import SessionKeys, SessionHelper

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired

from db_models.game import Game, Player
from game_logic.gameparams import GameParams
from globals import db

import random
import string

from utils.memoize import Memoize

mod_gameselect = Blueprint('gameselect', __name__)


@Memoize
def get_game_manager():
    return GameManager(db)


@Memoize
def get_player_manager():
    return PlayerManager(db)


class GameForm(FlaskForm):
    action = SubmitField()
    player_name = StringField(validators=[DataRequired()])


class JoinForm(GameForm):
    game_key = StringField(validators=[DataRequired()])


class CreateGameForm(GameForm):
    b_falsics = IntegerField(validators=[DataRequired()])


def on_join(form):
    game = get_game_manager().get_game(form.game_key.data)
    # TODO: wipe the old player, if set in session
    player = get_player_manager().create_player(form.player_name.data, game)
    game.join_player(player, False)
    SessionHelper.set(SessionKeys.GAME_KEY, form.game_key.data)
    SessionHelper.set(SessionKeys.PLAYER_ID, player.model.id)

    return redirect('/waitroom')


def on_create(form):
    params = GameParams(form.b_falsics.data)
    game = get_game_manager().create_game(params)
    # TODO: wipe the old player, if set in session
    player = get_player_manager().create_player(form.player_name.data, game)
    game.join_player(player, True)
    db.session.commit()
    SessionHelper.set(SessionKeys.GAME_KEY, game.model.uniqueCode)
    SessionHelper.set(SessionKeys.PLAYER_ID, player.model.id)
    return redirect('/waitroom')


@mod_gameselect.route('/', methods=['GET', 'POST'])
def index():
    join_form = JoinForm()
    create_form = CreateGameForm()
    form = None
    try:
        if join_form.validate_on_submit():
            form = join_form
            return on_join(join_form)
        if create_form.validate_on_submit():
            form = create_form
            return on_create(create_form)
    except UserError as e:
        if e.error_type == UserError.ErrorType.INVALID_NAME:
            g.error_name = e.message
        else:
            raise
        return render_template('index.html', form=form)
    game_key = SessionHelper.get(SessionKeys.GAME_KEY, '')
    if 'k' in request.args:
        if not request.args['k'].isalpha():
            raise HackAttemptError("Некорректный ключ игры")
        game_key = request.args['k']

    g.game_key = game_key
    return render_template("index.html", form=create_form)

