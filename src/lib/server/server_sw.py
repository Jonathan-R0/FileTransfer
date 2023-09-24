from threading import Lock
from server_client_download import ServerClientDownload
from src.lib.common.package import PackageParser, NormalPackage, HandshakePackage
from src.lib.common.socket_wrapper import SocketWrapper
import logging


class ServerStopAndWait:
    def __init__(self, host: str, port: int, dirpath: str):
        self.host = host
        self.port = port
        self.dirpath = dirpath
        self.clients = []
        self.clients_lock = Lock()
        self.socket_wrapper = SocketWrapper()
        self.socket_wrapper.bind(self.host, self.port)

    def start(self) -> None:
        logging.debug(' Listening...')
        while True:
            data, address = self.socket_wrapper.recvfrom(1024)
            logging.debug(f' Received data from {address}: {data}')

            try:
                package = PackageParser.parse_handshake_package(data)
                self.process_handshake_package(package)
                self.return_handshake_package(package, address)

            except:
                logging.debug(' Invalid handshake')
                continue

            try:
                package = PackageParser.parse_normal_package(data)
                for client in self.clients:
                    if client.address == address:
                        client.already_client = True
                self.process_package(package)
                self.return_normal_package(package, address)

            except:
                logging.debug(' Invalid package')
                continue

    def process_handshake_package(self, package: HandshakePackage) -> None:
        pass
        if package.is_upload:  # WARNING NO EXISTE ESTE ATRIBUTO
            # procesar paquetito
            pass

    def return_handshake_package(self, package: HandshakePackage, address: str) -> None:
        package = package.pack_handshake_return()
        self.socket_wrapper.sendto(package, address)

    def process_package(self, package: NormalPackage) -> None:
        pass
        if package.is_upload:  # WARNING NO EXISTE ESTE ATRIBUTO
            # procesar paquetito
            pass

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
