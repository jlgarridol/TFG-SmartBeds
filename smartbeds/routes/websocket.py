from smartbeds import app
from flask_socketio import SocketIO
from flask_socketio import emit
from smartbeds.process.receive import get_processor
from smartbeds.process.receive import BedProcess
from smartbeds.api.api import API
import numpy as np
from socketio import Client
from smartbeds.utils import get_sio_connect

from threading import Thread

socketio = SocketIO(app)
namespace_threads = {}


class Broadcaster:

    def __init__(self, namespace, bed_processor: BedProcess, app):
        self._namespace = "/"+namespace
        self._bed = bed_processor
        self._app = app

    def emiter(self):
        with app.app_context():
            while not self._bed.stopped:
                package = self._bed.next_package()
                if package is not None:
                    Broadcaster.clean_package(package)
                    emit("package", package, namespace=self._namespace, json=True, broadcast=True)

    @staticmethod
    def clean_package(package):
        for p in package:
            for i in range(len(package[p])):
                if issubclass(type(package[p][i]), np.integer):
                    package[p][i] = int(package[p][i])

    def start(self):
        Thread(target=self.emiter, daemon=True).start()


@socketio.on('give_me_data')
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
    if namespace not in namespace_threads:  # Se crea el listener
        namespace_threads[namespace] = Broadcaster(namespace, get_processor(data['bedname']), app)
        namespace_threads[namespace].start()


# Se generan request para todas las camas y mantener el broadcast
def generate_request():
    beds = API.get_instance().get_all_beds_info()
    for bed in beds:
        namespace = bed['UUID']+"_"+bed['MAC']
        print(namespace)
        sio = Client()
        sio.connect(get_sio_connect())
        sio.emit("give_me_data", {"namespace": namespace, "bedname": "Cama 1"})

