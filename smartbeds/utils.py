import json
import os

with open(os.path.dirname(__file__) + '/resources/project.json') as f:
    data = json.load(f)


def get_sql_config():
    return data['database']


def get_secret_key():
    return data['secret-key']