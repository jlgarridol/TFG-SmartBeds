import smartbeds.vars as v
from flask_socketio import emit
from smartbeds.process.receive import get_processor
from smartbeds.process.proc import BedProcess
from smartbeds.api import api
import numpy as np
from socketio import Client
from smartbeds.utils import get_sio_connect
import eventlet
from threading import Thread


class Broadcaster:

    def __init__(self, namespace, bed_processor: BedProcess, app):
        self._namespaces = ["/"+namespace]
        self._bed = bed_processor
        self._app = app

    def emiter(self):
        with v.app.app_context():
            while not self._bed.stopped:
                package = self._bed.next_package()
                if package is not None:
                    Broadcaster.clean_package(package)
                    for n in self._namespaces:
                        emit("package", package, namespace=n, json=True, broadcast=True)
                        eventlet.sleep(0)

    def add_namespace(self, namespace):
        self._namespaces.append("/"+namespace)

    @staticmethod
    def clean_package(package):
        for p in package:
            for i in range(len(package[p])):
                if issubclass(type(package[p][i]), np.integer):
                    package[p][i] = int(package[p][i])

    def start(self):
        Thread(target=self.emiter, daemon=True).start()


@v.socketio.on('give_me_data')
def give_me_data(data):
    """
    Este evento se lanzaría para garantizar
    que el proceso de recepción de datos ha
    comenzado. Crearía el broadcaster correspondiente
    si no estuviese y en caso de que ya exista
    no haría nada.

    :param data: diccionario con el espacio de nombres a escuchar
    """

    namespace = data['namespace']
    if v.version < 1 and len(v.namespace_threads) > 0:
        brd = v.namespace_threads.values()[0]
        brd.add_namespace(namespace)
        v.namespace_threads[namespace] = brd
    elif namespace not in v.namespace_threads:  # Se crea el listener
        v.namespace_threads[namespace] = Broadcaster(namespace, get_processor(data['bedname']), v.app)
        v.namespace_threads[namespace].start()


# Se generan request para todas las camas y mantener el broadcast
def generate_request(beds=None):
    if beds is None:
        beds = api.API.get_instance().get_all_beds_info()
    for bed in beds:
        namespace = bed['UUID']+"_"+bed['MAC']
        print("Comenzamos a escuchar")
        sio = Client()
        max_tries = 6
        tries = 0
        flag = False
        while max_tries > tries and not flag:
            try:
                sio.connect(get_sio_connect())
                flag = True
            except:
                tries += 1
                eventlet.sleep(1)
        if flag:
            sio.emit("give_me_data", {"namespace": namespace, "bedname": "Cama 1"})
        else:
            raise Exception("Conexión fallada")
        if v.version < 1:
            break  # En esta situación solo se crea una request.
