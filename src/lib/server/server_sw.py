from threading import Lock
from lib.server.server_client_download import ServerClientDownload
from lib.server.server_client_upload import ServerClientUpload
from lib.common.package import PackageParser, NormalPackage, HandshakePackage
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
                self.process_handshake_package(package)
                self.return_handshake_package(package, address)

            except:
                try:
                    package = PackageParser.parse_normal_package(data)
                    for client in self.clients:
                        if client.address == address:
                            client.already_client = True
                    self.process_package(package)
                    NormalPackage.return_normal_package(address)

                except:
                    logging.debug(' Invalid package')
                    continue




    def process_handshake_package(self, package: PackageParser) -> None:
        if package.is_upload:
            self.add_client(ServerClientUpload(package.address, package.file_name, package.file_size, self.dirpath))
        else:
            self.add_client(ServerClientDownload(package.address, package.file_name, self.dirpath))



    def return_handshake_package(self, package: PackageParser, address: tuple) -> None:
        package = package.pack_handshake_return()
        self.socket_wrapper.sendto(package, address)

        

    def process_package(self, package: PackageParser) -> None:
        if package.is_upload:
            self.process_upload_package(package)
        else:
            self.process_download_package(package)


    def return_normal_package(self, package: PackageParser, address: tuple) -> None:
        package = package.pack_normal_package_return(package) #aca deberia recibir el paquete para que pueda usar sus atributos
        self.socket_wrapper.sendto(package, address)

    def add_client(self, client: ServerClientDownload) -> None:
        if client not in self.clients:
            with self.clients_lock:
                self.clients.append(client)
        #como sigue?
        #el cliente deberia tener un metodo que se encargue de recibir los paquetes
        #tambien saber todo lo que tiene que saber del archivo




            

            