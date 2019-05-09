from smartbeds.routes.websocket import socketio as application
from smartbeds.routes.websocket import generate_request
import threading
from smartbeds import app
#from eventlet import monkey_patch as patch_all
from gevent.monkey import patch_all
import gevent

if __name__ == '__main__':
    patch_all()
    threading.Thread(target=generate_request, daemon=True).start()
    print("Lanzamiento")
    application.run(app, debug=False)
