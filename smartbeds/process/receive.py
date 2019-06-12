"""Recibimos datos de la cama"""

import smartbeds.api as api
from smartbeds.process import new_bed_listeners
import smartbeds.vars as v


def load_beds_listeners():
    beds = api.API.get_instance().get_all_beds_info()
    mode = "ALL"
    if v.version < 1:
        mode = "ONLY"
    for b in beds:
        new_bed_listeners(b['ip_group'], b['port'], b['bed_name'], mode=mode)


def get_processor(name):
    return v.processors[name]
