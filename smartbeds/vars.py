import threading

version = 0.15


def start():
    global app, socketio, db, bed_listeners, processors, namespace_threads, login_manager, sess
    app = None
    socketio = None
    db = None
    login_manager = None
    sess = None
    bed_listeners = {}
    processors = {}
    namespace_threads = {}


def after_db():
    from smartbeds.process.receive import load_beds_listeners

    th = threading.Thread(target=load_beds_listeners, daemon=True)
    th.start()

    return th
