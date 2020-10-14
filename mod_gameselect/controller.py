from flask import request, render_template, \
    flash, g, session, redirect, url_for

from flask import Blueprint
from sqlalchemy.exc import IntegrityError

from Exceptions.hack_attempt import HackAttemptError
from Exceptions.user_error import UserError
from db_models.deckentry import DeckEntry
from logic.game_logic import game2redirect
from logic.game_manager import GameManager
from logic.player_manager import PlayerManager
from session import SessionKeys, SessionHelper

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, BooleanField
from wtforms.validators import DataRequired, InputRequired

from db_models.game import Game, Player
from logic.gameparams import GameParams, EndGameDeaths, DefCardDeal
from globals import db

import random
import string

from utils.conversion import first_or_none
from utils.g_helper import set_current_player
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
    b_falsics = IntegerField(validators=[InputRequired()])
    b_offence = IntegerField(validators=[InputRequired()])
    b_defence = IntegerField(validators=[InputRequired()])
    acc_prob = IntegerField(validators=[InputRequired()])
    endgame = IntegerField(validators=[InputRequired()])
    only_admin_starts = BooleanField(validators=[])
    can_attack_anyone = BooleanField(validators=[])
    deck_size = IntegerField()
    num_rounds = IntegerField()
    def_card_deal = IntegerField(validators=[InputRequired()])
    def_card_deal_size = IntegerField()
    hardcore_mode = BooleanField(validators=[])


class ExitForm(FlaskForm):
    action = SubmitField()


def on_join(form):
    game = get_game_manager().get_game(form.game_key.data)
    # TODO: wipe the old player, if set in session
    player = get_player_manager().create_player(form.player_name.data, game)
    game.join_player(player, False)
    SessionHelper.set(SessionKeys.GAME_KEY, form.game_key.data)
    SessionHelper.set(SessionKeys.PLAYER_ID, player.model.id)

    return redirect('/waitroom')


def on_exit(form):
    pm = get_player_manager()
    player = pm.get_my_player()
    if player is None:
        return redirect('/')

    game = get_game_manager().get_my_game()
    game.leave_player(player)
    db.session.commit()
    game.notify()
    if first_or_none(filter(lambda x: not x.model.hasLeft and x.model.isOnline, game.get_players(False))) is None:
        get_game_manager().delete_game(game)
    SessionHelper.delete(SessionKeys.GAME_KEY)
    SessionHelper.delete(SessionKeys.PLAYER_ID)
    return redirect('/')


def rejoin() -> bool:
    player = get_player_manager().get_my_player()
    try:
        if player is not None and player.model.game.id == get_game_manager().get_my_game().model.id:
            print("this player is already in this game with name", player.model.name)
            return True
    except BaseException as e:
        print(e)
    SessionHelper.delete(SessionKeys.PLAYER_ID)
    SessionHelper.delete(SessionKeys.GAME_KEY)
    return False


def on_create(form):
    endgame_map = {
        0: EndGameDeaths.NotEnabled,
        1: EndGameDeaths.NotEnabled,
        2: EndGameDeaths.OneDead,
        3: EndGameDeaths.AllButOneDead
    }
    def_card_deal_map = {
        0: DefCardDeal.DealFixed,
        1: DefCardDeal.DealPlayerCount,
        2: DefCardDeal.KeepSize,
        3: DefCardDeal.DealAverageSpend,
        4: DefCardDeal.RemainingPlusFixed,
    }
    params = GameParams(form.b_falsics.data, form.b_defence.data,
                        form.b_offence.data, form.acc_prob.data / 100.0,
                        endgame_map[form.endgame.data], form.deck_size.data, form.num_rounds.data,
                        form.only_admin_starts.data, form.can_attack_anyone.data, def_card_deal_map[form.def_card_deal.data],
                        form.def_card_deal_size.data, form.hardcore_mode.data)
    game = get_game_manager().create_game(params)
    # TODO: wipe the old player, if set in session
    player = get_player_manager().create_player(form.player_name.data, game)
    game.join_player(player, True)
    db.session.commit()
    SessionHelper.set(SessionKeys.GAME_KEY, game.model.uniqueCode)
    SessionHelper.set(SessionKeys.PLAYER_ID, player.model.id)
    return redirect('/waitroom')


@mod_gameselect.route('/logout', methods=['POST'])
def logout():
    exit_form = ExitForm()
    if exit_form.validate_on_submit():
        return on_exit(exit_form)
    return redirect('/')


@mod_gameselect.route('/', methods=['GET', 'POST'])
def index():
    set_current_player()
    join_form = JoinForm()
    create_form = CreateGameForm()
    if rejoin():
        return redirect(game2redirect(GameManager(db).get_my_game(), get_player_manager().get_my_player()))
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
        elif e.error_type == UserError.ErrorType.INVALID_GAME:
            g.error_game = e.message
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
