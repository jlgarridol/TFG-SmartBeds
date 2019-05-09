from smartbeds.routes.websocket import socketio
from smartbeds.routes.websocket import generate_request
import threading
from smartbeds import app
from gevent.monkey import patch_all

if __name__ == '__main__':
    patch_all()
    threading.Thread(target=generate_request, daemon=True).start()
    print("Lanzamiento")
    socketio.run(app, debug=False, host="127.0.0.1", port=3031)

