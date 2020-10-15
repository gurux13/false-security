from flask import Blueprint, redirect, url_for, render_template, g
from flask_socketio import SocketIO, emit, join_room
from dataclasses import dataclass

from Exceptions.hack_attempt import HackAttemptError
from Exceptions.user_error import UserError
from globals import db
from logic.game_logic import game2redirect
from logic.game_manager import GameManager
from logic.player_manager import PlayerManager
from mod_gameselect.controller import ExitForm
from session import SessionHelper, SessionKeys
from utils.g_helper import set_current_player

from utils.memoize import Memoize
from utils.response import Response
from globals import socketio
from utils.socketio_helper import wrapped_socketio

mod_game_wr = Blueprint('game_wr', __name__)


@dataclass
class WaitroomResponse:
    game_name: str = None
    players: list = None
    can_start: bool = False
    admin_player: str = None
    redirect_to: str = None
    game_link: str = None
    current_player: str = None



def get_state():
    gm = GameManager(db)
    pm = PlayerManager(db)
    game = gm.get_my_game(optional=True)
    self = pm.get_my_player()
    redirect_url = game2redirect(game, self)
    if redirect_url is not None and redirect_url != '/waitroom':
        return WaitroomResponse(redirect_to=redirect_url)
    return WaitroomResponse(
        game_name=game.model.uniqueCode,
        current_player=pm.get_my_player().model.name,
        players=[{'name': x.model.name, 'is_admin': x.model.isAdmin, 'is_online': x.model.isOnline} for x in game.get_players(False)],
        can_start=game.can_start(pm.get_my_player()),
        game_link='?k=' + game.model.uniqueCode,
    )


@wrapped_socketio('waitroom', 'waitroom')
def waitroom():
    result = get_state()
    if result.game_name is not None:
        join_room(result.game_name)
    return result

@wrapped_socketio('start', 'start')
def start_game():
    gm = get_game_manager()
    pm = get_player_manager()
    game = g.game
    if not game.is_waitroom():
        raise UserError("Игра не может быть начата без комнаты ожидания!")
    if not game.can_start(pm.get_my_player()):
        raise HackAttemptError("Попытка начать игру игроком, который не может этого делать!")
    game.start()
    return True

@Memoize
def get_game_manager():
    return GameManager(db)


@Memoize
def get_player_manager():
    return PlayerManager(db)


@mod_game_wr.route('/waitroom')
def wr():
    set_current_player()
    try:
        game = get_game_manager().get_my_game()
        player = get_player_manager().get_my_player()
    except UserError:
        return redirect(url_for('gameselect.index'))
    #TODO move ExitForm to different file
    return render_template('waitroom.html', form=ExitForm())
