from flask import Blueprint, redirect, url_for, render_template, g
from flask_socketio import SocketIO, emit, join_room
from dataclasses import dataclass

from Exceptions.user_error import UserError
from globals import db
from logic.card_logic import CardLogic
from logic.card_manager import CardManager
from logic.game_logic import GameLogic, game2redirect
from logic.game_manager import GameManager
from logic.player_logic import PlayerLogic
from logic.player_manager import PlayerManager
from mod_game.game_state import UiGame, UiPlayer, UiCard, UiCardType, UiRound
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


@wrapped_socketio("subscribe", "subscribe")
def subscribe():
    join_room(g.game.model.uniqueCode)


@wrapped_socketio('state', 'state')
def get_state():
    keep_alive()
    game = g.game
    self = get_player_manager().get_my_player()
    redirect_url = game2redirect(game, self)
    if redirect_url is not None and redirect_url != '/game':
        return GameState(redirect_to=redirect_url)
    return prepare_state(game, self)


@wrapped_socketio('endgame_state', 'endgame_state')
def get_endgame_state():
    keep_alive()
    game = g.game
    self = get_player_manager().get_my_player()
    redirect_url = game2redirect(game, self)
    if redirect_url is not None and redirect_url != '/endgame':
        return GameState(redirect_to=redirect_url)
    return prepare_state(game, self)


def prepare_state(game: GameLogic, player: PlayerLogic) -> GameState:
    pm = PlayerManager(db)
    if player is None:
        return GameState(
            redirect_to='/'
        )
    players = game.get_players(False)
    round_number = 0 if game.cur_round is None else game.cur_round.roundNo
    ui_game = UiGame(
        game_name=game.model.uniqueCode,
        self_player=player.model.id,
        players=[
            UiPlayer(
                id=p.model.id,
                name=p.model.name,
                is_admin=p.model.isAdmin,
                is_online=p.model.isOnline,
                has_left=p.model.hasLeft,
                on_offence=False,
                on_defence=False,
                neighbour_right=p.model.neighbourId,
                can_attack=game.can_attack(player, p),
                money=p.get_money(),
            ) for p in players
        ],
        hand=map_opt(lambda c: make_ui(c, game, player), player.get_hand()),
        current_battles=[battle.to_ui() for battle in game.get_battles(True)],
        round_no=round_number,
        is_complete=game.is_complete(),
    )

    return GameState(
        redirect_to='',
        game=ui_game
    )


def assert_has_game():
    if g.game is None:
        raise UserError("Игра не найдена")


def keep_alive():
    if g.game is not None:
        g.game.keep_alive()


@wrapped_socketio('log', 'log')
def log(starting_from):
    assert_has_game()
    keep_alive()
    return [x.to_ui() for x in g.game.get_old_rounds(starting_from)]


@wrapped_socketio('attack', 'attack')
def attack(player_id):
    assert_has_game()
    keep_alive()
    g.game.attack(
        get_player_manager().get_my_player(),
        get_player_manager().get_player(player_id)
    )


@wrapped_socketio('play', 'play')
def play_card(card_ids):
    assert_has_game()
    keep_alive()
    player = get_player_manager().get_my_player()
    for card in card_ids:
        g.game.play_card(get_card_manager().get_card(card), player)
    return True


@wrapped_socketio('done_def', 'done_def')
def done_defending():
    assert_has_game()
    keep_alive()
    g.game.end_battle(get_player_manager().get_my_player())


@wrapped_socketio('card', 'card')
def get_card(card_id):
    return get_card_manager().get_card(card_id).to_ui(True)


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


@mod_game_process.route('/endgame')
def endgame():
    set_current_player()
    try:
        game = get_game_manager().get_my_game()
        player = get_player_manager().get_my_player()
    except UserError:
        return redirect(url_for('gameselect.index'))
    return render_template('endgame.html', form=ExitForm())
