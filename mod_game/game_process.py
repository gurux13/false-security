from flask import Blueprint, redirect, url_for, render_template
from flask_socketio import SocketIO, emit, join_room
from dataclasses import dataclass

from Exceptions.user_error import UserError
from globals import db
from logic.card_logic import CardLogic
from logic.card_manager import CardManager
from logic.game_logic import GameLogic
from logic.game_manager import GameManager
from logic.player_logic import PlayerLogic
from logic.player_manager import PlayerManager
from mod_game.game_state import UiGame, UiPlayer, UiCard, UiCardType
from mod_gameselect.controller import ExitForm
from session import SessionHelper, SessionKeys
from utils.conversion import map_opt
from utils.g_helper import set_current_player

from utils.memoize import Memoize
from utils.response import Response
from globals import socketio
from utils.socketio_helper import wrapped_socketio

mod_game_process = Blueprint('game_process', __name__)


@dataclass
class GameState:
    redirect_to: str
    game: UiGame = None


def make_ui(card: CardLogic, game: GameLogic, player: PlayerLogic) -> UiCard:
    rv = card.to_ui()
    rv.can_play = game.can_play_card(card, player)
    return rv


@wrapped_socketio('state', 'state')
def get_state():
    gm = GameManager(db)
    pm = PlayerManager(db)
    if not (SessionHelper.has(SessionKeys.PLAYER_ID) and SessionHelper.has(SessionKeys.GAME_KEY)):
        return GameState(redirect_to='/')
    game = gm.get_my_game()
    if game.is_waitroom():
        return GameState(redirect_to='/waitroom')
    player = pm.get_my_player()
    # TODO: What do we do with completed games?
    if not game.is_running():
        return GameState(redirect_to='/')
    players = game.get_players()
    ui_game = UiGame(
        game_name=game.model.uniqueCode,
        self_player=player.model.id,
        players=[
            UiPlayer(
                id=p.model.id,
                name=p.model.name,
                is_admin=p.model.isAdmin,
                is_online=p.model.isOnline,
                on_offence=False,
                on_defence=False,
                neighbour_right=p.model.neighbourId,
                can_attack=game.can_attack(player, p),
            ) for p in players
        ],
        hand=map_opt(lambda c: make_ui(c, game, player), player.get_hand()),
        current_battles=[battle.to_ui() for battle in game.get_battles()],
    )

    return GameState(
        redirect_to='',
        game=ui_game
    )


@wrapped_socketio('attack', 'attack')
def attack(player_id):
    print("Attacking", player_id)
    get_game_manager() \
        .get_my_game() \
        .attack(
        get_player_manager().get_my_player(),
        get_player_manager().get_player(player_id)
    )


@wrapped_socketio('play', 'play')
def play_card(card_id):
    print("Playing card", card_id)
    get_game_manager() \
        .get_my_game() \
        .play_card(
        get_card_manager().get_card(card_id),
        get_player_manager().get_my_player()
    )
    return True


@wrapped_socketio('done_def', 'done_def')
def done_defending():
    get_game_manager().get_my_game().end_battle(get_player_manager().get_my_player())


@wrapped_socketio('card', 'card')
def get_card(card_id):
    return get_card_manager().get_card(card_id).to_ui()


@wrapped_socketio('cards', 'cards')
def get_cards():
    return [c.to_ui() for c in get_card_manager().get_all_cards()]


@Memoize
def get_game_manager():
    return GameManager(db)


@Memoize
def get_player_manager():
    return PlayerManager(db)


@Memoize
def get_card_manager():
    return CardManager(db)


@mod_game_process.route('/game')
def game():
    set_current_player()
    try:
        game = get_game_manager().get_my_game()
        player = get_player_manager().get_my_player()
    except UserError:
        return redirect(url_for('gameselect.index'))
    return render_template('game.html', form=ExitForm())
