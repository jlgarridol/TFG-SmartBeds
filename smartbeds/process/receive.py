"""Recibimos datos de la cama"""

import socket
import struct
from queue import Queue
from threading import Thread
from smartbeds.api.api import API
from smartbeds.process.proc import BedProcess

_bed_listeners = {}
_processors = {}

class BedListener:

    def __init__(self, ip: str, port: int):
        self._ip = ip
        self._port = port
        self.stopped = False
        self._queue = Queue()

    def stop(self):
        self.stopped = True

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self._ip, self._port))
        group = socket.inet_aton(self._ip)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while not self.stopped:
            package = s.recv(1024).decode("utf-8")
            self._queue.put(package)

    def next_package(self):
        if self._queue.empty():
            return None
        else:
            return self._queue.get()

    def start(self):
        Thread(target=self.run, daemon=True).start()


def load_beds_listeners():
    beds = API.get_instance().get_all_beds_info()
    for b in beds:
        new_bed_listeners(b['ip_group'], b['port'], b['bed_name'])


def new_bed_listeners(ip: str, port: int, name: str):
    global _bed_listeners

    bed = BedListener(ip, port)
    bed.start()
    bedp = BedProcess(bed)
    bedp.start()
    _bed_listeners[name] = bed
    _processors[name] = bedp


def remove_bed_listener(name: str):
    global _bed_listeners

    bed = _bed_listeners.pop(name)
    if bed is not None:
        bed.stop()


def get_processor(name):
    return _processors[name]
