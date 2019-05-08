from flask import Flask
from mysql.connector import MySQLConnection
from smartbeds.api import api
from smartbeds.utils import *
from smartbeds.process.receive import load_beds_listeners
import os

#Definir rutas
STATIC_DIR = os.path.dirname(os.path.abspath(__file__)) + "/resources/assets"
TEMPLATE_DIR = STATIC_DIR + "/html"

#exit(0)
app = Flask(__name__, static_folder=STATIC_DIR, template_folder=TEMPLATE_DIR)
app.secret_key = get_secret_key()

db = MySQLConnection(**get_sql_config())
api.API(db) #Se instancia la API

# Se cargan las camas
load_beds_listeners()

import smartbeds.routes.web
import smartbeds.routes.webapi
import smartbeds.routes.websocket


