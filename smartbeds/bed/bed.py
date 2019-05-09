"""
Simulador de datos de una cama real.
Cada 400 milisegundos se envía un dato a través de UDP sobre la red local.
"""
from time import sleep
import socket, traceback, sys, struct

__author__="José Luis Garrido Labrador"
IP = "224.3.29.71"
PORT = 5007
MULTICAST_TTL = 2
INTERVAL = 0.4

if __name__ == "__main__":
    # Creamos un socket (según https://stackoverflow.com/questions/603852/how-do-you-udp-multicast-in-python)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ttl = struct.pack('b', 1)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    try:
        # Leemos los datos reales de la cama
        with open('data.csv', 'r', encoding="utf-8") as data:
            # Ignoramos la cabecera
            _ = data.readline()
            # La ejecución es hasta el final
            # a menos que se mate el proceso
            while True:
                row = data.readline() # Se lee una linea
                if not row: # Si se acaba el fichero
                    data.seek(0, 0) # Se vuelve a empezar
                    # Y se vuelve a ignorar la primera linea
                    _ = data.readline()
                else:  # En caso contrario enviamos el paquete
                    s.sendto(bytes(row, "utf-8"), (IP, PORT))
                    print(row)
                    sys.stdout.flush()
                    sleep(INTERVAL)  # Esperamos a mandar un nuevo paquete
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception:
        traceback.print_exc()
