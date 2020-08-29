from functools import wraps

from flask import g
from flask_socketio import emit

from Exceptions.hack_attempt import HackAttemptError
from Exceptions.user_error import UserError
from globals import socketio, db
from logic.game_manager import GameManager
from utils.response import Response


def commit_and_notify_if_dirty():
    db.session.commit()
    if g.game is not None and g.game.is_dirty():
        g.game.notify()


def wrapped_socketio(message, response_message=None):
    def converter(handler):
        def thehandler(*args):
            rv = None
            gm = GameManager(db)
            g.game = gm.get_my_game(optional=True)
            try:
                rv = Response.Ok(handler(*args)).as_dicts()
                commit_and_notify_if_dirty()
            except UserError as e:
                rv = Response.Error("Ошибка действия: " + e.message).as_dicts()
                db.session.rollback()
            except HackAttemptError as e:
                rv = Response.Error("Неразрешённое действие: " + e.message)
                db.session.rollback()
            except Exception as e:
                rv = Response.Error(str(e)).as_dicts()
                db.session.rollback()
                raise
            finally:
                db.session.remove()
            if response_message is not None:
                emit(response_message, rv)
            else:
                if not rv['ok']:
                    print("NOT OK Response:", rv.message)

        return socketio.on(message)(thehandler)

    return converter
