"""Recibimos datos de la cama"""

from smartbeds.api import api
from smartbeds.process import new_bed_listeners
import smartbeds.vars as v
import eventlet


def load_beds_listeners():
    beds = api.API.get_instance().get_all_beds_info()
    for b in beds:
        print(b)
        new_bed_listeners(b['ip_group'], b['port'], b['bed_name'])


def get_processor(name):
    return v.processors[name]
