from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
import os
import sys

# I utterly hate Python sometimes
# https://stackoverflow.com/questions/46622408/flask-socket-io-message-events-in-different-files

local_mode = len(sys.argv) == 2 and sys.argv[1] == 'local'

if not local_mode:
    critical_env = ['FLASK_KEY', 'MYSQL_USER', 'MYSQL_PASSWORD']
    for env in critical_env:
        if env not in os.environ or len(os.environ[env]) == 0:
            raise Exception("Missing critical env " + env)

FLASK_KEY = 'Changeme' if local_mode else os.environ['FLASK_KEY']
MYSQL_USER = '' if local_mode else os.environ['MYSQL_USER']
MYSQL_PASSWORD = '' if local_mode else os.environ['MYSQL_PASSWORD']

app = Flask(__name__)

app.config['SECRET_KEY'] = FLASK_KEY
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# install libmysqlclient-dev!
if not local_mode:
    app.config[
        'SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://' + MYSQL_USER + ':' + \
                                     MYSQL_PASSWORD + '@localhost/fs?charset=utf8mb4'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app)
