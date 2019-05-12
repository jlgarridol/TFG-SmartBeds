from flask import Flask
from smartbeds.api import api
from smartbeds.utils import *
import smartbeds.vars as v
from flask_socketio import SocketIO
import os

def start():
    print("Inicio de configuración de la aplicación")
    v.start()
    # Definir rutas
    STATIC_DIR = os.path.dirname(os.path.abspath(__file__)) + "/resources/assets"
    TEMPLATE_DIR = STATIC_DIR + "/html"
    #Crear aplicación
    v.app = Flask(__name__, static_folder=STATIC_DIR, template_folder=TEMPLATE_DIR)
    v.app.secret_key = get_secret_key()
    v.socketio = SocketIO(v.app)

    api.API(get_sql_config()) #Se instancia la API

    # Se cargan las camas
    print("Configuración terminada")

    v.after_db()


