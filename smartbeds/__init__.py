import smartbeds.vars as v

def start():
    v.start()

    from flask import Flask
    from smartbeds import utils
    from flask_socketio import SocketIO
    import os

    print("Inicio de configuración de la aplicación")

    # Definir rutas
    STATIC_DIR = os.path.dirname(os.path.abspath(__file__)) + "/resources/assets"
    TEMPLATE_DIR = STATIC_DIR + "/html"
    # Crear aplicación
    v.app = Flask(__name__, static_folder=STATIC_DIR, template_folder=TEMPLATE_DIR)
    v.app.secret_key = utils.get_secret_key()
    v.socketio = SocketIO(v.app)
    print(v.app.secret_key)

    from smartbeds.api import api
    api.API(utils.get_sql_config())  # Se instancia la API

    # Se cargan las camas
    print("Configuración terminada")

    return v.after_db()


