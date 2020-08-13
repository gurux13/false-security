from functools import wraps

from flask_socketio import emit

from globals import socketio, db
from utils.response import Response


def wrapped_socketio(message, response_message=None):
    def converter(handler):
        def thehandler(*args):
            rv = None
            try:
                rv = Response.Ok(handler(*args)).as_dicts()
                db.session.commit()
            except Exception as e:
                rv = Response.Error(str(e)).as_dicts()
                db.session.rollback()
                raise
            finally:
                db.session.remove()
            if response_message is not None:
                emit(response_message, rv)
        return socketio.on(message)(thehandler)

    return converter
