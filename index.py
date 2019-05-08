from smartbeds.routes.websocket import socketio as application
from smartbeds.routes.websocket import generate_request
import threading
from smartbeds import app

if __name__ == '__main__':
    threading.Thread(target=generate_request, daemon=True).start()
    application.run(app, debug=False)
