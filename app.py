from flask import Flask, render_template

from mod_test.test import mod_test

if __name__ != '__main__':
    import sys
    import os
    if os.path.split(sys.argv[0])[1].replace('.py', '') == __name__:
        raise ImportError('No. Please do not import app. It will lead too all kinds of ridiculous stuff.')

app = Flask(__name__)

# TODO: Replace with server-side configuration
app.config['SECRET_KEY'] = 'secret!'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# install libmysqlclient-dev!
if False:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:Ey*zM5a1v4cu@localhost/fs?charset=utf8mb4'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

import globals


print('starting...')


@app.route('/io')
def hello_world():
    return render_template('test_io.html')

@app.route('/instruction')
def rules():
   return render_template('instruction.html')


if __name__ == '__main__':
    # Registering socketio listeners
    import mod_game.waitroom
    import mod_game.game_state
    import connection_events
    
    from mod_gameselect.controller import mod_gameselect

    app.register_blueprint(mod_gameselect)
    from mod_game.waitroom import mod_game_wr
    from mod_game.game_process import mod_game_process

    app.register_blueprint(mod_game_wr)
    app.register_blueprint(mod_game_process)
    app.register_blueprint(mod_test, url_prefix="/test")
    globals.socketio.run(app)
