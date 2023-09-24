from threading import Lock
from lib.server.server_client_download import ServerClientDownload
from lib.server.server_client_upload import ServerClientUpload
from lib.common.package import PackageParser
from lib.common.socket_wrapper import SocketWrapper
import logging

class ServerStopAndWait:
    def __init__(self, host: str, port: int, dirpath: str):
        self.host = host
        self.port = port
        self.dirpath = dirpath
        self.clients = []
        self.clients_lock = Lock()
        self.socket_wrapper = SocketWrapper(self.host, self.port)

    def start(self) -> None:
        logging.debug(' Listening...')
        while True:
            data, address = self.socket_wrapper.recvfrom()
            logging.debug(f' Received data from {address}: {data}')
            try:
                package = PackageParser.parse_handshake_package(data)
                if package.is_upload:
                    self.add_client(ServerClientUpload(address, package.file_name, package.file_size, self.dirpath))
                else:
                    self.add_client(ServerClientDownload(address, package.file_name, self.dirpath))
            except:
                try:
                    package = PackageParser.parse_normal_package(data)
                    for client in self.clients:
                        if client.address == address:
                            client.process_package(package) ## TODO implementar
                except:
                    logging.debug(' Invalid package')
                    continue


    def add_client(self, client: ServerClientDownload) -> None:
        if client not in self.clients:
            with self.clients_lock:
                self.clients.append(client)
        #como sigue?
        #el cliente deberia tener un metodo que se encargue de recibir los paquetes
        #tambien saber todo lo que tiene que saber del archivo




            

            