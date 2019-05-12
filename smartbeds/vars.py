def start():
    global app, socketio, db
    app = None
    socketio = None
    db = None


def after_db():
    from smartbeds.process.receive import load_beds_listeners

    load_beds_listeners()
