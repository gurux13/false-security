from flask import Flask, render_template

from mod_test.test import mod_test
from flask import send_from_directory

if __name__ != '__main__':
    import sys
    import os
    if os.path.split(sys.argv[0])[1].replace('.py', '') == __name__:
        raise ImportError('No. Please do not import app. It will lead too all kinds of ridiculous stuff.')

import globals
app = globals.app

print('starting...')


@app.route('/io')
def hello_world():
    return render_template('test_io.html')

@app.route('/favicon.ico')
def favicon():
    import os
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')

@app.route('/instruction')
def rules():
   return render_template('instruction.html')

@app.route('/glossary')
def glossary():
   return render_template('glossary.html')


if True or __name__ == '__main__':
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
if __name__ == '__main__':
    globals.socketio.run(app)
