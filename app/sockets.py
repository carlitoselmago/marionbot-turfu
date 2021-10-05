from flask_socketio import SocketIO

@socketio.on('browser_ready')
def test_connect():
    print('Client connected:')
