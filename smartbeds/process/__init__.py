import socket
import struct
from queue import Queue
from threading import Thread
from smartbeds.process.proc import BedProcess
import smartbeds.vars as v


def new_bed_listeners(ip: str, port: int, name: str):
    global _bed_listeners
    print("Lanzando procesos de la cama:", name)
    bed = BedListener(ip, port)
    bed.start()
    bedp = BedProcess(bed)
    bedp.start()
    v.bed_listeners[name] = bed
    v.processors[name] = bedp


def remove_bed_listener(name: str):
    global _bed_listeners

    bed = _bed_listeners.pop(name)
    if bed is not None:
        bed.stop()


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
