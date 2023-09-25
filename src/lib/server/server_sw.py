from threading import Lock
from server_client_download import ServerClientDownload
from src.lib.common.package import NormalPackage, HandshakePackage, EndHandshakePackage, NormalPackage
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

            if address not in clients:
                clients.append(address) # TODO cambiar por una instancia de la clase cliente que corresponda, de ser necesario, de lo contrario borrarlas.
                incoming_package = InitialHandshakePackage(data)
                first_ack_package = HandshakePackage(incoming_package)
                self.socket_wrapper.sendto(address, first_ack_package.pack_handshake_return())
            else:
                try:
                    incoming_package = NormalPackage(data)
                

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
