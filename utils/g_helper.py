from flask import g

from globals import db
from logic.player_manager import PlayerManager
from session import SessionHelper, SessionKeys


def set_current_player():
    if SessionHelper.has(SessionKeys.PLAYER_ID):
        pm = PlayerManager(db)
        g.current_player = pm.get_my_player()



