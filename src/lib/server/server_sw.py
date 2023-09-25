from threading import Lock
from server_client_download import ServerClientDownload
from server_client_upload import ServerClientUpload
from src.lib.common.package import NormalPackage, HandshakePackage, EndHandshakePackage, InitialHandshakePackage
from src.lib.common.socket_wrapper import SocketWrapper
from src.lib.common.config import *
import logging


class ServerStopAndWait:
    def __init__(self, host: str, port: int, dirpath: str):
        self.host = host
        self.port = port
        self.dirpath = dirpath
        self.clients = []
        self.clients_lock = Lock() # TODO ojo con los try/catch en los locks que podemos dejar un deadlock si no tenemos un release en el finally
        self.socket_wrapper = SocketWrapper()
        self.socket_wrapper.bind(self.host, self.port)


    def start(self) -> None:
        logging.debug(' Listening...')
        while True:
            data, address = self.socket_wrapper.recvfrom(NORMAL_PACKAGE_SIZE)
            logging.debug(f' Received data from {address}: {data}')

            if address not in self.clients:
                self.clients.append(address) # TODO cambiar por una instancia de la clase cliente que corresponda, de ser necesario, de lo contrario borrarlas.
                incoming_package = InitialHandshakePackage(data)
                first_ack_package = HandshakePackage(incoming_package)
                self.socket_wrapper.sendto(address, first_ack_package.pack_handshake_return())
            else:
                incoming_package = EndHandshakePackage(data)
                #una vez que se recibe el ack y el seq en 0 no se hace nada mas
                #si es upload vos le envias el ack y el seq en 0 y no haces nada mas
                #si es download vos le envias el ack y el seq en 0 y le envias el paquete
                #una vez que envias, esperas el ack y el seq en 1
                #ese formato de paquete coincide con el endhandshakepackage, que tiene solo ack y seq (atr!!!)
               
                if first_ack_package.is_upload:
                    #server client upload debe recibir los paquetitos y guardarlos en un archivo
                    client = ServerClientUpload(address, incoming_package.file_name, incoming_package.file_size, incoming_package.seq, incoming_package.ack)
                else:
                    #server client download debe segmentar los paquetitos y segun el ack y el seq enviarlos
                    client = ServerClientDownload(address, incoming_package.file_name, incoming_package.file_size, incoming_package.seq, incoming_package.ack)

                

    def return_handshake_package(self, package: HandshakePackage, address: str) -> None:
        package = package.pack_handshake_return()
        self.socket_wrapper.sendto(package, address)

    def return_normal_package(self, package: NormalPackage, address: str) -> None:
        package = package.pack_normal_package_return()
        self.socket_wrapper.sendto(package, address)

    def add_client(self, client: ServerClientDownload) -> None:
        if client not in self.clients:
            with self.clients_lock:
                self.clients.append(client)
        # como sigue?
        # el cliente deberia tener un metodo que se encargue de recibir los paquetes
        # tambien saber todo lo que tiene que saber del archivo
