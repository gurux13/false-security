from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from mod_gameselect.controller import mod_gameselect


app = Flask(__name__)
# TODO: Replace with server-side configuration
app.config['SECRET_KEY'] = 'secret!'
app.register_blueprint(mod_gameselect)

socketio = SocketIO(app)
print('starting...')
@app.route('/io')
def hello_world():
    return render_template('test_io.html')

@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)

@socketio.on('my event')
def handle_my_custom_event(arg1):
    print('received args: ' + str(arg1))

count = 0

@socketio.on('clicked')
def handle_my_custom_event2():
    global count
    count += 1
    emit('upd', count, broadcast=True)
    print('sent')

if __name__ == '__main__':
    socketio.run(app)

