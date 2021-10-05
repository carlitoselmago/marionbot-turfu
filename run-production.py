#!venv/bin/python
#from app import app
#from flask_socketio import SocketIO
from app.chat import *

#socketio = SocketIO(app)
#app.run(debug=False, host="0.0.0.0", port=10000)
socketio.run(app,debug=True,port="5000",host="0.0.0.0")
