import smartbeds.vars as v


def start():
    v.start()

    from flask import Flask
    from smartbeds import utils
    from flask_socketio import SocketIO
    from flask_login import LoginManager
    from flask_session import Session
    import os

    print("Inicio de configuración de la aplicación")

    # Definir rutas
    STATIC_DIR = os.path.dirname(os.path.abspath(__file__)) + "/resources/assets"
    TEMPLATE_DIR = STATIC_DIR + "/html"
    # Otras constantes
    SESSION_TYPE = 'null'
    # Crear aplicación
    v.app = Flask(__name__, static_folder=STATIC_DIR, template_folder=TEMPLATE_DIR)
    v.app.config['SECRET_KEY'] = utils.get_secret_key()

    v.app.config['SESSION_TYPE'] = SESSION_TYPE
    v.login_manager = LoginManager()

    # Inicialización de aplicaciones
    v.login_manager.init_app(v.app)
    v.sess = Session(v.app)
    v.socketio = SocketIO(v.app)

    # COnfiguramos las aplicaciones
    import smartbeds.routes as routes
    v.login_manager.session_protection = "strong"
    v.login_manager.user_loader(routes.user_loader)

    from smartbeds.api import api
    api.API(utils.get_sql_config()) # Se instancia la API

    # Se cargan las camas
    print("Configuración terminada")

    return v.after_db()


