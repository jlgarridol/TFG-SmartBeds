from flask import Flask
from mysql.connector import MySQLConnection
from smartbeds.api import api
from smartbeds.utils import *

app = Flask(__name__)
app.secret_key = get_secret_key()
db = MySQLConnection(**get_sql_config())
api.API(db) #Se instancia la API

import smartbeds.routes.webapi #Se añaden las rutas de la Api

