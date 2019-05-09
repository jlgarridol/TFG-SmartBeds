from smartbeds.routes.websocket import socketio as application
from smartbeds.routes.websocket import generate_request
import threading
from smartbeds import app
from gevent.monkey import patch_all

if __name__ == '__main__':
    patch_all()
    threading.Thread(target=generate_request, daemon=True).start()
    print("Lanzamiento")
    application.run(app)
