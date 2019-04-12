import json
import os

def get_sql_config():
    with open(os.path.dirname(__file__)+'/resources/project.json') as f:
        data = json.load(f)
    return data['database']
