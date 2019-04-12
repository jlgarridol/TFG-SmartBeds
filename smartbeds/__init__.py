from flask import Flask
from mysql.connector import MySQLConnection
from smartbeds.api import api
from smartbeds.utils import get_sql_config

app = Flask(__name__)
db = MySQLConnection(**get_sql_config())
api.API(db)

import smartbeds.routes.webapi

