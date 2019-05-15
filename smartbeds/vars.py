def start():
    global app, socketio, db, bed_listeners, processors
    app = None
    socketio = None
    db = None
    bed_listeners = {}
    processors = {}


def after_db():
    from smartbeds.process.receive import load_beds_listeners

    #load_beds_listeners()
