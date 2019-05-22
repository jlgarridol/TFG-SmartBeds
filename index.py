import smartbeds
import sys
import smartbeds.vars as v
import threading
import traceback

if __name__ == '__main__':

    try:
        th = smartbeds.start()
        th.join()
        print("Comenzamos")

        from eventlet import monkey_patch as patch_all
        patch_all()
        print("Parcheo completado")
        sys.stdout.flush()

        import smartbeds.routes.web
        import smartbeds.routes.webapi
        import smartbeds.routes.websocket as wbs

        th.join()
        threading.Thread(target=wbs.generate_request, daemon=True).start()
        print("Arranque")
        sys.stdout.flush()
        v.socketio.run(v.app, debug=False, host="127.0.0.1", port=3031)
        print("Cierre")
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception:
        traceback.print_exc()
