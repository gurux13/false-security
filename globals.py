from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

# I utterly hate Python sometimes
# https://stackoverflow.com/questions/46622408/flask-socket-io-message-events-in-different-files

app = Flask(__name__)

# TODO: Replace with server-side configuration
app.config['SECRET_KEY'] = 'secret!'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# install libmysqlclient-dev!
if False:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://fs:<FSPASSWORD>@localhost/fs?charset=utf8mb4'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app)
