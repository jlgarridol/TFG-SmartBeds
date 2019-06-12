import threading

version = 0.15


def start():
    global app, socketio, db, bed_listeners, processors, namespace_threads, testusers
    app = None
    socketio = None
    db = None
    bed_listeners = {}
    processors = {}
    namespace_threads = {}
    testusers=0


def after_db():
    from smartbeds.process.receive import load_beds_listeners

    th = threading.Thread(target=load_beds_listeners, daemon=True)
    th.start()

    return th
