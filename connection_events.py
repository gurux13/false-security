from flask_socketio import SocketIO, emit

from game_logic.game_manager import GameManager
from game_logic.player_manager import PlayerManager
from game_logic.player_logic import PlayerLogic
from globals import socketio, db
from session import SessionHelper, SessionKeys
from utils.response import Response


@socketio.on('disconnect')
def on_disconnect():
    change_state(False)


@socketio.on('connect')
def on_connect():
    change_state(True)


def change_state(is_online: bool):
    if SessionHelper.has(SessionKeys.PLAYER_ID):
        pm = PlayerManager(db)
        player = pm.get_my_player()
        if player is None:
            return
        try:
            player.set_online(is_online)
            change_admin(is_online, player)
            print("made player online", player.model.name, is_online)
            db.session.commit()
            db.session.remove()
        except Exception as e:
            # emit('waitroom', Response.Error("Не удалось сменить статус").as_dicts())
            db.session.rollback()
            db.session.remove()
            raise


def change_admin(is_online: bool, player: PlayerLogic):
    if not is_online and player.model.isAdmin:
        gm = GameManager(db)
        new_adm = next((p.model for p in gm.get_my_game().get_players() if (not p.model.isAdmin and p.model.isOnline)), None)
        if new_adm is not None:
            new_adm.isAdmin = True
            player.model.isAdmin = False
            db.session.commit()
            gm.get_my_game().notify()

