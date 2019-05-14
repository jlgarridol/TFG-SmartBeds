import smartbeds
smartbeds.start()

import threading
from gevent.monkey import patch_all
import smartbeds.vars as v
import smartbeds.routes.web
import smartbeds.routes.webapi
import smartbeds.routes.websocket as wbs

if __name__ == '__main__':
    patch_all()
    print("Parcheo completado")
    #threading.Thread(target=wbs.generate_request, daemon=True).start()
    print("Arranque")
    v.socketio.run(v.app, debug=True, host="127.0.0.1", port=3031)
    print("Cierre")
