from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

# I utterly hate Python sometimes
# https://stackoverflow.com/questions/46622408/flask-socket-io-message-events-in-different-files

try:
    from __main__ import app
except ImportError:
    from app import app

db = SQLAlchemy(app)
socketio = SocketIO(app)
