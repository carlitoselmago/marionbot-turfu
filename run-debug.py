#!venv/bin/python
import logging
from app.chat import *

sys.path.append("transfchatbot")
log = logging.getLogger('werkzeug')
log.disabled = True


if __name__ == '__main__':
    print("Open in http://localhost:8080/")
    socketio.run(app,debug=True,port="8080",host="0.0.0.0")

"""
#app.run(debug=True,port="8000",host="0.0.0.0")
socketio.run(app,debug=True,port="8000",host="0.0.0.0")
app.logger.disabled = True
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024    # 5 Mb limit
"""
