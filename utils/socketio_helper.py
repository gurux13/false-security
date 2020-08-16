from functools import wraps

from flask_socketio import emit

from Exceptions.hack_attempt import HackAttemptError
from Exceptions.user_error import UserError
from globals import socketio, db
from utils.response import Response


def wrapped_socketio(message, response_message=None):
    def converter(handler):
        def thehandler(*args):
            rv = None
            try:
                rv = Response.Ok(handler(*args)).as_dicts()
                db.session.commit()
            except UserError as e:
                rv = Response.Error("Ошибка действия: " + e.message).as_dicts()
                db.session.rollback()
            except HackAttemptError as e:
                rv = Response.Error("Неразрешённое действие: " + e.message)
                db.session.rollback()
            except Exception as e:
                rv = Response.Error(str(e)).as_dicts()
                db.session.rollback()
                #raise
            finally:
                db.session.remove()
            if response_message is not None:
                emit(response_message, rv)
        return socketio.on(message)(thehandler)

    return converter
