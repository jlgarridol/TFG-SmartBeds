import json
import os
import pickle as pk

with open(os.path.dirname(__file__) + '/resources/project.json') as f:
    data = json.load(f)


def get_sql_config():
    return data['database']


def get_secret_key():
    return data['secret-key']


def get_sio_connect():
    return data['url']+":"+str(data['port'])


def get_model():
    with open(os.path.dirname(__file__) + '/resources/rfc.pkl', 'rb') as rfc:
        r = pk.load(rfc)
    return r


def new_number():
    return data['number']+1