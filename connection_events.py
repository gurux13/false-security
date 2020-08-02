from flask_socketio import SocketIO

from game_logic.game_manager import GameManager
from game_logic.player_manager import PlayerManager
from globals import socketio, db
from session import SessionHelper, SessionKeys

@socketio.on('disconnect')
def on_disconnect():
    change_state(False)


@socketio.on('connect')
def on_connect():
    change_state(True)

def change_state(is_online: bool):
    if (SessionHelper.has(SessionKeys.PLAYER_ID)):
        pm = PlayerManager(db)
        player = pm.get_my_player()
        try:
            player.set_online(is_online)
            db.session.commit()
            db.session.remove()
        except Exception as e:
            emit('waitroom', Response.Error("Не удалось сменить статус").as_dicts())
            db.session.rollback()
            db.session.remove()
        print("made player online", is_online)
