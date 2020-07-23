from flask import request, render_template, \
    flash, g, session, redirect, url_for

from flask import Blueprint
from sqlalchemy.exc import IntegrityError

from db_models.deckentry import DeckEntry
from session import SessionKeys, SessionHelper

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired

from db_models.game import Game, Player
from game_logic.gameparams import GameParams
from app import db

import random
import string

mod_gameselect = Blueprint('gameselect', __name__)


def get_random_string(length):
    letters = string.ascii_uppercase + string.ascii_lowercase
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


def make_player(form):
    player = Player(name=form.player_name, money=0, hand=None)
    return player


def on_create(form):
    retries = 5
    while retries > 0:
        # TODO: Make sure this is cryptographically secure
        game_key = get_random_string(6)
        player = make_player(form)
        params = GameParams(form.b_falsics.data)
        game = Game(uniqueCode=game_key, params=params.to_db(), roundsCompleted=0, isComplete=False)
        player.isAdmin = True
        try:
            db.session.add(game)
            db.session.commit()
            break
        except IntegrityError as e:
            db.session.rollback()
            print(dir(e))
            retries -= 1
            continue
    else:
        return "Почему-то не получилось создать игру. Пожалуйста, попробуйте ещё раз."
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

@mod_gameselect.route('/waitroom')
def wr():
    #from flask_sqlalchemy import SQLAlchemy
    #db = SQLAlchemy()
    game_key = SessionHelper.get(SessionKeys.GAME_KEY)
    game = Game.query.filter_by(uniqueCode=game_key).first()
    de = DeckEntry(game=game, order=random.randint(0, 10000))
    game.deck.append(de)

    db.session.commit()
    deck = '<br/>'.join([str(x.order) for x in game.deck])
    return 'Играем в игру ' + game.uniqueCode + ", колода: " + deck

@mod_gameselect.route('/test')
def test():
    return 'x'
